import copy
from collections import (
    Counter,
)
from pathlib import (
    Path,
)
from typing import (
    List,
    Optional,
    Tuple,
)

import dpdata
import numpy as np

from pfd.exploration.render import (
    TrajRender,
)
from dpgen2.exploration.report import (
    ExplorationReport,
)

from . import (
    ConfFilters,
    ConfSelector,
)


class ConfSelectorFrames(ConfSelector):
    """Select frames from trajectories as confs.

    Parameters:
    trust_level: TrustLevel
        The trust level
    conf_filter: ConfFilters
        The configuration filter

    """

    def __init__(
        self,
        traj_render: TrajRender,
        # report: ExplorationReport,
        max_numb_sel: Optional[int] = None,
        conf_filters: Optional[ConfFilters] = None,
    ):
        self.max_numb_sel = max_numb_sel
        self.conf_filters = conf_filters
        self.traj_render = traj_render

    # self.report = report

    def select(
        self,
        trajs: List[Path],
        type_map: Optional[List[str]] = None,
        optional_outputs: Optional[List[Path]] = None,
    ) -> List[Path]:
        """Select configurations

        Parameters
        ----------
        trajs : List[Path]
            A `list` of `Path` to trajectory files generated by LAMMPS
        model_devis : List[Path]
            A `list` of `Path` to model deviation files generated by LAMMPS.
            Format: each line has 7 numbers they are used as
            # frame_id  md_v_max md_v_min md_v_mean  md_f_max md_f_min md_f_mean
            where `md` stands for model deviation, v for virial and f for force
        type_map : List[str]
            The `type_map` of the systems
        optional_outputs : List[Path]
            Optional outputs of the exploration

        Returns
        -------
        confs : List[Path]
            The selected confgurations, stored in a folder in deepmd/npy format, can be parsed as dpdata.MultiSystems. The `list` only has one item.
        report : ExplorationReport
            The exploration report recoding the status of the exploration.

        """

        # self.report.clear()
        # id_cand_list = self.report.get_candidate_ids(self.max_numb_sel)

        ms = self.traj_render.get_confs(
            trajs,
            # id_cand_list,
            type_map,
            self.conf_filters,
            optional_outputs,
        )

        out_path = Path("confs")
        out_path.mkdir(exist_ok=True)
        ms.to_deepmd_npy(out_path)  # type: ignore
        print("Select %s of frames" % ms.get_nframes())

        return [out_path]
