from io import BytesIO

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


INK = colors.HexColor("#111827")
MUTED = colors.HexColor("#64748b")
ROSE = colors.HexColor("#be123c")
LINE = colors.HexColor("#cbd5e1")


def _register_font():
    font_candidates = [
        "/app/fonts/NotoSansCJKtc-Regular.otf",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in font_candidates:
        try:
            pdfmetrics.registerFont(TTFont("OpenPediCareCJK", path, subfontIndex=0))
            return "OpenPediCareCJK"
        except Exception:
            continue
    try:
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        return "STSong-Light"
    except Exception:
        return "Helvetica"


def _wrap_text(text, font_name, font_size, max_width):
    lines = []
    raw_lines = str(text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line:
            lines.append("")
            continue
        current = ""
        for char in line:
            candidate = f"{current}{char}"
            if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = char.strip()
        if current:
            lines.append(current)
    return lines


def build_school_note_pdf(visit):
    output = visit.output
    font_name = _register_font()
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"OpenPediCare Visit Summary - {visit.patient.name}")

    page_width, page_height = A4
    left = 18 * mm
    right = page_width - 18 * mm
    top = page_height - 18 * mm
    bottom = 18 * mm
    content_width = right - left
    y = top

    def new_page():
        nonlocal y
        pdf.showPage()
        y = top
        pdf.setFont(font_name, 9)
        pdf.setFillColor(MUTED)
        pdf.drawString(left, page_height - 11 * mm, "OpenPediCare")
        pdf.setStrokeColor(LINE)
        pdf.line(left, page_height - 14 * mm, right, page_height - 14 * mm)
        y = page_height - 23 * mm

    def ensure_space(height):
        if y - height < bottom:
            new_page()

    def draw_wrapped(text, font_size=11, leading=16, color=INK):
        nonlocal y
        pdf.setFont(font_name, font_size)
        pdf.setFillColor(color)
        for line in _wrap_text(text, font_name, font_size, content_width):
            if not line:
                y -= leading * 0.55
                continue
            ensure_space(leading)
            pdf.drawString(left, y, line)
            y -= leading

    def draw_section(title, text):
        nonlocal y
        if not str(text or "").strip():
            return
        ensure_space(36)
        y -= 5
        pdf.setFont(font_name, 13)
        pdf.setFillColor(ROSE)
        pdf.drawString(left, y, title)
        y -= 15
        draw_wrapped(text)
        y -= 8

    signed = visit.signed_by or getattr(getattr(visit.doctor, "profile", None), "signature_text", "") or visit.doctor.get_full_name() or visit.doctor.username
    signed_at = timezone.localtime(visit.signed_at).strftime("%Y-%m-%d %H:%M") if visit.signed_at else "醫師審核後生效"
    generated_at = timezone.localtime(output.generated_at).strftime("%Y-%m-%d %H:%M")
    warning_signs = "\n".join(f"- {item}" for item in (output.warning_signs or []))

    pdf.setFont(font_name, 18)
    pdf.setFillColor(ROSE)
    pdf.drawString(left, y, "OpenPediCare 看診摘要與衛教文件")
    y -= 24

    pdf.setStrokeColor(LINE)
    pdf.line(left, y, right, y)
    y -= 17

    meta = [
        f"患者：{visit.patient.name}",
        f"年齡：{visit.patient.age_years} 歲",
        f"性別：{visit.patient.get_gender_display()}",
        f"診次：{visit.id}",
        f"狀態：{visit.get_status_display()}",
        f"產生時間：{generated_at}",
    ]
    pdf.setFont(font_name, 10)
    pdf.setFillColor(MUTED)
    for index, item in enumerate(meta):
        x = left + (index % 2) * (content_width / 2)
        if index and index % 2 == 0:
            y -= 15
        pdf.drawString(x, y, item)
    y -= 24

    draw_section("看診摘要", output.visit_summary or output.parent_summary)
    draw_section("家長衛教內容", output.parent_education or output.school_note)
    draw_section("患者衛教內容", output.patient_education or output.child_explanation)
    draw_section("警示徵兆", warning_signs)
    draw_section("追蹤計畫", output.follow_up_plan)

    ensure_space(70)
    pdf.setStrokeColor(LINE)
    pdf.line(left, y, right, y)
    y -= 18
    draw_wrapped(f"醫師電子簽名：{signed}", font_size=10, leading=14)
    draw_wrapped(f"簽署時間：{signed_at}", font_size=10, leading=14)
    y -= 8
    draw_wrapped(
        "本文件為診後照護與溝通輔助，不取代醫師臨床判斷。若患者出現急性惡化，請依醫囑或緊急流程就醫。",
        font_size=9,
        leading=13,
        color=MUTED,
    )

    pdf.save()
    buffer.seek(0)
    return buffer
