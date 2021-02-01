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
# from drugs import Estradiol


class EstradiolCypionate(drug.Drug):
    def __init__(self):
        super().__init__("Estradiol cypionate", timedelta(days=9))
        self.set_flood_in([1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
                           8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7.5, 7.5, 7, 7,
                           7, 7, 7, 7, 6.5, 6.5, 6, 6, 6, 6, 6, 6, 5.5, 5.5, 5.5, 5, 5, 5, 4.5, 4.5, 4.5, 4, 4, 4,
                           3.5, 3.5, 3.5, 3, 3, 3, 2.5, 2.5, 2.5, 2, 2, 2, 1.5, 1.5, 1, 1, .5, .5])
