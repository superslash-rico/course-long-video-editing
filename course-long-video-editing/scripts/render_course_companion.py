#!/usr/bin/env python3
"""Render editable lesson JSON as a Superslash student PDF and copyable Markdown.

Uses the A4 reading system from superslash-brand. No networking, AI generation,
system-font installation, private contact data, or automatic publication.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import parse_qsl, urlsplit
from xml.sax.saxutils import escape

try:
    from PIL import Image
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import BaseDocTemplate, Flowable, Frame, KeepTogether, PageBreak, PageTemplate, Paragraph, Spacer
except ImportError as exc:
    raise SystemExit('PDF generation requires ReportLab and Pillow in the current project Python environment; no dependencies were installed.') from exc

SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SKILL_ROOT / 'assets'


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be nonempty text')
    return value.strip()


def safe_url(value):
    if value is None:
        return None
    url = text(value, 'source.url')
    if any(ord(c) < 32 for c in url):
        raise ValueError('Source URL contains control characters')
    parsed = urlsplit(url)
    if parsed.scheme not in {'https', 'http'} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Source URLs must be public HTTP(S) addresses without credentials')
    if parsed.hostname.lower() in {'localhost', '127.0.0.1', '::1'}:
        raise ValueError('A local preview address is not a student source link')
    secret_keys = {'token', 'access_token', 'id_token', 'api_key', 'apikey', 'authorization', 'password', 'signature', 'x-amz-signature', 'x-amz-credential', 'x-amz-security-token'}
    if any(k.lower().replace('-', '_') in {x.replace('-', '_') for x in secret_keys} for k, _ in parse_qsl(parsed.query)):
        raise ValueError('Source URL contains an authentication or signed-download parameter; use a public landing page')
    return url


def validate(data, draft=False):
    if not isinstance(data, dict) or data.get('schemaVersion') != 1:
        raise ValueError('Expected a schemaVersion=1 lesson object')
    if data.get('templateOnly') is not False:
        raise ValueError('Fill the course content template and set templateOnly=false before rendering')
    example = data.get('isTemplateExample') is True
    basis = data.get('basis', {})
    if not isinstance(basis, dict):
        raise ValueError('basis must be an object')
    if not example and not draft and basis.get('checkedAgainstFinalCourse') is not True:
        raise ValueError('Check against the final course, or use --draft for an explicitly marked draft')
    clean = {'title': text(data.get('title'), 'title'), 'introduction': text(data.get('introduction'), 'introduction'), 'isTemplateExample': example}
    course = data.get('course', {})
    if not isinstance(course, dict):
        raise ValueError('course must be an object')
    clean['course'] = {k: text(course[k], f'course.{k}') for k in ['series', 'lessonNumber', 'instructor', 'versionDate'] if course.get(k) is not None}
    points = data.get('keyPoints', [])
    if not isinstance(points, list):
        raise ValueError('keyPoints must be an array')
    clean['keyPoints'] = [text(x, 'keyPoints[]') for x in points]
    mapping = data.get('mindmap')
    clean['mindmap'] = None
    if mapping is not None:
        if not isinstance(mapping, dict) or not isinstance(mapping.get('branches'), list) or not mapping['branches']:
            raise ValueError('mindmap requires a title and nonempty branches, or use null')
        branches = []
        for branch in mapping['branches']:
            if not isinstance(branch, dict) or not isinstance(branch.get('items', []), list):
                raise ValueError('Each mindmap branch must have a text title and an items array')
            branches.append({'title': text(branch.get('title'), 'mindmap.branch.title'), 'items': [text(x, 'mindmap.branch.items[]') for x in branch.get('items', [])]})
        clean['mindmap'] = {'title': text(mapping.get('title'), 'mindmap.title'), 'branches': branches}
    sections = data.get('sections', [])
    sources = data.get('sources', [])
    if not isinstance(sections, list) or not isinstance(sources, list):
        raise ValueError('sections and sources must be arrays')
    clean['sections'] = []
    for section in sections:
        if not isinstance(section, dict):
            raise ValueError('Each section must be an object')
        clean['sections'].append({'heading': text(section.get('heading'), 'section.heading'), 'text': text(section.get('text'), 'section.text')})
    clean['sources'] = []
    seen = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError('Each source must be an object')
        identifier = text(source.get('id'), 'source.id')
        if identifier in seen:
            raise ValueError('Source IDs must be unique')
        seen.add(identifier)
        item = {'id': identifier, 'title': text(source.get('title'), 'source.title'), 'url': safe_url(source.get('url'))}
        item.update({k: text(source[k], f'source.{k}') for k in ['publisher', 'role', 'note', 'publishedDate', 'accessedDate'] if source.get(k) is not None})
        clean['sources'].append(item)
    return clean


def asset(relative):
    candidate = (ASSETS / relative).resolve()
    if not candidate.is_relative_to(ASSETS.resolve()) or not candidate.is_file():
        raise ValueError(f'Missing or unsafe brand asset: {relative}')
    return candidate


def markup(value):
    return escape(value).replace('\n', '<br/>')


class CoursePDF(BaseDocTemplate):
    def __init__(self, path, data, draft):
        self.brand = json.loads((ASSETS / 'brand/course-companion.json').read_text(encoding='utf-8'))
        for weight in ['regular', 'medium', 'semibold', 'bold']:
            name = 'Course-MiSans-' + weight
            if name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, str(asset(self.brand['fonts'][weight]))))
        pdfmetrics.registerFontFamily('Course-MiSans-regular', normal='Course-MiSans-regular', bold='Course-MiSans-bold', italic='Course-MiSans-regular', boldItalic='Course-MiSans-bold')
        fmt = self.brand['formats']['a4_portrait']
        self.page_width, self.page_height, self.margin = fmt['width_pt'], fmt['height_pt'], fmt['margin_pt']
        self.content_width = self.page_width - 2 * self.margin
        self.data, self.draft = data, draft
        super().__init__(str(path), pagesize=(self.page_width, self.page_height), title=data['title'], author=self.brand['company_name'], leftMargin=self.margin, rightMargin=self.margin, topMargin=110, bottomMargin=64, pageCompression=1)
        self.addPageTemplates(PageTemplate('reading', [Frame(self.margin, 64, self.content_width, self.page_height-174, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=self.paint_page))
        palette = self.brand['editorial_palette']
        self.body = ParagraphStyle('CourseBody', fontName='Course-MiSans-regular', fontSize=11.5, leading=17.5, textColor=colors.HexColor(palette['ink']), spaceAfter=12, wordWrap='CJK')
        self.heading = ParagraphStyle('CourseHeading', parent=self.body, fontName='Course-MiSans-semibold', fontSize=22, leading=31, spaceBefore=12, spaceAfter=16, keepWithNext=True)
        self.hero = ParagraphStyle('CourseHero', parent=self.heading, fontSize=30, leading=40, spaceBefore=0, spaceAfter=20)
        self.small = ParagraphStyle('CourseSmall', parent=self.body, fontSize=8.5, leading=13, textColor=colors.HexColor(palette['muted']))
        self.label = ParagraphStyle('CourseLabel', parent=self.body, fontName='Course-MiSans-medium', fontSize=9.5, leading=14, textColor=colors.HexColor(self.brand['official_palette']['blue']), spaceAfter=10)
        self.outline_count = 0

    def p(self, value, style=None):
        return Paragraph(markup(value), style or self.body)

    def h(self, value, hero=False):
        result = self.p(value, self.hero if hero else self.heading)
        result.course_outline = True
        return result

    def paint_page(self, canvas, doc):
        b = self.brand
        canvas.saveState()
        canvas.setFillColor(colors.HexColor(b['editorial_palette']['paper']))
        canvas.rect(0, 0, self.page_width, self.page_height, fill=1, stroke=0)
        logo = asset(b['logos']['dark_on_light'])
        with Image.open(logo) as im:
            logo_height = 108 * im.height / im.width
        canvas.drawImage(str(logo), self.margin, self.page_height-63, width=108, height=logo_height, mask='auto')
        canvas.setFillColor(colors.HexColor(b['editorial_palette']['muted']))
        canvas.setFont('Course-MiSans-regular', 8.2)
        canvas.drawRightString(self.page_width-self.margin, self.page_height-51, '模板示例 · 非实际课程' if self.data['isTemplateExample'] else '课程资料草稿' if self.draft else '课程学习资料')
        canvas.setStrokeColor(colors.HexColor(b['editorial_palette']['rule']))
        canvas.setLineWidth(.5)
        canvas.line(self.margin, self.page_height-80, self.page_width-self.margin, self.page_height-80)
        canvas.line(self.margin, 47, self.page_width-self.margin, 47)
        canvas.setFont('Course-MiSans-regular', 7.8)
        canvas.drawString(self.margin, 29, b['company_name'])
        canvas.drawRightString(self.page_width-self.margin, 29, f"{b['domain']}  /  {doc.page:02d}")
        canvas.linkURL(b['website'], (self.page_width-self.margin-100, 23, self.page_width-self.margin, 39), relative=0)
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if getattr(flowable, 'course_outline', False):
            self.outline_count += 1
            key = f'course-section-{self.outline_count}'
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(flowable.getPlainText(), key, level=0)


class MindmapPage(Flowable):
    """Bounded, measured tree; lines are drawn behind text and never cross labels."""
    GAP = 22

    def __init__(self, title, branches, pdf, report):
        super().__init__()
        self.width = pdf.content_width
        self.title, self.branches, self.pdf, self.report = title, branches, pdf, report
        self.text_x = 177
        self.text_width = self.width-self.text_x
        self.root_style = ParagraphStyle('MapRoot', parent=pdf.body, fontName='Course-MiSans-semibold', fontSize=14, leading=21, textColor=colors.white, alignment=1, spaceAfter=0)
        self.branch_style = ParagraphStyle('MapBranch', parent=pdf.body, fontName='Course-MiSans-semibold', fontSize=14, leading=21, spaceAfter=0, textColor=colors.HexColor(pdf.brand['official_palette']['blue']))
        self.item_style = ParagraphStyle('MapItem', parent=pdf.body, fontSize=10.5, leading=16, spaceAfter=0)
        self.root = pdf.p(title, self.root_style)
        self.root_height = self.root.wrap(112, 10000)[1]+26
        self.rows = [self.measure(branch) for branch in branches]
        self.height = max(self.root_height+12, sum(row['height'] for row in self.rows)+self.GAP*(len(self.rows)-1))
        if self.height > 500.1:
            raise ValueError('Mindmap page exceeds readable capacity; split branches or shorten labels')

    def measure(self, branch):
        title = self.pdf.p(branch['title'], self.branch_style)
        title_height = title.wrap(self.text_width, 10000)[1]
        items = [self.pdf.p('• ' + x, self.item_style) for x in branch['items']]
        heights = [p.wrap(self.text_width, 10000)[1] for p in items]
        return {'title': title, 'titleHeight': title_height, 'items': items, 'heights': heights, 'height': title_height + (8+sum(heights)+4*(len(items)-1) if items else 0)}

    def wrap(self, available_width, available_height):
        return self.width, self.height

    def draw(self):
        c, b = self.canv, self.pdf.brand
        c.saveState()
        centers, y = [], self.height
        for row in self.rows:
            centers.append(y-row['height']/2)
            y -= row['height']+self.GAP
        trunk = 151
        c.setStrokeColor(colors.HexColor('#C8BEE9'))
        c.setLineWidth(1)
        c.line(136, self.height/2, trunk, self.height/2)
        c.line(trunk, min(centers+[self.height/2]), trunk, max(centers+[self.height/2]))
        for center in centers:
            c.line(trunk, center, self.text_x-9, center)
        c.setFillColor(colors.HexColor(b['official_palette']['blue']))
        root_y = (self.height-self.root_height)/2
        c.roundRect(0, root_y, 136, self.root_height, 10, fill=1, stroke=0)
        self.root.drawOn(c, 12, root_y+13)
        boxes = [{'kind': 'root', 'x':0, 'y':root_y, 'w':136, 'h':self.root_height}]
        y = self.height
        for row in self.rows:
            row['title'].drawOn(c, self.text_x, y-row['titleHeight'])
            boxes.append({'kind':'branch-title','x':self.text_x,'y':y-row['titleHeight'],'w':self.text_width,'h':row['titleHeight']})
            cursor = y-row['titleHeight']-8
            for item, h in zip(row['items'], row['heights']):
                item.drawOn(c, self.text_x, cursor-h)
                boxes.append({'kind':'branch-item','x':self.text_x,'y':cursor-h,'w':self.text_width,'h':h})
                cursor -= h+4
            y -= row['height']+self.GAP
        self.report.append({'page':c.getPageNumber(),'width':self.width,'height':self.height,'boxes':boxes})
        c.restoreState()


def mindmap_pages(mapping, pdf, report):
    """Split complete item lists across readable pages; never drop the tail."""
    units = []
    for branch in mapping['branches']:
        current = {'title': branch['title'], 'items': []}
        for item in branch['items']:
            candidate = {'title':current['title'],'items':current['items']+[item]}
            try:
                MindmapPage(mapping['title'], [candidate], pdf, [])
            except ValueError:
                if not current['items']:
                    raise ValueError('One mindmap label is too long; use a short label and move its explanation to sections')
                units.append(current)
                current = {'title':branch['title']+'（续）','items':[item]}
                MindmapPage(mapping['title'], [current], pdf, [])
            else:
                current = candidate
        units.append(current)
    pages, group = [], []
    for branch in units:
        try:
            MindmapPage(mapping['title'], group+[branch], pdf, [])
        except ValueError:
            if not group:
                raise
            pages.append(MindmapPage(mapping['title'], group, pdf, report))
            group = [branch]
        else:
            group.append(branch)
    if group:
        pages.append(MindmapPage(mapping['title'], group, pdf, report))
    return pages


def render(data, output, draft, report):
    pdf = CoursePDF(output, data, draft)
    story = [pdf.p('课程资料 / STUDY NOTES', pdf.label), pdf.h(data['title'], hero=True), pdf.p(data['introduction'])]
    metadata = '  ·  '.join(data['course'].values())
    if metadata:
        story += [pdf.p(metadata, pdf.small)]
    if data['keyPoints']:
        story += [pdf.h('本课要点')]
        story += [pdf.p(f'{i:02d}  {point}') for i, point in enumerate(data['keyPoints'], 1)]
    for section in data['sections']:
        story += [pdf.h(section['heading']), pdf.p(section['text'])]
    if data['mindmap']:
        for i, page in enumerate(mindmap_pages(data['mindmap'], pdf, report), 1):
            story += [PageBreak(), pdf.h('本课思维导图' + (f' · {i}' if i>1 else '')), page]
    if data['sources']:
        story += [PageBreak(), pdf.h('材料与信息来源')]
        for source in data['sources']:
            entry = []
            title = f"[{source['id']}] {source['title']}"
            if source['url']:
                href = escape(source['url'], {'"':'&quot;'})
                entry += [Paragraph(f'<link href="{href}" color="{pdf.brand["official_palette"]["blue"]}">{markup(title)}</link>', pdf.body)]
            else:
                entry += [pdf.p(title)]
            details = '  ·  '.join(source[k] for k in ['publisher','role','publishedDate'] if source.get(k))
            if source.get('accessedDate'):
                details += ('  ·  ' if details else '') + '访问：'+source['accessedDate']
            if details:
                entry += [pdf.p(details, pdf.small)]
            if source.get('note'):
                entry += [pdf.p(source['note'])]
            if source['url']:
                entry += [pdf.p(source['url'], pdf.small)]
            story += [KeepTogether(entry), Spacer(1, 10)]
    pdf.build(story)


def markdown(data, draft):
    lines = [f"# {data['title']}", '', '模板示例，非实际课程。' if data['isTemplateExample'] else '课程资料草稿。' if draft else '', '', '## 课程简介', '', data['introduction'], '']
    if data['keyPoints']:
        lines += ['## 本课要点', ''] + ['- '+x for x in data['keyPoints']] + ['']
    for section in data['sections']:
        lines += ['## '+section['heading'], '', section['text'], '']
    if data['mindmap']:
        lines += ['## 思维导图', '', data['mindmap']['title'], '']
        for branch in data['mindmap']['branches']:
            lines += ['- '+branch['title']] + ['  - '+x for x in branch['items']]
        lines += ['']
    if data['sources']:
        lines += ['## 材料与信息来源', '']
        for source in data['sources']:
            lines += [f"- [{source['id']}] {source['title']}" + ('：'+source['url'] if source['url'] else '')]
            for key in ['publisher','role','note','publishedDate','accessedDate']:
                if source.get(key): lines += ['  '+source[key]]
    return '\n'.join(lines).strip()+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--content', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--draft', action='store_true', help='Mark all pages as a draft and allow not-yet-final course basis')
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--layout-report', type=Path, help='Optional project-side mindmap layout evidence; not a visual approval')
    args = parser.parse_args()
    data = validate(json.loads(args.content.read_text(encoding='utf-8')), args.draft)
    output = args.output.resolve()
    if output.suffix.lower() != '.pdf':
        raise ValueError('--output must be a PDF path')
    md = output.with_name(output.stem+'-文案.md')
    destinations = [output, md] + ([args.layout_report.resolve()] if args.layout_report else [])
    if len(set(destinations)) != len(destinations) or args.content.resolve() in destinations:
        raise ValueError('Input JSON, PDF, copyable text and layout report must use distinct paths')
    for path in destinations:
        if path.exists() and not args.overwrite:
            raise FileExistsError(f'Refusing overwrite: {path}')
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.course-companion-', suffix='.pdf', dir=output.parent)
    os.close(fd)
    temporary = Path(name)
    layout = []
    try:
        render(data, temporary, args.draft, layout)
        if not args.overwrite and (output.exists() or md.exists()):
            raise FileExistsError('Output appeared during render; refusing overwrite')
        os.replace(temporary, output)
        md.write_text(markdown(data, args.draft), encoding='utf-8')
    finally:
        if temporary.exists(): temporary.unlink()
    if args.layout_report:
        args.layout_report.parent.mkdir(parents=True, exist_ok=True)
        args.layout_report.write_text(json.dumps({'scope':'measured mindmap boxes only; visual and source checks still required','pages':layout},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pdf':str(output),'copyableText':str(md),'templateExample':data['isTemplateExample'],'draft':args.draft,'networkUsed':False,'contentAndLinkTruthVerifiedByRenderer':False},ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
