from pathlib import Path
from typing import Dict, Union, List, TypedDict, Optional, Tuple, Any, TypeVar
from datetime import datetime, date, timedelta, time

import funcy
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

import re

date_parser_iso = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
date_parser_eu  = re.compile(r"^(\d{2})[./](\d{2})[./](\d{4})$")
time_parser     = re.compile(r"^(\d{1,2}):(\d{2}):(\d{2})$")


T = TypeVar('T', int, float, str, bool)


class YAMLdrug(TypedDict):
  name:   str
  factor: float


class YAMLdose(TypedDict):
  date: datetime
  dose: float


class YAMLevent(TypedDict):
  event_date:         date
  transition:         timedelta


class YAMLmodel(TypedDict):
  start_date:         date
  timedelta:          timedelta
  days_into_future:   int
  corrected_std_dev:  bool
  events:             List[YAMLevent]


class YAMLlabs(TypedDict):
  date:       datetime
  values:     Dict[str, float]


class YAMLplot(TypedDict):
  begin_day:      int
  end_day:        int
  time_absolute:  bool
  title:          Optional[str]
  x_ticks:        Optional[int]
  y_window:       Optional[Tuple[float, float]]


class YAMLgraph(TypedDict):
  y_window:             Tuple[float, float]
  two_std_dev_in_band:  bool
  units:                timedelta
  plots:                List[YAMLplot]
  confidence:           bool
  x_label:              str
  y_label:              str
  x_offset:             int
  deactivate_full_plot: bool
  prediction_error:     bool
  use_x_date:           bool


