# ***************************************
# Author: Jing Xie
# Created Date: 2020-3
# Updated Date: 2020-3-20
# Email: jing.xie@pnnl.gov
# ***************************************

import os.path
import json
import warnings


class JsonExporter:
    """Export the .json file(s)"""

    def __init__(self):
        """
        """

    def dump_json(self, json_path_fn, json_data_dic,
                  sort_flag=False, indent_val=4):
        """Dump the data dictionary into a json file
        """
        with open(json_path_fn, 'w') as hf_json:
            json.dump(json_data_dic, hf_json,
                      sort_keys=sort_flag, indent=indent_val)

    @staticmethod
    def get_gld_endpoints(gld_comp_list, gld_ep_obj_dic, ep_property,
                          ep_type='string', ep_global=False):
        """
        Static method for handling different types of endpoints
        """
        glp_ep_list = []
        for cur_comp_str in gld_comp_list:
            cur_ep_dic = {}

            # --other properties
            cur_ep_dic['global'] = ep_global
            cur_ep_dic['name'] = cur_comp_str
            cur_ep_dic['type'] = ep_type

            # --'info' property
            if cur_comp_str in gld_ep_obj_dic:
                cur_ep_info_obj = gld_ep_obj_dic[cur_comp_str]
            else:
                cur_ep_info_obj = cur_comp_str
            cur_ep_info_dic = {
                "object": cur_ep_info_obj,
                "property": ep_property
            }
            cur_ep_dic['info'] = json.dumps(cur_ep_info_dic)

            # --assemble
            glp_ep_list.append(cur_ep_dic)
        return glp_ep_list

    def get_cc_endpoints(self, cc_ep_type='string', cc_ep_global=False):
        """
        Member method for adding a controller with respect to each endpoint defined in the GLD json file
        """
        # ~~controllers
        cc_ep_pref = 'ctrl_'

        self.cc_ep_list = []
        self.cc_list_all_key = []
        for cur_gld_ep_name in self.gld_list_all_key:
            cur_cc_ep_dict = {}

            cur_cc_ep_dict['global'] = cc_ep_global
            cur_cc_ep_dict['name'] = cc_ep_pref + cur_gld_ep_name
            cur_cc_ep_dict['destination'] = f"{self.gld_json_config_name}/{cur_gld_ep_name}"
            cur_cc_ep_dict['type'] = cc_ep_type

            self.cc_ep_list.append(cur_cc_ep_dict)
            self.cc_list_all_key.append(cur_cc_ep_dict['name'])

    def get_ns3_endpoints(self, ns3_ep_info="0", ns3_ep_global=False):
        """
        """
        self.ns3_ep_list = []

        # --adding the endpoints defined in the GLD json file
        for cur_gld_ep_name in self.gld_list_all_key:
            cur_gld_ep_dict = {}
            cur_gld_ep_dict['name'] = f"{self.gld_json_config_name}/{cur_gld_ep_name}"
            cur_gld_ep_dict['info'] = ns3_ep_info
            cur_gld_ep_dict['global'] = ns3_ep_global

            self.ns3_ep_list.append(cur_gld_ep_dict)

        # --adding the endpoints defined in the CC json file
        for cur_cc_ep_name in self.cc_list_all_key:
            cur_cc_ep_dict = {}
            cur_cc_ep_dict['name'] = f"{self.cc_json_config_name}/{cur_cc_ep_name}"
            cur_cc_ep_dict['info'] = ns3_ep_info
            cur_cc_ep_dict['global'] = ns3_ep_global

            self.ns3_ep_list.append(cur_cc_ep_dict)

    def get_ns3_sub_filters(self, list_all_key, json_config_name,
                            ns3_filter_oper="reroute", ns3_filter_prop_name="newdestination"):

        # --adding filters
        for cur_gld_ep_name in list_all_key:
            cur_ns3_filter_dict = {}
            cur_ns3_filter_dict['name'] = f"{self.ns3_filters_pref}{json_config_name}_{cur_gld_ep_name}"
            cur_ns3_filter_dict['sourcetargets'] = [
                f"{json_config_name}/{cur_gld_ep_name}"]
            cur_ns3_filter_dict['operation'] = ns3_filter_oper

            # ~~property dict
            cur_ns3_filter_prop_dict = {}
            cur_ns3_filter_prop_dict['name'] = ns3_filter_prop_name
            cur_ns3_filter_prop_dict['value'] = f"{self.ns3_json_config_name}/{json_config_name}/{cur_gld_ep_name}"

            cur_ns3_filter_dict['properties'] = cur_ns3_filter_prop_dict

            # ~~assemble
            self.ns3_filters_list.append(cur_ns3_filter_dict)

    def get_ns3_filters(self):
        self.ns3_filters_pref = "filter_"
        self.ns3_filters_list = []

        self.get_ns3_sub_filters(self.gld_list_all_key,
                                 self.gld_json_config_name)
        self.get_ns3_sub_filters(self.cc_list_all_key,
                                 self.cc_json_config_name)

    def export_gld_json(self, output_json_path_fn, json_data_settings_dic, ep_all_list, list_all_key):
        # --record
        self.gld_json_config_name = json_data_settings_dic['name']

        # --prepare
        self.gld_data = {}
        self.gld_data.update(json_data_settings_dic)
        self.gld_data["endpoints"] = ep_all_list

        # --dump
        self.dump_json(output_json_path_fn, self.gld_data)

        # --record
        self.gld_list_all_key = list_all_key

    def export_cc_json(self, output_json_path_fn, json_data_settings_dic):
        # --record
        self.cc_json_config_name = json_data_settings_dic['name']

        # --prepare
        self.cc_data = {}
        self.cc_data.update(json_data_settings_dic)

        # --end points
        p.get_cc_endpoints()

        if not hasattr(self, 'cc_ep_list'):
            warnings.warn(
                "The attribute 'cc_ep_list' is not initialized. An empty list is used.")
            self.cc_ep_list = []
        self.cc_data["endpoints"] = self.cc_ep_list

        # --dump
        self.dump_json(output_json_path_fn, self.cc_data)

    def export_ns3_json(self, output_json_path_fn, json_data_settings_dic):
        # --record
        self.ns3_json_config_name = json_data_settings_dic['name']

        # --prepare
        self.ns3_data = {}
        self.ns3_data.update(json_data_settings_dic)

        # --end points
        self.get_ns3_endpoints()
        self.ns3_data["endpoints"] = self.ns3_ep_list

        # --filters
        self.get_ns3_filters()
        self.ns3_data["filters"] = self.ns3_filters_list

        # --dump
        self.dump_json(output_json_path_fn, self.ns3_data)


