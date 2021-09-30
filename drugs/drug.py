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

from typing import Optional, List, Tuple
from drugs.drug_classes import DrugClass
from datetime import timedelta
from funcy import map


class Drug(object):
  name:                   str
  name_blood:             str
  half_life:              timedelta
  drug_class:             Optional[DrugClass]
  flood_in:               Optional[List[float]]
  flood_in_timedelta:     timedelta
  blood_value_factor:     float
  metabolites:            List[Tuple[str, float]]

  def __init__(self, name: str, half_life: timedelta, drug_class: Optional[DrugClass] = None):
    self.name               = name
    self.name_blood         = name
    self.half_life          = half_life
    self.drug_class         = drug_class
    self.flood_in           = None
    self.flood_in_timedelta = timedelta(hours=1)
    self.metabolites        = []

  def set_flood_in(self, flood_in: List[float]):
    self.flood_in = flood_in
    total = sum(flood_in)
    self.flood_in = list(map(lambda x: x/total, self.flood_in))

  def add_metabolite(self, drug_in: str, factor: float):
    self.metabolites.append((drug_in, factor))

  def get_metabolism_factor(self, step: timedelta) -> float:
    hl_step = self.half_life.total_seconds() / step.total_seconds()
    factor = 2 ** (-1.0 / hl_step)
    return factor

  def get_metabolites(self, decay_amount: float) -> List[Tuple[str, float]]:
    out = []
    for drug, factor in self.metabolites:
      out.append((drug, decay_amount * factor))
    return out

  def get_name(self) -> str:
    return self.name

  def __hash__(self):
    return hash(self.name)