class YAMLparser(object):
  drugs:            Dict[str, YAMLdrug]
  model:            YAMLmodel
  graph:            YAMLgraph
  labs:             List[YAMLlabs]
  doses:            Dict[str, List[YAMLdose]]
  print_estimates:  List[datetime]

  def __init__(self, file: Path):
    self.drugs            = {}
    self.labs             = []
    self.doses            = {}
    self.print_estimates  = []
    with file.open('r') as yaml_file:
      raw_yaml_data = load(yaml_file, Loader=Loader)
      self.parse_drugs(raw_yaml_data)
      self.parse_model(raw_yaml_data)
      self.parse_graph(raw_yaml_data)
      self.parse_labs(raw_yaml_data)
      self.parse_doses(raw_yaml_data)
      self.parse_print_estimates(raw_yaml_data)

  @staticmethod
  def __general_parser(data: Dict[str, Any],
                       field_in: Union[str, List[str]],
                       datatype: type,
                       default: Optional[T] = None,
                       print_warning: bool = True) -> Optional[T]:
    if not isinstance(field_in, list):
      field_in = [field_in]
    for field in field_in:
      if field in data:
        if isinstance(data[field], datatype):
          return data[field]
        if default is not None and print_warning:
          print(f"WARNING: Cannot parse {field} field as {datatype}, defaulting to {default}, got: {data}")
    return default

  @staticmethod
  def _parse_int(data: Dict[str, Any],
                 field_in: Union[str, List[str]],
                 default: Optional[int] = None) -> Optional[int]:
    return YAMLparser.__general_parser(data, field_in, int, default)

  @staticmethod
  def _parse_float(data: Dict[str, Any],
                   field_in: Union[str, List[str]],
                   default: Optional[float] = None) -> Optional[float]:
    res = YAMLparser.__general_parser(data, field_in, float, None, False)
    if res is None:
      res = YAMLparser.__general_parser(data, field_in, int, None, False)
      if res is not None:
        return float(res)
      else:
        if default is not None:
          print(f"WARNING: Cannot parse {field_in} field as float, defaulting to {default}, got: {data}")
        return default
    else:
      return res

  @staticmethod
  def _parse_str(data: Dict[str, Any],
                 field_in: Union[str, List[str]],
                 default: Optional[str] = None) -> Optional[str]:
    return YAMLparser.__general_parser(data, field_in, str, default)

  @staticmethod
  def _parse_bool(data: Dict[str, Any],
                  field_in: Union[str, List[str]],
                  default: Optional[bool] = None) -> Optional[bool]:
    return YAMLparser.__general_parser(data, field_in, bool, default)

  @staticmethod
  def _parse_time(data: Dict[str, Any],
                  field_in: Union[str, List[str]],
                  default: Optional[time] = None) -> Optional[time]:
    if not isinstance(field_in, list):
      field_in = [field_in]
    for field in field_in:
      if field in data:
        # print(f"{data[field]} ({type(data[field])})")
        if isinstance(data[field], str):
          # print(data[field])
          match = time_parser.match(data[field])
          if match:
            # print("matched time")
            return time(hour=int(match.group(1)), minute=int(match.group(2)), second=int(match.group(3)))
          else:
            print(f"WARNING: time needs to be a valid time, got {data}")
    return default

  @staticmethod
  def _parse_date(data: Dict[str, Any],
                  field_in: Union[str, List[str]],
                  t: Optional[Union[int, time]] = None) -> Union[date, datetime]:
    if not isinstance(field_in, list):
      field_in = [field_in]
    for field in field_in:
      if field in data and isinstance(data[field], datetime):
        return data[field]
      if field in data and isinstance(data[field], date):
        d = data[field]
        if t is not None:
          if isinstance(t, int):
            return datetime(year=d.year, month=d.month, day=d.day, hour=t)
          else:
            return datetime.combine(date(year=d.year, month=d.month, day=d.day), t)
        else:
          return d
    raise Exception(f"ERROR: Cannot parse date in {data}")

  @staticmethod
  def _parse_timedelta(data: Dict[str, Any],
                       field_in: Union[str, List[str]] = "timedelta",
                       default: Optional[timedelta] = timedelta(hours=1)) -> timedelta:
    def parser(d: Dict[str, Union[str, int]]) -> Optional[timedelta]:
      if "unit" in d and "value" in d:
        unit = d["unit"]
        val = d["value"]
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

    if not isinstance(field_in, list):
      field_in = [field_in]
    # noinspection PyBroadException
    for field in field_in:
      try:
        if field in data:
          timedelta_raw = data[field]
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
    return default

  @staticmethod
  def _parse_tuple(data: Dict[str, Any],
                   field_in: Union[str, List[str]] = ("y_window", "y-window"),
                   length: int = 2,
                   check_type: Optional[Union[type, List[type]]] = None,
                   cast: Optional[type] = None,
                   default: Optional[Tuple] = None) -> Optional[Tuple]:
    if not isinstance(field_in, list):
      field_in = [field_in]
    if check_type is not None and not isinstance(check_type, list):
      check_type = [check_type]
    for field in field_in:
      if field in data:
        y_win = data[field]
        if check_type is not None:
          for item in y_win:
            checks = map(lambda x: isinstance(item, x), check_type)
            if not funcy.any(checks):
              print(f"WARNING: Item {item} is not matching the possible types {check_type}")
        if cast is not None:
          y_win = map(cast, y_win)
        if isinstance(y_win, list) and len(y_win) == length:
          return tuple(y_win)
        else:
          print(f"WARNING: Cannot parse y_window, expecting a list of exactly two integers, "
                f"got: {data[field]}")
    return default

  def parse_print_estimates(self, raw_data: Dict[str, Any]) -> None:
    pr_est = None
    if "print_estimates" in raw_data:
      pr_est = raw_data['print_estimates']
    elif "print-estimates" in raw_data:
      pr_est = raw_data['print-estimates']
    if pr_est is not None:
      assert isinstance(pr_est, list)
      for est in pr_est:
        hour = self._parse_int(est, 'hour', 12)
        hour = self._parse_time(est, 'time', hour)
        pr_est_date = self._parse_date(est, 'date', hour)
        self.print_estimates.append(pr_est_date)

  def parse_drugs(self, raw_data: Dict[str, Any]) -> None:
    if "drugs" in raw_data:
      drugs = raw_data['drugs']
    elif "drug" in raw_data:
      drugs = raw_data['drug']
    else:
      raise Exception("ERROR: drugs is a mandatory category")
    assert isinstance(drugs, dict)
    self.drugs = {}
    for k in drugs.keys():
      if isinstance(drugs[k], str):
        self.drugs[k] = YAMLdrug(name=drugs[k], factor=1.0)
      if isinstance(drugs[k], dict):
        drug = drugs[k]
        name = self._parse_str(drug, 'name')
        if name is not None:
          factor = self._parse_float(drug, 'factor', 1.0)
          self.drugs[k] = YAMLdrug(name=name, factor=factor)
        else:
          raise Exception(f"ERROR: drug without a name: {drug}")

  def parse_model(self, raw_data: Dict[str, Any]) -> None:
    def parse_event(ev: Dict[str, Any]) -> Optional[YAMLevent]:
      ev_date = self._parse_date(ev, ['start', 'date', 'start_date', 'start-date'], None)
      if ev_date is None:
        return None
      ev_transition = self._parse_timedelta(ev, ['transition', 'duration'], timedelta(days=30))
      return YAMLevent(event_date=ev_date, transition=ev_transition)

    if "model" in raw_data:
      assert isinstance(raw_data["model"], dict)
      model: Dict[str, Union[str, int, date, bool, Dict[str, Union[str, int]]]] = raw_data["model"]
      if "start_date" in model:
        start_date = YAMLparser._parse_date(model, ['start_date', 'start-date'])
        time_d = self._parse_timedelta(model)
        days_into_future = self._parse_int(model, 'days_into_future', 90)
        corrected_std_dev = self._parse_bool(model, ['corrected_std_dev', 'corrected-std-dev'])
        events = None
        if "event" in model:
          events = model['event']
        elif "events" in model:
          events = model['events']
        event_list = []
        if events is not None:
          if isinstance(events, list):
            for event in events:
              e = parse_event(event)
              if e is not None:
                event_list.append(e)
          elif isinstance(events, dict):
            e = parse_event(events)
            if e is not None:
              event_list.append(e)
          else:
            raise Exception("ERROR: Events needs to be a list or a dictionary")

        self.model = YAMLmodel(start_date=start_date,
                               timedelta=time_d,
                               days_into_future=days_into_future,
                               corrected_std_dev=corrected_std_dev,
                               events=event_list)
      else:
        raise Exception("ERROR: start_date is needed in model!")
    else:
      raise Exception("ERROR: model is a mandatory category")

  def parse_graph(self, raw_data: Dict[str, Any]) -> None:
    def parse_plot(plot_data: Dict[str, Union[int, str]]) -> Optional[YAMLplot]:
      def get_common_parameters(plot_d: Dict[str, Union[int, str]],
                                t_in: Optional[str],
                                x_t_in: int,
                                y_win: Optional[Tuple[float, float]] = None
                                ) -> Tuple[Optional[str], int, Optional[Tuple[float, float]]]:
        t   = self._parse_str(plot_d, 'title', t_in)
        x_t = self._parse_int(plot_d, ['x_ticks', 'x-ticks'], x_t_in)
        y_w = self._parse_tuple(plot_d, ['y-window', 'y_window'], 2, check_type=[float, int], default=y_win)
        return t, x_t, y_w

      past_days = self._parse_int(plot_data, ['past_days', 'past-days', 'past'])
      start_day = self._parse_int(plot_data, ['start_day', 'start-day', 'start'])
      if past_days is not None:
        future_days   = self._parse_int(plot_data, ['future_days', 'future-days', 'future'], 14)
        title, x_ticks, y_win = get_common_parameters(plot_data, None, 7)
        return YAMLplot(begin_day=past_days,
                        end_day=future_days,
                        time_absolute=False,
                        title=title,
                        x_ticks=x_ticks,
                        y_window=y_win)
      elif start_day is not None:
        end_day     = self._parse_int(plot_data, ['end_day', 'end-day', 'end'], start_day + 90)
        title, x_ticks, y_win = get_common_parameters(plot_data, None, 7)
        return YAMLplot(begin_day=start_day,
                        end_day=end_day,
                        time_absolute=True,
                        title=title,
                        x_ticks=x_ticks,
                        y_window=y_win)
      else:
        print(f"WARNING: past_days is a mandatory category, missing in entry, discarding\n\t{plot_data}")
        return None

    y_window: Tuple[int, int]   = (0, 400)
    two_std_dev_in_band:  bool  = True
    plots: List[YAMLplot]       = []
    units                       = timedelta(hours=1)
    deactivate_full_plot        = False
    confidence                  = True
    x_label                     = "Time (days)"
    y_label                     = "Estimated blood levels (ng/l)"
    x_offset                    = 0
    prediction_error            = False
    use_x_date                  = False
    graph = None
    if "graph" in raw_data:
      graph = raw_data['graph']
    elif "graphs" in raw_data:
      graph = raw_data['graphs']
    if graph is not None:
      assert(isinstance(graph, dict))
      y_window = self._parse_tuple(graph, ["y_window", "y-window"], 2, check_type=int, default=y_window)
      two_std_dev_in_band = self._parse_bool(graph, ['two_std_dev_in_band', 'two-std-dev-in-band'], two_std_dev_in_band)
      units = self._parse_timedelta(graph, "units", units)
      prediction_error = self._parse_bool(graph, ['prediction_error', 'prediction-error'], prediction_error)
      deactivate_full_plot = self._parse_bool(graph,
                                              ['deactivate_full_plot', 'deactivate-full-plot'],
                                              deactivate_full_plot)
      confidence = self._parse_bool(graph, 'confidence', confidence)
      use_x_date = self._parse_bool(graph, ['use_x_date', 'use-x-date'], use_x_date)
      x_label = self._parse_str(graph, ['x-label', 'x_label'], x_label)
      y_label = self._parse_str(graph, ['y-label', 'y_label'], y_label)
      x_offset = self._parse_int(graph, ['x_offset', 'x-offset'], 0)
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
                           deactivate_full_plot=deactivate_full_plot,
                           units=units,
                           confidence=confidence,
                           x_label=x_label,
                           y_label=y_label,
                           x_offset=x_offset,
                           prediction_error=prediction_error,
                           use_x_date=use_x_date
                           )

  def parse_labs(self, raw_data: Dict[str, Any]) -> None:
    def parse_lab(lab_data: Dict[str, Union[str, int, date, Dict[str, float]]]) -> Optional[YAMLlabs]:
      values   = {}
      if 'date' in lab_data:
        hour = self._parse_int(lab_data, 'hour', 12)
        hour = self._parse_time(lab_data, 'time', hour)
        lab_date = self._parse_date(lab_data, 'date', hour)
        val = self._parse_float(lab_data, ['values', 'value'])
        if val is None:
          if 'values' in lab_data and isinstance(lab_data['values'], dict):
            val = lab_data['values']
          elif 'value' in lab_data and isinstance(lab_data['value'], dict):
            val = lab_data['values']
          if val is not None:
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
          hour = self._parse_int(dose, 'hour', 9)
          hour = self._parse_time(dose, 'time', hour)
          dose_date = self._parse_date(dose, 'date', hour)
          if dose_date is not None:
            dose_amount = self._parse_float(dose, ['dose', 'amount'])
            if dose_amount is not None:
              repeat = self._parse_timedelta(dose, "repeat", None)
              if repeat is not None:
                count  = self._parse_int(dose['repeat'], 'count', 1) + 1
                for n in range(count):
                  self.doses[drug].append(YAMLdose(date=dose_date+(n*repeat), dose=dose_amount))
              else:
                self.doses[drug].append(YAMLdose(date=dose_date, dose=dose_amount))
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
