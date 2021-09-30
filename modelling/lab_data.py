from datetime import datetime
from typing import Dict, Optional

import drugs


class LabData:
  time: datetime
  labs: Dict[str, float]  # Tuple of value and unit for each drug

  def __init__(self, time: datetime, data: Optional[Dict[str, float]] = None):
    self.time = time
    if data is None:
      self.labs = {}
    else:
      self.labs = data

  def add_value(self, drug, val):
    self.labs[drug] = val

