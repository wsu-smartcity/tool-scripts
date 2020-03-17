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
    def __init__(self):
        """
        #==Path & dict
        self.json_path_fn = json_path_fn
        self.json_fn = os.path.basename(json_path_fn)
        self.json_path = os.path.dirname(json_path_fn)

        self.json_data_dic = json_data_dic
        """
    
    def export_json(self, json_path_fn, json_data_dic):
        """Export json file
        """
        with open(json_path_fn, 'w') as hf_json:
            json.dump(json_data_dic, hf_json, sort_keys=False, indent=4)

def luan(list_cbs, ep_obj_dict):
    ep_type = 'string'
    ep_property = "status"

    ep_list = []
    for cur_comp_str in list_cbs:
        cur_ep_dic = {}
        cur_ep_dic['name'] = cur_comp_str
        cur_ep_dic['type'] = ep_type

        if cur_comp_str in ep_obj_dict:
            cur_ep_info_obj = ep_obj_dict[cur_comp_str]
        else:
            cur_ep_info_obj = cur_comp_str    
        cur_ep_info_dic = {"object": cur_ep_info_obj, "property": ep_property}
        cur_ep_dic['info'] = json.dumps(cur_ep_info_dic)

        ep_list.append(cur_ep_dic)

    return ep_list

def test_export_json():
    #==Parameters
    output_json_path_fn = 'Duke_gld_config.json'

    #--file configs
    json_data_settings_dic = {'name': 'GLD',
            'coreType': 'zmq',
            'loglevel': 7,
            'period': 1e-2,
            'wait_for_current_time_update': True,
            }
    #--end Points
    list_cbs_key = ['CB' + str(x) for x in range(1,5)]
    list_cbs_val = ['CB_' + str(x) for x in range(1,5)]
    ep_cbs_obj_dict = dict(zip(list_cbs_key, list_cbs_val))
    ep_cbs_list = luan(list_cbs_key, ep_cbs_obj_dict)
    
    list_rcls_key = ['RCL' + str(x) for x in range(1,13)]
    ep_rcls_obj_dict = {'RCL1': 'RCL1_53547349_1207',
                        'RCL2': 'RCL2_53547361_1207',
                        'RCL5': 'RCL5_410845731_1209',
                        'RCL7': 'RCL7_39067965_1210',
                        'RCL8': 'RCL8_164887213_1210',
                        'RCL9': 'RCL9_39057658_1209',
                        'RCL10': 'RCL11_616009826_1210',
                        'RCL11': 'RCL11_616009826_1210',
                        'RCL12': 'RCL12_164887203_1212'}
    ep_rcls_list = luan(list_rcls_key, ep_rcls_obj_dict)

    #--prepare
    data = {}
    data.update(json_data_settings_dic)
    data["endpoints"] = ep_cbs_list + ep_rcls_list
    
    #==Test & Demo
    p = JsonExporter()
    p.export_json(output_json_path_fn,data)


if __name__ == '__main__':
    test_export_json()
