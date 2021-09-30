from pathlib import Path
from typing import Dict, Union, List, TypedDict, Optional, Tuple, Any
from datetime import datetime, date, timedelta

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

import re

date_parser_iso = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
date_parser_eu  = re.compile(r"(\d{2})[./](\d{2})[./](\d{4})")


class YAMLdose(TypedDict):
  date: datetime
  dose: float


class YAMLmodel(TypedDict):
  start_date:         date
  timedelta:          timedelta
  days_into_future:   int
  corrected_std_dev:  bool


class YAMLlabs(TypedDict):
  date:       datetime
  values:     Dict[str, float]


class YAMLplot(TypedDict):
  begin_day:      int
  end_day:        int
  time_absolute:  bool
  title:          Optional[str]
  x_ticks:        Optional[int]


class YAMLgraph(TypedDict):
  y_window:             Tuple[int, int]
  two_std_dev_in_band:  bool
  units:                timedelta
  plots:                List[YAMLplot]


class YAMLparser(object):
  drugs:  Dict[str, str]
  model:  YAMLmodel
  graph:  YAMLgraph
  labs:   List[YAMLlabs]
  doses:  Dict[str, List[YAMLdose]]

  def __init__(self, file: Path):
    self.drugs = {}
    self.labs  = []
    self.doses = {}
    with file.open('r') as yaml_file:
      raw_data = load(yaml_file, Loader=Loader)
      self.parse_drugs(raw_data)
      self.parse_model(raw_data)
      self.parse_graph(raw_data)
      self.parse_labs(raw_data)
      self.parse_doses(raw_data)

  def parse_drugs(self, raw_data: Dict[str, Any]) -> None:
    drugs = None
    if "drugs" in raw_data:
      drugs = raw_data['drugs']
    elif "drug" in raw_data:
      drugs = raw_data['drug']
    else:
      raise Exception("ERROR: drugs is a mandatory category")
    assert isinstance(drugs, dict)
    self.drugs = drugs

  def parse_model(self, raw_data: Dict[str, Any]) -> None:
    if "model" in raw_data:
      assert isinstance(raw_data["model"], dict)
      model: Dict[str, Union[str, int, date, bool, Dict[str, Union[str, int]]]] = raw_data["model"]
      if "start_date" in model:
        start_date = YAMLparser.parse_date(model["start_date"])
        time_d = self.parse_timedelta(model)
        days_into_future = 90
        if "days_into_future" in model:
          if isinstance(model["days_into_future"], int):
            days_into_future = model["days_into_future"]
          else:
            print(f"WARNING: Cannot parse days_into_future as int: {model['days_into_future']}")
        corrected_std_dev = True
        if "corrected_std_dev" in model:
          if isinstance(model["corrected_std_dev"], bool):
            corrected_std_dev = model["corrected_std_dev"]
          else:
            print(f"WARNING: Cannot parse corrected_std_dev as bool: {model['corrected_std_dev']}")
        self.model = YAMLmodel(start_date=start_date,
                               timedelta=time_d,
                               days_into_future=days_into_future,
                               corrected_std_dev=corrected_std_dev)
      else:
        raise Exception("ERROR: start_date is needed in model!")
    else:
      raise Exception("ERROR: model is a mandatory category")

  def parse_graph(self, raw_data: Dict[str, Any]) -> None:
    def parse_plot(plot_data: Dict[str, Union[int, str]]) -> Optional[YAMLplot]:
      def get_title_x_ticks(plot_d: Dict[str, Union[int, str]],
                            t_in: Optional[str],
                            x_t_in: int) -> Tuple[Optional[str], int]:
        t   = t_in
        x_t = x_t_in
        if "title" in plot_data:
          t = str(plot_data['title'])
        if "x_ticks" in plot_data:
          if isinstance(plot_data['x_ticks'], int):
            x_t = plot_data['x_ticks']
          else:
            print(f"WARNING: x_ticks needs to be an integer, got: {plot_data['x_ticks']}\n"
                  f"         using default value of 7")
        return t, x_t

      if "past_days" in plot_data:
        if not isinstance(plot_data['past_days'], int):
          print(f"WARNING: past_days needs to be an integer, got: {plot_data['past_days']}")
          return None
        past_days     = plot_data['past_days']
        future_days   = 14
        if "future_days" in plot_data:
          if isinstance(plot_data['future_days'], int):
            future_days = plot_data['future_days']
          else:
            print(f"WARNING: past_days needs to be an integer, got: {plot_data['past_days']}\n"
                  f"         using default value of 14")
        title, x_ticks = get_title_x_ticks(plot_data, None, 7)
        return YAMLplot(begin_day=past_days,
                        end_day=future_days,
                        time_absolute=False,
                        title=title,
                        x_ticks=x_ticks)
      elif "start_day" in plot_data:
        if not isinstance(plot_data['start_day'], int):
          print(f"WARNING: start_day needs to be an integer, got: {plot_data['start_day']}")
          return None
        start_day   = plot_data['start_day']
        end_day     = start_day + 90
        if "end_day" in plot_data:
          if not isinstance(plot_data['end_day'], int):
            print(f"WARNING: end_day needs to be an integer, got: {plot_data['end_day']}")
            return None
          end_day = plot_data['end_day']
        title, x_ticks = get_title_x_ticks(plot_data, None, 7)
        return YAMLplot(begin_day=start_day,
                        end_day=end_day,
                        time_absolute=True,
                        title=title,
                        x_ticks=x_ticks)
      else:
        print(f"WARNING: past_days is a mandatory category, missing in entry, discarding\n\t{plot_data}")
        return None

    y_window: Tuple[int, int]   = (0, 400)
    two_std_dev_in_band:  bool  = True
    plots: List[YAMLplot]       = []
    units                       = timedelta(seconds=1)
    graph = None
    if "graph" in raw_data:
      graph = raw_data['graph']
    elif "graphs" in raw_data:
      graph = raw_data['graphs']
    if graph is not None:  
      assert(isinstance(graph, dict))
      if "y_window" in graph:
        y_win = graph['y_window']
        if isinstance(y_win, list) and len(y_win) == 2 and isinstance(y_win[0], int) and isinstance(y_win[1], int):
          y_window = tuple(y_win)
        else:
          print(f"WARNING: Cannot parse y_window, expecting a list of exactly two integers, "
                f"got: {graph['y_window']}")
      if "two_std_dev_in_band" in raw_data:
        tsdib = raw_data['two_std_dev_in_band']
        if isinstance(tsdib, bool):
          two_std_dev_in_band = tsdib
        else:
          print(f"WARNING: Cannot parse two_std_dev_in_band as bool, got: {tsdib}")
      units = self.parse_timedelta(graph, "units")
      if "plots" in graph:
        plts = graph['plots']
        if isinstance(plts, dict):
          p = parse_plot(plts)
          if p is not None:
            plots.append(p)
        elif isinstance(plts, list):
          for pl in plts:
            p = parse_plot(pl)
            if p is not None:
              plots.append(p)
        else:
          print(f"WARNING: Cannot parse plots, got: {plts}")
    self.graph = YAMLgraph(y_window=y_window,
                           two_std_dev_in_band=two_std_dev_in_band,
                           plots=plots,
                           units=units)
    
  def parse_labs(self, raw_data: Dict[str, Any]) -> None:
    def parse_lab(lab_data: Dict[str, Union[str, int, date, Dict[str, float]]]) -> Optional[YAMLlabs]:
      lab_date = None
      hour     = 12
      values   = {}
      if 'date' in lab_data:
        if 'hour' in lab_data:
          if isinstance(lab_data['hour'], int):
            hour = lab_data['hour']
          else:
            print(f"WARNING: Cannot parse hour field, defaulting to 12, got: {lab_data}")
        else:
          print(f"INFO: Hour not defined for lab data, defaulting to 12")
        if isinstance(lab_data['date'], date):
          lab_date = self.parse_date(lab_data['date'], hour)
        else:
          print(f"WARNING: Date needs to be a valid date, got: {lab_data}")
        val = None
        if 'values' in lab_data:
          val = lab_data['values']
        elif 'value' in lab_data:
          val = lab_data['value']
        if val is not None:
          if isinstance(val, dict):
            for k, v in val.items():
              if isinstance(k, str) and (isinstance(v, float) or isinstance(v, int)):
                values[k] = float(v)
              else:
                print(f"WARNING: Expected a dict of str->float for lab values, got: {lab_data}")
          else:
            print(f"WARNING: Expected a dict of str->float for lab values, got: {lab_data}")
        else:
          print(f"WARNING: Lab data without values: {lab_data}")
          return None
      else:
        print(f"WARNING: Missing date field from lab data, it is mandatory, skipping entry: {lab_data}")
        return None
      if len(values) == 0:
        return None
      if lab_date is None:
        return None
      return YAMLlabs(date=lab_date, values=values)
    
    labs = None
    if "labs" in raw_data:
      labs = raw_data['labs']
    elif "lab" in raw_data:
      labs = raw_data['lab']
    if labs is not None:
      if isinstance(labs, dict):
        lab = parse_lab(labs)
        if lab is not None:
          self.labs.append(lab)
      if isinstance(labs, list):
        for lab in labs:
          lb = parse_lab(lab)
          if lb is not None:
            self.labs.append(lb)

  def parse_doses(self, raw_data: Dict[str, Any]) -> None:
    drug_doses = None
    if 'doses' in raw_data:
      drug_doses = raw_data['doses']
    elif 'dose' in raw_data:
      drug_doses = raw_data['dose']
    if drug_doses is None:
      raise Exception("ERROR: Doses is a mandatory field")
    if not isinstance(drug_doses, dict):
      raise Exception("ERROR: Doses needs to be a dict of drugs with a list of doses as value")
    for drug, doses in drug_doses.items():
      if drug not in self.drugs:
        print(f"WARNING: Could not find reference {drug} in the drugs section, skipping")
        continue
      if not isinstance(doses, list):
        print(f"WARNING: Doses must be in a list, skipping.\n"
              f"         got: {doses[0:max(80, len(doses))]}")
        continue
      self.doses[drug] = []
      for dose in doses:
        if 'date' in dose:
          hour = 9
          if 'hour' in dose:
            if isinstance(dose['hour'], int):
              hour = dose['hour']
            else:
              print(f"WARNING: hour needs to be an integer, got {dose['hour']}")
          if isinstance(dose['date'], date):
            dose_date = self.parse_date(dose['date'], hour)
            if 'dose' in dose:
              if isinstance(dose['dose'], float) or isinstance(dose['dose'], int):
                dose_amount = float(dose['dose'])
                self.doses[drug].append(YAMLdose(date=dose_date, dose=dose_amount))
              else:
                print(f"WARMING: dose needs to be numeric, skipping\n"
                      f"         got {dose}")
            else:
              print(f"WARNING: dose is a mandatory field for a dose, skipping\n"
                    f"         got {dose}")
          else:
            print(f"WARNING: date must be a valid date, got {dose['date']}")
        else:
          print(f"WARNING: date is a mandatory field for a dose, skipping\n"
                f"         got: {dose}")
    cumulative_length = 0
    for doses in self.doses.values():
      cumulative_length += len(doses)
    if cumulative_length == 0:
      raise Exception("ERROR: we need doese to do a calculation")

  @staticmethod
  def parse_timedelta(model: Dict[str, Any], name: str = "timedelta") -> timedelta:
    def parser(data: Dict[str, Union[str, int]]) -> Optional[timedelta]:
      if "unit" in data and "value" in data:
        unit  = data["unit"]
        val = data["value"]
        if unit in ['weeks', 'week', 'wk', 'w']:
          return timedelta(weeks=val)
        if unit in ['days', 'day', 'd']:
          return timedelta(days=val)
        if unit in ['hours', 'hour', 'h']:
          return timedelta(hours=val)
        if unit in ['minutes', 'minute', 'min', 'm']:
          return timedelta(minutes=val)
        if unit in ['seconds', 'second', 'sec', 's']:
          return timedelta(seconds=val)
        if unit in ['milliseconds', 'millisecond', 'ms']:
          return timedelta(milliseconds=val)
        if unit in ['microseconds', 'microsecond', 'us', 'µs']:
          return timedelta(microseconds=val)
        return None

    # noinspection PyBroadException
    try:
      if name in model:
        timedelta_raw = model[name]
        if isinstance(timedelta_raw, list):
          out = timedelta(seconds=0)
          for td in timedelta_raw:
            value = parser(td)
            if value is not None:
              out += value
            else:
              print(f"WARNING: Couldn't parse partial timedelta: {td}")
          return out
        if isinstance(timedelta_raw, dict):
          value = parser(timedelta_raw)
          if value is not None:
            return value
          else:
            print(f"WARNING: Couldn't parse timedelte: {timedelta_raw}\n"
                  f"NOTICE: Using default timedelta of 1 hour")
            return timedelta(hours=1)
    except Exception as e:
      print(f"WARNING: Parsing Error: {e}")
      return timedelta(hours=1)

  @staticmethod
  def parse_date(d: date, t: Optional[int] = None) -> Union[date, datetime]:
    if t is not None:
      return datetime(year=d.year, month=d.month, day=d.day, hour=t)
    else:
      return date(year=d.year, month=d.month, day=d.day)
