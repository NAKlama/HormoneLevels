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

from drugs import *
from modelling import *
from graphing.plot import plot_drugs

from datetime import date, datetime, timedelta, time

lisdex = Lisdexamphetamine()
damph  = Dexamphetamine()

# Using Days instead of hours for accuracy
# So one day in the future is actually one hour in the future
# The resolution of the modelling is currently fixed to one hour, and this is a quick
# way to increase the resolution to 2.5 minutes.

doses_pattern = [
  ([(9, 30)], "Lisdex 30mg@9:00"),
  ([(9, 40)], "Lisdex 40mg@9:00"),
  ([(9, 30), (12, 10)], "Lisdex 30mg@9:00, 10mg@12:00"),
  ([(9, 30), (13, 10)], "Lisdex 30mg@9:00, 10mg@13:00"),
  ([(9, 30), (14, 10)], "Lisdex 30mg@9:00, 10mg@14:00"),
  ([(9, 50)], "Lisdex 50mg@9:00"),
]

for pattern, title in doses_pattern:
  model = BodyModel(date(2021, 7, 12), timedelta(minutes=5))

  for i in range(12, 20):
    for hour, dose in pattern:
      model.add_dose(lisdex, dose, datetime(2021, 7, i, hour))

  days_into_future = 10
  model.calculate_timeline(date(2021, 7, 12) + timedelta(days=days_into_future))
  # model.estimate_blood_levels(corrected_std_dev=True)

  y_window = (0, 20)
  duration_factor = model.step / timedelta(hours=1)
  duration = model.duration * duration_factor

  data = model.get_plot_data(timedelta(hours=1), offset=-7*24)

  plot_drugs(data=data,
             title=title,
             x_window=(0, 24),
             y_window=y_window,
             x_label="Time (hours)",
             x_ticks=1,
             y_label="Substance in body (mg)")
