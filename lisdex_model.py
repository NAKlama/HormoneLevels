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

model = BodyModel(date(2021, 7, 12), timedelta(minutes=5))
dose = 30

model.add_dose(lisdex, dose, datetime(2021, 7, 12, 0))
model.add_dose(lisdex, dose, datetime(2021, 7, 13, 0))
model.add_dose(lisdex, dose, datetime(2021, 7, 14, 0))
model.add_dose(lisdex, dose, datetime(2021, 7, 15, 0))
model.add_dose(lisdex, dose, datetime(2021, 7, 16, 0))
model.add_dose(lisdex, dose, datetime(2021, 7, 17, 0))
model.add_dose(lisdex, dose, datetime(2021, 7, 18, 0))
model.add_dose(lisdex, dose, datetime(2021, 7, 19, 0))
model.add_dose(lisdex, 10, datetime(2021, 7, 19, 4))
# model.add_dose(lisdex, 50, datetime(2021, 7, 19, 0))


days_into_future = 10
model.calculate_timeline(date(2021, 7, 12) + timedelta(days=days_into_future))
# model.estimate_blood_levels(corrected_std_dev=True)

y_window = (0, 20)
duration_factor = model.step / timedelta(hours=1)
duration = model.duration * duration_factor

data = model.get_plot_data(timedelta(hours=1))

plot_drugs(data=data,
           x_window=(24*7, 24*8),
           y_window=y_window,
           x_label="Time (hours)",
           x_ticks=1,
           y_label="Substance in body (mg)")
