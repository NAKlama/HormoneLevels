from pathlib import Path

from drugs import *
from modelling import *
from graphing.plot import plot_drugs

from datetime import time

from parser.yaml_parser import *

from graphing.color_list import get_color

config = YAMLparser(Path('hormones.yaml'))

drugs = {}
for drug_key, drug_name in config.drugs.items():
  drug_class = drug_db(drug_name)
  if drug_class is not None:
    drugs[drug_key] = drug_class()
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
model.estimate_blood_levels(corrected_std_dev=config.model['corrected_std_dev'])

for drug in drugs.keys():
  print(model.get_current_blood_level_message(drug))
  print(f"{drugs[drug].name}: "
        f"{model.doses_amount[drug]:8.2f}mg over {model.doses_count[drug]} doses for an average "
        f"dose of {model.doses_amount[drug]/model.doses_count[drug]:5.3f}mg")

now = float((datetime.today() - datetime.combine(model.starting_date, time())).total_seconds()) / \
      (3600.0 * float(config.graph['units'] / config.model['timedelta']))
duration_factor = model.step / config.graph['units']
duration = model.duration * duration_factor

fortnight_ago     = duration - (14+days_into_future)*24
month_ago         = duration - (30+days_into_future)*24
three_months_ago  = duration - (90+days_into_future)*24
half_year_ago     = duration - (183+days_into_future)*24

y_window = config.graph['y_window']

if config.graph['two_std_dev_in_band']:
  std_deviations_in_band = 2
else:
  std_deviations_in_band = 1

if std_deviations_in_band == 1:
  # 68% confidence at a single standard deviation
  confidence = 68
  data = model.get_plot_data(config.graph['units'], True, color=True)
elif std_deviations_in_band == 2:
  # 95% Confidence at twice the standard deviation
  confidence = 95.5
  data = model.get_plot_data(config.graph['units'], True, stddev_multiplier=2, color=True)
else:
  raise Exception("Can only have one or two standard deviations as banding options")

avg_levels = {}
for n, drug in enumerate(config.doses.keys()):
  avg_level, std_dev_level = model.get_statistical_data(drug)
  print(f"Average blood level for {drugs[drug].name} is {avg_level:6.2f} ± {std_dev_level*2:6.2f} ng/l (P<.046)")
  avg_levels[drugs[drug].name] = (avg_level, std_dev_level, get_color(n+len(drugs)+1))

lab_levels = model.get_plot_lab_levels()

xticks = 7
while duration > xticks * 20:
  xticks *= 2

plot_drugs(data=data,
           x_window=(0, duration),
           y_window=y_window,
           y_label="Estimated blood levels (ng/l)",
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
             y_label="Estimated blood levels (ng/l)",
             lab_data=lab_levels,
             confidence_val=confidence,
             now=now,
             title=plot['title'],
             avg_levels=avg_levels
             )
