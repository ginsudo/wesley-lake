"""Reconstruct a walk from an EXIF CSV: cluster photos into stops, compute distances."""
import csv, math, sys
def hav(a, b):
    R = 6371000; p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp = p2 - p1; dl = math.radians(b[1] - a[1])
    x = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(x))
def secs(dt): return int(dt[11:13])*3600 + int(dt[14:16])*60 + int(dt[17:19])
def stops(rows, dist_m=35, gap_s=75):
    rows = sorted(rows, key=lambda r: r['dt'])
    out, cur = [], [rows[0]]
    for prev, r in zip(rows, rows[1:]):
        d = hav((float(prev['lat']), float(prev['lon'])), (float(r['lat']), float(r['lon'])))
        if d > dist_m or secs(r['dt']) - secs(prev['dt']) > gap_s:
            out.append(cur); cur = []
        cur.append(r)
    out.append(cur); return out
if __name__ == '__main__':
    rows = [r for r in csv.DictReader(open(sys.argv[1])) if r['lat'] and r['dt']]
    bydate = {}
    for r in rows: bydate.setdefault(r['dt'][:10].replace(':','-'), []).append(r)
    for d in sorted(bydate):
        ss = stops(bydate[d]); cum = 0
        print(f"\n== {d} == {len(bydate[d])} photos, {len(ss)} stops")
        for i, s in enumerate(ss, 1):
            if i > 1: cum += hav((float(ss[i-2][-1]['lat']), float(ss[i-2][-1]['lon'])),
                                 (float(s[0]['lat']), float(s[0]['lon'])))
            fl = s[0]['file'] + (f"..{s[-1]['file']}" if len(s) > 1 else "")
            print(f"  {i:>2} {fl:<34} {s[0]['dt'][11:]}  {float(s[0]['lat']):.5f} {float(s[0]['lon']):.5f}  {cum:>5.0f}m  n={len(s)}")
