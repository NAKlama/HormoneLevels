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

from distutils.core import setup

setup(
  name="HormoneLevels",
  description="Compute and graph hormone levels for transgender HRT",
  version='0.4.0',
  license="GPLv3",
  author="Nina Alexandra Klama",
  author_email="gitlab@fklama.de",
  install_requires=[
    'funcy',
    'matplotlib',
    'numpy',
    'PyYAML',
  ],
)
