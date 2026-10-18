#!/usr/bin/env python3
"""Build the one-page downloadable CV. Requires Python 3 and reportlab.

Run from the repository root: python3 _scripts/build_cv.py
The website's JSON Resume supplies identity, public links, and publication metadata;
compact experience copy below is tailored to the one-page format.
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'assets/json/resume.json').read_text())
FONT_DIR = Path('/usr/share/fonts/truetype/lato')
for name, file in [('Lato', 'Lato-Regular.ttf'), ('Lato-Light', 'Lato-Light.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))
pdfmetrics.registerFontFamily('Lato', normal='Lato', italic='Lato')
INK = colors.HexColor('#30383e')
MUTED = colors.HexColor('#66737d')
BLUE = colors.HexColor('#155e80')
OUTPUT = ROOT / 'assets/pdf/Ariel_Gjaci_CV.pdf'
c = canvas.Canvas(str(OUTPUT), pagesize=(612, 792))
c.setTitle('Ariel Gjaci - Curriculum Vitae - October 2026')
c.setAuthor('Ariel Gjaci')
c.setSubject('Multimodal generative learning, spatial audio, and human motion generation')


def paragraph(text, x, y, width, size=9, leading=11.5, font='Lato', color=INK, after=4):
    style = ParagraphStyle('cv', fontName=font, fontSize=size, leading=leading, textColor=color)
    p = Paragraph(text, style)
    _, height = p.wrap(width, 792)
    if y - height < 29:
        raise ValueError(f'CV exceeds one page near: {text[:75]}')
    p.drawOn(c, x, y - height)
    return y - height - after


def section(label, x, y, width):
    y -= 7
    y = paragraph(label.upper(), x, y, width, size=11.4, leading=14, font='Lato-Light', color=BLUE, after=6)
    return y


def bullet(text, x, y, width):
    c.setFillColor(BLUE)
    c.circle(x + 2.2, y - 5.3, 1.25, fill=1, stroke=0)
    return paragraph(text, x + 10, y, width - 10, size=8.8, leading=11, after=3)


def role(title, dates, bullets, y):
    y = paragraph(title, 222, y, 356, size=9.5, leading=12, font='Lato', after=2)
    y = paragraph(dates, 222, y, 356, size=8.5, leading=10, color=MUTED, after=5)
    for text in bullets:
        y = bullet(text, 222, y, 356)
    return y - 6


c.setFillColor(INK)
c.setFont('Lato-Light', 29)
c.drawCentredString(306, 752, DATA['basics']['name'])
c.setFont('Lato', 9.3)
c.setFillColor(MUTED)
c.drawCentredString(306, 733, 'Postdoctoral Researcher | Multimodal Generative Learning | Spatial Audio | Human Motion')
contact = '<link href="mailto:ariel.gjaci@iit.it" color="#155e80">ariel.gjaci@iit.it</link>  |  +39 348 377 6041  |  Genoa, Italy'
style = ParagraphStyle('contact', fontName='Lato', fontSize=9, leading=12, alignment=1, textColor=INK)
p = Paragraph(contact, style); _, h = p.wrap(544, 30); p.drawOn(c, 34, 712)
links = [('Website', DATA['basics']['url'])] + [(x['network'], x['url']) for x in DATA['basics']['profiles']]
text = ' &nbsp; | &nbsp; '.join(f'<link href="{escape(url)}" color="#155e80">{escape(label)}</link>' for label, url in links)
p = Paragraph(text, style); _, h = p.wrap(544, 30); p.drawOn(c, 34, 697)
c.setStrokeColor(colors.HexColor('#d6dfe4')); c.setLineWidth(.6); c.line(34, 686, 578, 686)

x, width, y = 34, 168, 675
y = section('Education', x, y, width)
for title, institution, dates, details in [
 ('Ph.D. Artificial Intelligence<br/>&amp; Robotics', 'University of Genoa', 'Nov 2021 - May 2025 (defended)', 'Research collaboration with<br/>King\'s College London'),
 ('M.Sc. Robotics Engineering', 'University of Genoa', '2018 - 2021 | 103/110', 'Thesis: Culture-Aware Co-Speech Gestures using GANs'),
 ('B.Sc. Biomedical Engineering', 'University of Genoa', '2014 - 2018 | 92/110', 'Thesis: Activity in Hippocampal Neuronal Networks')]:
    y = paragraph(title, x, y, width, font='Lato', size=9.4, leading=12, after=2)
    y = paragraph(institution, x, y, width, size=8.8, leading=11, after=2)
    y = paragraph(dates, x, y, width, size=8.2, leading=10.5, color=MUTED, after=3)
    y = paragraph(details, x, y, width, size=8.5, leading=11, after=12)
y = section('Core Skills', x, y, width)
for title, text in [
 ('Programming', 'Python; C/C++; R; MATLAB/Simulink; LaTeX'),
 ('ML Frameworks', 'PyTorch; Scikit-learn; TensorFlow'),
 ('Methods', 'Diffusion transformers; flow matching; neural audio codecs; domain generalization'),
 ('Research Systems', 'Linux; SLURM; multi-GPU training; Git; ROS&nbsp;1')]:
    y = paragraph(title.upper(), x, y, width, font='Lato', size=8.5, leading=11, after=2)
    y = paragraph(text, x, y, width, size=8.6, leading=11, after=9)
y = section('Languages', x, y, width)
y = paragraph('Italian (native)<br/>English (fluent)<br/>Albanian (native)', x, y, width, size=8.8, leading=12, after=9)
y = section('Training', x, y, width)
y = paragraph('Modern Topics in Machine Learning (MaLGa); Robotics Summer School (Scuola Superiore Sant\'Anna); Coursera DL/NLP courses.', x, y, width, size=8.5, leading=11, after=9)

right_y = section('Professional Experience', 222, 675, 356)
right_y = role('ITALIAN INSTITUTE OF TECHNOLOGY | Postdoctoral Researcher', 'Feb 2025 - Present | Genoa, Italy', [
 escape(DATA['work'][0]['highlights'][0]),
 'Built 3D sound-source localization on room point clouds using MVDR, DAS, and MaxRE beamforming.',
 'Curating multimodal spatial-audio data and writing a survey on learning-based spatial audio rendering.'
], right_y)
right_y = role('UNIVERSITY OF GENOA &amp; KCL | PhD Researcher', 'Nov 2021 - May 2025', [
 'Developed rule-based and GAN-based culture-aware co-speech gestures for social robots (AIRO; International Journal of Social Robotics).',
 'Analyzed cultural cues in multimodal interactions with classical and deep learning models (AIRO; AHRI @ ACII).',
 'Developed semantic-similarity algorithms for symbolic and deictic gesture labeling (IEEE RO-MAN 2024).',
 'Built TED4C-L: 106.45 hours from 764 speakers across four cultures; learned speaker-independent culture embeddings with Fishr and adversarial learning.',
 'Designed ALaDiT, a diffusion-transformer for culture-aware motion generation, as part of SICAGE (ECCV 2026, main conference).'
], right_y)
right_y = role('AKKA TECHNOLOGIES | Software Engineer', 'May 2021 - Oct 2021 | Italy', [
 'Developed Python backend software for aircraft panels and presented a working demo to stakeholders.'
], right_y)
right_y = section('Teaching & Service', 222, right_y, 356)
for text in [
 'Teaching assistant: Foundations of Informatics (C++), 60h; Mobile Programming (Android/Kotlin), 30h, University of Genoa.',
 'Co-organizer, ECCV workshop <i>Expressive Encounters</i>; session chair, IEEE RO-MAN 2024.',
 'Reviewer: AAAI, ECCV, ACM Multimedia, IROS, ICMI, and International Journal of Social Robotics.'
]: right_y = bullet(text, 222, right_y, 356)
right_y = section('Publications', 222, right_y - 3, 356)
# Abbreviated author names and venues keep the full publication list on one page.
short_authors = [
 'Gjaci A., Sgorbissa A., Murino V.',
 'Gjaci A., Schmuck V., Sgorbissa A., Celiktutan O.',
 'Gjaci A., Recchiuto C.T., Sgorbissa A.',
 'Gjaci A., Recchiuto C.T., Sgorbissa A.',
 'Gjaci A., Oneto L., Recchiuto C.T., Sgorbissa A.',
 'Gjaci A., Recchiuto C.T., Sgorbissa A.'
]
venues = ['ECCV 2026, main conference, pp. 392-411.', 'AHRI @ ACII Workshop, 2024.', 'IEEE RO-MAN, 2024.', 'Int. Journal of Social Robotics, 2022.', 'AIRO Workshop, 2022.', 'AIRO Workshop, 2021.']
for pub, authors, venue in zip(DATA['publications'], short_authors, venues):
    text = f'{authors} <link href="{escape(pub["url"])}" color="#30383e">{escape(pub["name"])}</link>. {venue}'
    right_y = paragraph(text, 222, right_y, 356, size=8.1, leading=10.1, after=4)

c.setFont('Lato', 7)
c.setFillColor(MUTED)
c.drawRightString(578, 17, 'Updated 18 October 2026')
c.save()
print(f'Created {OUTPUT}; left bottom={y:.1f}pt, right bottom={right_y:.1f}pt')
