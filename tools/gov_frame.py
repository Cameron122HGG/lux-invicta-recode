"""Government portrait frames for LI, made from the plain base-game frame (charframe_<size>.dds).
Ribbon pixels = blue-violet in the plain frame AND purple in the Roman imperial frame (only the ribbons change between
governments), so rings and gems keep their colours unless a ring style is set. Writes uncompressed BGRA DDS with the
original header (no mipmaps). usage: python -P gov_frame.py <preset> <vanilla_gfx_interface> <preview.png> <target_dir>...
One preset per LI government (2026-11-15). Each frame strip holds 6 ranks: unlanded, baron, count, duke, king, emperor.
To change a colour, edit its preset and re-run for that preset, with both mod copies as targets. Needs Pillow + numpy.
example: python -P tools/gov_frame.py classical "<CK2>/gfx/interface" preview.png gfx/interface"""
import sys, os, colorsys
import numpy as np
from PIL import Image

PRESETS = {
    # suffix, ribbon hue (deg), ribbon saturation gain, ribbon value gain, marble gold rings, marble silver rings
    'classical': dict(suffix='_classical', hue=195, sat=1.45, val=1.0, marble_gold=True, marble_silver=True),
    'oriental_monarchy': dict(suffix='_oriental_monarchy', hue=21, sat=2.4, val=1.1, marble_gold=False, marble_silver=False),
    # radical governments (ribbon base: sat ~0.34, val ~0.53, so gains set the target)
    'absolutist': dict(suffix='_absolutist', hue=220, sat=0.15, val=0.34, marble_gold=False, marble_silver=False),   # iron black
    'anarchist': dict(suffix='_anarchist', hue=85, sat=2.2, val=1.2, marble_gold=False, marble_silver=False),        # acid lime
    'demagogic': dict(suffix='_demagogic', hue=322, sat=2.2, val=1.3, marble_gold=False, marble_silver=False),       # fuchsia
    'hegemonic': dict(suffix='_hegemonic', hue=222, sat=2.5, val=1.05, marble_gold=False, marble_silver=False),      # royal cobalt
    'messianic': dict(suffix='_messianic', hue=46, sat=1.0, val=1.65, marble_gold=False, marble_silver=False),       # radiant pale gold
    'mystic': dict(suffix='_mystic', hue=258, sat=2.0, val=0.65, marble_gold=False, marble_silver=False),            # deep indigo
}
MARBLE_SAT, MARBLE_GAMMA, SILVER_TINT = 0.10, 0.65, 0.06
SIZES = ('150', '100', '75', '50', '34')

P = PRESETS[sys.argv[1]]; V, PREVIEW = sys.argv[2:4]; TARGETS = sys.argv[4:]

def load(p):
    b = open(p, 'rb').read(); hdr = b[:128]
    h, w = int.from_bytes(hdr[12:16], 'little'), int.from_bytes(hdr[16:20], 'little')
    return hdr, np.frombuffer(b[128:128 + w * h * 4], dtype=np.uint8).reshape(h, w, 4).copy()   # B G R A

def hue_sat(px):
    rgb = px[..., [2, 1, 0]].astype(float) / 255.0
    mx, mn = rgb.max(axis=2), rgb.min(axis=2); d = mx - mn
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.zeros_like(mx); nz = d > 1e-6
    rm = nz & (mx == r); gm = nz & (mx == g) & ~rm; bm = nz & ~rm & ~gm
    h[rm] = ((g - b)[rm] / d[rm]) % 6; h[gm] = (b - r)[gm] / d[gm] + 2; h[bm] = (r - g)[bm] / d[bm] + 4
    return h * 60, np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)

def recolour(out, src, ys, xs, f):
    for y, x in zip(ys, xs):
        b_, g_, r_ = src[y, x, :3] / 255.0
        r2, g2, b2 = colorsys.hsv_to_rgb(*f(*colorsys.rgb_to_hsv(r_, g_, b_)))
        out[y, x, :3] = [round(b2 * 255), round(g2 * 255), round(r2 * 255)]

previews = []
for s in SIZES:
    hdr, plain = load(os.path.join(V, f'charframe_{s}.dds'))
    _, roman = load(os.path.join(V, f'charframe_{s}_romanimperial.dds'))
    diff = np.abs(plain[..., :3].astype(int) - roman[..., :3].astype(int)).max(axis=2)
    hp, sp = hue_sat(plain); hr, _ = hue_sat(roman)
    alpha = plain[..., 3] > 0
    mask = (diff > 6) & alpha & (hp >= 205) & (hp <= 275) & (sp > 0.08) & (hr >= 275) & (hr <= 335)
    out = plain.copy()
    ys, xs = np.nonzero(mask)
    shift = P['hue'] / 360 - float(np.median(hp[mask])) / 360
    recolour(out, plain, ys, xs, lambda h, sa, v: ((h + shift) % 1.0, min(1.0, sa * P['sat']), min(1.0, v * P['val'])))
    fw = plain.shape[1] // 6
    if P['marble_gold']:
        g = np.zeros_like(mask); g[:, fw * 4:] = True
        g &= ~mask & alpha & (hp >= 18) & (hp <= 62) & (sp > 0.15)
        gy, gx = np.nonzero(g)
        recolour(out, plain, gy, gx, lambda h, sa, v: (0.11, sa * MARBLE_SAT, min(1.0, v ** MARBLE_GAMMA)))
    if P['marble_silver']:
        sv = np.zeros_like(mask); sv[:, fw * 2:fw * 4] = True
        sv &= ~mask & alpha & (sp < 0.30)
        sy, sx = np.nonzero(sv)
        recolour(out, plain, sy, sx, lambda h, sa, v: (0.11, SILVER_TINT, min(1.0, v ** MARBLE_GAMMA)))
    data = hdr + out.tobytes()
    for t in TARGETS:
        open(os.path.join(t, f'charframe_{s}{P["suffix"]}.dds'), 'wb').write(data)
    previews.append(Image.fromarray(out[..., [2, 1, 0, 3]], 'RGBA'))
    print(s, 'ribbon px', int(mask.sum()))

W = max(p.size[0] for p in previews); H = sum(p.size[1] + 8 for p in previews)
bg = Image.new('RGBA', (W, H), (90, 90, 90, 255)); y = 0
for p in previews:
    bg.alpha_composite(p, (0, y)); y += p.size[1] + 8
bg.convert('RGB').save(PREVIEW)
