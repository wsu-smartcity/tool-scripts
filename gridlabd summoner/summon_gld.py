# ***************************************
# Author: Jing Xie
# Created Date: 2020-4-13
# Updated Date: 2020-4-19
# Email: jing.xie@pnnl.gov
# ***************************************

import os.path
import subprocess
import shutil
import pathlib

import sys

sys.path.append("../gridlabd parser")

from parse_glm import GlmParser


class GldSmn:
    """Run GLD and save results"""

    def __init__(
        self,
        gld_path,
        glm_path,
        glm_fn,
        gld_csv_path,
        stor_csv_path,
        gld_exe_fn=r"gridlabd.exe",
        gld_csv_suff=r".csv",
    ):
        """Init the settings
        """
        # ==GLD EXE
        self.gld_path = gld_path
        self.gld_exe_fn = gld_exe_fn

        # ==GLM
        self.glm_path = glm_path
        self.glm_fn = glm_fn

        # ==CVS
        self.gld_csv_path = gld_csv_path
        self.gld_csv_suff = gld_csv_suff
        self.stor_csv_path = stor_csv_path

        # ==Preprocess
        self.glm_pfn = os.path.join(glm_path, glm_fn)

    def run_gld(self, arg_shell=True):
        """Run the gld
        """
        subprocess.run(
            [self.gld_exe_fn, self.glm_pfn], cwd=self.gld_path, shell=arg_shell
        )

    def prep_rslts_flr(self, dst_flr_path):
        if os.path.exists(dst_flr_path):
            # shutil.rmtree(dst_flr_path)
            self.clean_flr(dst_flr_path)
        else:
            os.makedirs(dst_flr_path)

    def clean_flr(self, folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))

    def move_rslts_files(self, dst_flr_path):
        """Move files
        """
        for root, _, files in os.walk(self.gld_csv_path):
            for cur_fn in files:
                if cur_fn.endswith(self.gld_csv_suff):
                    src_pfn = os.path.join(root, cur_fn)
                    cur_relpath = os.path.relpath(root, self.gld_csv_path)
                    cur_dst_path = os.path.join(dst_flr_path, cur_relpath)
                    pathlib.Path(cur_dst_path).mkdir(parents=True, exist_ok=True)
                    cur_dst_pfn = os.path.join(cur_dst_path, cur_fn)

                    shutil.move(src_pfn, cur_dst_pfn)

    def save_results(self, dst_flr_path=""):
        """Dump the data dictionary into a json file
        """
        if not dst_flr_path:
            dst_flr_path = self.stor_csv_path

        # ==Prepare the storage folder
        self.prep_rslts_flr(dst_flr_path)

        # ==Move files
        self.move_rslts_files(dst_flr_path)

    def save_glm_copy(self, src_fn):
        """
        """
        # ==make a copy of the source file (e.g., an inv glm file)
        # inv_glm_copy_pfn = os.path.join(inv_glm_path, "Copy_" + inv_glm_fn)
        # shutil.copyfile(inv_glm_pfn, inv_glm_copy_pfn)

    def init_GlmParser(
        self,
        inv_glm_path,
        inv_glm_src_fn,
        inv_glm_dst_fn,
        inv_q_list=[],
        inv_nm_list=[],
    ):
        # ==Assign
        self.inv_glm_path = inv_glm_path
        self.inv_glm_src_fn = inv_glm_src_fn
        self.inv_glm_dst_fn = inv_glm_dst_fn

        self.inv_nm_list = inv_nm_list
        self.inv_q_list = inv_q_list

        self.inv_glm_src_pfn = os.path.join(inv_glm_path, inv_glm_src_fn)
        self.inv_glm_dst_pfn = os.path.join(inv_glm_path, inv_glm_dst_fn)

        # ==Init GlmParser
        self.gp = GlmParser()

    def run_inv_qplayer(
        self, cur_inv_nm, cur_inv_glm_lines_str, cur_inv_re_tpl, igs_str
    ):
        """Modify the Q_Out of the selected inverter via a player file
        """
        # --params (multi-recorder)
        mr_csv_fn = f"{cur_inv_nm}.csv"
        mr_prop_str = f"{cur_inv_nm}:VA_Out.imag, meter_n256824166_1212:measured_voltage_A, q_player:value"
        mr_interval = 1

        # --params (player)
        player_nm_str = "q_player"
        player_file_str = "inv_q.player"

        # --create a multi-recorder
        glm_obj_mr_str = (
            f"//==Multi-Recorder\n"
            f"object multi_recorder {{\n"
                f"\tinterval {mr_interval};\n"
                f"\tproperty {mr_prop_str};\n"
                f"\tfile {mr_csv_fn};\n"
            f"}}\n"
        )

        # --create a player
        glm_obj_player_class_str = """
//==Player (extended mode)
class player {
    double value;
}\n
"""

        glm_obj_player_obj_str = (
            f"object player {{\n"
                f"\tname {player_nm_str};\n"
                f"\tfile {player_file_str};\n"
            f"}}\n"
        )

        glm_obj_player_str = glm_obj_player_class_str + glm_obj_player_obj_str

        # --plug the player.value into the Q_Out of the current inverter
        # ~~get inv rated power
        cur_inv_rp_list = self.gp.extract_attr("rated_power", cur_inv_glm_lines_str)

        assert len(cur_inv_rp_list) == 1
        cur_inv_rp = float(cur_inv_rp_list[0])

        # ~~update Q_Out
        cur_q_var_str = f"{player_nm_str}.value * {cur_inv_rp}"
        cur_inv_glm_lines_mod_str = self.gp.modify_attr(
            "Q_Out", cur_q_var_str, cur_inv_glm_lines_str
        )

        # ~~replace the obj portion in the source string
        cur_q_inv_glm_str = self.gp.replace_obj(
            cur_inv_re_tpl, igs_str, cur_inv_glm_lines_mod_str
        )

        # --insert the multi-recorder & player into the target glm file
        cur_inv_glm_str = glm_obj_mr_str + glm_obj_player_str + cur_q_inv_glm_str

        # --export glm, run GLD, and save csv files
        self.gp.export_glm(self.inv_glm_dst_pfn, cur_inv_glm_str)
        self.run_gld()
        cur_results_flr_name = f"{cur_inv_nm}"
        cur_results_flr_pfn = os.path.join(self.stor_csv_path, cur_results_flr_name)
        self.save_results(cur_results_flr_pfn)
    
    def run_inv_qlist(self, cur_inv_nm, cur_inv_glm_lines_str, cur_inv_re_tpl, igs_str):
        # --data sanity check
        assert self.inv_q_list

        # --run gld for each q value
        for cur_q_pu in self.inv_q_list:
            # --get inv rated power
            cur_inv_rp_list = self.gp.extract_attr("rated_power", cur_inv_glm_lines_str)

            assert len(cur_inv_rp_list) == 1
            cur_inv_rp = float(cur_inv_rp_list[0])

            # --update Q_Out
            cur_q_var = cur_q_pu * cur_inv_rp
            cur_inv_glm_lines_mod_str = self.gp.modify_attr(
                "Q_Out", str(cur_q_var), cur_inv_glm_lines_str
            )

            # --replace the obj portion in the source string
            cur_q_inv_glm_str = self.gp.replace_obj(
                cur_inv_re_tpl, igs_str, cur_inv_glm_lines_mod_str
            )

            # --export glm, run GLD, and save csv files
            self.gp.export_glm(self.inv_glm_dst_pfn, cur_q_inv_glm_str)
            self.run_gld()
            cur_results_flr_name = f"{cur_inv_nm}_{cur_q_pu}"
            cur_results_flr_pfn = os.path.join(self.stor_csv_path, cur_results_flr_name)
            self.save_results(cur_results_flr_pfn)

    def run_inv(self, run_player_mode=True):
        # --search the list of inverters if not given
        if not self.inv_nm_list:
            self.inv_nm_list = self.gp.read_inv_names(self.inv_glm_src_pfn)

        # --prepare the results folder
        self.prep_rslts_flr(self.stor_csv_path)

        # --run gld for each inverter
        for cur_inv_nm in self.inv_nm_list:
            # --read contents of the inv glm file
            igs_str = self.gp.import_file(self.inv_glm_src_pfn)

            # --search the current inverter
            cur_inv_glm_lines_list, cur_inv_re_tpl = self.gp.find_obj_via_attr(
                "inverter", "name", cur_inv_nm, igs_str
            )

            if len(cur_inv_glm_lines_list) == 1:
                cur_inv_glm_lines_str = cur_inv_glm_lines_list[0]
            else:
                raise ValueError("The source glm is problematic")

            # --run gld for each q value in a given list
            if run_player_mode:
                self.run_inv_qplayer(
                    cur_inv_nm, cur_inv_glm_lines_str, cur_inv_re_tpl, igs_str
                )
            else:
                self.run_inv_qlist(
                    cur_inv_nm, cur_inv_glm_lines_str, cur_inv_re_tpl, igs_str
                )


