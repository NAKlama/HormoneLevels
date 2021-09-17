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


class EstradiolValerate(drug.Drug):
  def __init__(self, mode: str = ""):
    if mode == "gel":
      halflife = timedelta(hours=36)
    else:
      halflife = timedelta(hours=1, minutes=30)
    super().__init__("Estradiol", halflife)
    if mode == "gel":
      self.set_flood_in([1,2,3,2,1])
