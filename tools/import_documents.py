# -*- coding: utf-8 -*-
"""One-off: turn the Secretariat's .docx and .pdf files into web documents.

Reads from the archive folders, writes content/documents/*.json and copies the
PDFs into assets/documents/. Re-run if a source document is replaced.
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


def paragraphs(path):
    """(kind, text) for each paragraph: 'li' for list items, 'p' otherwise."""
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    xml = xml.replace("</w:tr>", "\n")
    xml = re.sub(r"</w:tc>", "\t", xml)
    out = []
    for para in re.findall(r"<w:p[ >].*?</w:p>|<w:p/>", xml, re.S):
        listed = "<w:numPr>" in para
        text = re.sub(r"<w:tab[^>]*/>", "\t", para)
        text = re.sub(r"<[^>]+>", "", text)
        text = _html.unescape(text).replace("\u00a0", " ").strip()
        text = re.sub(r"[ \t]+", " ", text)
        if text:
            out.append(("li", text) if listed else ("p", text))
    return out


def blocks_from(pairs, heading_re):
    """Fold paragraphs into heading / paragraph / list blocks."""
    blocks, bullets = [], []

    def flush():
        if bullets:
            blocks.append({"type": "list", "items": bullets[:]})
            bullets.clear()

    for kind, text in pairs:
        if heading_re and re.match(heading_re, text):
            flush()
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
    print("  content/documents/%s.json  (%d blocks)" % (slug, len(data.get("body", []))))


def copy_pdf(src_rel, name):
    src = os.path.join(ARCHIVE, src_rel)
    if not os.path.exists(src):
        print("  ! missing PDF:", src_rel)
        return ""
    shutil.copy2(src, os.path.join(PDFS, name))
    print("  assets/documents/%s  (%d KB)" % (name, os.path.getsize(src) // 1024))
    return "/assets/documents/" + name


LAW = "00_Laws and Regulations"

# ---------------------------------------------------------------- By-Laws
pairs = paragraphs(os.path.join(ARCHIVE, LAW,
                                "1_By-Laws of IAHR-APD (amended in 2004)_Reveised 2025.docx"))
body = blocks_from(pairs[2:], r"^\d+\.\s")
put("by-laws", {
    "title": "By-Laws of IAHR-APD",
    "kind": "statute",
    "status": "In force",
    "version": "Revised edition, 2025",
    "summary": pairs[1][1] if len(pairs) > 1 else "",
    "intro": "The By-Laws govern the conduct of the Division. This is the edition currently in force. "
             "Superseded editions are listed at the foot of the page.",
    "pdf": "",
    "body": body,
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
for slug, docx, pdf, title in [
    ("best-paper-award-rules",
     "2_Founding Statement and Rules of IAHR-APD Best Paper Award.docx",
     "Founding Statement and Rules of IAHR-APD Best Paper Award.pdf",
     "Founding Statement and Rules of the IAHR-APD Best Paper Award"),
    ("distinguished-membership-award-statement",
     "3_Statement of Distinguished IAHR-APD Membership Award (Appr. Aug. 2009).docx",
     "Statement of Distinguished IAHR-APD Membership Award (Appr. Aug. 2009).pdf",
     "Statement of the Distinguished IAHR-APD Membership Award"),
]:
    pairs = paragraphs(os.path.join(ARCHIVE, LAW, docx))
    put(slug, {
        "title": title,
        "kind": "statute",
        "status": "In force",
        "version": "Approved August 2009" if "distinguished" in slug else "Founding statement",
        "summary": "",
        "intro": "",
        "pdf": copy_pdf(LAW + "/" + pdf, slug + ".pdf"),
        "body": blocks_from(pairs[1:], r"^\d+\.\s"),
        "superseded": [],
    })

# ---------------------------------------------------------------- congress guidance
for slug, pdf, title in [
    ("regional-congress-guidelines",
     "Guidelines for IAHR Regional Congresses (from IAHR Secretariat).pdf",
     "Guidelines for IAHR Regional Congresses"),
    ("congress-working-sheet",
     "Working Sheet for IAHR-APD Congress.pdf",
     "Working sheet for the IAHR-APD Congress"),
    ("congress-hosting-proposal-format",
     "Proposal format for hosting IAHR-APD Congress.pdf",
     "Proposal format for hosting an IAHR-APD Congress"),
]:
    print(" ", title)
    copy_pdf(LAW + "/" + pdf, slug + ".pdf")

# ---------------------------------------------------------------- annual reports
REPORTS = "05_Annual Report"
for slug, docx, year in [
    ("annual-report-2025", "IAHR APD Annual Report 2025.docx", "2025"),
    ("annual-report-2024", "IAHR RDs Annual Report 2024_20250519.docx", "2024"),
    ("annual-report-2023", "Annual Report 2023 (APD).docx", "2023"),
]:
    src = os.path.join(ARCHIVE, REPORTS, docx)
    if not os.path.exists(src):
        print("  ! missing:", docx)
        continue
    pairs = paragraphs(src)
    pairs = [(k, t) for k, t in pairs if not re.match(r"^0{2,}\s", t)]
    put(slug, {
        "title": "IAHR-APD Annual Report %s" % year,
        "kind": "report",
        "status": "",
        "version": year,
        "summary": "The Division's report to the IAHR Council for %s." % year,
        "intro": "",
        "pdf": "",
        "body": blocks_from(pairs[1:], r"^(Activities of the Year|Plans|Membership|Publications|"
                                       r"Awards|Financial|Executive Committee|Congress|Other)"),
        "superseded": [],
    })

print("\ndone")
