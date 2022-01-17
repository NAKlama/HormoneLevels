from typing import List
from funcy import map
from math import sqrt


class SizedPot(object):
  size: int
  data: List[float]
  sum: float

  def __init__(self, size: int):
    self.size = size
    self.data = []

  def add_data(self, point: float):
    self.data.append(point)
    while len(self.data) > self.size:
      self.data.pop(0)

  def calc_std_dev(self, average: float) -> float:
    sqsum = sum(map(lambda x: (x - average)**2, self.data))
    if len(self.data) <= 1:
      return 0.0
    size_factor = 1 / (len(self.data) - 1.5)
    return sqrt(size_factor * sqsum)

  def running_std_dev(self, point: float, average: float):
    self.add_data(point)
    return self.calc_std_dev(average)
