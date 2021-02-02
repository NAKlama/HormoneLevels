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

from typing import Optional, Tuple, Dict, List
import matplotlib.pyplot as plt
import numpy as np
import drugs


def plot_drugs(data:            Tuple[np.ndarray, Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]],
               x_window:        Optional[Tuple[float, float]] = None,
               y_window:        Optional[Tuple[float, float]] = None,
               now:             Optional[float] = None,
               # drug_order:      Optional[List[str]] = None,
               x_ticks:         int = 7,
               y_label:         Optional[str] = None,
               lab_data:        Optional[Dict[str, Tuple[List[int], List[float]]]] = None,
               confidence_val:  int = 68):
    plt.figure(dpi=800)
    dT, drugs = data
    for name, drug_plot in drugs.items():
        value, minimum, maximum = drug_plot
        plt.plot(dT, value, label=f'{name}')
        plt.fill_between(dT, minimum, maximum, label=f'{name} {confidence_val}% confidence interval', alpha=0.5)
        if lab_data is not None and name in lab_data:
            plt.scatter(lab_data[name][0], lab_data[name][1], s=10)
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

