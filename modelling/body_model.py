# HormoneLevels - Calculate Hormone levels for Hormone Replacement Therapy
# Copyright (C) 2021  Nina Alexandra Klama
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Union

import numpy as np

from drugs.drug import Drug
from modelling.dose import Dose
from datetime import datetime, date, timedelta, time
from funcy import take, map, count, drop

from modelling.lab_data import LabData


class BodyModel:
    starting_date: date
    step: timedelta
    doses_list: Dict[Drug, List[Dose]]
    labs_list: List[LabData]
    blood_level_factors: Dict[Drug, Tuple[float, float]]
    lab_levels: Dict[Drug, List[Tuple[datetime, float]]]
    drugs_timeline: Dict[Drug, List[float]]
    duration: int
    real_duration: int
    doses_count: int
    doses_amount: float

    def __init__(self, starting_date: date, timesteps: timedelta):
        self.starting_date = starting_date
        self.step = timesteps
        self.doses_list = {}
        self.drugs_timeline = {}
        self.blood_level_factors = {}
        self.labs_list = []
        self.lab_levels = {}
        self.duration = 0
        self.real_duration = 0
        self.doses_count = 0
        self.doses_amount = 0.0

    @staticmethod
    def delta_to_hours(td: timedelta) -> int:
        return math.ceil(td.total_seconds() / 3600.0)

    def add_dose(self, drug: Drug, amount: float, time_in: datetime):
        dose = Dose(drug, amount, time_in)
        if dose.time < datetime.combine(self.starting_date, time()):
            raise Exception("Doses cannot be before starting date")
        if dose.drug not in self.doses_list:
            self.doses_list[dose.drug] = []
        for d in dose.get_subdoses():
            self.doses_list[dose.drug].append(d)
        self.doses_list[dose.drug].sort(key=lambda x: x.time)
        self.doses_count += 1
        self.doses_amount += amount

    def add_lab_data(self, data_in: Union[LabData, List[LabData]]):
        if type(data_in) is type(LabData):
            data = [data_in]
        else:
            data = data_in
        for d in data:
            self.labs_list.append(d)

    def calculate_timeline(self, until: date):
        drugs = set(self.doses_list.keys())
        while True:
            start_len = len(drugs)
            new_drugs = []
            for d in drugs:
                for m, x in d.metabolites:
                    new_drugs.append(m)
            for d in new_drugs:
                drugs.add(d)
            if len(drugs) == start_len:
                break
        for drug in drugs:
            self.drugs_timeline[drug] = []
        self.duration = math.ceil((until - self.starting_date).total_seconds() / self.step.total_seconds())
        self.real_duration = math.ceil((date.today() - self.starting_date).total_seconds() / self.step.total_seconds())
        for t in range(self.duration):
            time_t = datetime.combine(self.starting_date, time()) + self.step * t
            for d in drugs:
                if t > 0:
                    last_val = self.drugs_timeline[d][-1]
                    curr_val = last_val * d.get_metabolism_factor(self.step)
                    self.drugs_timeline[d].append(curr_val)
                    metabolites = d.get_metabolites(last_val - curr_val)
                    for drug, amount in metabolites:
                        if drug not in self.doses_list:
                            self.doses_list[drug] = []
                        self.doses_list[drug].insert(0, Dose(drug, amount, time_t, True))
                else:
                    self.drugs_timeline[d].append(0.0)
                while d in self.doses_list and self.doses_list[d] and len(self.doses_list[d]) > 0 and self.doses_list[d][0].time <= time_t:
                    dose = self.doses_list[d].pop(0)
                    self.drugs_timeline[d][t] += dose.amount

    def __get_timepoint(self, t: datetime) -> int:
        timepoint = datetime(t.year, t.month, t.day, t.hour)
        return math.floor((timepoint - datetime.combine(self.starting_date,
                                                        time())).total_seconds() / self.step.total_seconds())

    def get_drug_at_timepoint(self, d: Drug, t: datetime) -> float:
        return self.drugs_timeline[d][self.__get_timepoint(t)]

    def get_blood_level_at_timepoint(self, d: Drug, t: datetime) -> Tuple[float, float, float]:
        timeline    = self.drugs_timeline[d]
        timepoint   = self.__get_timepoint(t)
        avg, stddev = self.blood_level_factors[d]
        return timeline[timepoint], avg, stddev

    def get_current_blood_level_message(self, d: Drug) -> str:
        drug_amount, factor_avg, factor_stddev = self.get_blood_level_at_timepoint(d, datetime.now())
        return f"Estimated blood level ({d.name_blood}): " \
               f"{drug_amount * factor_avg:6.2f} ± " \
               f"{factor_stddev * 2:5.2f} ng/l (P<.046)"

    def estimate_blood_levels(self, corrected_std_dev: bool = True):
        for lab_data in self.labs_list:
            for d in lab_data.labs.keys():
                self.lab_levels[d] = []

        for lab_data in self.labs_list:
            for d, val in lab_data.labs.items():
                self.lab_levels[d].append((lab_data.time, val))

        drugs = set(self.lab_levels.keys())
        for d in drugs:
            level_matcher = list(map(lambda x: (x[1], self.get_drug_at_timepoint(d, x[0])), self.lab_levels[d]))
            estimates = list(map(lambda x: (x[0] / x[1]), level_matcher))
            average_est = sum(map(lambda x: x / len(estimates), estimates))
            levels = list(map(lambda x: (x[0], x[1] * average_est), level_matcher))
            if len(estimates) > 1 and corrected_std_dev:
                std_dev = math.sqrt(sum(map(lambda x: (x[0] - x[1])**2, levels)) / (len(levels)-1))
                # std_dev = math.sqrt(sum(map(lambda x: (x - average_est)**2, estimates)) / (len(estimates)-1))
            else:
                std_dev = math.sqrt(sum(map(lambda x: (x[0] - x[1]) ** 2, levels)) / len(levels))
                # std_dev = math.sqrt(sum(map(lambda x: (x - average_est)**2, estimates)) / len(estimates))
            self.blood_level_factors[d] = (average_est, std_dev)

    def get_plot_data(self, plot_delta: timedelta = timedelta(days=1), adjusted: bool = False, sd_mult: float = 1.0) -> \
            Tuple[np.ndarray, Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]]:
        t_arr = np.array(list(take(self.duration, map(lambda x:
                                                          x * (self.step.total_seconds()/plot_delta.total_seconds()),
                                                      count()))))
        # print(f't_arr.size()={len(t_arr)}')
        out = {}
        drugs = sorted(list(self.drugs_timeline.keys()), key=lambda x: x.name)
        for drug in drugs:
            timeline = self.drugs_timeline[drug]
            if adjusted:
                out[drug.name_blood] = (
                    np.array(list(map(lambda x: x * self.blood_level_factors[drug][0], timeline))),
                    np.array(list(map(
                        lambda x: x * self.blood_level_factors[drug][0] - self.blood_level_factors[drug][1] * sd_mult,
                        timeline))),
                    np.array(list(map(
                        lambda x: x * self.blood_level_factors[drug][0] + self.blood_level_factors[drug][1] * sd_mult,
                        timeline))),
                )
            else:
                arr = np.array(timeline)
                out[drug.name_blood] = (arr, arr, arr)
            # print(f't_arr.size({drug.name})={len(out[drug.name])}')
        return t_arr, out

    def get_statistical_data(self, drug: Drug) -> Tuple[float, float]:
        blood_levels   = list(drop(7*24,
                                   take(self.real_duration,
                                        map(lambda x: x * self.blood_level_factors[drug][0],
                                            self.drugs_timeline[drug]))))
        levels_avg     = sum(blood_levels) / len(blood_levels)
        sq_delta       = list(map(lambda x: (x - levels_avg)**2, blood_levels))
        levels_std_dev = math.sqrt(sum(sq_delta) / len(blood_levels))
        return levels_avg, levels_std_dev

    def get_plot_lab_levels(self) -> Dict[str, Tuple[List[int], List[float]]]:
        lab_levels = {}
        for drug, ll_data in self.lab_levels.items():
            lab_levels[drug.name] = (
                list(map(lambda x: (
                    ((x[0] - datetime.combine(self.starting_date, time())).total_seconds() / (3600 * 24))), ll_data)),
                list(map(lambda x: x[1], ll_data))
            )

        return lab_levels


