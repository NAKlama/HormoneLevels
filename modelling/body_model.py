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


import math
from typing import List, Dict, Tuple, Union, Optional, Callable

import funcy
import numpy as np

from drugs.drug import Drug
from datetime import datetime, date, timedelta, time
from funcy import take, map, count, drop, lmap

from modelling.group_sum import GroupSum
from modelling.lab_data import LabData
from modelling.dose import Dose
from modelling.sized_pot import SizedPot
from graphing.color_list import get_color

import multiprocessing as mp


plot_data_type = Union[Tuple[np.ndarray, np.ndarray, np.ndarray],
                       Tuple[np.ndarray, np.ndarray, np.ndarray, str]]


def calculate_running_statistics(in_data: Tuple[List[int], List[float], int]) \
        -> Tuple[List[float], List[float]]:
  steps, list_avg, i = in_data
  sized_pot = SizedPot(steps[i])
  group_sum = GroupSum()
  group_sum.counts_needed(list(steps))
  group_sum.set_data(list_avg)
  average = lmap(lambda s: s[0] / max(min(steps[i], s[1]), 1),
                 zip(map(group_sum.sum_getter(steps[i]), range(len(list_avg))),
                     range(len(list_avg))))
  std_dev = lmap(lambda s: sized_pot.running_std_dev(*s),
                 zip(list_avg, average))
  return average, std_dev


