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

mph = Methylphenidate()

# Using Days instead of hours for accuracy
# So one day in the future is actually one hour in the future
# The resolution of the modelling is currently fixed to one hour, and this is a quick
# way to increase the resolution to 2.5 minutes.

model = BodyModel(date(2021, 5, 17))

model.add_dose(mph, 10, datetime(2021, 5, 17, 0))
model.add_dose(mph,  5, datetime(2021, 5, 20, 0))
model.add_dose(mph,  5, datetime(2021, 5, 23, 0))


days_into_future = 12
model.calculate_timeline(date.today() + timedelta(days=days_into_future))
model.estimate_blood_levels(corrected_std_dev=True)

y_window = (0, 10)

data = model.get_plot_data()

plot_drugs(data=data,
           x_window=(0, model.duration/24.0),
           y_window=y_window,
           x_label="Time(hours)",
           x_ticks=2,
           y_label="Proportionate dose")