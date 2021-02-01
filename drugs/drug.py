from typing import Optional, List, Tuple, Type, Iterable, Dict
from drugs.drug_classes import DrugClass
from datetime import timedelta
from funcy import map, repeat, take


class Drug(object):
    name:                   str
    half_life:              timedelta
    drug_class:             Optional[DrugClass]
    flood_in:               Optional[List[float]]
    blood_value_factor:     float
    metabolites:             List[Tuple[Type["Drug"], float]]

    def __init__(self, name: str, half_life: timedelta, drug_class: Optional[DrugClass] = None):
        self.name       = name
        self.half_life  = half_life
        self.drug_class = drug_class
        self.flood_in   = None
        self.metabolites = []

    def set_flood_in(self, flood_in: List[float]):
        self.flood_in = flood_in
        total = sum(flood_in)
        self.flood_in = list(map(lambda x: x/total, self.flood_in))

    def add_metabolite(self, drug_in: Type["Drug"], factor: float):
        self.metabolites.append((drug_in, factor))

    def one_hour_metabolism(self) -> float:
        hl_hours = self.half_life.total_seconds() / 3600.0
        factor = 2 ** (-1.0 / hl_hours)
        return factor

    def get_metabolites(self, decay_curve: Iterable[float]) -> Dict[Type["Drug"], Iterable[float]]:
        out = {}
        for d, factor in self.metabolites:
            print(d.get_name())
            if d not in out:
                out[d] = []
                out[d].append(repeat(0.0))
            curve = map(lambda x: x * d.one_hour_metabolism() * factor, decay_curve)
            print(list(take(10, curve)))
            # metabolites = drug.get_metabolites(curve)
            # for d, crv in metabolites.items():
            #     if d not in out:
            #         out[d] = []
            #         out[d].append(repeat(0.0))
            #     out[d].append(crv)
        return out

    def get_name(self) -> str:
        return self.name

    def __hash__(self):
        return hash(self.name)