class BodyModel:
  starting_date: date
  step: timedelta
  drugs: Dict[str, Drug]
  doses_list: Dict[str, List[Dose]]
  labs_list: List[LabData]
  blood_level_factors: Dict[str, List[Tuple[float, float]]]
  factors_timeline: Dict[str, List[Tuple[float, float]]]
  running_average:  Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]
  running_stddev:   Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]
  lab_levels: Dict[str, List[Tuple[datetime, float]]]
  lab_events: Dict[str, List[List[Tuple[datetime, float]]]]
  drugs_timeline: Dict[str, List[float]]
  duration: int
  real_duration: int
  doses_count: Dict[str, int]
  doses_amount: Dict[str, float]
  events: List[Tuple[date, timedelta]]
  step_days: Tuple[int, int, int]

  def __init__(self, starting_date: date, time_steps: timedelta):
    self.starting_date = starting_date
    self.drugs = {}
    self.drugs_by_name = {}
    self.step = time_steps
    self.doses_list = {}
    self.drugs_timeline = {}
    self.blood_level_factors = {}
    self.labs_list = []
    self.factor_timeline = {}
    self.lab_levels = {}
    self.lab_events = {}
    self.duration = 0
    self.real_duration = 0
    self.doses_count = {}
    self.doses_amount = {}
    self.events = []
    self.step_days = (5, 30, 90)

  @staticmethod
  def delta_to_hours(td: timedelta) -> int:
    return math.ceil(td.total_seconds() / 3600.0)

  def add_drugs(self, drug_name: str, drug: Drug):
    self.drugs[drug_name] = drug
    self.drugs_by_name[drug.name] = drug_name
    self.doses_amount[drug_name]  = 0
    self.doses_count[drug_name]   = 0

  def add_event(self, when: date, how_long: timedelta):
    self.events.append((when, how_long))
    self.events.sort(key=lambda x: x[0])

  def add_dose(self, drug: str, amount: float, time_in: datetime):
    dose = Dose(self.drugs[drug], amount, time_in)
    if dose.time < datetime.combine(self.starting_date, time()):
      raise Exception("Doses cannot be before starting date")
    if drug not in self.doses_list:
      self.doses_list[drug] = []
    for d in dose.get_partial_doses():
      self.doses_list[drug].append(d)
    self.doses_list[drug].sort(key=lambda x: x.time)
    if drug not in self.doses_count:
      self.doses_count[drug] = 0
    if drug not in self.doses_amount:
      self.doses_amount[drug] = 0.0
    if time_in <= datetime.now():
      self.doses_count[drug] += 1
      self.doses_amount[drug] += amount

  def add_lab_data(self, data_in: Union[LabData, List[LabData]]):
    if type(data_in) is type(LabData):
      data = [data_in]
    else:
      data = data_in
    for d in data:
      self.labs_list.append(d)

  def calculate_timeline(self, until: date):
    drugs = set(self.doses_list.keys())
    while True:
      start_len = len(drugs)
      new_drugs = set()
      for d in drugs:
        for m, _ in self.drugs[d].metabolites:
          new_drugs.add(self.drugs_by_name[m])
      for d in new_drugs:
        drugs.add(d)
      if len(drugs) == start_len:
        break
    for drug in drugs:
      self.drugs_timeline[drug] = []
    self.duration = math.ceil((until - self.starting_date).total_seconds() / self.step.total_seconds())
    self.real_duration = math.ceil((date.today() - self.starting_date).total_seconds() / self.step.total_seconds())
    for t in range(self.duration):
      time_t = datetime.combine(self.starting_date, time()) + self.step * t
      for d in drugs:
        if t > 0:
          last_val = self.drugs_timeline[d][-1]
          curr_val = last_val * self.drugs[d].get_metabolism_factor(self.step)
          self.drugs_timeline[d].append(curr_val)
          metabolites = self.drugs[d].get_metabolites(last_val - curr_val)
          for drug, amount in metabolites:
            if drug not in self.doses_list:
              self.doses_list[self.drugs_by_name[drug]] = []
            self.doses_list[self.drugs_by_name[drug]].insert(0, Dose(self.drugs[self.drugs_by_name[drug]],
                                                             amount, time_t, True))
        else:
          self.drugs_timeline[d].append(0.0)
        while d in self.doses_list and \
                self.doses_list[d] and \
                len(self.doses_list[d]) > 0 and \
                self.doses_list[d][0].time <= time_t:
          dose = self.doses_list[d].pop(0)
          self.drugs_timeline[d][t] += dose.amount

  def __get_timepoint(self, t: datetime) -> int:
    timepoint = datetime(t.year, t.month, t.day, t.hour)
    return math.floor((timepoint - datetime.combine(self.starting_date,
                                                    time())).total_seconds() / self.step.total_seconds())

  def get_drug_at_timepoint(self, d: str, t: datetime) -> float:
    return self.drugs_timeline[d][self.__get_timepoint(t)]

  def get_blood_level_at_timepoint(self, d: str, t: datetime) -> Tuple[float, float, float]:
    timeline    = self.drugs_timeline[d]
    timepoint   = self.__get_timepoint(t)
    # avg = 0.0
    # stddev = 0.0
    if d in self.blood_level_factors:
      if len(self.events) > 0:
        # events_max = len(self.events)-1
        ev_num = 0
        if len(self.events) > 0:
          if len(self.blood_level_factors[d]) > ev_num + 1:
            e_date, e_duration = self.events[ev_num]
            e_date = datetime.combine(e_date, time())
            if e_date+e_duration > t > e_date:
              factor = (t - e_date) / e_duration
              avg_0, stddev_0 = self.blood_level_factors[d][ev_num]
              avg_1, stddev_1 = self.blood_level_factors[d][ev_num+1]
              avg    = avg_1 * factor    + avg_0    + (1-factor)
              stddev = stddev_1 * factor + stddev_0 + (1-factor)
              return timeline[timepoint], avg, stddev
            elif e_date + e_duration <= t:
              ev_num += 1
              return timeline[timepoint], self.blood_level_factors[d][ev_num][0], self.blood_level_factors[d][ev_num][1]
            else:
              return timeline[timepoint], self.blood_level_factors[d][ev_num][0], self.blood_level_factors[d][ev_num][1]
          else:
            return timeline[timepoint], self.blood_level_factors[d][ev_num][0], self.blood_level_factors[d][ev_num][1]
        else:
          return timeline[timepoint], self.blood_level_factors[d][0][0], self.blood_level_factors[d][0][1]
      else:
        avg, stddev = self.blood_level_factors[d][0]
    else:
      avg    = timeline[timepoint]
      stddev = timeline[timepoint]
    return timeline[timepoint], avg, stddev

  def get_current_blood_level_message(self, d: str,
                                      std_dev_count: int = 2,
                                      p_confidence: str = ".046") -> Optional[str]:
    if d in self.lab_levels:
      drug_amount, factor_avg, factor_stddev = self.get_blood_level_at_timepoint(d, datetime.now())
      return f"Estimated blood level ({self.drugs[d].name_blood}): " \
             f"{drug_amount * factor_avg:6.2f} ± " \
             f"{factor_stddev * std_dev_count:5.2f} ng/l (P<{p_confidence})" \
             f"     -     factor: {factor_avg:6.1f}"
    return None

  def estimate_blood_levels(self, corrected_std_dev: bool = True):
    self.lab_events = {}
    for lab_data in self.labs_list:
      for d in lab_data.labs.keys():
        self.lab_levels[d] = []
        self.lab_events[d] = []

    for lab_data in self.labs_list:
      for d, val in lab_data.labs.items():
        self.lab_levels[d].append((lab_data.time, val))
        if len(self.events) > 0:
          for x in range(len(self.events)+1):
            self.lab_events[d].append([])
          for n, event in enumerate(self.events):
            if n == 0 and lab_data.time < datetime.combine(event[0], time()):
              self.lab_events[d][0].append((lab_data.time, val))
              break
            if lab_data.time > datetime.combine(event[0], time()):
              self.lab_events[d][n+1].append((lab_data.time, val))
              break
        else:
          if len(self.lab_events[d]) == 0:
            self.lab_events[d].append([])
          self.lab_events[d][0].append((lab_data.time, val))

    drugs = set(self.lab_levels.keys())
    for d in drugs:
      if d in self.lab_levels:
        if d not in self.blood_level_factors:
          self.blood_level_factors[d] = []
          for _ in range(len(self.events) + 1):
            self.blood_level_factors[d].append((0.0, 0.0))

        for event_num in range(len(self.events)+1):
          level_matcher = list(map(lambda x: (x[1], self.get_drug_at_timepoint(d, x[0])),
                                   self.lab_events[d][event_num]))
          estimates = list(map(lambda x: (x[0] / x[1]), level_matcher))
          average_est = sum(map(lambda x: x / len(estimates), estimates))
          levels = list(map(lambda x: (x[0], x[1] * average_est), level_matcher))
          if len(estimates) > 1 and corrected_std_dev:
            std_dev = math.sqrt(sum(map(lambda x: (x[0] - x[1])**2, levels)) / (len(levels)-1.5))
            # std_dev = math.sqrt(sum(map(lambda x: (x - average_est)**2, estimates)) / (len(estimates)-1))
          else:
            std_dev = math.sqrt(sum(map(lambda x: (x[0] - x[1]) ** 2, levels)) / len(levels))
            # std_dev = math.sqrt(sum(map(lambda x: (x - average_est)**2, estimates)) / len(estimates))

          self.blood_level_factors[d][event_num] = (average_est, std_dev)

  def get_plot_data(self,
                    plot_delta: timedelta = timedelta(days=1),
                    adjusted: bool = False,
                    stddev_multiplier: float = 1.0,
                    offset: float = 0.0,
                    color: bool = False,
                    use_x_date: bool = False) -> \
          Tuple[np.ndarray, Dict[str, plot_data_type]]:
    t_arr = take(self.duration,
                 map(lambda x: x * (self.step.total_seconds()/plot_delta.total_seconds()) + offset,
                     count()))
    if use_x_date:
      t_arr = map(lambda x: datetime.combine(self.starting_date, time()) + plot_delta * x, t_arr)
    t_arr = np.array(list(t_arr))

    # print(f't_arr.size()={len(t_arr)}')
    out = {}
    drugs = sorted(list(self.drugs_timeline.keys()), key=lambda x: self.drugs[x].name)

    step_time_d = int(self.step.total_seconds())

    steps = (int(math.ceil(int(timedelta(days=self.step_days[0]).total_seconds()) / step_time_d)),
             int(math.ceil(int(timedelta(days=self.step_days[1]).total_seconds()) / step_time_d)),
             int(math.ceil(int(timedelta(days=self.step_days[2]).total_seconds()) / step_time_d)))

    self.running_average = {}
    self.running_stddev  = {}

    for n, drug in enumerate(drugs):
      # print(f"{n}: {drug}")
      timeline = self.drugs_timeline[drug]
      drug_name = self.drugs[drug].name_blood
      # print(f"{steps}/{len(timeline)}")

      if self.drugs[drug].factor != 1.0:
        drug_name += f" (x{self.drugs[drug].factor})"

      if adjusted and drug in self.blood_level_factors and len(self.blood_level_factors[drug]) > 0:
        # print(self.blood_level_factors)
        factor_timeline = []
        ev_num = 0
        for t in range(len(timeline)):
          t_time = datetime.combine(self.starting_date, time()) + t * self.step
          if len(self.events) > 0:
            if len(self.blood_level_factors[drug]) > ev_num + 1:
              if datetime.combine(self.events[ev_num][0], time())+self.events[ev_num][1] > \
                      t_time > datetime.combine(self.events[ev_num][0], time()):
                factor: timedelta = t_time - datetime.combine(self.events[ev_num][0], time())
                factor: float = factor / self.events[ev_num][1]
                factor_timeline.append((self.blood_level_factors[drug][ev_num+1][0] * factor +
                                        self.blood_level_factors[drug][ev_num][0] * (1-factor),
                                        self.blood_level_factors[drug][ev_num+1][1] * factor +
                                        self.blood_level_factors[drug][ev_num][1] * (1 - factor)
                                        ))
              elif datetime.combine(self.events[ev_num][0], time()) + self.events[ev_num][1] <= t_time:
                ev_num += 1
                factor_timeline.append(self.blood_level_factors[drug][ev_num])
              else:
                factor_timeline.append(self.blood_level_factors[drug][ev_num])
            else:
              factor_timeline.append(self.blood_level_factors[drug][ev_num])
          else:
            factor_timeline.append(self.blood_level_factors[drug][0])
        self.factor_timeline[drug] = factor_timeline

        list_avg     = lmap(lambda x: x[0] * x[1][0], zip(timeline, factor_timeline))
        arr_avg = np.array(list_avg)
        arr_min = np.array(lmap(
              lambda x: x[0] * x[1][0] - x[1][1] * stddev_multiplier,
              zip(timeline, factor_timeline)))
        arr_max = np.array(lmap(
              lambda x: x[0] * x[1][0] + x[1][1] * stddev_multiplier,
              zip(timeline, factor_timeline)))

        sized_pots: Tuple[SizedPot]
        sized_pots = tuple(map(lambda s: SizedPot(s), steps))

        mp_ctx = mp.get_context('fork')
        statistics_data = [(steps, list_avg, i) for i in range(3)]
        with mp_ctx.Pool(3) as mp_pool:
          statistics_results = mp_pool.map(calculate_running_statistics, statistics_data)

        running_average, running_std_dev = tuple(map(list, list(zip(*statistics_results))))

        self.running_average[drug_name] = tuple(map(np.array, running_average))
        self.running_stddev[drug_name]  = tuple(map(np.array, running_std_dev))

        if color:
          # print(f"{drug}: {n} => {get_color(n)}")
          out[drug_name] = (arr_avg, arr_min, arr_max, get_color(n))
        else:
          out[drug_name] = (arr_avg, arr_min, arr_max)
      else:
        arr = np.array(timeline) * self.drugs[drug].factor
        if color:
          out[drug_name] = (arr, arr, arr, get_color(n))
        else:
          out[drug_name] = (arr, arr, arr)
      # print(f't_arr.size({drug.name})={len(out[drug.name])}')
    return t_arr, out

  def get_statistical_data(self, drug: str) -> Optional[Tuple[float, float]]:
    # print(list(self.blood_level_factors.keys()))
    # print(drug)
    if drug not in self.blood_level_factors:
      return None
    blood_levels   = list(drop(7*24,
                               take(self.real_duration,
                                    map(lambda x: x[0] * x[1][0],
                                        zip(self.drugs_timeline[drug], self.factor_timeline[drug])))))
    levels_avg     = sum(blood_levels) / len(blood_levels)
    sq_delta       = list(map(lambda x: (x - levels_avg)**2, blood_levels))
    levels_std_dev = math.sqrt(sum(sq_delta) / len(blood_levels))
    return levels_avg, levels_std_dev

  def get_plot_lab_levels(self, use_date: bool = False) -> Dict[str, Tuple[List[Union[int, datetime]], List[float]]]:
    lab_levels = {}
    for drug, ll_data in self.lab_levels.items():
      start_time = datetime.combine(self.starting_date, time())
      if use_date:
        times = list(map(funcy.first, ll_data))
      else:
        times = list(map(lambda x: ((x[0] - start_time).total_seconds() / (3600 * 24)), ll_data))
      lab_levels[self.drugs[drug].name_blood] = (
        times,
        list(map(lambda x: x[1], ll_data))
      )
    return lab_levels
