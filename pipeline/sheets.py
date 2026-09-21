"""Pass 1: build per-stop contact sheets for overview (NOT for identification)."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
import pillow_heif
pillow_heif.register_heif_opener()
def sheet(paths, out, thumb=900, cols=3):
    ims = []
    for p in paths:
        im = Image.open(p); im.thumbnail((thumb, thumb)); ims.append((os.path.basename(p), im))
    if not ims: return
    cols = min(cols, len(ims)); rows = (len(ims)+cols-1)//cols
    w = max(i.width for _, i in ims); h = max(i.height for _, i in ims)
    s = Image.new("RGB", (cols*w, rows*(h+50)), "white"); d = ImageDraw.Draw(s)
    # Both environments, in order: macOS first, then the Cowork Linux VM.
    # The old code named only the Linux path, so on the Mac every contact sheet
    # fell back to a ~10 px bitmap font and the filenames were unreadable --
    # which defeats the point of a sheet you navigate BY filename.
    f = None
    for path in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "/System/Library/Fonts/Helvetica.ttc",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            f = ImageFont.truetype(path, 40); break
        except Exception:
            continue
    if f is None:
        try: f = ImageFont.load_default(size=40)
        except TypeError: f = ImageFont.load_default()
    for i, (n, im) in enumerate(ims):
        x = (i % cols)*w; y = (i//cols)*(h+50)
        s.paste(im, (x, y+50)); d.text((x+10, y+5), n, fill="black", font=f)
    s.save(out, quality=88); print(out, s.size, len(ims), "photos")
if __name__ == '__main__':
    sheet(sys.argv[2:], sys.argv[1])
