import math
from pathlib import Path

import numpy as np

from drugs import *
from modelling import *
from graphing.plot import plot_drugs

from datetime import time

from parser.yaml_parser import *

from graphing.color_list import get_color

from sys import argv

config = YAMLparser(Path(argv[1]))

drugs = {}
for drug_key, drug in config.drugs.items():
  drug_name    = drug['name']
  drug_factor  = drug['factor']
  drug_class = drug_db(drug_name)
  if drug_class is not None:
    drugs[drug_key] = drug_class()
    drugs[drug_key].factor = drug_factor
  else:
    print(f"WARNING: Cannot find drug {drug_name} in database")

model = BodyModel(config.model['start_date'], config.model['timedelta'])
for drug_key, drug_class in drugs.items():
  model.add_drugs(drug_key, drug_class)

for drug, doses in config.doses.items():
  for dose in doses:
    model.add_dose(drug, dose['dose'], dose['date'])

lab_data = []
for lab in config.labs:
  lab_values = {}
  for drug, value in lab['values'].items():
    lab_values[drug] = value
  lab_data.append(LabData(lab['date'], lab_values))
model.add_lab_data(lab_data)

days_into_future = config.model['days_into_future']
model.calculate_timeline(date.today() + timedelta(days=days_into_future))
if len(lab_data) > 0:
  model.estimate_blood_levels(corrected_std_dev=config.model['corrected_std_dev'])

  for drug in drugs.keys():
    ll_message = model.get_current_blood_level_message(drug)
    if ll_message is not None:
      print(ll_message)
    if model.doses_count[drug] > 0 and model.doses_amount[drug] > 0.0:
      print(f"{drugs[drug].name}: "
            f"{model.doses_amount[drug]:8.2f}mg over {model.doses_count[drug]} doses for an average "
            f"dose of {model.doses_amount[drug]/model.doses_count[drug]:5.3f}mg")

now = float((datetime.today() - datetime.combine(model.starting_date, time())).total_seconds()) / \
      (3600.0 * float(config.graph['units'] / config.model['timedelta']))
duration_factor = model.step / config.graph['units']
duration = model.duration * duration_factor

# fortnight_ago     = duration - (14+days_into_future)*24
# month_ago         = duration - (30+days_into_future)*24
# three_months_ago  = duration - (90+days_into_future)*24
# half_year_ago     = duration - (183+days_into_future)*24

y_window = config.graph['y_window']

if config.graph['two_std_dev_in_band']:
  std_deviations_in_band = 2
else:
  std_deviations_in_band = 1

if std_deviations_in_band == 1:
  # 68% confidence at a single standard deviation
  confidence = 68
  data = model.get_plot_data(config.graph['units'], True,
                             color=True, offset=config.graph['x_offset'])
elif std_deviations_in_band == 2:
  # 95% Confidence at twice the standard deviation
  confidence = 95.5
  data = model.get_plot_data(config.graph['units'], True,
                             stddev_multiplier=2, color=True, offset=config.graph['x_offset'])
else:
  raise Exception("Can only have one or two standard deviations as banding options")

avg_levels = {}
if len(lab_data) > 0:
  for n, drug in enumerate(config.drugs.keys()):
    stats = model.get_statistical_data(drug)
    if stats is not None:
      avg_level, std_dev_level = stats
      print(f"Average blood level for {drugs[drug].name} is {avg_level:6.2f} ± {std_dev_level*2:6.2f} ng/l (P<.046)")
      avg_levels[drugs[drug].name] = (avg_level, std_dev_level, get_color(n+len(drugs)+1))

  lab_levels = model.get_plot_lab_levels()
else:
  lab_levels = None

# blood_draw = datetime(year=2021, month=10, day=7, hour=10, minute=40)
# if blood_draw is not None:
#   estimate_at_last_lab = model.get_blood_level_at_timepoint('estradiol', blood_draw)
#   print(f"Estimate at blood draw: {estimate_at_last_lab[0] * estimate_at_last_lab[1]:6.2f} ± "
#         f"{estimate_at_last_lab[2]*2:5.2f} ng/l (P<.046)")

xticks = 7
while duration > xticks * 20:
  xticks *= 2

if not config.graph['confidence']:
  confidence = None

if not config.graph['deactivate_full_plot']:
  plot_drugs(data=data,
             x_window=(0, duration),
             y_window=y_window,
             x_label=config.graph['x_label'],
             y_label=config.graph['y_label'],
             lab_data=lab_levels,
             confidence_val=confidence,
             now=now,
             title="Full view",
             x_ticks=xticks,
             avg_levels=avg_levels)

for plot in config.graph['plots']:
  if plot['time_absolute']:
    past_window   = plot['begin_day']
    future_window = plot['end_day']
  else:
    past_window   = duration - (plot['begin_day'] + days_into_future)
    future_window = (duration - days_into_future) + plot['end_day']
  plot_drugs(data=data,
             x_window=(past_window, future_window),
             y_window=y_window,
             x_ticks=plot['x_ticks'],
             x_label=config.graph['x_label'],
             y_label=config.graph['y_label'],
             lab_data=lab_levels,
             confidence_val=confidence,
             now=now,
             title=plot['title'],
             avg_levels=avg_levels
             )

if config.graph['prediction_error']:
  times = []
  prediction_data = {}
  arrays = {}
  min_t = 10000000
  max_t = 0
  magnitude = 0.0
  for lab in config.labs:
    lab_date   = lab['date']
    lab_value  = lab['values']
    plot_start = datetime.combine(config.model['start_date'], time(0, 0, 0))
    lab_time   = (lab_date - plot_start).total_seconds() / config.graph['units'].total_seconds()
    min_t      = min(min_t, lab_time)
    max_t      = max(max_t, lab_time)
    times.append(lab_time)
    for drug, lab_val in lab_value.items():
      predicted = model.get_blood_level_at_timepoint(drug, lab_date)
      predicted = predicted[0] * predicted[1]
      if drug not in prediction_data:
        prediction_data[drug] = []
      # print(f"{predicted} -> {lab_val}")
      val = ((lab_val - predicted) / lab_val) * 100
      if val >= 0:
        magnitude = max(magnitude, val)
      else:
        magnitude = max(magnitude, -val)
      prediction_data[drug].append(val)
  for drug, data in prediction_data.items():
    arrays[drug] = (np.array(data), np.array(data), np.array(data))
  duration_labs = max_t - min_t + 14
  delta = 7
  tick_count = math.floor(duration_labs / delta)
  while tick_count > 12:
    delta *= 2
    tick_count = math.floor(duration_labs / delta)

  plot_drugs(data=(np.array(times), arrays),
             x_window=(max(min_t - 7, 0), min(max_t + 7, duration)),
             y_window=(-magnitude * 1.2, magnitude * 1.2),
             x_ticks=delta,
             x_label=config.graph['x_label'],
             y_label="Deviation of estimation (%)",
             title="Prediction accuracy",
             plot_markers=True,
             )


