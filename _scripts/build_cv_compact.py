#!/usr/bin/env python3
"""Build the one-page, two-column CV from the same JSON as the full CV.

Run from the repository root: python3 _scripts/build_cv_compact.py
Requires reportlab and Lato fonts. Set CV_FONT_DIR if fonts are elsewhere.
The full two-page CV remains the primary download.
"""
import json
import os
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'assets/json/resume.json').read_text(encoding='utf-8'))
FONT_DIR = Path(os.environ.get('CV_FONT_DIR', '/usr/share/fonts/truetype/lato'))
for name, filename in [('Lato', 'Lato-Regular.ttf'), ('Lato-Bold', 'Lato-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily('Lato', normal='Lato', bold='Lato-Bold', italic='Lato', boldItalic='Lato-Bold')

INK = colors.HexColor('#263238')
MUTED = colors.HexColor('#53616b')
ACCENT = colors.HexColor('#225b70')
PAGE_W, PAGE_H = A4
MARGIN = 34
WIDTH = PAGE_W - 2 * MARGIN
LEFT_WIDTH = 156
GAP = 22
RIGHT_X = MARGIN + LEFT_WIDTH + GAP
RIGHT_WIDTH = PAGE_W - MARGIN - RIGHT_X
OUTPUT = ROOT / 'assets/pdf/Ariel_Gjaci_CV_One_Page.pdf'
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
c.setTitle('Ariel Gjaci - One-page CV')
c.setAuthor(DATA['basics']['name'])
c.setSubject('Multimodal generative learning, spatial audio, and human motion generation')


def paragraph(text, y, x=MARGIN, width=WIDTH, size=9.3, leading=12, after=4,
              font='Lato', color=INK):
    style = ParagraphStyle('compact', fontName=font, fontSize=size, leading=leading, textColor=color)
    p = Paragraph(text, style)
    _, height = p.wrap(width, PAGE_H)
    if y - height < 37:
        raise ValueError(f'One-page CV overflows near: {text[:100]}')
    p.drawOn(c, x, y - height)
    return y - height - after


def section(text, y, x, width):
    return paragraph(escape(text.upper()), y - 7, x, width, size=10.4, leading=14,
                     after=6, font='Lato-Bold', color=ACCENT)


def bullet(text, y):
    c.setFillColor(INK)
    c.circle(RIGHT_X + 2, y - 5.4, 1.1, fill=1, stroke=0)
    return paragraph(escape(text), y, RIGHT_X + 10, RIGHT_WIDTH - 10, after=4)


def dates(start, end=None):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    def human(value):
        parts = value.split('-')
        return f'{months[int(parts[1]) - 1]} {parts[0]}' if len(parts) > 1 else parts[0]
    return f'{human(start)} - {human(end) if end else "Present"}'


# Shared header; all contacts remain selectable text and clickable links.
y = PAGE_H - MARGIN
y = paragraph(escape(DATA['basics']['name']), y, size=26, leading=31, after=4, font='Lato-Bold')
y = paragraph('Postdoctoral Researcher | Multimodal Generative Learning | Spatial Audio | Human Motion',
              y, size=9.6, leading=13, after=4)
y = paragraph(f'<link href="mailto:{escape(DATA["basics"]["email"])}">{escape(DATA["basics"]["email"])}</link>'
              f' | {escape(DATA["basics"]["phone"])} | Genoa, Italy', y, size=9.3, leading=12, after=3)
links = [('Website', DATA['basics']['url'])] + [(x['network'], x['url']) for x in DATA['basics']['profiles']]
y = paragraph(' | '.join(f'<link href="{escape(url)}" color="#225b70">{escape(label)}</link>' for label, url in links),
              y, leading=12, after=7)
y = paragraph(escape(DATA['basics']['summary']), y, leading=12.2, after=8)
top = y
c.setStrokeColor(colors.HexColor('#dce4e7'))
c.setLineWidth(0.5)
c.line(MARGIN, top + 1, PAGE_W - MARGIN, top + 1)

# Draw the main experience column in one sequence for coherent text extraction.
y = section('Professional Experience', top, RIGHT_X, RIGHT_WIDTH)
for index, work in enumerate(DATA['work']):
    y = paragraph(escape(work['position']), y, RIGHT_X, RIGHT_WIDTH,
                  size=10.1, leading=13, after=2, font='Lato-Bold')
    y = paragraph(escape(work['name']), y, RIGHT_X, RIGHT_WIDTH,
                  size=9.4, leading=12, after=2)
    y = paragraph(escape(dates(work['startDate'], work.get('endDate'))), y, RIGHT_X, RIGHT_WIDTH,
                  size=8.8, leading=11, after=4, color=MUTED)
    # Keep the work descriptions factual; the longer version retains all bullets.
    highlights = work['highlights']
    if index == 0:
        highlights = highlights[:2] + [highlights[2]]
    elif index == 1:
        highlights = highlights[:3]
    for item in highlights:
        y = bullet(item, y)
    y -= 5

y = section('Selected Publications', y, RIGHT_X, RIGHT_WIDTH)
for pub in [DATA['publications'][0], DATA['publications'][2], DATA['publications'][3]]:
    publisher = pub['publisher'].split(',')[0]
    text = f'<link href="{escape(pub["url"])}">{escape(pub["name"])}</link>. {escape(publisher)}, {escape(pub["releaseDate"])}.'
    y = paragraph(text, y, RIGHT_X, RIGHT_WIDTH, size=9.1, leading=11.7, after=5)
y = paragraph('<link href="https://arielgjaci.com/publications/" color="#225b70">Full publication list</link>',
              y, RIGHT_X, RIGHT_WIDTH, size=9, leading=11, after=2)
y = section('Teaching and Service', y, RIGHT_X, RIGHT_WIDTH)
y = paragraph('Teaching assistant (C++, Android/Kotlin); ECCV workshop co-organizer; reviewer for AAAI, ECCV, ACM Multimedia, IROS, ICMI, and IJSR; IEEE RO-MAN 2024 session chair.',
              y, RIGHT_X, RIGHT_WIDTH, size=9, leading=11.7, after=0)
right_bottom = y

# The sidebar contains supporting facts, with no skill bars or rating graphics.
y = section('Technical Skills', top, MARGIN, LEFT_WIDTH)
skill_lookup = {skill['name']: skill['keywords'] for skill in DATA['skills']}
for title, keys in [
    ('Programming', ['Programming']),
    ('Machine Learning', ['ML Frameworks']),
    ('Training and Tools', ['Model Training', 'Tools']),
    ('Systems', ['Systems']),
]:
    y = paragraph(escape(title), y, MARGIN, LEFT_WIDTH, size=9.4, leading=12,
                  after=2, font='Lato-Bold')
    items = [item for key in keys for item in skill_lookup[key]]
    y = paragraph(escape('; '.join(items)), y, MARGIN, LEFT_WIDTH,
                  size=9.1, leading=11.7, after=7)

y = section('Education', y, MARGIN, LEFT_WIDTH)
for education in DATA['education']:
    y = paragraph(escape(f'{education["studyType"]} {education["area"]}'), y, MARGIN, LEFT_WIDTH,
                  size=9.4, leading=12, after=3, font='Lato-Bold')
    y = paragraph(escape(education['institution']), y, MARGIN, LEFT_WIDTH,
                  size=9.1, leading=11.7, after=2)
    y = paragraph(escape(dates(education['startDate'], education['endDate'])), y, MARGIN, LEFT_WIDTH,
                  size=8.8, leading=11, after=5, color=MUTED)
    if education['studyType'] == 'Ph.D.':
        y = paragraph("Research collaboration with King's College London.", y, MARGIN, LEFT_WIDTH,
                      size=9.1, leading=11.7, after=7)
    y -= 3

y = section('Research Focus', y, MARGIN, LEFT_WIDTH)
y = paragraph(escape('; '.join(skill_lookup['Research Focus'])) + '.', y, MARGIN, LEFT_WIDTH,
              size=9.1, leading=11.7, after=4)
y = section('Languages', y, MARGIN, LEFT_WIDTH)
for language in DATA['languages']:
    fluency = 'native' if language['fluency'] == 'Native speaker' else language['fluency'].lower()
    y = paragraph(escape(f'{language["language"]} ({fluency})'), y, MARGIN, LEFT_WIDTH,
                  size=9.1, leading=11.7, after=2)

c.setFont('Lato', 7.5)
c.setFillColor(MUTED)
c.drawString(MARGIN, 21, 'Ariel Gjaci')
c.drawRightString(PAGE_W - MARGIN, 21, '1 / 1')
c.save()
print(f'One-page CV columns end at {y:.1f} / {right_bottom:.1f} pt')
print(f'Created {OUTPUT}')
