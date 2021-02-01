# from typing import List, Tuple, Optional, Dict
# import matplotlib.pyplot as plt
# import matplotlib as mpl
#
# from drug_model.body import ConfidenceArray
# import numpy as np
#
# def plot_graph(dT:              np.ndarray,
#                drugs:           Dict[str, ConfidenceArray],
#                sum:             Optional[ConfidenceArray] = None,
#                avg:             Optional[List[float]] = None,
#                x_window:        Optional[Tuple[float, float]] = None,
#                y_window:        Optional[Tuple[float, float]] = None,
#                now:             Optional[float] = None,
#                drug_order:      Optional[List[str]] = None,
#                display_text:    Optional[Tuple[float, float, List[str]]] = None,
#                x_ticks:         int = 7,
#                red_level:       float = 5.0,
#                green_band:      float = 10.0,
#                yellow_level:    float = 20.0,
#                legend_location: Optional[str] = None,
#                figtext:         Optional[str] = None,
#                show_bands:      bool = True,
#                y_label:         Optional[str] = None,
#                show_confidence: bool = True,
#                ):
#   def plot(dT:              np.ndarray,
#            drugs:           Dict[str, ConfidenceArray],
#            sum:             Optional[ConfidenceArray] = None,
#            avg:             Optional[List[float]] = None,
#            x_window:        Optional[Tuple[float, float]] = None,
#            y_window:        Optional[Tuple[float, float]] = None,
#            now:             Optional[float] = None,
#            drug_order:      Optional[List[str]] = None,
#            display_text:    Optional[Tuple[float, float, List[str]]] = None,
#            x_ticks:         int = 7,
#            red_level:       float = 5.0,
#            green_band:      float = 10.0,
#            yellow_level:    float = 20.0,
#            legend_location: Optional[str] = None,
#            figtext:         Optional[str] = None,
#            show_bands:      bool = True,
#            y_label:         Optional[str] = None,
#            show_confidence: bool = True,
#            ):
#     plt.interactive(False)
#     plt.figure(dpi=400)
#     if drug_order is not None:
#       all_drugs = set(drugs.keys())
#       ordering = drug_order
#       for d in all_drugs:
#         if d not in ordering:
#           ordering.append(d)
#     else:
#       ordering = list(drugs.keys())
#     for drug_name in ordering:
#       if drug_name in drugs:
#         drug_data = drugs[drug_name]
#         val, err = drug_data.get_np_arrays()
#         lower = val - err
#         upper = val + err
#         if show_confidence:
#           plt.fill_between(dT, lower, upper, label=f'{drug_name} Confidence', alpha=0.5)
#         plt.plot(dT, val, label=f'{drug_name}')
#
#     if sum is not None:
#       sum_val, sum_err = sum.get_np_arrays()
#       lower = sum_val - sum_err
#       upper = sum_val + sum_err
#       plt.fill_between(dT, lower, upper, label=f'Sum Confidence', alpha=0.5)
#       plt.plot(dT, sum_val, label=f'Sum')
#
#     if avg is not None:
#       avg_arr = np.array(avg)
#       plt.plot(dT, avg_arr, label=f'Running Avg')
#
#     if show_bands:
#       plt.axhspan(0, red_level, facecolor='red', alpha=0.2)
#       plt.axhspan(red_level, green_band, facecolor='green', alpha=0.2)
#       plt.axhspan(green_band, yellow_level, facecolor='yellow', alpha=0.2)
#
#     if x_window is not None:
#       plt.xlim(left=x_window[0], right=x_window[1])
#     if y_window is not None:
#       plt.ylim(bottom=y_window[0], top=y_window[1])
#     plt.grid()
#     if now is not None:
#       plt.axvline(now)
#     if figtext is not None:
#       plt.figtext(.12, .935, figtext)  # f'{datetime.datetime.now()}'
#     if display_text is not None:
#       x, y, text = display_text
#       plt.figtext(x, y, "\n".join(text),
#                   family='monospace',
#                   size='x-small',
#                   linespacing=0.9)
#     plt.xlabel('Time (days)')
#     if y_label is None:
#       plt.ylabel('Prednisolone equivalent current body dose (mg)')
#     else:
#       plt.ylabel(y_label)
#     plt.xticks(range(int(x_window[0]), int(x_window[1]) + 1, x_ticks))
#     if legend_location is None:
#       plt.legend()
#     else:
#       plt.legend(loc=legend_location)
#     plt.show()
#
#
#   plot(dT, drugs, sum, avg, x_window, y_window, now, drug_order, display_text, x_ticks, red_level,
#                   green_band, yellow_level, legend_location, figtext, show_bands, y_label, show_confidence)
# # executor.submit(plot, dT, drugs, sum, avg, x_window, y_window, now, drug_order, display_text, x_ticks, red_level,
# #                   green_band, yellow_level, legend_location, figtext, show_bands, y_label, show_confidence)
from typing import Optional, Tuple, Dict, List
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

