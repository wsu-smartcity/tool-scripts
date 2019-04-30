## ***************************************
# Authors: Jing Xie, Xin Li
# Updated Date: 2019-4-30
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
            return json.dumps({"type": "load", "name": self.name, "bus1": self.bus1, "kw": self.kW, "kvar": self.kvar})

        def get_dict(self):
            return {"name": self.name, "bus1": self.bus1, "kw": self.kW, "kvar": self.kvar}

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

    def sum_load_microgrid(self, mg_bus_list):
        mg_kw_total = 0
        mg_kvar_total = 0

        for cur_item in self.loads_list:
            cur_bus_id_str = cur_item["bus1"].split('.')[0]
            
            if cur_bus_id_str in mg_bus_list:
                mg_kw_total += float(cur_item["kw"])
                mg_kvar_total += float(cur_item["kvar"])

        return mg_kw_total, mg_kvar_total


if __name__ == '__main__':
    dss_file_path_fn = 'IEEE123Master.dss' #Note that the filename cannot end with slash(es)
    p = DssParser(dss_file_path_fn)
    p.read_content(dss_file_path_fn)

    #==Test the function that sums up the total load of a microgrid
    #print(p.loads_list)
    
    #--MG2
    mg2_bus_list = str([48,47,49,50,51,151,
                        44,45,46,
                        42,43,
                        40,41,
                        135,35,39,
                        37,36,38])
    mg2_kw_total, mg2_kvar_total = p.sum_load_microgrid(mg2_bus_list)
    print("Microgrid #2: {} kW, {} kVar".format(mg2_kw_total,mg2_kvar_total))

    #--MG3
    mg3_bus_list = str([300,111,
                        108,109,110,112,113,
                        105,106,107,114,
                        101,102,103,104,
                        197])
    mg3_kw_total, mg3_kvar_total = p.sum_load_microgrid(mg3_bus_list)
    print("Microgrid #3: {} kW, {} kVar".format(mg3_kw_total,mg3_kvar_total))

    #--MG4
    mg4_bus_list = str([97,98,99,100,450,451,
                        67,68,69,70,71,
                        72,73,74,75,
                        76,77,78,79,
                        96,94,80,85,
                        95,93,91,89,87,86,81,84,
                        195,92,90,88,82,83])
    mg4_kw_total, mg4_kvar_total = p.sum_load_microgrid(mg4_bus_list)
    print("Microgrid #4: {} kW, {} kVar".format(mg4_kw_total,mg4_kvar_total))

    #--MG_ALL
    mg_all_bus_list = str(list(range(1000)))
    mg_all_kw_total, mg_all_kvar_total = p.sum_load_microgrid(mg_all_bus_list)
    print("Microgrid #all: {} kW, {} kVar".format(mg_all_kw_total,mg_all_kvar_total))
