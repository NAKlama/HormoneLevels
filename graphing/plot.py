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

from typing import Optional, Tuple, Dict
import matplotlib.pyplot as plt
import numpy as np


def plot_drugs(data:            Tuple[np.ndarray, Dict[str, np.ndarray]],
               x_window:        Optional[Tuple[float, float]] = None,
               y_window:        Optional[Tuple[float, float]] = None,
               now:             Optional[float] = None,
               # drug_order:      Optional[List[str]] = None,
               x_ticks:         int = 7,
               y_label:         Optional[str] = None):
    plt.figure(dpi=800)
    dT, drugs = data
    for name, drug_plot in drugs.items():
        plt.plot(dT, drug_plot, label=f'{name}')
    if x_window is not None:
        plt.xlim(left=x_window[0], right=x_window[1])
        plt.xticks(range(int(x_window[0]), int(x_window[1]) + 1, x_ticks))
    if y_window is not None:
        plt.ylim(bottom=y_window[0], top=y_window[1])
    plt.grid()
    if now is not None:
        plt.axvline(now)
    plt.xlabel("Time (days)")
    if y_label is None:
        plt.ylabel("Drug in body (mg)")
    else:
        plt.ylabel(y_label)
    plt.legend()
    plt.show()

