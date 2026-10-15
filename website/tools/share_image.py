"""Prepare the original Lemqo share card. Production builds use the saved PNG."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
BASE = Path(__file__).resolve().parents[1]
FONTS = Path('C:/Windows/Fonts')
image = Image.new('RGB', (1200 * SCALE, 630 * SCALE), '#f7f7f0')
draw = ImageDraw.Draw(image)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), int(size * SCALE))


def text(position, value, name, size, color, anchor=None):
    draw.text(tuple(int(v * SCALE) for v in position), value,
              font=font(name, size), fill=color, anchor=anchor)


def line(points, color='#d9dbcf', width=1):
    draw.line([(int(x * SCALE), int(y * SCALE)) for x, y in points],
              fill=color, width=max(1, int(width * SCALE)))


def box(bounds, fill, outline=None, radius=5):
    draw.rounded_rectangle(tuple(int(v * SCALE) for v in bounds),
                           radius=radius * SCALE, fill=fill,
                           outline=outline, width=SCALE)


line([(60, 116), (1140, 116)])
line([(60, 560), (1140, 560)])
line([(77, 40), (94, 50), (94, 71), (77, 81), (60, 71), (60, 50), (77, 40)], '#252d29', 1.5)
line([(77, 40), (77, 60), (60, 71)], '#252d29', 1.5)
line([(60, 50), (77, 60), (94, 50)], '#252d29', 1.5)
line([(77, 60), (94, 71)], '#252d29', 1.5)
line([(77, 60), (77, 81)], '#252d29', 1.5)
text((110, 37), 'Lemqo.', 'georgia.ttf', 43, '#252d29')
text((891, 59), 'AN OPEN AI FOR MATH PROJECT', 'consola.ttf', 11, '#6c7166')
text((62, 169), 'Start from zero.', 'georgia.ttf', 64, '#252d29')
text((62, 255), 'Prove every step.', 'georgiai.ttf', 64, '#a6553d')
text((65, 389), 'Autonomous exploration.', 'segoeui.ttf', 19, '#6c7166')
text((65, 422), 'Independent verification. Open to everyone.', 'segoeui.ttf', 19, '#6c7166')
text((65, 581), 'LEM Q.E.D. / OPEN SOURCE. OPEN POSSIBILITIES.', 'consola.ttf', 11, '#a6553d')
text((1051, 581), 'lemqo.com', 'consola.ttf', 13, '#6c7166')

for x in range(765, 1128, 20):
    for y in range(155, 518, 20):
        draw.ellipse((x*SCALE, y*SCALE, x*SCALE+2, y*SCALE+2), fill='#c9c9bf')
line([(940, 226), (940, 252), (840, 277)], '#a6553d', 1.5)
line([(940, 226), (940, 252), (1040, 277)], '#a6553d', 1.5)
line([(840, 326), (840, 349), (940, 379)], '#a6553d', 1.5)
line([(1040, 326), (1040, 349), (940, 379)], '#a6553d', 1.5)
line([(940, 425), (940, 452)], '#a6553d', 1.5)
box((874, 176, 1006, 226), '#f7f7f0', '#aeb4a3')
text((940, 201), 'P ∧ Q', 'georgia.ttf', 24, '#252d29', 'mm')
box((806, 277, 874, 326), '#f7f7f0', '#aeb4a3')
text((840, 301), 'P', 'georgia.ttf', 25, '#252d29', 'mm')
box((1006, 277, 1074, 326), '#f7f7f0', '#aeb4a3')
text((1040, 301), 'Q', 'georgia.ttf', 25, '#252d29', 'mm')
box((874, 379, 1006, 425), '#f7f7f0', '#aeb4a3')
text((940, 402), 'Q ∧ P', 'georgia.ttf', 24, '#252d29', 'mm')
box((780, 452, 1100, 512), '#e8ebdf', '#899a82')
text((940, 483), '(P ∧ Q) → (Q ∧ P)', 'georgia.ttf', 23, '#33432e', 'mm')
image.resize((1200, 630), Image.Resampling.LANCZOS).save(BASE / 'src' / 'social-card.png', optimize=True)
print('Share card prepared: 1200 x 630')
