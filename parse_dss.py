## ***************************************
# Authors: Jing Xie, Xin Li
# Updated Date: 2019-1-18
# Emails: jing.xie@ucdconnect.ie
#  ***************************************

import re
import json
import os.path
import ntpath


class DssParser:
    def __init__(self, master_file):
        self.master_file = ntpath.basename(master_file)
        self.file_path = ntpath.dirname(master_file)
        self.master_file_noext, _ = os.path.splitext(master_file)

        self.switch_line_threshold = 0.005
        self.special_transformer_flag = 0
        self.special_transformer = self.Transformer(0,0,0)

        self.lines_list = []
        self.switches_list = []
        self.loads_list = []

    def get_master_file_noext(self):
        return self.master_file_noext

    class Transformer:
        def __init__(self, name, bus1, bus2):
            self.name = name
            self.bus1 = bus1
            self.bus2 = bus2

        def __str__(self):
            return json.dumps({"type": "transformer", "name": self.name, "bus1": self.bus1, "bus2": self.bus2})

        def get_dict(self):
            return {"name": self.name, "bus1": self.bus1, "bus2": self.bus2}

    class Line:
        def __init__(self, name, bus1, bus2):
            self.name = name
            self.bus1 = bus1
            self.bus2 = bus2

        def __str__(self):
            return json.dumps({"type": "line", "name": self.name, "bus1": self.bus1, "bus2": self.bus2})

        def get_dict(self):
            return {"name": self.name, "bus1": self.bus1, "bus2": self.bus2}

    class Switch:
        def __init__(self, name, bus1, bus2):
            self.name = name
            self.bus1 = bus1
            self.bus2 = bus2

        def __str__(self):
            return json.dumps({"type": "switch", "name": self.name, "bus1": self.bus1, "bus2": self.bus2})

        def get_dict(self):
            return {"name": self.name, "bus1": self.bus1, "bus2": self.bus2}

    class Load:
        def __init__(self, name, bus1, kW, kvar):
            self.name = name
            self.bus1 = bus1
            self.kW = kW
            self.kvar = kvar

        def __str__(self):
            return json.dumps({"type": "load", "name": self.name, "bus1": self.bus1, "kW": self.kW, "kvar": self.kvar})

        def get_dict(self):
            return {"name": self.name, "bus1": self.bus1, "kw": self.kW}

    def parse_transformer(self, line):
        if 'new transformer' in line:
            # print("transformer found")
            name = re.match(r'.*new transformer.(.*?) .*', line, re.M | re.I).group(1)
            bus1 = re.match(r'.* buses=\[(.*?) (.*?)\] .*', line, re.M | re.I).group(1)
            bus2 = re.match(r'.* buses=\[(.*?) (.*?)\] .*', line, re.M | re.I).group(2)

            #[This helps with removing the leading and trailing space. However, there may be other tricky formats/symbols need to be handled.]
            #[@TODO: In the DSS file, there cannot be space between the '=' and bus ID, e.g., "bus= 61s" will not work.]
            bus2 = bus2.strip()

            cur_trans = self.Transformer(name, bus1, bus2)
            print(cur_trans)
            self.lines_list.append(cur_trans.get_dict()) # [Note that transformers are counted as lines.]
        else:
            pass

    def parse_line_or_switch(self, line):
        if 'New Line' in line:
            length = re.match(r'.*Length=(.*?)[ |\n]', line, re.M | re.I).group(1)

            name = re.match(r'.*NEW Line.(.*?) .*', line, re.M | re.I).group(1)

            #[Solved: It is good to be able to hanlde this case, in which the line name has space and is quoted.
            #    e.g., New Line."MG1 Circuit Breaker". Although it is uncertain whether this is allowed in OpenDSS or not.]
            if '"' in name:
                name = re.match(r'.*NEW Line."(.*?)" .*', line, re.M | re.I).group(1)
            
            bus1 = re.match(r'.*Bus1=(.*?) .*', line, re.M | re.I).group(1)
            bus2 = re.match(r'.*Bus2=(.*?) .*', line, re.M | re.I).group(1)

            if float(length) > self.switch_line_threshold:
                # print("Line found")
                cur_line = self.Line(name, bus1, bus2)
                print(cur_line)
                self.lines_list.append(cur_line.get_dict())
            else:
                # print("Switch found")
                cur_switch = self.Switch(name, bus1, bus2)
                print(cur_switch)
                self.switches_list.append(cur_switch.get_dict())
        else:
            pass

    def parse_load(self, line):
        if 'New Load' in line:
            name = re.match(r'.*New Load.(.*?) .*', line, re.M | re.I).group(1)
            bus1 = re.match(r'.*Bus1=(.*?) .*', line, re.M | re.I).group(1)
            kw = re.match(r'.*kw=(.*?) .*', line, re.M | re.I).group(1)
            kvar = re.match(r'.*kvar=(.*?)[ |\n]', line, re.M | re.I).group(1)

            cur_load = self.Load(name, bus1, kw, kvar)
            print(cur_load)
            self.loads_list.append(cur_load.get_dict())


    def read_content(self, file_name):
        o_file = open(file_name, 'r')
        for line in o_file.readlines():
            # print(line)
            if line[0] == '!':
                continue

            if 'Redirect' in line:
                new_file_name = re.sub("\s+", " ", line).split(' ')[1]
                if os.path.exists(self.file_path + new_file_name):
                    self.read_content(self.file_path + new_file_name)

                continue

            if 'New Transformer' in line:
                self.special_transformer.name = re.match(r'.*New Transformer.(.*?) .*', line, re.M | re.I).group(1)
                self.special_transformer_flag = 1
                continue

            if self.special_transformer_flag == 1 and '~ wdg=1' in line:
                self.special_transformer.bus1 = re.match(r'.*bus=(.*?) .*', line, re.M | re.I).group(1)
                self.special_transformer_flag = 1

            if self.special_transformer_flag == 1 and '~ wdg=2' in line:
                self.special_transformer.bus2 = re.match(r'.*bus=(.*?) .*', line, re.M | re.I).group(1)
                # print('special transformer found')
                print(self.special_transformer)
                self.lines_list.append(self.special_transformer.get_dict())
                self.special_transformer_flag = 0
                continue

            self.parse_transformer(line)
            self.parse_line_or_switch(line)
            self.parse_load(line)


if __name__ == '__main__':
    dss_file_path_fn = 'IEEE123Master.dss' #Note that the filename cannot end with slash(es)
    p = DssParser(dss_file_path_fn)
    p.read_content(dss_file_path_fn)



