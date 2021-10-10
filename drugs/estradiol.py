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

import drugs.drug as drug
from datetime import timedelta


class Estradiol(drug.Drug):
  def __init__(self, mode: str = "gel"):
    half_life = timedelta(hours=1, minutes=30)
    super().__init__("Estradiol", half_life)


class EstradiolGel(drug.Drug):
  def __init__(self):
    half_life = timedelta(hours=36)
    super().__init__("Estradiol Gel", half_life)
    self.set_flood_in([1, 2, 3, 2, 1])
    self.flood_in_timedelta = timedelta(hours=1)
    self.add_metabolite("Estradiol", 1.0)


