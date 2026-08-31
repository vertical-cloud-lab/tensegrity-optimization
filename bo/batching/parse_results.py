"""Collect slicer time/material estimates from the batch-size sweep into a CSV."""
import csv, json, re, sys, glob, os

def gcode_stats(path):
    st = {}
    with open(path, errors='ignore') as f:
        head = f.read(20000)
    m = re.search(r'; model printing time: ([^;]+); total estimated time: (.+)', head)
    def to_s(txt):
        d = re.findall(r'(\d+)([hms])', txt)
        mult = {'h': 3600, 'm': 60, 's': 1}
        return sum(int(v) * mult[u] for v, u in d)
    st['model_time_s'] = to_s(m.group(1))
    st['total_time_s'] = to_s(m.group(2))
    w = re.search(r'; total filament weight \[g\] : ([\d.]+),([\d.]+)', head)
    st['pla_total_g'] = float(w.group(1)); st['tpu_total_g'] = float(w.group(2))
    return st

def result_stats(path):
    r = json.load(open(path))
    p = r['sliced_plates'][0]
    ft = p['feature_type_times']
    fil = {f['id']: f for f in p['filaments']}
    return {
        'prime_tower_s': round(ft.get('Prime tower', 0)),
        'flush_s': round(ft.get('Flush', 0)),
        'travel_s': round(ft.get('Travel', 0)),
        'undefined_s': round(ft.get('Undefined', 0)),
        'support_s': round(ft.get('Support', 0) + ft.get('Support interface', 0)),
        'pla_main_g': round(fil[1]['main_used_g'], 2),
        'tpu_main_g': round(fil[2]['main_used_g'], 2),
    }

rows = []
for n in range(1, 10):
    g = sorted(glob.glob(f'out_{n}/plate_*.gcode'))
    assert len(g) == 1, f'N={n}: expected 1 plate, got {g}'
    row = {'n_articles': n}
    row.update(gcode_stats(g[0]))
    row.update(result_stats(f'out_{n}/result.json'))
    rows.append(row)

t1 = rows[0]['total_time_s']
for row in rows:
    n = row['n_articles']
    row['sequential_total_s'] = n * t1
    row['per_article_s'] = round(row['total_time_s'] / n)
    row['savings_pct'] = round(100 * (1 - row['total_time_s'] / (n * t1)), 1)

# real heterogeneous batch, split over two plates (5 + 4 articles)
for tag in ('plateA', 'plateB'):
    g = sorted(glob.glob(f'out_{tag}/plate_*.gcode'))
    if g:
        assert len(g) == 1, f'{tag}: expected 1 plate, got {g}'
        row = {'n_articles': f'real-batch-{tag}'}
        row.update(gcode_stats(g[0]))
        row.update(result_stats(f'out_{tag}/result.json'))
        rows.append(row)

# as-printed baseline: every plate of the original batch file, sliced as is
import os
if glob.glob('out_asprinted/plate_*.gcode'):
    for g in sorted(glob.glob('out_asprinted/plate_*.gcode'),
                    key=lambda p: int(re.search(r'plate_(\d+)', p).group(1))):
        k = int(re.search(r'plate_(\d+)', g).group(1))
        row = {'n_articles': f'asprinted-plate-{k}'}
        row.update(gcode_stats(g))
        rows.append(row)

fields = ['n_articles','model_time_s','total_time_s','per_article_s','sequential_total_s','savings_pct',
          'prime_tower_s','flush_s','travel_s','undefined_s','support_s',
          'pla_total_g','tpu_total_g','pla_main_g','tpu_main_g']
with open('batch-walltime-results.csv', 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=fields)
    wr.writeheader()
    for row in rows:
        wr.writerow({k: row.get(k, '') for k in fields})
print(open('batch-walltime-results.csv').read())
