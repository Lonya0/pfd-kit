import unittest
import os
import json
import sys

sys.path.append("../")
import tempfile
from pfd.entrypoint.submit import submit_ft
from dflow.python import OPIO


class TestWorkflowFinetune(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # poscar
        self.poscar = os.path.join(self.test_dir, "foo.vasp")
        with open(self.poscar, "w") as f:
            f.write("foo")
        # INPUT file
        self.input = os.path.join(self.test_dir, "foo.scf")
        with open(self.input, "w") as f:
            f.write("foo")
        # pp file
        self.pp = os.path.join(self.test_dir, "foo.upf")
        with open(self.pp, "w") as f:
            f.write("foo")
        # orb file
        self.orb = os.path.join(self.test_dir, "foo.orb")
        with open(self.orb, "w") as f:
            f.write("foo")
        # model file
        self.model = os.path.join(self.test_dir, "foo.pt")
        with open(self.model, "w") as f:
            f.write("foo")
        # model train script file
        self.train_script = os.path.join(self.test_dir, "foo.json")
        with open(self.train_script, "w") as f:
            json.dump({"foo": "foo"}, f, indent=4)
        self.config_param = {
            "default_step_config": {
                "template_config": {
                    "image": "registry.dp.tech/dptech/deepmd-kit:2024Q1-d23cf3e"
                },
            },
            "task": {"type": "finetune", "init_training": True, "skip_aimd": False},
            "inputs": {"type_map": ["foo"], "mass_map": [1.0]},
            "conf_generation": {
                "init_configurations": {
                    "type": "file",
                    "prefix": "./",
                    "fmt": "vasp/poscar",
                    "files": [self.poscar],
                },
                "pert_generation": [
                    {
                        "conf_idx": [0],
                        "atom_pert_distance": 0.1,
                        "cell_pert_fraction": 0.03,
                        "pert_num": 5,
                    }
                ],
            },
            "aimd": {"inputs_config": {"input_file": self.input}},
            "exploration": {
                "init_training": True,
                "skip_aimd": True,
                "max_iter": 1,
                "converge_config": {"type": "energy_rmse", "RMSE": 0.01},
                "filter": [{"type": "distance"}],
                "type": "lmp",
                "config": {
                    "command": "lmp -var restart 0",
                    "shuffle_models": False,
                    "head": None,
                },
                "stages": [
                    [
                        {
                            "conf_idx": [0],
                            "n_sample": 1,
                            "exploration": {
                                "type": "lmp-md",
                                "ensemble": "npt",
                                "dt": 0.005,
                                "nsteps": 100,
                                "temps": [300],
                                "press": [1],
                                "trj_freq": 1,
                            },
                            "max_sample": 100,
                        }
                    ]
                ],
            },
            "fp": {
                "type": "fpop_abacus",
                "task_max": 50,
                "extra_output_files:": [],
                "run_config": {
                    "command": "OMP_NUM_THREADS=4 mpirun -np 8 abacus | tee log"
                },
                "inputs_config": {
                    "input_file": self.input,
                    "pp_files": {
                        "foo": self.pp,
                    },
                    "orb_files": {
                        "foo": self.orb,
                    },
                },
            },
            "train": {
                "comment": "Training script for downstream DeePMD model",
                "type": "dp",
                "config": {
                    "impl": "pytorch",
                    "init_model_policy": "no",
                    "init_model_with_finetune": True,
                },
                "template_script": self.train_script,
                "init_models_paths": [self.model],
                "numb_models": 1,
            },
        }

    os.environ["DFLOW_DEBUG"] = "1"

    def test_wf_io(self):
        assert submit_ft(self.config_param, no_submission=True)


if __name__ == "__main__":
    unittest.main()