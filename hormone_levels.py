import math

import numpy as np

from drugs import *
from modelling import *
from graphing.plot import plot_drugs

import datetime
from parser.yaml_parser import *
from graphing.color_list import get_color

from sys import argv


STEP_DAYS = (5, 30, 90)


class HormoneLevels:
  config:             YAMLparser
  drugs:              Dict[str, Drug]
  std_dev_count:      int
  p_confidence:       str
  model:              BodyModel
  lab_data_list:      List[LabData]
  days_into_future:   int
  now:                Union[datetime, float]
  duration_factor:    float
  duration:           float
  y_window:           Tuple[float, float]
  data:               Tuple[np.ndarray, Dict[str, plot_data_type]]
  confidence:         Optional[float]
  avg_levels:         Dict[str, Tuple[float, float, str]]
  lab_levels:         Dict[str, Tuple[List[Union[int, datetime]], List[float]]]
  xticks:             int
  start_model:        datetime

  def __init__(self):
    # starttime = datetime.now()

    self.config = YAMLparser(Path(argv[1]))
    self.initialize_drugs(self.config)
    self.get_std_dev_vars(self.config)
    self.model = BodyModel(self.config.model['start_date'],
                           self.config.model['timedelta'])

    self.add_drugs(self.model, self.drugs)
    self.add_doses(self.model, self.config)
    self.get_lab_data(self.model, self.config)
    self.add_events(self.model, self.config)

    self.days_into_future = self.config.model['days_into_future']
    self.model.calculate_timeline(date.today() + timedelta(days=self.days_into_future))

    if len(self.lab_data_list) > 0:
      self.model.estimate_blood_levels(corrected_std_dev=self.config.model['corrected_std_dev'])
      self.print_drug_data(self.model, self.drugs)

    self.now = self.calculate_now()
    self.duration_factor = self.model.step / self.config.graph['units']
    self.duration = self.model.duration * self.duration_factor

    # fortnight_ago     = duration - (14+days_into_future)*24
    # month_ago         = duration - (30+days_into_future)*24
    # three_months_ago  = duration - (90+days_into_future)*24
    # half_year_ago     = duration - (183+days_into_future)*24

    self.y_window = self.config.graph['y_window']

    self.model.step_days = STEP_DAYS
    self.data, self.confidence = self.get_data()
    self.avg_levels, self.lab_levels = self.calculate_lab_levels()

    self.print_estimates()
    self.calculate_xticks()
    self.start_model = datetime.combine(self.config.model['start_date'], time())

    if not self.config.graph['confidence']:
      self.confidence = None

    self.full_plot()
    self.plots()
    self.plot_prediction_error()
    # print(datetime.now() - starttime)

  def initialize_drugs(self, config: YAMLparser) -> None:
    self.drugs = {}
    for drug_key, drug_obj in config.drugs.items():
      drug_name = drug_obj['name']
      drug_factor = drug_obj['factor']
      drug_class = drug_db(drug_name)
      if drug_class is not None:
        self.drugs[drug_key] = drug_class()
        self.drugs[drug_key].factor = drug_factor
      else:
        print(f"WARNING: Cannot find drug {drug_name} in database")

  def get_std_dev_vars(self, config: YAMLparser) -> None:
    self.std_dev_count = 1
    self.p_confidence = ".317"
    if config.graph["two_std_dev_in_band"]:
      self.std_dev_count = 2
      self.p_confidence = ".046"

  @staticmethod
  def add_drugs(model: BodyModel, drugs: Dict[str, Drug]) -> None:
    for drug_key, drug_class in drugs.items():
      model.add_drugs(drug_key, drug_class)

  @staticmethod
  def add_doses(model: BodyModel, config: YAMLparser) -> None:
    for drug_name, doses in config.doses.items():
      for dose in doses:
        model.add_dose(drug_name, dose['dose'], dose['date'])

  def get_lab_data(self, model: BodyModel, config: YAMLparser):
    self.lab_data_list = []
    for lab in config.labs:
      lab_values = {}
      for drug_key, value in lab['values'].items():
        lab_values[drug_key] = value
      self.lab_data_list.append(LabData(lab['date'], lab_values))
    model.add_lab_data(self.lab_data_list)

  @staticmethod
  def add_events(model: BodyModel, config: YAMLparser) -> None:
    if len(config.model['events']) > 0:
      for event in config.model['events']:
        model.add_event(event['event_date'], event['transition'])

  def print_drug_data(self, model: BodyModel, drugs: Dict[str, Drug]) -> None:
    for drug_key in drugs.keys():
      ll_message = model.get_current_blood_level_message(drug_key, self.std_dev_count, self.p_confidence)
      if ll_message is not None:
        print(ll_message)
      if model.doses_count[drug_key] > 0 and model.doses_amount[drug_key] > 0.0:
        print(f"{drugs[drug_key].name}: "
              f"{model.doses_amount[drug_key]:8.2f}mg over {model.doses_count[drug_key]} doses for an average "
              f"dose of {model.doses_amount[drug_key] / model.doses_count[drug_key]:5.3f}mg")

  def calculate_now(self) -> float:
    seconds_since_start = float((datetime.today() - datetime.combine(self.model.starting_date, time())).total_seconds())
    return seconds_since_start / (3600.0 * float(self.config.graph['units'] / self.config.model['timedelta']))

  def get_data(self) -> Tuple[Tuple[np.ndarray, Dict[str, plot_data_type]], float]:
    if self.std_dev_count == 1:
      # 68% confidence at a single standard deviation
      confidence = 68
      data = self.model.get_plot_data(self.config.graph['units'],
                                      True,
                                      color=True,
                                      offset=self.config.graph['x_offset'],
                                      use_x_date=self.config.graph['use_x_date'])
    elif self.std_dev_count == 2:
      # 95% Confidence at twice the standard deviation
      confidence = 95.5
      data = self.model.get_plot_data(self.config.graph['units'],
                                      True,
                                      stddev_multiplier=2,
                                      color=True,
                                      offset=self.config.graph['x_offset'],
                                      use_x_date=self.config.graph['use_x_date'])
    else:
      raise Exception("Can only have one or two standard deviations as banding options")
    return data, confidence

  def calculate_lab_levels(self) -> Tuple[Dict[str, Tuple[float, float, str]],
                                          Dict[str, Tuple[List[Union[int, datetime]], List[float]]]
                                          ]:
    avg_levels = {}
    if len(self.lab_data_list) > 0:
      for n, drug_key in enumerate(self.config.drugs.keys()):
        stats = self.model.get_statistical_data(drug_key)
        if stats is not None:
          avg_level, std_dev_level = stats
          print(f"Average blood level for {self.drugs[drug_key].name} "
                f"is {avg_level:6.2f} "
                f"± {std_dev_level * self.std_dev_count:6.2f} ng/l (P<{self.p_confidence})")
          avg_levels[self.drugs[drug_key].name] = (avg_level, std_dev_level, get_color(n + len(self.drugs) + 1))

      lab_levels = self.model.get_plot_lab_levels(self.config.graph['use_x_date'])
    else:
      lab_levels = None
    return avg_levels, lab_levels

  def print_estimates(self) -> None:
    if len(self.config.print_estimates) > 0:
      for blood_draw in self.config.print_estimates:
        try:
          estimate_at_last_lab = self.model.get_blood_level_at_timepoint('Estradiol', blood_draw)
        except KeyError:
          estimate_at_last_lab = self.model.get_blood_level_at_timepoint('Testosterone', blood_draw)
        print(f"Estimate at {blood_draw}: {estimate_at_last_lab[0] * estimate_at_last_lab[1]:6.2f} ± "
              f"{estimate_at_last_lab[2] * self.std_dev_count:5.2f} ng/l (P<{self.p_confidence})")

  def calculate_xticks(self) -> None:
    self.xticks = 7
    while self.duration > self.xticks * 20:
      self.xticks *= 2

  def full_plot(self) -> None:
    if not self.config.graph['deactivate_full_plot']:
      if self.config.graph['use_x_date']:
        x_win = (self.start_model, self.start_model + self.config.graph['units'] * self.duration)
        self.now = datetime.now()
      else:
        x_win = (0, self.duration)
      plot_drugs(data=self.data,
                 x_window=x_win,
                 y_window=self.y_window,
                 x_label=self.config.graph['x_label'],
                 y_label=self.config.graph['y_label'],
                 lab_data=self.lab_levels,
                 confidence_val=self.confidence,
                 now=self.now,
                 title="Full view",
                 x_ticks=self.xticks,
                 avg_levels=self.avg_levels,
                 plot_dates=self.config.graph['use_x_date'],
                 moving_average=self.model.running_average,
                 moving_deviation=self.model.running_stddev,
                 avg_length=STEP_DAYS,
                 )

  def plots(self) -> None:
    for plot in self.config.graph['plots']:
      if plot['time_absolute']:
        past_window = plot['begin_day']
        future_window = plot['end_day']
      else:
        past_window = self.duration - (plot['begin_day'] + self.days_into_future)
        future_window = (self.duration - self.days_into_future) + plot['end_day']
      if plot['y_window'] is not None:
        y_win = plot['y_window']
      else:
        y_win = self.y_window
      if self.config.graph['use_x_date']:
        x_win = (self.start_model + self.config.graph['units'] * past_window,
                 self.start_model + self.config.graph['units'] * future_window)
        self.now = datetime.now()
      else:
        x_win = (past_window, future_window)
      plot_drugs(data=self.data,
                 x_window=x_win,
                 y_window=y_win,
                 x_ticks=plot['x_ticks'],
                 x_label=self.config.graph['x_label'],
                 y_label=self.config.graph['y_label'],
                 lab_data=self.lab_levels,
                 confidence_val=self.confidence,
                 now=self.now,
                 title=plot['title'],
                 avg_levels=self.avg_levels,
                 plot_dates=self.config.graph['use_x_date'],
                 moving_average=self.model.running_average,
                 moving_deviation=self.model.running_stddev,
                 avg_length=STEP_DAYS,
                 )

  def plot_prediction_error(self) -> None:
    if self.config.graph['prediction_error']:
      times = []
      prediction_data = {}
      arrays = {}
      if self.config.graph['use_x_date']:
        min_t = datetime(2200, 12, 31, 23, 59, 59)
        max_t = datetime(1970, 1, 1, 0, 0, 0)
      else:
        min_t = 10000000
        max_t = 0
      magnitude = 0.0
      x_window = (0, 0)
      for lab in self.config.labs:
        lab_date = lab['date']
        lab_value = lab['values']
        plot_start = datetime.combine(self.config.model['start_date'], time(0, 0, 0))
        if self.config.graph['use_x_date']:
          lab_time = lab_date
          min_t = min(min_t, lab_time)
          max_t = max(max_t, lab_time)
          # if lab_time < min_t:
          #   min_t = lab_time
          # if lab_time > max_t:
          #   max_t = lab_time
          x_window = (min_t - timedelta(days=7), max_t + timedelta(days=7))
        else:
          lab_time = (lab_date - plot_start).total_seconds() / self.config.graph['units'].total_seconds()
          min_t = min(min_t, lab_time)
          max_t = max(max_t, lab_time)
          x_window = (max(min_t - 7, 0), min(max_t + 7, self.duration))

        times.append(lab_time)
        for drug_key, lab_val in lab_value.items():
          predicted = self.model.get_blood_level_at_timepoint(drug_key, lab_date)
          predicted = predicted[0] * predicted[1]
          if drug_key not in prediction_data:
            prediction_data[drug_key] = []
          # print(f"{predicted} -> {lab_val}")
          val = ((lab_val - predicted) / lab_val) * 100
          if val >= 0:
            magnitude = max(magnitude, val)
          else:
            magnitude = max(magnitude, -val)
          prediction_data[drug_key].append(val)
      for drug_key, data in prediction_data.items():
        arrays[drug_key] = (np.array(data), np.array(data), np.array(data))
      if self.config.graph['use_x_date']:
        duration_labs = math.ceil((max_t - min_t + timedelta(days=14)).total_seconds() / (3600 * 24))
      else:
        duration_labs = max_t - min_t + 14
      delta = 7
      tick_count = math.floor(duration_labs / delta)
      while tick_count > 12:
        delta *= 2
        tick_count = math.floor(duration_labs / delta)

      plot_drugs(data=(np.array(times), arrays),
                 x_window=x_window,
                 y_window=(-magnitude * 1.2, magnitude * 1.2),
                 x_ticks=delta,
                 x_label=self.config.graph['x_label'],
                 y_label="Deviation of estimation (%)",
                 title="Prediction accuracy",
                 plot_markers=True,
                 plot_dates=self.config.graph['use_x_date'],
                 )


if __name__ == '__main__':
  HormoneLevels()
