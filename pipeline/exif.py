import os, sys, csv, math
from PIL import Image
import pillow_heif
pillow_heif.register_heif_opener()
def dms(v, ref):
    try:
        d = float(v[0]) + float(v[1])/60 + float(v[2])/3600
    except Exception: return None
    return -d if str(ref).upper() in ('S','W') else d
def parse(path):
    r = {'file': os.path.basename(path), 'dt':'', 'tz':'', 'model':'', 'lat':None,
         'lon':None, 'alt':None, 'dir':None, 'w':'', 'h':'',
         # Optics. `eq35` is the only honest measure of how far this frame is
         # zoomed: `focal` is the PHYSICAL lens and never changes within a lens,
         # so a 26 mm and a 272 mm frame both report 5.96 mm. See framing.py.
         'focal':None, 'eq35':None, 'zoom':None, 'lens':''}
    try: im = Image.open(path)
    except Exception as e: r['err']=str(e); return r
    r['w'], r['h'] = im.size
    ex = im.getexif()
    if not ex: return r
    r['model'] = ex.get(0x0110,'') or ''
    try: sub = ex.get_ifd(0x8769)
    except Exception: sub = {}
    r['dt'] = sub.get(0x9003,'') or ''
    r['tz'] = sub.get(0x9011,'') or ''
    try: r['focal'] = float(sub.get(0x920A)) if sub.get(0x920A) is not None else None
    except Exception: pass
    try: r['eq35'] = int(sub.get(0xA405)) if sub.get(0xA405) is not None else None
    except Exception: pass
    try: r['zoom'] = round(float(sub.get(0xA404)), 3) if sub.get(0xA404) is not None else None
    except Exception: pass
    r['lens'] = sub.get(0xA434,'') or ''
    try: g = ex.get_ifd(0x8825)
    except Exception: g = {}
    if g:
        r['lat'] = dms(g.get(2), g.get(1,'N'))
        r['lon'] = dms(g.get(4), g.get(3,'E'))
        try: r['alt'] = float(g.get(6)) if g.get(6) is not None else None
        except Exception: pass
        try: r['dir'] = float(g.get(17)) if g.get(17) is not None else None
        except Exception: pass
    return r
if __name__ == '__main__':
    rows = [parse(p) for p in sorted(sys.argv[2:])]
    with open(sys.argv[1],'w',newline='') as f:
        w = csv.DictWriter(f, fieldnames=['file','dt','tz','model','lat','lon','alt','dir','w','h',
                                          'focal','eq35','zoom','lens','err'],
                           extrasaction='ignore')
        w.writeheader(); w.writerows(rows)
    print("wrote", sys.argv[1], len(rows), "rows")