def test_export_gld_json():
    # ==Parameters
    # --file path & name
    output_json_path_fn = 'Duke_gld_config.json'

    # --file configs
    json_data_settings_dic = {
        'name': 'GLD',
        'coreType': 'zmq',
        'loglevel': 7,
        'period': 1e-2,
        'wait_for_current_time_update': True,
    }
    # --end Points
    # ~~switches
    ep_property = "status"

    list_cbs_key = ['CB' + str(x) for x in range(1, 5)]
    list_cbs_val = ['CB_' + str(x) for x in range(1, 5)]
    ep_cbs_obj_dic = dict(zip(list_cbs_key, list_cbs_val))
    ep_cbs_list = JsonExporter.get_gld_endpoints(list_cbs_key, ep_cbs_obj_dic,
                                                 ep_property)

    list_rcls_key = ['RCL' + str(x) for x in range(1, 13)]
    ep_rcls_obj_dic = {'RCL1': 'RCL1_53547349_1207',
                       'RCL2': 'RCL2_53547361_1207',
                       'RCL5': 'RCL5_410845731_1209',
                       'RCL7': 'RCL7_39067965_1210',
                       'RCL8': 'RCL8_164887213_1210',
                       'RCL9': 'RCL9_39057658_1209',
                       'RCL11': 'RCL11_616009826_1210',
                       'RCL12': 'RCL12_164887203_1212'}
    ep_rcls_list = JsonExporter.get_gld_endpoints(list_rcls_key, ep_rcls_obj_dic,
                                                  ep_property)

    # ~~inverters
    ep_inv_property = 'Q_Out'

    list_invs_key = ['PV_S2_n256860617_1207']
    list_invs_val = ['Inv_S2_n256860617_1207']
    ep_invs_obj_dic = dict(zip(list_invs_key, list_invs_val))
    ep_invs_list = JsonExporter.get_gld_endpoints(list_invs_key, ep_invs_obj_dic,
                                                  ep_inv_property)

    # --prepare
    ep_all_list = ep_cbs_list + ep_rcls_list + ep_invs_list
    list_all_key = list_cbs_key + list_rcls_key + list_invs_key

    # ==Init & Export
    p = JsonExporter()
    p.export_gld_json(output_json_path_fn,
                      json_data_settings_dic, ep_all_list, list_all_key)

    return p


def test_export_cc_json(p):
    # ==Parameters
    output_json_path_fn = 'Duke_cc_config.json'

    # --file configs
    json_data_settings_dic = {
        'name': 'CC',
        'coreType': 'zmq',
        'loglevel': 7,
        'period': 1e-2,
        'wait_for_current_time_update': True
    }

    # ==Export
    p.export_cc_json(output_json_path_fn, json_data_settings_dic)


def test_export_ns3_json(p):
    # ==Parameters
    output_json_path_fn = 'Duke_ns3_config.json'

    # --file configs
    json_data_settings_dic = {
        "name": "ns3",
        "coreType": "zmq",
        "loglevel": 7,
        "period": 1e-9,
        "wait_for_current_time_update": True
    }

    # ==Export
    p.export_ns3_json(output_json_path_fn, json_data_settings_dic)


if __name__ == '__main__':
    p = test_export_gld_json()
    test_export_cc_json(p)
    test_export_ns3_json(p)
