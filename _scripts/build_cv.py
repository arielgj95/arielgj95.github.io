#!/usr/bin/env python3
"""Build a readable, single-column, two-page CV from the website's JSON Resume.

Run from the repository root: python3 _scripts/build_cv.py
Requires reportlab and the Lato font family. Set CV_FONT_DIR if fonts are elsewhere.
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
MARGIN = 41
WIDTH = PAGE_W - 2 * MARGIN
OUTPUT = ROOT / 'assets/pdf/Ariel_Gjaci_CV.pdf'
c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
c.setTitle('Ariel Gjaci - Curriculum Vitae')
c.setAuthor(DATA['basics']['name'])
c.setSubject('Multimodal generative learning, spatial audio, and human motion generation')


def paragraph(text, y, size=10.1, leading=13.5, after=5, font='Lato', color=INK, indent=0):
    style = ParagraphStyle('cv', fontName=font, fontSize=size, leading=leading, textColor=color)
    p = Paragraph(text, style)
    _, height = p.wrap(WIDTH - indent, PAGE_H)
    if y - height < 41:
        raise ValueError(f'CV page {c.getPageNumber()} overflows near: {text[:100]}')
    p.drawOn(c, MARGIN + indent, y - height)
    return y - height - after


def section(title, y):
    return paragraph(escape(title.upper()), y - 9, size=11.2, leading=15, after=7, font='Lato-Bold', color=ACCENT)


def bullet(text, y):
    c.setFillColor(INK)
    c.circle(MARGIN + 2.4, y - 6.1, 1.25, fill=1, stroke=0)
    return paragraph(escape(text), y, indent=12, after=4)


def dates(start, end=None):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    def human(value):
        parts = value.split('-')
        return f'{months[int(parts[1]) - 1]} {parts[0]}' if len(parts) > 1 else parts[0]
    return f'{human(start)} - {human(end) if end else "Present"}'


def footer(number):
    c.setFont('Lato', 8)
    c.setFillColor(MUTED)
    c.drawString(MARGIN, 24, 'Ariel Gjaci')
    c.drawRightString(PAGE_W - MARGIN, 24, f'{number} / 2')


# The PDF text is drawn in visual reading order, with no sidebar or text columns.
y = PAGE_H - MARGIN
y = paragraph(escape(DATA['basics']['name']), y, size=27, leading=32, after=5, font='Lato-Bold')
y = paragraph('Postdoctoral Researcher | Multimodal Generative Models | Diffusion Transformers', y,
              size=10, leading=14, after=5)
y = paragraph('<link href="mailto:ariel.gjaci@iit.it">ariel.gjaci@iit.it</link> | +39 348 377 6041 | Genoa, Italy',
              y, size=9.8, leading=13, after=4)
links = [('Website', DATA['basics']['url'])] + [(x['network'], x['url']) for x in DATA['basics']['profiles']]
y = paragraph(' | '.join(f'<link href="{escape(url)}" color="#225b70">{escape(label)}</link>' for label, url in links),
              y, size=9.8, leading=13, after=9)
y = paragraph(escape(DATA['basics']['summary']), y, after=3)
y = section('Professional Experience', y)
for work in DATA['work']:
    y = paragraph(f'{escape(work["name"].upper())} | {escape(work["position"])}', y,
                  size=10.4, leading=14, after=3, font='Lato-Bold')
    y = paragraph(escape(dates(work['startDate'], work.get('endDate')) + ' | ' + work['location']), y,
                  size=9.5, leading=12.5, color=MUTED, after=4)
    if work.get('summary'):
        y = paragraph(escape(work['summary']), y, after=4)
    for item in work['highlights']:
        y = bullet(item, y)
    y -= 7

y = section('Research Focus and Technical Skills', y)
for skill in DATA['skills']:
    y = paragraph(f'{escape(skill["name"])}: {escape("; ".join(skill["keywords"]))}.', y,
                  size=9.7, leading=12.8, after=3)
print(f'Page 1 content ends at {y:.1f} pt')
footer(1)
c.showPage()
y = PAGE_H - MARGIN
y = section('Education', y)
for education in DATA['education']:
    y = paragraph(f'{escape(education["institution"].upper())} | {escape(education["studyType"])} in {escape(education["area"])}',
                  y, size=10.4, leading=14, after=3, font='Lato-Bold')
    date_text = dates(education['startDate'], education['endDate'])
    if education.get('score'):
        date_text += ' | ' + education['score']
    y = paragraph(escape(date_text), y, size=9.5, leading=12.5, color=MUTED, after=4)
    for item in education.get('courses', []):
        y = paragraph(escape(item), y, after=3)
    y -= 5

y = section('Publications', y)
for pub in DATA['publications']:
    authors = pub['summary'].replace('Ariel Gjaci', 'A. Gjaci').replace('Antonio Sgorbissa', 'A. Sgorbissa').replace('Vittorio Murino', 'V. Murino')
    authors = authors.replace('Carmine Tommaso Recchiuto', 'C. T. Recchiuto').replace('Viktor Schmuck', 'V. Schmuck').replace('Oya Celiktutan', 'O. Celiktutan').replace('Luca Oneto', 'L. Oneto')
    text = f'{escape(authors)}. <link href="{escape(pub["url"])}">{escape(pub["name"])}</link>. {escape(pub["publisher"])}. {escape(pub["releaseDate"])}.'
    y = paragraph(text, y, size=9.5, leading=12.5, after=7)

y = section('Teaching and Service', y)
for item in DATA['volunteer'][0]['highlights']:
    y = bullet(item, y)

y = section('Selected Training', y)
y = paragraph("Topics in Modern Machine Learning (MaLGa, 2023); Robotics and Intelligent Machines Summer School (Scuola Superiore Sant'Anna, 2023).", y,
              size=9.5, leading=12.5, after=3)
y = section('Languages', y)
y = paragraph('; '.join(f'{escape(x["language"])} ({"native" if x["fluency"] == "Native speaker" else x["fluency"].lower()})' for x in DATA['languages']) + '.',
              y, size=9.7, leading=13, after=0)
print(f'Page 2 content ends at {y:.1f} pt')
footer(2)
c.save()
print(f'Created {OUTPUT}')
