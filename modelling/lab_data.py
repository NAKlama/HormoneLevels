from datetime import datetime
from typing import Dict, Tuple

import drugs


class LabData:
    time: datetime
    labs: Dict[drugs.drug.Drug, float]  # Tuple of value and unit for each drug

    def __init__(self, time: datetime):
        self.time = time
        self.labs = {}

    def add_value(self, drug, val):
        self.labs[drug] = val

