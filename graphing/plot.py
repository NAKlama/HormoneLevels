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
import sys
from typing import Optional, Tuple, Dict, List, Union

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


plot_data = Union[Tuple[np.ndarray, np.ndarray, np.ndarray],
                  Tuple[np.ndarray, np.ndarray, np.ndarray, str]]


def plot_drugs(data:            Tuple[np.ndarray, Dict[str, plot_data]],
               x_window:        Optional[Tuple[float, float]] = None,
               y_window:        Optional[Tuple[float, float]] = None,
               now:             Optional[float] = None,
               # drug_order:      Optional[List[str]] = None,
               x_ticks:         int = 7,
               x_label:         Optional[str] = None,
               y_label:         Optional[str] = None,
               title:           Optional[str] = None,
               lab_data:        Optional[Dict[str, Tuple[List[int], List[float]]]] = None,
               confidence_val:  Optional[float] = None,
               avg_levels:      Optional[Dict[str, Tuple[float, float, str]]] = None,
               moving_average:  Optional[Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]] = None,
               plot_markers:    bool = False,
               no_avg_label:    bool = True,
               plot_dates:      bool = False,
               avg_length:      Optional[Tuple[int, int, int]] = None):
  avg_colors = ["#A00000", "#006000", "#000000"]
  avg_style  = [":", "-.", "--"]
  if avg_length is None:
    avg_length = (5, 30, 90)
  plt.figure(dpi=800, tight_layout=True)
  plt.rc('xtick', labelsize=6)
  plt.rc('ytick', labelsize=6)
  plt.rc('legend', fontsize=6)
  plt.rc('axes', labelsize=6, titlesize=10)
  plt.rc('figure', titlesize=10)
  plt.margins(x=0)
  if title is not None:
    plt.title(title)
  d_t, drugs = data
  if avg_levels is not None:
    for name, avg_level in avg_levels.items():
      avg, std_dev, color = avg_level
      avg_line = np.array([avg for _ in range(len(d_t))])
      label = f'{name} average value'
      if no_avg_label:
        label = "_nolegend_"
      if plot_dates:
        plt.plot_date(d_t, avg_line,
                      label=label,
                      color=color,
                      linestyle="-",
                      markersize=0,
                      zorder=1)
      else:
        plt.plot(d_t, avg_line, label=label, color=color, zorder=1)
      plt.axhspan(avg - std_dev, avg + std_dev, facecolor=color, alpha=0.3, zorder=2)
      plt.axhspan(avg - 2*std_dev, avg + 2*std_dev, facecolor=color, alpha=0.2, zorder=2)
  for name, drug_plot in drugs.items():
    color = None
    if len(drug_plot) == 4:
      value, minimum, maximum, color = drug_plot
    else:
      value, minimum, maximum = drug_plot
    # print(type(value))
    # print(type(minimum))
    # print(type(maximum))
    sys.stdout.flush()
    if sum(value - minimum) == 0:
      plot_cofidence = False
    else:
      plot_cofidence = True
    if color is not None:
      if plot_markers:
        if plot_dates:
          if moving_average is not None and name in moving_average:
            for i in range(3):
              plt.plot_date(d_t, moving_average[name][i],
                            marker=".",
                            linestyle=avg_style[i],
                            label=f'{name} {avg_length[i]}d average',
                            color=avg_colors[i],
                            zorder=5)
          plt.plot_date(d_t, value,
                        marker=".",
                        linestyle="-",
                        label=f'{name}',
                        color=color,
                        zorder=4)
        else:
          if moving_average is not None and name in moving_average:
            for i in range(3):
              plt.plot(d_t, moving_average[name][i],
                       marker=".",
                       linestyle=avg_style[i],
                       label=f'{name} {avg_length[i]}d average',
                       color=avg_colors[i],
                       zorder=5)
          plt.plot(d_t, value,
                   marker=".",
                   linestyle="-",
                   label=f'{name}',
                   color=color,
                   zorder=4)
      else:
        if plot_dates:
          if moving_average is not None and name in moving_average:
            for i in range(3):
              plt.plot_date(d_t, moving_average[name][i],
                            linestyle=avg_style[i],
                            label=f'{name} {avg_length[i]}d average',
                            markersize=0,
                            color=avg_colors[i],
                            zorder=5)
          plt.plot_date(d_t, value,
                        label=f'{name}',
                        linestyle="-",
                        markersize=0,
                        linewidth=1,
                        color=color,
                        zorder=4)
        else:
          if moving_average is not None and name in moving_average:
            for i in range(3):
              plt.plot(d_t, moving_average[name][i],
                       linestyle=avg_style[i],
                       label=f'{name} {avg_length[i]}d average',
                       color=avg_colors[i],
                       zorder=5)
          plt.plot(d_t, value,
                   label=f'{name}',
                   color=color,
                   linewidth=1,
                   zorder=4)
    else:
      if plot_markers:
        if plot_dates:
          if moving_average is not None and name in moving_average:
            for i in range(3):
              plt.plot_date(d_t, moving_average[name][i],
                            marker=".",
                            label=f'{name} {avg_length[i]}d average',
                            linestyle=avg_style[i],
                            zorder=5,
                            linewidth=2)
          plt.plot_date(d_t, value,
                        marker=".",
                        linestyle="-",
                        linewidth=2,
                        label=f'{name}',
                        zorder=4)
        else:
          if moving_average is not None and name in moving_average:
            for i in range(3):
              plt.plot(d_t, moving_average[name][i],
                       linestyle=avg_style[i],
                       marker=".",
                       label=f'{name} {avg_length[i]}d average',
                       zorder=5)
          plt.plot(d_t, value,
                   marker=".",
                   linestyle="-",
                   label=f'{name}',
                   zorder=4)
      else:
        if plot_dates:
          if moving_average is not None and name in moving_average:
            for i in range(3):
              plt.plot_date(d_t, moving_average[name][i],
                            label=f'{name} {avg_length[i]}d average',
                            linestyle="--",
                            zorder=5,
                            linewidth=2)
          plt.plot_date(d_t, value, label=f'{name}', zorder=4, linewidth=2)
        else:
          if moving_average is not None and name in moving_average:
            for i in range(3):
              plt.plot(d_t, moving_average[name][i],
                       label=f'{name} {avg_length[i]}d average',
                       linestyle="--",
                       zorder=5)
          plt.plot(d_t, value, label=f'{name}', zorder=4)
    if confidence_val is not None and plot_cofidence:
      if color is not None:
        plt.fill_between(d_t, minimum, maximum, label=f'{name} {confidence_val}% confidence interval',
                         alpha=0.5, color=color, zorder=3)
      else:
        plt.fill_between(d_t, minimum, maximum, label=f'{name} {confidence_val}% confidence interval',
                         alpha=0.5, zorder=3)
    if lab_data is not None and name in lab_data:
      if color is not None:
        plt.scatter(lab_data[name][0], lab_data[name][1], label=f'{name} lab values',
                    marker='.', color="red", zorder=6)
      else:
        plt.scatter(lab_data[name][0], lab_data[name][1], label=f'{name} lab values',
                    marker='.', zorder=6)
  if x_window is not None:
    plt.xlim(left=x_window[0], right=x_window[1])
    if plot_dates:
      # x_axis = axis.get_xaxis()
      axis = plt.gca()
      axis.xaxis.axis_date()
      axis.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
      axis.xaxis.set_major_locator(mdates.AutoDateLocator())
      plt.gcf().autofmt_xdate()
    else:
      plt.xticks(range(int(x_window[0]), int(x_window[1]) + 1, x_ticks))

  if y_window is not None:
    plt.ylim(bottom=y_window[0], top=y_window[1])
  plt.grid()
  plt.axhline(y=0.0, color='k', zorder=0)
  if now is not None:
    plt.axvline(now, color="red", linewidth=1, zorder=0)
  if x_label is None:
    plt.xlabel("Time (days)")
  else:
    plt.xlabel(x_label)
  if y_label is None:
    plt.ylabel("Drug in body (mg)")
  else:
    plt.ylabel(y_label)
  plt.legend(loc="lower center")
  plt.show()
