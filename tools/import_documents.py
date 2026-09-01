# -*- coding: utf-8 -*-
"""One-off: turn the Secretariat's .docx and .pdf files into web documents.

Reads from the archive folders, writes content/documents/*.json and copies the
supplied PDFs into assets/documents/. Documents without a supplied PDF get one
generated at build time from the same text.

Re-run if a source document is replaced.
"""
import html as _html
import json
import os
import re
import shutil
import zipfile

ARCHIVE = "E:/Work/09_IAHR-APD"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(HERE, "content", "documents")
PDFS = os.path.join(HERE, "assets", "documents")
os.makedirs(DOCS, exist_ok=True)
os.makedirs(PDFS, exist_ok=True)

# Anchored shapes and text boxes leave these behind in the paragraph stream.
JUNK = re.compile(r"^((left|right)(top|bottom)\d*|\d{4,}|_+|-{3,})$")
BULLET = re.compile(r"^\s*([\u2022\u25cf\u25aa\u00b7o]|[-\u2013\u2014])\s+")


def paragraphs(path):
    """(kind, text) per paragraph. kind is 'h' (bold), 'li' (list) or 'p'."""
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    xml = re.sub(r"</w:tc>", "\t", xml)
    out = []
    for para in re.findall(r"<w:p[ >].*?</w:p>|<w:p/>", xml, re.S):
        listed = "<w:numPr>" in para
        runs = re.findall(r"<w:r[ >].*?</w:r>", para, re.S)
        bold = bool(runs) and all("<w:b/>" in r or '<w:b ' in r for r in runs)
        text = re.sub(r"<w:tab[^>]*/>", "\t", para)
        text = re.sub(r"<[^>]+>", "", text)
        text = _html.unescape(text).replace("\u00a0", " ").strip()
        text = re.sub(r"[ \t]+", " ", text)
        if not text or JUNK.match(text):
            continue
        if BULLET.match(text):
            out.append(("li", BULLET.sub("", text).strip()))
        elif listed:
            out.append(("li", text))
        elif bold and len(text) < 120:
            out.append(("h", text))
        else:
            out.append(("p", text))
    return out


def blocks_from(pairs, heading_re=None):
    """Fold paragraphs into heading / text / list blocks."""
    blocks, bullets = [], []

    def flush():
        if bullets:
            blocks.append({"type": "list", "items": bullets[:]})
            bullets.clear()

    for kind, text in pairs:
        # Word tables sometimes glue a section title to its explanatory line.
        m = re.match(r"^(.{4,80}?)(Including but not limited to.*)$", text)
        if m:
            flush()
            blocks.append({"type": "heading", "text": m.group(1).strip()})
            blocks.append({"type": "text", "text": m.group(2).strip()})
            continue
        is_heading = kind == "h" or (heading_re and re.match(heading_re, text))
        if is_heading:
            flush()
            # Word tables sometimes glue a section title to its explanatory line.
            blocks.append({"type": "heading", "text": text})
        elif kind == "li":
            bullets.append(text)
        else:
            flush()
            blocks.append({"type": "text", "text": text})
    flush()
    return blocks


