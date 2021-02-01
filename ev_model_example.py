from drugs import *
from modelling import *
from graphing.plot import plot_drugs

from datetime import date, datetime, timedelta, time

ev = EstradiolValerate()
model = BodyModel(date(2020, 12, 12))

model.add_dose(ev, 2.5, datetime(2020, 12, 12, 9))
model.add_dose(ev, 2.5, datetime(2020, 12, 13, 9))
model.add_dose(ev, 2.5, datetime(2020, 12, 15, 9))
model.add_dose(ev, 2.5, datetime(2020, 12, 18, 11))
model.add_dose(ev, 2.5, datetime(2020, 12, 21, 9))
model.add_dose(ev, 2.5, datetime(2020, 12, 23, 9))
model.add_dose(ev, 2.5, datetime(2020, 12, 26, 15))

days_into_future = 30
model.calculate_timeline(date.today() + timedelta(days=days_into_future))
now = float((datetime.today() - datetime.combine(model.starting_date, time())).total_seconds()) / (3600 * 24)

fortnight_ago = model.duration - (14+days_into_future)*24
month_ago = model.duration - (30+days_into_future)*24

y_window = (0, 8)

plot_drugs(data=model.get_plot_data(),
           x_window=(0, model.duration/24.0),
           y_window=y_window,
           now=now)
plot_drugs(data=model.get_plot_data(),
           x_window=(fortnight_ago/24.0, (model.duration/24.0)-16),
           y_window=y_window,
           now=now)
plot_drugs(data=model.get_plot_data(),
           x_window=(month_ago/24.0, (model.duration/24.0)-16),
           y_window=y_window,
           now=now)


# # 12.12. 9:00
# d, t = add_dose(d, 2.5, t, int(24), output)  # 13.12. 9:00
# d, t = add_dose(d, 2.5, t, int(2 * 24 + 2), output)  # 15.12. 9:00
# d, t = add_dose(d, 2.5, t, int(3 * 24 - 2), output)  # 18.12. 11:00
# d, t = add_dose(d, 2.5, t, int(3 * 24), output)  # 21.12. 9:00
# d, t = add_dose(d, 2.5, t, int(2 * 24 + 6), output)  # 23.12. 9:00
#
# d, t = add_dose(d, 2.5, t, int(3 * 24 - 4), output)  # 26.12. 15:00
# d, t = add_dose(d, 2.5, t, int(3 * 24 + 1), output)  # 29.12. 11:00
# d, t = add_dose(d, 2.5, t, int(3 * 24), output)  # 01.01. 12:00
# d, t = add_dose(d, 2.5, t, int(3 * 24 - 3), output)  # 04.01. 9:00
# d, t = add_dose(d, 2.5, t, int(3 * 24 + 3), output)  # 07.01. 12:00
# d, t = add_dose(d, 2.5, t, int(2 * 24 - 3), output)  # 09.01. 9:00
# d, t = add_dose(d, 2.5, t, int(3 * 24), output)  # 12.01. 9:00
# d, t = add_dose(d, 2.5, t, int(3 * 24), output)  # 15.01. 9:00
# d, t = add_dose(d, 3.0, t, int(3 * 24), output)  # 18.01. 9:00
# d, t = add_dose(d, 2.4, t, int(3 * 24), output)  # 20.01. 9:00