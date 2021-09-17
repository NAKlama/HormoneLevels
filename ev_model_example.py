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

ev = EstradiolValerate()

# Adjust the dates to be a few days in the past, but all after the BodyModel start date
# for a small demonstration

model = BodyModel(date(2020, 12, 12), timedelta(hours=1))

model.add_dose(ev, 2.5, datetime(2020, 12, 12, 9))
model.add_dose(ev, 2.5, datetime(2020, 12, 13, 8))
model.add_dose(ev, 2.5, datetime(2020, 12, 15, 9))
model.add_dose(ev, 2.5, datetime(2020, 12, 18, 10))
model.add_dose(ev, 2.5, datetime(2020, 12, 21, 9))
model.add_dose(ev, 2.5, datetime(2020, 12, 23, 9))
model.add_dose(ev, 2.5, datetime(2020, 12, 26, 14))
model.add_dose(ev, 2.5, datetime(2020, 12, 29, 11))
model.add_dose(ev, 2.5, datetime(2021,  1,  1, 13))
model.add_dose(ev, 2.5, datetime(2021,  1,  4, 9))
model.add_dose(ev, 2.5, datetime(2021,  1,  7, 11))
model.add_dose(ev, 2.5, datetime(2021,  1,  9, 9))
model.add_dose(ev, 2.5, datetime(2021,  1, 12, 9))
model.add_dose(ev, 2.5, datetime(2021,  1, 15, 7))
model.add_dose(ev, 3.0, datetime(2021,  1, 18, 9))
model.add_dose(ev, 2.4, datetime(2021,  1, 21, 9))
model.add_dose(ev, 2.9, datetime(2021,  1, 24, 10))
model.add_dose(ev, 2.7, datetime(2021,  1, 27, 10))
model.add_dose(ev, 3.0, datetime(2021,  1, 30, 12))
model.add_dose(ev, 2.5, datetime(2021,  2, 1, 9))
model.add_dose(ev, 2.9, datetime(2021,  2, 3, 8))

model.add_lab_data([
    LabData(datetime(2021, 1, 7, 12), {ev: 214.0}),
    LabData(datetime(2021, 1, 25, 12), {ev: 251.0})
])

days_into_future = 30
model.calculate_timeline(date.today() + timedelta(days=days_into_future))
model.estimate_blood_levels(corrected_std_dev=True)

print(model.get_current_blood_level_message(ev))

now = float((datetime.today() - datetime.combine(model.starting_date, time())).total_seconds()) / (3600 * 24)

fortnight_ago = model.duration - (14+days_into_future)*24
month_ago = model.duration - (30+days_into_future)*24

# y_window = (0, 8)
y_window = (0, 400)

# 68% confidence at a single standard deviation
confidence = 68
data = model.get_plot_data(timedelta(days=1), True)

# 95% Confidence at twice the standard deviation
# confidence = 95
# data = model.get_plot_data(True, sd_mult=2)

lab_levels = model.get_plot_lab_levels()

plot_drugs(data=data,
           x_window=(0, model.duration/24.0),
           y_window=y_window,
           y_label="Estimated blood levels (ng/l)",
           lab_data=lab_levels,
           confidence_val=confidence,
           now=now)
plot_drugs(data=data,
           x_window=(fortnight_ago/24.0, (model.duration/24.0)-16),
           y_window=y_window,
           y_label="Estimated blood levels (ng/l)",
           lab_data=lab_levels,
           confidence_val=confidence,
           now=now)
plot_drugs(data=data,
           x_window=(month_ago/24.0, (model.duration/24.0)-16),
           y_window=y_window,
           y_label="Estimated blood levels (ng/l)",
           lab_data=lab_levels,
           confidence_val=confidence,
           now=now)
