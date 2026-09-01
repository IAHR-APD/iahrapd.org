# -*- coding: utf-8 -*-
"""A very small PDF writer, standard library only.

Enough to turn a document's blocks into a readable, downloadable PDF: a title,
headings, paragraphs and bullet lists, wrapped and paginated, in the base-14
Helvetica faces that every reader has built in. No external packages, so the
build has nothing to install and nothing that can go stale.
"""
import zlib

# Base-14 Helvetica widths (1/1000 em) for the printable ASCII range.
_W = (
    "222 259 355 556 556 889 667 191 333 333 389 584 278 333 278 278 "
    "556 556 556 556 556 556 556 556 556 556 278 278 584 584 584 556 "
    "1015 667 667 722 722 667 611 778 722 278 500 667 556 833 722 778 "
    "667 778 722 667 611 722 667 944 667 667 611 278 278 278 469 556 "
    "333 556 556 500 556 556 278 556 556 222 222 500 222 833 556 556 "
    "556 556 333 500 278 556 500 722 500 500 500 334 260 334 584"
).split()
WIDTHS = {chr(32 + i): int(w) for i, w in enumerate(_W)}

PAGE_W, PAGE_H = 595.28, 841.89          # A4 points
MARGIN_X, MARGIN_TOP, MARGIN_BOT = 62, 74, 62
BODY_W = PAGE_W - 2 * MARGIN_X


def _width(text, size):
    return sum(WIDTHS.get(c, 556) for c in text) * size / 1000.0


def _wrap(text, size, width):
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = (line + " " + w).strip()
        if _width(trial, size) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines or [""]


def _esc(text):
    out = []
    for ch in text:
        if ch in "()\\":
            out.append("\\" + ch)
        elif 32 <= ord(ch) < 127:
            out.append(ch)
        else:
            # WinAnsi has no room for the rest; fall back to sensible ASCII
            out.append({"’": "'", "‘": "'", "“": '"', "”": '"',
                        "–": "-", "—": "-", "·": "-", " ": " ",
                        "…": "...", "­": "-"}.get(ch, "?"))
    return "".join(out)


class _Page:
    def __init__(self):
        self.ops = []


def build_pdf(title, subtitle, blocks, footer=""):
    """blocks: [{"type": "heading"|"text"|"list", "text"/"items": ...}] -> bytes"""
    pages, page = [], _Page()
    y = PAGE_H - MARGIN_TOP

    def new_page():
        nonlocal page, y
        pages.append(page)
        page = _Page()
        y = PAGE_H - MARGIN_TOP

    def emit(text, size, font, indent=0, gap_before=0, leading=None):
        nonlocal y
        leading = leading or size * 1.38
        y -= gap_before
        for line in _wrap(text, size, BODY_W - indent):
            if y - leading < MARGIN_BOT:
                new_page()
            y -= leading
            page.ops.append("BT /%s %.1f Tf 1 0 0 1 %.1f %.1f Tm (%s) Tj ET"
                            % (font, size, MARGIN_X + indent, y, _esc(line)))

    emit(title, 19, "F2", leading=24)
    if subtitle:
        emit(subtitle, 9.5, "F1", gap_before=6, leading=13)
    y -= 10
    page.ops.append("0.82 0.86 0.89 RG 0.8 w %.1f %.1f m %.1f %.1f l S"
                    % (MARGIN_X, y, PAGE_W - MARGIN_X, y))
    y -= 8

    for b in blocks:
        if b["type"] == "heading":
            emit(b["text"], 12.5, "F2", gap_before=16, leading=17)
        elif b["type"] == "list":
            for item in b["items"]:
                start_y = y
                emit(item, 10, "F1", indent=18, gap_before=5, leading=14)
                page.ops.append("BT /F1 10 Tf 1 0 0 1 %.1f %.1f Tm (-) Tj ET"
                                % (MARGIN_X + 6, start_y - 5 - 14 + 3.5))
        else:
            emit(b["text"], 10, "F1", gap_before=9, leading=14.5)

    pages.append(page)

    if footer:
        for i, p in enumerate(pages, 1):
            p.ops.append("BT /F1 8 Tf 0.45 0.5 0.55 rg 1 0 0 1 %.1f %.1f Tm (%s) Tj ET"
                         % (MARGIN_X, 40, _esc("%s   |   page %d of %d" % (footer, i, len(pages)))))

    objs, out = [], bytearray(b"%PDF-1.4\n")
    n_pages = len(pages)
    page_ids = [4 + i * 2 for i in range(n_pages)]

    objs.append("<< /Type /Catalog /Pages 2 0 R >>")
    objs.append("<< /Type /Pages /Kids [%s] /Count %d >>"
                % (" ".join("%d 0 R" % i for i in page_ids), n_pages))
    objs.append("<< /Font << /F1 %d 0 R /F2 %d 0 R >> >>" % (4 + n_pages * 2, 5 + n_pages * 2))

    for i, p in enumerate(pages):
        stream = zlib.compress(("\n".join(p.ops)).encode("latin-1"))
        objs.append("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] "
                    "/Resources 3 0 R /Contents %d 0 R >>" % (PAGE_W, PAGE_H, page_ids[i] + 1))
        objs.append(("<< /Length %d /Filter /FlateDecode >>" % len(stream), stream))

    objs.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    objs.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")

    offsets = []
    for i, obj in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i
        if isinstance(obj, tuple):
            out += obj[0].encode("latin-1") + b"\nstream\n" + obj[1] + b"\nendstream"
        else:
            out += obj.encode("latin-1")
        out += b"\nendobj\n"

    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    return bytes(out)
