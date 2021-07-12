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

from typing import List, Iterable

from drugs.drug import Drug
from datetime import datetime, timedelta
from funcy import map, count


class Dose:
    drug:   Drug
    amount: float
    time:   datetime
    hour_dose: bool
    new_dose: bool

    def __init__(self, drug: Drug, amount: float, time: datetime, is_subdose: bool = False):
        self.drug = drug
        self.amount = amount
        self.time = datetime(time.year, time.month, time.day, time.hour)
        self.hour_dose = is_subdose

    def get_subdoses(self) -> List["Dose"]:
        if self.drug.flood_in is None or self.hour_dose is True:
            return [Dose(self.drug, self.amount, self.time, True)]
        else:
            out = []
            flood_in_lenght = len(self.drug.flood_in)
            for t, flood_in in enumerate(self.drug.flood_in):
                dose = self.amount * flood_in
                out.append(Dose(self.drug, dose, self.time + self.drug.flood_in_timedelta * t, False))
            return out

    def get_decay_curve(self, stepping: timedelta) -> Iterable[float]:
        def calc_decay(t: int) -> float:
            hl_steps = self.drug.half_life.total_seconds() / stepping.total_seconds()
            factor = 2 ** (float(t) / hl_steps)
            return self.amount * factor
        return map(calc_decay, count())

    # def get_metabolites(self) -> Dict[Type[Drug], Iterable[float]]:
    #     out = {}
    #     metabolites = {}
    #     for drug, factor in self.drug.metabolites:
    #         out[drug] = map(lambda now, prev: (prev - now) * factor,
    #                         with_prev(self.get_decay_curve(), fill=0.0))
    #     return out

