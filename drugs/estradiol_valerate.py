import drugs.drug as drug
from datetime import timedelta
# from drugs import Estradiol


class EstradiolValerate(drug.Drug):
    def __init__(self):
        super().__init__("Estradiol", timedelta(days=4, hours=12))
        self.set_flood_in([1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
                           7, 7, 7, 7, 6, 6, 6, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1, .5, .5])