def test_GldSmn():
    """
    Params & Init
    """
    # ==Parameters (for GldSmn)
    gld_path = r"D:\test glms"
    gld_exe_fn = r"gridlabd.exe"

    # Note that:
    # 1) the path and folder of the main glm file cannot have the bracket, this is not supported by GLD... E.g., this does not work: glm_path = r"D:\Duke_UC3_S1_[For UTK]"
    # 2) if the main glm file includes other glm files, those must be put under the gld_path, unless the full path is specified in the main glm file
    glm_path = gld_path  # r"D:\test glms"
    glm_fn = r"Duke_Main.glm"

    gld_csv_path = gld_path
    gld_csv_suff = r".csv"
    stor_csv_path = r"D:\csv files"

    # ==Instance of GldSmn
    p = GldSmn(
        gld_path,
        glm_path,
        glm_fn,
        gld_csv_path,
        stor_csv_path,
        gld_exe_fn,
        gld_csv_suff,
    )

    # ==Parameters (for GlmParser)
    inv_glm_path = glm_path
    inv_glm_src_fn = r"Copy_SolarPV.glm"
    inv_glm_dst_fn = r"SolarPV.glm"

    inv_nm_list = []

    # --create q list (if not using the player mode)
    inv_q_upper_lim = 1.0
    inv_q_lower_lim = -1.0
    inv_q_stepsize = 8e-1

    inv_q_list_len = 1 + int((inv_q_upper_lim - inv_q_lower_lim) / inv_q_stepsize)
    inv_q_list = [inv_q_lower_lim + x * inv_q_stepsize for x in range(inv_q_list_len)]

    # ==Init the Instance of GlmParser
    p.init_GlmParser(
        inv_glm_path, inv_glm_src_fn, inv_glm_dst_fn, inv_q_list, inv_nm_list
    )

    """
    Demos
    """
    # ==Demo 01 (modify Q_Out directly in glm)
    # p.run_inv(run_player_mode=False)

    # ==Demo 02 (modify Q_Out via player)
    p.run_inv(run_player_mode=True)

    # ==Demo 03
    # --run GLD
    # p.run_gld()

    # --save CSV files
    # p.save_results()


if __name__ == "__main__":
    test_GldSmn()
