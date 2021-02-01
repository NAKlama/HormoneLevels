import math
import operator
from typing import List, Dict, Tuple

import numpy as np

from drugs.drug import Drug
from modelling.dose import Dose
from datetime import datetime, date, timedelta, time
from funcy import concat, take, interleave, repeat, map, count


def delta_to_hours(td: timedelta) -> int:
    return math.ceil(td.total_seconds() / 3600.0)


class BodyModel:
    starting_date = date
    doses_list: Dict[Drug, List[Dose]]
    drugs_timeline: Dict[Drug, List[float]]
    duration: int

    def __init__(self, starting_date: date):
        self.starting_date = starting_date
        self.doses_list = {}
        self.drugs_timeline = {}

    def add_dose(self, drug: Drug, amount: float, time_in: datetime):
        dose = Dose(drug, amount, time_in);
        if dose.time < datetime.combine(self.starting_date, time()):
            raise Exception("Doses cannot be before starting date")
        if dose.drug not in self.doses_list:
            self.doses_list[dose.drug] = []
        for d in dose.get_subdoses():
            self.doses_list[dose.drug].append(d)
        self.doses_list[dose.drug].sort(key=lambda x: x.time)

    def calculate_timeline(self, until: date):
        drugs = set(self.doses_list.keys())
        for drug in drugs:
            self.drugs_timeline[drug] = []
        self.duration = math.ceil((until - self.starting_date).total_seconds() / 3600)
        for t in range(self.duration):
            time_t = datetime.combine(self.starting_date, time()) + timedelta(hours=t)
            for d in drugs:
                if t > 0:
                    last_val = self.drugs_timeline[d][-1]
                    self.drugs_timeline[d].append(last_val * d.one_hour_metabolism())
                else:
                    self.drugs_timeline[d].append(0.0)
                while self.doses_list[d] and len(self.doses_list[d]) > 0 and self.doses_list[d][0].time <= time_t:
                    dose = self.doses_list[d].pop(0)
                    self.drugs_timeline[d][t] += dose.amount

    def get_plot_data(self) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        t_arr = np.array(list(take(self.duration, map(lambda x: x * (1.0/24.0), count()))))
        print(f't_arr.size()={len(t_arr)}')
        out = {}
        for drug, timeline in self.drugs_timeline.items():
            out[drug.name] = np.array(timeline)
            print(f't_arr.size({drug.name})={len(out[drug.name])}')
        return t_arr, out


