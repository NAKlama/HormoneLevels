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
from funcy import take, map, count

from modelling.lab_data import LabData


def delta_to_hours(td: timedelta) -> int:
    return math.ceil(td.total_seconds() / 3600.0)


class BodyModel:
    starting_date: date
    doses_list: Dict[Drug, List[Dose]]
    labs_list: List[LabData]
    blood_level_factors: Dict[Drug, Tuple[float, float]]
    drugs_timeline: Dict[Drug, List[float]]
    duration: int

    def __init__(self, starting_date: date):
        self.starting_date = starting_date
        self.doses_list = {}
        self.drugs_timeline = {}
        self.blood_level_factors = {}

    def add_dose(self, drug: Drug, amount: float, time_in: datetime):
        dose = Dose(drug, amount, time_in);
        if dose.time < datetime.combine(self.starting_date, time()):
            raise Exception("Doses cannot be before starting date")
        if dose.drug not in self.doses_list:
            self.doses_list[dose.drug] = []
        for d in dose.get_subdoses():
            self.doses_list[dose.drug].append(d)
        self.doses_list[dose.drug].sort(key=lambda x: x.time)

    def add_lab_data(self, data_in: Union[LabData, List[LabData]]):
        if type(data_in) is not type(LabData):
            data = [data_in]
        else:
            data = data_in
        for d in data:
            self.labs_list.append(d)

    def calculate_timeline(self, until: date):
        drugs = set(self.doses_list.keys())
        for drug in drugs:
            self.drugs_timeline[drug] = []
        self.duration = math.ceil((until - self.starting_date).total_seconds() / 3600)
        for t in range(self.duration):
            time_t = datetime.combine(self.starting_date, time()) + timedelta(hours=t)
            for d in drugs:
                if t > 0:
                    last_val = self.drugs_timeline[d][-1]
                    self.drugs_timeline[d].append(last_val * d.one_hour_metabolism())
                else:
                    self.drugs_timeline[d].append(0.0)
                while self.doses_list[d] and len(self.doses_list[d]) > 0 and self.doses_list[d][0].time <= time_t:
                    dose = self.doses_list[d].pop(0)
                    self.drugs_timeline[d][t] += dose.amount

    def get_drug_at_timepoint(self, d: Drug, t: datetime) -> float:
        timepoint = datetime(t.year, t.month, t.day, t.hour)
        i = math.floor((timepoint - datetime.combine(self.starting_date, time())).total_seconds() / 3600)
        return self.drugs_timeline[d][i]

    def estimate_blood_levels(self):
        levels: Dict[Drug, List[Tuple[datetime, float]]] = {}
        for lab_data in self.labs_list:
            for d in lab_data.labs.keys():
                levels[d] = []

        for lab_data in self.labs_list:
            for d, val in lab_data.labs.items():
                levels[d].append((lab_data.time, val))

        drugs = set(levels.keys())
        for d in drugs:
            level_matcher = map(lambda x: (x[1], self.get_drug_at_timepoint(d, x[0])), levels)
            estimates = list(map(lambda x: (x[1] / x[0]), level_matcher))
            average_est = sum(map(lambda x: x / len(estimates)), estimates)
            std_dev = math.sqrt(sum(map(lambda x: (x - average_est)**2, estimates)) / len(estimates))
            self.blood_level_factors[d] = (average_est, std_dev)

    def get_plot_data(self) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        t_arr = np.array(list(take(self.duration, map(lambda x: x * (1.0/24.0), count()))))
        print(f't_arr.size()={len(t_arr)}')
        out = {}
        for drug, timeline in self.drugs_timeline.items():
            out[drug.name] = np.array(timeline)
            print(f't_arr.size({drug.name})={len(out[drug.name])}')
        return t_arr, out


