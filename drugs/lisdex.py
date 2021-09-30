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


class Dexamphetamine(drug.Drug):
  def __init__(self):
    super().__init__("Dexamphetamine", timedelta(hours=10))


class Lisdexamphetamine(drug.Drug):
    def __init__(self):
        super().__init__("Lisdexamphetamine", timedelta(minutes=30))
        flood_in = [0.0] * 15
        for i in range(30):
          flood_in.append((i+1)/30)
        for i in [1] * 60:
          flood_in.append(i)
        for i in range(45):
          flood_in.append((45-i)/45)
        self.set_flood_in(flood_in)
        self.flood_in_timedelta = timedelta(minutes=1)
        self.add_metabolite("Dexamphetamine", 0.296)
