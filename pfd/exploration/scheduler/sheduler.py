from typing import Dict, List
import copy
from pfd.exploration import explore_styles
from pfd.exploration.task import ExplorationStage, BaseExplorationTaskGroup
import logging


class Scheduler:
    """
    This would manage every part of workflow status
    """

    def __init__(
        self,
        model_style: str = "dp",
        explore_style: str = "lmp",
        mass_map: List = [],
        type_map: List = [],
        explore_stages: List[List[Dict]] = [[{}]],
        max_iter: int = 1,
    ) -> None:

        # exploration stages
        self._explore_stages = explore_stages

        # iteration numbers
        self._idx_stage = 0

        # set iteratiion number
        self._iter_numb = 0

        # set type map
        self._type_map = type_map

        # set mass map
        self._mass_map = mass_map

        # model style
        self._model_style = model_style

        # exploration style
        self._explore_style = explore_style

        # workflow convergence
        self._converge = False

        # stage convergence
        self._converge_stage = False

        # max iterations
        self._max_iter = max_iter

        # first iteration
        self._is_first_iteration = True

    @property
    def model_style(self):
        return self._model_style

    @property
    def explore_style(self):
        return self._explore_style

    @property
    def expl_stages(self):
        return self._explore_stages

    @property
    def iter_numb(self):
        return self._iter_numb

    @property
    def idx_stage(self):
        return self._idx_stage

    @property
    def type_map(self):
        return self._type_map

    @property
    def mass_map(self):
        return self._mass_map

    @property
    def max_iteration(self):
        return self._max_iter

    @property
    def convergence(self):
        return self._converge

    @property
    def is_first_iteration(self):
        return self._is_first_iteration

    @is_first_iteration.setter
    def is_first_iteration(self, value: bool):
        self._is_first_iteration = value

    def set_explore_tasks(self, systems):
        _expl_stage = ExplorationStage()
        for task_grp in self.expl_stages[self.idx_stage]:
            for idx in task_grp["conf_idx"]:
                _expl_stage.add_task_group(
                    explore_styles[self.model_style][self.explore_style]["task"](
                        systems[idx],
                        self.type_map,
                        self.mass_map,
                        task_grp,
                    )
                )
        return _expl_stage.make_task()

    def set_convergence(self, convergence_stage: bool = False) -> None:
        if self.iter_numb >= self.max_iteration:
            logging.info("Max number of iteration reached. Stop exploration...")
            self._converge = True
        elif convergence_stage is True:
            if self.idx_stage + 1 >= len(self.expl_stages):
                logging.info("All stages converged...")
                self._converge = True
            else:
                logging.info(
                    "Task %s converged, continue to the next stage..." % self.idx_stage
                )
                self.next_stage()

        if not self.is_first_iteration:
            self.next_iter()
        else:
            self.is_first_iteration = False

    def next_iter(self) -> None:
        self._iter_numb += 1

    def next_stage(self) -> None:
        self._idx_stage += 1

    def get_status(self):
        pass
