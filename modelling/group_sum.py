import operator
# import sys
from collections import Counter
from typing import List, Union, Iterable, Iterator, Tuple, Callable, Optional, Any, TypeVar
from itertools import tee, chain

from funcy import lmap, flatten, group_by, with_prev


def with_ten_prev(seq: Iterable, fill=None) -> Iterator:
  a, b, c, d, e, f, g, h, i, j, k = tee(seq, 11)
  return zip(a,
             chain([fill], b),
             chain([fill] * 2, c),
             chain([fill] * 3, d),
             chain([fill] * 4, e),
             chain([fill] * 5, f),
             chain([fill] * 6, g),
             chain([fill] * 7, h),
             chain([fill] * 8, i),
             chain([fill] * 9, j),
             chain([fill] * 10, k),
             )


def with_six_prev(seq: Iterable, fill=None) -> Iterator:
  a, b, c, d, e, f, g = tee(seq, 7)
  return zip(a,
             chain([fill], b),
             chain([fill] * 2, c),
             chain([fill] * 3, d),
             chain([fill] * 4, e),
             chain([fill] * 5, f),
             chain([fill] * 6, g),
             )


def with_four_prev(seq: Iterable, fill=None) -> Iterator:
  a, b, c, d, e = tee(seq, 5)
  return zip(a,
             chain([fill], b),
             chain([fill] * 2, c),
             chain([fill] * 3, d),
             chain([fill] * 4, e),
             )


def with_two_prev(seq: Iterable, fill=None) -> Iterator:
  a, b, c = tee(seq, 3)
  return zip(a,
             chain([fill], b),
             chain([fill] * 2, c),
             )


TEST_FACTORS = [2, 3, 5, 7, 11]

FACTOR_GROUPER = {
  2: with_prev,
  3: with_two_prev,
  5: with_four_prev,
  7: with_six_prev,
  11: with_ten_prev,
}


def group_sums(group_f: Callable[[Iterable, float], List[float]],
               in_list: List[float]) -> List[float]:
  return lmap(sum, group_f(in_list, 0.0))


def modulo_group(n: int, seq: Iterable) -> List[List[Any]]:
  grouped = group_by(lambda l: l[0] % n, enumerate(seq))
  return lmap(lambda l: lmap(lambda t: t[1], l), map(lambda g: grouped[g], range(0, n)))


WithFactors = Tuple[int, List[int]]
T = TypeVar('T')


def product(seq: Iterable[T]) -> T:
  from functools import reduce
  return reduce(operator.mul, seq)


class GroupSum:
  factors: List[int]

  groups:   Optional[List["GroupSum"]]
  # data:     List[float]
  raw_data: List[float]

  def __init__(self, factors=None):
    if factors is None:
      factors = []
    self.factors = factors
    # self.data     = []
    self.groups   = None

  def counts_needed(self, cn: Union[int, List[int]]):
    # print(f"Sizes: {cn}")
    _, common_factors = self.__get_common_factors(map(self.__factorize, cn))
    common_factors.sort()
    self.factors = common_factors
    # # print(f"Common Factors: {common_factors} sum={product(common_factors)}")
    # residuals = lremove(lambda r: r <= 1, map(lambda f: f // product(common_factors), cn))
    # while len(residuals) > 1:
    #   # print(f"Residual size: {residuals}")
    #   _, additional_factors = self.__factorize(min(residuals))
    #   additional_factors.sort()
    #   self.factors = additional_factors + self.factors
    #   residuals = lremove(lambda r: r <= 1, map(lambda f: f // product(self.factors), cn))
    # # print(f"Factors: {self.factors}")

  def set_data(self, data: List[float]):
    def generate_next_level(factors: List[int]) -> Callable[[List[float]], Optional["GroupSum"]]:
      def worker(d: List[float]) -> Optional["GroupSum"]:
        if len(factors) == 0:
          return None
        gs = GroupSum(factors)
        gs.set_data(d)
        return gs
      return worker
    if len(self.factors) > 1:
      factor = self.factors[-1]
      self.raw_data = data
      self.groups = lmap(generate_next_level(self.factors[:-1]),
                         modulo_group(factor, group_sums(FACTOR_GROUPER[factor], data)))
    else:
      self.raw_data = data
      # self.data = data
      self.groups = None

  def getsum(self, length: int, n: int) -> float:
    if self.groups is not None:
      this_factor = len(self.groups)
    else:
      this_factor = 1
    if self.groups is None:
      assert(this_factor == 1)
      residual   = length
      take_count = 0
    else:
      take_count = length // this_factor
      residual   = length % this_factor
    item_num   = n // this_factor
    offset     = n % this_factor

    out_sum = 0.0

    if take_count > 0 and residual == 0 and length != this_factor:
      out_sum += self.groups[offset].getsum(take_count, item_num)
    else:
      if length > n:
        out_sum += sum(self.raw_data[:n+1])
      else:
        out_sum += sum(self.raw_data[n-length+1:n+1])
    return out_sum

  def sum_getter(self, length: int) -> Callable[[int], float]:
    def worker(n: int) -> float:
      return self.getsum(length, n)
    return worker

  @staticmethod
  def __get_common_factors(factors_list: Iterable[WithFactors]) -> Tuple[List[WithFactors], List[int]]:
    fl_a, fl_b = tee(factors_list, 2)
    residual_factors = lmap(lambda fl: (fl[0], []), fl_a)
    common_factors = []
    grouped_factors = lmap(lambda wf: Counter(wf[1]),
                           fl_b)
    factors = set(flatten(map(lambda gf: list(gf.keys()), grouped_factors)))
    for f in factors:
      cnt = lmap(lambda gf: gf[f], grouped_factors)
      min_cnt = min(cnt)
      common_factors += [f] * min_cnt
      for rf, rf_cnt_old in zip(residual_factors, cnt):
        rf_cnt = rf_cnt_old - min_cnt
        if rf_cnt > 0:
          rf[1].append([f] * rf_cnt)
    return residual_factors, common_factors

  @staticmethod
  def __factorize(num_in: int) -> WithFactors:
    i = num_in
    found_factor = True
    factors = []
    while found_factor:
      found_factor = False
      for f in TEST_FACTORS:
        if f > i:
          break
        if i % f == 0:
          i /= f
          factors.append(f)
          found_factor = True
          break
    if i > 1:
      factors.append(i)
    return num_in, factors
