"""Reproducible fictional slate for integration demonstrations, never forecasts."""
import pandas as pd

DEMO_NOW = pd.Timestamp('2030-09-08 16:00:00', tz='UTC')

def synthetic_salary_csv():
    rows = []
    specs = {'QB': (5, 6200, 20), 'RB': (9, 5100, 15),
             'WR': (12, 4500, 13), 'TE': (6, 3400, 9), 'DST': (4, 2500, 6)}
    teams = ['ALP', 'BET', 'GAM', 'DEL']
    for pos, (count, salary, points) in specs.items():
        for i in range(count):
            rows.append({'Position': pos, 'Name': f'Synthetic {pos} {i+1:02}',
                         'ID': f'SYN-{pos}-{i+1:02}', 'Salary': salary + i * 150,
                         'TeamAbbrev': teams[i % 4],
                         'Game Info': 'ALP@BET 09/08/2030 01:00 PM ET' if i % 4 < 2 else 'GAM@DEL 09/08/2030 04:25 PM ET',
                         'AvgPointsPerGame': round(points + i * .7, 2)})
    return pd.DataFrame(rows).to_csv(index=False).encode('utf-8')
