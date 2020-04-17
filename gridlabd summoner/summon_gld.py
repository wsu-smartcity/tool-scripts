# ***************************************
# Author: Jing Xie
# Created Date: 2020-4-13
# Updated Date: 2020-4-17
# Email: jing.xie@pnnl.gov
# ***************************************

import os.path
import subprocess
import shutil
import pathlib

import sys
sys.path.append('../gridlabd parser')

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
        self, inv_glm_path, inv_glm_src_fn, inv_glm_dst_fn, inv_q_list, inv_nm_list=[]
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

    def run_inv_qlist(self):
        # --read contents of the inv glm file
        igs_str = self.gp.import_file(self.inv_glm_src_pfn)

        if not self.inv_nm_list:
            self.inv_nm_list = self.gp.read_inv_names(self.inv_glm_src_pfn)

        self.prep_rslts_flr(self.stor_csv_path)

        for cur_inv_nm in self.inv_nm_list[0:1]:
            cur_inv_glm_lines_list, cur_inv_re_tpl = self.gp.find_obj_via_attr(
                "inverter", "name", cur_inv_nm, igs_str
            )

            if len(cur_inv_glm_lines_list) == 1:
                cur_inv_glm_lines_str = cur_inv_glm_lines_list[0]
            else:
                raise ValueError("The source glm is problematic")

            for cur_q in self.inv_q_list:
                # --update Q_Out
                cur_inv_glm_lines_mod_str = self.gp.modify_attr(
                    "Q_Out", str(cur_q), cur_inv_glm_lines_str
                )

                # --replace the obj portion in the source string
                cur_q_inv_glm_str = self.gp.replace_obj(
                    cur_inv_re_tpl, igs_str, cur_inv_glm_lines_mod_str
                )

                # --export, run, & save
                self.gp.export_glm(self.inv_glm_dst_pfn, cur_q_inv_glm_str)
                self.run_gld()
                cur_results_flr_name = f"{cur_inv_nm}_{cur_q}"
                cur_results_flr_pfn = os.path.join(
                    self.stor_csv_path, cur_results_flr_name
                )
                self.save_results(cur_results_flr_pfn)


def test_GldSmn():
    """
    Params & Init
    """
    # ==Parameters (for GldSmn)
    gld_path = r"D:\Duke_UC3_S1_[For UTK]"
    gld_exe_fn = r"gridlabd.exe"

    glm_path = r"D:\test glms"  # r"D:\Duke_UC3_S1_[For UTK]"
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
    inv_q_base = 1e2
    inv_q_list = [x / 10 * inv_q_base for x in range(2)]

    # --prep
    # inv_glm_src_pfn = os.path.join(inv_glm_path, inv_glm_src_fn)

    # ==Init the Instance of GlmParser
    p.init_GlmParser(
        inv_glm_path, inv_glm_src_fn, inv_glm_dst_fn, inv_q_list, inv_nm_list
    )

    """
    Demos
    """
    # ==Demo 01
    p.run_inv_qlist()

    # ==Demo 02
    # --run GLD
    # p.run_gld()

    # --save CSV files
    # p.save_results()


if __name__ == "__main__":
    test_GldSmn()