def put(slug, data):
    with open(os.path.join(DOCS, slug + ".json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    kinds = {}
    for b in data.get("body", []):
        kinds[b["type"]] = kinds.get(b["type"], 0) + 1
    print("  %-44s %s" % (slug + ".json", kinds))


def copy_pdf(src_rel, name):
    src = os.path.join(ARCHIVE, src_rel)
    if not os.path.exists(src):
        print("  ! missing PDF:", src_rel)
        return ""
    shutil.copy2(src, os.path.join(PDFS, name))
    return "/assets/documents/" + name


REPORT_HEADINGS = (r"^(Activities of|Journal of Hydro|\d+(st|nd|rd|th) IAHR[- ]APD Congress|"
                   r"Membership|Awards?|Financial|Executive Committee|Publications|Outreach)")

LAW = "00_Laws and Regulations"
REPORTS = "05_Annual Report"

# ---------------------------------------------------------------- By-Laws
pairs = paragraphs(os.path.join(ARCHIVE, LAW,
                                "1_By-Laws of IAHR-APD (amended in 2004)_Reveised 2025.docx"))
put("by-laws", {
    "title": "By-Laws of IAHR-APD",
    "kind": "statute",
    "status": "In force",
    "version": "Revised edition, 2025",
    "order": 1,
    "summary": pairs[1][1] if len(pairs) > 1 else "",
    "intro": "The By-Laws govern the conduct of the Division. This is the edition currently in force. "
             "Superseded editions are listed at the foot of the page.",
    "pdf": "",
    "body": blocks_from(pairs[2:], r"^\d+\.\s"),
    "superseded": [
        {"title": "By-Laws of IAHR-APD, as amended December 2004, Hong Kong",
         "note": "Replaced by the 2025 revised edition.",
         "pdf": copy_pdf(LAW + "/By-Laws of IAHR-APD (amended in 2004).pdf", "by-laws-2004.pdf")},
        {"title": "By-Laws of the Asian Pacific Regional Division, adopted April 1991",
         "note": "Adopted by the Executive Committee in Beijing on 15 November 1990 and approved by the "
                 "IAHR Council on 1 April 1991. Not held by the Secretariat in digital form.",
         "pdf": ""},
    ],
})

# ---------------------------------------------------------------- award statements
for slug, docx, pdf, title, version, order in [
    ("best-paper-award-rules",
     "2_Founding Statement and Rules of IAHR-APD Best Paper Award.docx",
     "Founding Statement and Rules of IAHR-APD Best Paper Award.pdf",
     "Founding Statement and Rules of the IAHR-APD Best Paper Award", "Founding statement", 2),
    ("distinguished-membership-award-statement",
     "3_Statement of Distinguished IAHR-APD Membership Award (Appr. Aug. 2009).docx",
     "Statement of Distinguished IAHR-APD Membership Award (Appr. Aug. 2009).pdf",
     "Statement of the Distinguished IAHR-APD Membership Award", "Approved August 2009", 3),
]:
    pairs = paragraphs(os.path.join(ARCHIVE, LAW, docx))
    put(slug, {
        "title": title, "kind": "statute", "status": "In force", "version": version, "order": order,
        "summary": "", "intro": "",
        "pdf": copy_pdf(LAW + "/" + pdf, slug + ".pdf"),
        "body": blocks_from(pairs[1:], r"^\d+\.\s"),
        "superseded": [],
    })

# ---------------------------------------------------------------- congress hosting pack
for slug, docx, pdf, title, order in [
    ("regional-congress-guidelines",
     "4_Guidelines for IAHR Regional Congresses (from IAHR Secretariat).docx",
     "Guidelines for IAHR Regional Congresses (from IAHR Secretariat).pdf",
     "Guidelines for IAHR Regional Congresses", 1),
    ("congress-hosting-proposal-format",
     "6_Proposal format for hosting IAHR-APD Congress.docx",
     "Proposal format for hosting IAHR-APD Congress.pdf",
     "Proposal format for hosting an IAHR-APD Congress", 2),
    ("congress-working-sheet",
     "5_Working Sheet for IAHR-APD Congress.docx",
     "Working Sheet for IAHR-APD Congress.pdf",
     "Working sheet for the IAHR-APD Congress", 3),
]:
    pairs = paragraphs(os.path.join(ARCHIVE, LAW, docx))
    put(slug, {
        "title": title, "kind": "hosting", "status": "", "version": "", "order": order,
        "summary": "", "intro": "",
        "pdf": copy_pdf(LAW + "/" + pdf, slug + ".pdf"),
        "body": blocks_from(pairs[1:], r"^(\d+[\.\)]\s|[A-Z][A-Z \-]{6,}$)"),
        "superseded": [],
    })

# ---------------------------------------------------------------- annual reports
for slug, docx, year, order in [
    ("annual-report-2025", "IAHR APD Annual Report 2025.docx", "2025", 1),
    ("annual-report-2024", "IAHR RDs Annual Report 2024_20250519.docx", "2024", 2),
    ("annual-report-2023", "Annual Report 2023 (APD).docx", "2023", 3),
]:
    src = os.path.join(ARCHIVE, REPORTS, docx)
    if not os.path.exists(src):
        print("  ! missing:", docx)
        continue
    pairs = [(k, t) for k, t in paragraphs(src) if not re.match(r"^0{2,}\s", t)]
    put(slug, {
        "title": "IAHR-APD Annual Report %s" % year,
        "kind": "report", "status": "", "version": year, "order": order,
        "summary": "The Division's report to the IAHR Council for %s." % year,
        "intro": "", "pdf": "",
        "body": blocks_from(pairs[1:], REPORT_HEADINGS),
        "superseded": [],
    })

print("\ndone")
