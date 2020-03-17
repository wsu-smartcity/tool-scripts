## ***************************************
# Author: Jing Xie
# Created Date: 2020-3
# Updated Date: 2020-3-17
# Email: jing.xie@pnnl.gov
## ***************************************

import os.path
import json

class JsonExporter:
    """Parse the .glm file(s) and analysis/export"""
    def __init__(self, json_path_fn, json_data_dic):
        #==Path & dict
        self.json_path_fn = json_path_fn
        self.json_fn = os.path.basename(json_path_fn)
        self.json_path = os.path.dirname(json_path_fn)

        self.json_data_dic = json_data_dic
    
    def export_json(self):
        """Export json file
        """
        with open(self.json_path_fn, 'w') as hf_json:
            json.dump(self.json_data_dic, hf_json, sort_keys=False, indent=4)

def test_export_json():
    #==Parameters
    output_json_path_fn = 'Duke_gld_config.json'

    data = {'name': 'GLD',
            'coreType': 'zmq',
            'loglevel': 7,
            'period': 1e-2,
            'wait_for_current_time_update': True,
            }

    """
    data["endpoints"] = [
    {
      "name": "CB2",
      "type": "string",
      "info": "{\"object\" : \"CB_2\",\"property\" : \"status\"}"
    },
    {
      "name": "CB3",
      "type": "string",
      "info": "{\"object\" : \"CB_3\",\"property\" : \"status\"}"
    },
    {
      "name": "RCL3",
      "type": "string",
      "info": "{\"object\" : \"RCL3\",\"property\" : \"status\"}"
    }]
    """
    
    #==Prepare
    list_cbs = ['CB' + str(x) for x in range(1,3)]
    list_rcls = ['RCL' + str(x) for x in range(1,3)]
    
    #print(list_cbs)
    #print(list_rcls)

    ep_type = 'string'
    ep_property = "status"

    ep_list = []
    for cur_comp_str in list_cbs:
        print(cur_comp_str)
        cur_comp_dic = {}
        cur_comp_dic['name'] = cur_comp_str
        cur_comp_dic['type'] = ep_type

        cur_ep_info_str = ''
        cur_ep_info_dic = {"object": "RCL3", "property": "status"}
        cur_comp_dic['info'] = json.dumps(cur_ep_info_dic)

        ep_list.append(cur_comp_dic)
    print(ep_list)

    data["endpoints"] = ep_list
    
    #==Test & Demo
    p = JsonExporter(output_json_path_fn,data)
    p.export_json()

    luan = """{"wait_for_current_time_update": true}"""
    info = json.loads(luan)
    print(info)


if __name__ == '__main__':
    test_export_json()
