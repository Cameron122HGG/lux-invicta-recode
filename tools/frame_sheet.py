"""Contact sheet of government frames at one size: base-game frames plus LI's. usage: python -P frame_sheet.py <vanilla_gfx_interface> <li_dir> <size> <out.png>"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw
V, L, SZ, OUT = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
ROWS = [('Default (feudal)', V, ''), ('Tribal', V, '_tribal'), ('Republic', V, '_republic'), ('Merchant republic', V, '_merchantrepublic'),
        ('Theocracy', V, '_theocracy'), ('Theocratic feudal', V, '_theocraticfeudal'), ('Iqta', V, '_iqta'), ('Nomadic', V, '_nomadic'),
        ('Roman imperial', V, '_romanimperial'), ('Chinese imperial', V, '_chineseimperial'), ('Confucian', V, '_confucian_bureaucracy'),
        ('Holy order', V, '_order'),
        ('LI Classical', L, '_classical'), ('LI Oriental Despotic', L, '_oriental_monarchy'),
        ('LI Absolutist', L, '_absolutist'), ('LI Anarchist', L, '_anarchist'), ('LI Demagogic', L, '_demagogic'),
        ('LI Hegemonic', L, '_hegemonic'), ('LI Messianic', L, '_messianic'), ('LI Mystic', L, '_mystic')]
def img(p):
    b = open(p, 'rb').read(); fl = int.from_bytes(b[80:84], 'little'); bits = int.from_bytes(b[88:92], 'little')
    if (fl & 0x40) and bits == 32:
        h, w = int.from_bytes(b[12:16], 'little'), int.from_bytes(b[16:20], 'little')
        a = np.frombuffer(b[128:128 + w * h * 4], np.uint8).reshape(h, w, 4)
        return Image.fromarray(a[..., [2, 1, 0, 3]].copy(), 'RGBA')
    return Image.open(p).convert('RGBA')
ims = [(n, img(os.path.join(d, f'charframe_{SZ}{s}.dds'))) for n, d, s in ROWS]
w, h = ims[0][1].size; lab = 150; half = (len(ims) + 1) // 2
sheet = Image.new('RGBA', ((lab + w + 20) * 2, half * (h + 6) + 6), (70, 70, 74, 255)); d = ImageDraw.Draw(sheet)
for i, (n, im) in enumerate(ims):
    col, row = divmod(i, half); x = col * (lab + w + 20); y = 6 + row * (h + 6)
    d.text((x + 6, y + h // 2 - 6), n, fill=(240, 240, 240, 255) if n.startswith('LI') else (190, 190, 190, 255))
    sheet.alpha_composite(im, (x + lab, y))
sheet.convert('RGB').save(OUT)
