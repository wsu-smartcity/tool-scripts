## ***************************************
# Author: Jing Xie
# Created Date: 2020-3
# Updated Date: 2020-3-18
# Email: jing.xie@pnnl.gov
## ***************************************

import os.path
import json

class JsonExporter:
    """Parse the .glm file(s) and analysis/export"""
    def __init__(self):
        """
        """
    
    def export_json(self, json_path_fn, json_data_dic, sort_flag = False, indent_val = 4):
        """Export json file
        """
        with open(json_path_fn, 'w') as hf_json:
            json.dump(json_data_dic, hf_json, sort_keys=sort_flag, indent=indent_val)

    @staticmethod
    def get_endpoints(list_cbs, ep_obj_dict, ep_type, ep_property, ep_global=False):
        ep_list = []
        for cur_comp_str in list_cbs:
            cur_ep_dic = {}
            cur_ep_dic['global'] = ep_global
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
    #~~switches
    ep_type = 'string'
    ep_property = "status"
    
    list_cbs_key = ['CB' + str(x) for x in range(1,5)]
    list_cbs_val = ['CB_' + str(x) for x in range(1,5)]
    ep_cbs_obj_dic = dict(zip(list_cbs_key, list_cbs_val))
    ep_cbs_list = JsonExporter.get_endpoints(list_cbs_key, ep_cbs_obj_dic,
                                             ep_type, ep_property)
    
    list_rcls_key = ['RCL' + str(x) for x in range(1,13)]
    ep_rcls_obj_dic = {'RCL1': 'RCL1_53547349_1207',
                        'RCL2': 'RCL2_53547361_1207',
                        'RCL5': 'RCL5_410845731_1209',
                        'RCL7': 'RCL7_39067965_1210',
                        'RCL8': 'RCL8_164887213_1210',
                        'RCL9': 'RCL9_39057658_1209',
                        'RCL11': 'RCL11_616009826_1210',
                        'RCL12': 'RCL12_164887203_1212'}
    ep_rcls_list = JsonExporter.get_endpoints(list_rcls_key, ep_rcls_obj_dic,
                                              ep_type, ep_property)

    #~~inverters
    ep_inv_type = 'string'
    ep_inv_property = 'Q_Out'

    list_invs_key = ['PV_S2_n256860617_1207']
    list_invs_val = ['Inv_S2_n256860617_1207']
    ep_invs_obj_dic = dict(zip(list_invs_key, list_invs_val))
    ep_invs_list = JsonExporter.get_endpoints(list_invs_key, ep_invs_obj_dic,
                                              ep_inv_type, ep_inv_property)
    
    #--prepare
    data = {}
    data.update(json_data_settings_dic)
    data["endpoints"] = ep_cbs_list + ep_rcls_list + ep_invs_list
    
    #==Test & Demo
    p = JsonExporter()
    p.export_json(output_json_path_fn,data)


if __name__ == '__main__':
    test_export_json()
