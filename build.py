# -*- coding: utf-8 -*-
"""Build the IAHR-APD website.

    python build.py

Reads the JSON files under content/, writes plain static HTML into dist/.
Standard library only — no packages to install, nothing to keep up to date.
"""
import html
import json
import os
import re
import shutil

from pdfwriter import build_pdf

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, "content")
STATIC = os.path.join(HERE, "static")
ASSETS = os.path.join(HERE, "assets")
DIST = os.path.join(HERE, "dist")

# Where the site lives. Both are derived from `custom_domain` in content/site.json:
#   empty  -> the GitHub Pages project URL, served under /<repo>/
#   filled -> the real domain, served at the root, and a CNAME file is written
def _site_config():
    with open(os.path.join(CONTENT, "site.json"), encoding="utf-8") as f:
        domain = json.load(f).get("custom_domain", "").strip()
    if domain:
        return "https://" + domain, "", domain
    base = os.environ.get("BASE_PATH", "").rstrip("/")
    return os.environ.get("SITE_URL", "http://localhost:8788") + base, base, ""


SITE_URL, BASE, CUSTOM_DOMAIN = _site_config()

NAV = [
    ("/", "Home"),
    ("/about/", "About"),
    ("/governance/", "Governance"),
    ("/congresses/", "Congresses"),
    ("/awards/", "Awards"),
    ("/publications/", "Publications"),
    ("/news/", "News &amp; Events"),
    ("/gallery/", "Gallery"),
    ("/membership/", "Membership"),
    ("/contact/", "Contact"),
]


# ---------------------------------------------------------------- helpers
def load(name):
    with open(os.path.join(CONTENT, name), encoding="utf-8") as f:
        return json.load(f)


def ensure_pdf(doc):
    """Documents supplied as PDF keep theirs; the rest get one generated from
    the same text, so every document on the site can be downloaded."""
    if doc.get("pdf"):
        return doc["pdf"]
    rel = "/assets/documents/%s.pdf" % doc["slug"]
    out = os.path.join(DIST, rel.lstrip("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subtitle = doc.get("version") or doc.get("summary", "")
    with open(out, "wb") as f:
        f.write(build_pdf(doc["title"], subtitle, doc["body"],
                          "IAHR-APD  |  iahrapd.org"))
    return rel


def load_documents():
    """Every long-form document that gets its own page."""
    d = os.path.join(CONTENT, "documents")
    if not os.path.isdir(d):
        return []
    out = []
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".json"):
            with open(os.path.join(d, fn), encoding="utf-8") as f:
                doc = json.load(f)
            doc["slug"] = fn[:-5]
            doc["url"] = "/documents/%s/" % doc["slug"]
            out.append(doc)
    return out


def load_news():
    d = os.path.join(CONTENT, "news")
    items = []
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".json"):
            with open(os.path.join(d, fn), encoding="utf-8") as f:
                item = json.load(f)
            item["slug"] = fn[:-5]
            items.append(item)
    items.sort(key=lambda i: i.get("date", ""), reverse=True)
    return items


def e(text):
    """Escape a content value for use inside HTML text."""
    return html.escape(str(text or ""), quote=True)


def inline(text):
    """A deliberately small Markdown subset: **bold**, *italic*, [text](url)."""
    out = e(text)
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", out)
    return out


def rich(text):
    """Blocks: blank-line separated paragraphs, '- ' lists, '## ' headings."""
    blocks, out = re.split(r"\n\s*\n", (text or "").strip()), []
    for block in blocks:
        if not block.strip():
            continue
        lines = block.strip().split("\n")
        if all(l.strip().startswith("- ") for l in lines):
            items = "".join("<li>%s</li>" % inline(l.strip()[2:]) for l in lines)
            out.append("<ul class=\"plainlist\">%s</ul>" % items)
        elif lines[0].startswith("## "):
            out.append("<h3>%s</h3>" % inline(lines[0][3:]))
            if len(lines) > 1:
                out.append("<p>%s</p>" % inline(" ".join(lines[1:])))
        else:
            out.append("<p>%s</p>" % inline(" ".join(l.strip() for l in lines)))
    return "\n".join(out)


def pretty_date(iso):
    if not iso or len(iso) < 10:
        return e(iso)
    return "%s · %s · %s" % (iso[:4], iso[5:7], iso[8:10])


# Attributes whose value may be a site-absolute path.
PATH_ATTRS = ("href", "src", "data-full")


def rebase(markup):
    """Prefix every site-absolute path attribute with the base path. No-op at the root."""
    if not BASE:
        return markup
    out = re.sub(r'(%s)="/(?!/)' % "|".join(PATH_ATTRS), r'\1="' + BASE + '/', markup)
    # Anything still pointing at the server root would 404 under a sub-path.
    stray = re.findall(r'([a-z-]+)="(/(?!/)[^"]*)"', out)
    stray = [a for a in stray if not a[1].startswith(BASE + "/")]
    if stray:
        raise SystemExit("un-rebased absolute paths: %s" % stray[:5])
    return out


def rebase_css(css):
    """Same for url(/...) inside a stylesheet, which rebase() never sees."""
    if not BASE:
        return css
    return re.sub(r"url\((['\"]?)/(?!/)", lambda m: "url(" + m.group(1) + BASE + "/", css)


def externalise(markup):
    """Links off the site open in a new tab."""
    def fix(m):
        attrs = m.group(1)
        if "target=" in attrs:
            return m.group(0)
        return '<a %s target="_blank" rel="noopener">' % attrs
    return re.sub(r'<a ([^>]*href="https?://[^"]+"[^>]*)>', fix, markup)


def write(path, markup):
    full = os.path.join(DIST, path.strip("/"), "index.html") if path != "/" \
        else os.path.join(DIST, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(externalise(rebase(markup)))
    print("  %-24s %6d bytes" % (path, len(markup.encode("utf-8"))))


# ---------------------------------------------------------------- chrome
def head(site, title, description, path):
    full_title = title if title == site["short_name"] else "%s · %s" % (title, site["short_name"])
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:type" content="website">
<meta property="og:url" content="%s%s">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&amp;family=IBM+Plex+Sans:wght@400;500;600;700&amp;family=IBM+Plex+Serif:wght@500;600;700&amp;display=swap">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
""" % (e(full_title), e(description), SITE_URL, path, e(full_title), e(description), SITE_URL, path)


def header(path):
    items = "".join(
        '        <li><a href="%s"%s>%s</a></li>\n'
        % (href, ' aria-current="page"' if href == path else "", label)
        for href, label in NAV)
    return """<a class="skip" href="#main">Skip to content</a>
<header class="site">
  <div class="wrap masthead">
    <a class="lockup" href="/" aria-label="IAHR-APD home">
      <img class="logo" src="/assets/logo/iahr-apd.png" width="600" height="167"
           alt="IAHR-APD — Asia and Pacific Regional Division">
    </a>
    <div class="util">
      <a href="https://www.iahr.org/">IAHR Global &#8599;</a>
      <a class="btn ghost" href="/membership/">Join IAHR</a>
    </div>
  </div>
  <nav class="primary" aria-label="Primary">
    <div class="wrap">
      <ul>
%s      </ul>
    </div>
  </nav>
</header>
<main id="main">
""" % items


def footer(site):
    s = site["secretariat"]
    addr = "<br>\n          ".join(e(l) for l in s["address_lines"])
    return """</main>

<div class="lightbox" id="lightbox" hidden role="dialog" aria-modal="true" aria-label="Photograph">
  <button class="lb-close" id="lb-close" aria-label="Close">&times;</button>
  <button class="lb-prev" id="lb-prev" aria-label="Previous photograph">&lsaquo;</button>
  <button class="lb-next" id="lb-next" aria-label="Next photograph">&rsaquo;</button>
  <figure>
    <img id="lb-img" alt="">
    <figcaption id="lb-cap"></figcaption>
  </figure>
</div>

<footer class="site">
  <div class="wrap">
    <div class="fgrid">
      <div>
        <img class="logo-white" src="/assets/logo/iahr-apd-white.png" width="600" height="167" alt="IAHR-APD">
        <h4 style="margin-top:24px">Secretariat</h4>
        <p class="addr">
          <strong>IAHR-APD Secretariat</strong><br>
          %s<br>
          %s
        </p>
        <img class="logo-kict" src="/assets/logo/kict-white.png" width="372" height="100" alt="KICT">
      </div>
      <div><h4>The Division</h4><ul>
        <li><a href="/about/">About IAHR-APD</a></li>
        <li><a href="/governance/">Executive Committee</a></li>
        <li><a href="/about/#statutes">By-Laws &amp; regulations</a></li>
        <li><a href="/governance/#reports">Annual reports</a></li>
        <li><a href="/governance/#meetings">EC meeting records</a></li>
      </ul></div>
      <div><h4>Activities</h4><ul>
        <li><a href="/congresses/">APD Congresses</a></li>
        <li><a href="/congresses/#hosting">Hosting a Congress</a></li>
        <li><a href="/awards/">Awards</a></li>
        <li><a href="/publications/">JHER</a></li>
        <li><a href="/gallery/">Gallery</a></li>
      </ul></div>
      <div><h4>Elsewhere</h4><ul>
        <li><a href="%s">IAHR Global &#8599;</a></li>
        <li><a href="%s">IAHR membership &#8599;</a></li>
        <li><a href="%s">JHER on ScienceDirect &#8599;</a></li>
        <li><a href="%s">KICT &#8599;</a></li>
      </ul></div>
    </div>
    <div class="legal">
      <span>&copy; 2026 %s</span>
      <span>Secretariat hosted by KICT</span>
    </div>
  </div>
</footer>
<script src="/site.js" defer></script>
</body>
</html>
""" % (e(s["host"]), addr,
       e(site["links"]["iahr_global"]), e(site["links"]["iahr_membership"]),
       e(site["links"]["jher"]), e(site["links"]["kict"]), e(site["full_name"]))


def page(site, path, title, description, body):
    return head(site, title, description, path) + header(path) + body + footer(site)


def pagehead(eyebrow, title, lede):
    return """  <section class="pagehead"><div class="wrap">
    <div class="eyebrow">%s</div>
    <h1>%s</h1>
    <p>%s</p>
  </div></section>

""" % (e(eyebrow), e(title), inline(lede))


def band_head(eyebrow, title, sub="", more=None):
    more_html = '      <a class="more" href="%s">%s</a>\n' % (more[0], more[1]) if more else ""
    sub_html = '\n      <p class="sub">%s</p>' % inline(sub) if sub else ""
    return """    <div class="band-head">
      <div><div class="eyebrow">%s</div><h2>%s</h2>%s</div>
%s    </div>
""" % (e(eyebrow), e(title), sub_html, more_html)


def person_card(m):
    flag = ' <span class="tag">%s</span>' % e(m["flag"]) if m.get("flag") else ""
    return """        <div class="card">
          <img class="avatar" src="%s" width="420" height="525" loading="lazy" alt="%s">
          <div class="role">%s</div>
          <div class="who">%s</div>
          <div class="aff">%s%s</div>
          <div class="cty">%s</div>
        </div>
""" % (e(m["photo"]), e(m["name"]), e(m["role"]), e(m["name"]), e(m["affiliation"]), flag, e(m["country"]))


def laureate_list(entries):
    rows = ""
    for r in entries:
        names = "".join('<div class="name">%s <span class="aff">&middot; %s</span></div>'
                        % (e(p["name"]), e(p["note"])) for p in r["people"])
        rows += "        <li><b>%s</b><div>%s</div></li>\n" % (e(r["year"]), names)
    return '      <ul class="laureates">\n%s      </ul>\n' % rows


def doc_list(docs, extra=""):
    rows = ""
    for d in docs:
        href = e(d.get("file") or "#")
        fmt = '<span class="fmt">%s</span>' % e(d.get("format", "PDF"))
        rows += '        <li><a href="%s">%s %s</a></li>\n' % (href, e(d["title"]), fmt)
    return '      <ul class="docs"%s>\n%s      </ul>\n' % (extra, rows)


def doc_blocks(body):
    out = []
    for b in body:
        if b["type"] == "heading":
            out.append("<h3>%s</h3>" % e(b["text"]))
        elif b["type"] == "list":
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % e(i) for i in b["items"]))
        else:
            out.append("<p>%s</p>" % e(b["text"]))
    return "\n      ".join(out)


def build_document(site, doc):
    eyebrow = {"statute": "Statute",
               "hosting": "Congress hosting pack",
               "report": "Report to the IAHR Council"}.get(doc.get("kind"), "Document")
    body = pagehead(eyebrow, doc["title"], doc.get("summary", ""))

    pills = ""
    if doc.get("status"):
        pills += '<span class="pill now">%s</span>' % e(doc["status"])
    if doc.get("version"):
        pills += '<span class="pill">%s</span>' % e(doc["version"])
    if doc.get("pdf"):
        pills += '<a class="pill" href="%s">Download PDF</a>' % e(doc["pdf"])

    body += '  <section class="band tint"><div class="wrap">\n'
    if pills:
        body += '    <div class="docmeta">%s</div>\n' % pills
    if doc.get("intro"):
        body += '    <p class="sub" style="margin-top:16px">%s</p>\n' % inline(doc["intro"])
    body += '    <div class="doc prose" style="margin-top:26px">\n      '
    body += doc_blocks(doc["body"])
    body += '\n    </div>\n  </div></section>\n'

    if doc.get("superseded"):
        rows = ""
        for old in doc["superseded"]:
            link = ' &mdash; <a href="%s">PDF</a>' % e(old["pdf"]) if old.get("pdf") else ""
            rows += ('      <li><div class="t">%s%s</div><div class="n">%s</div></li>\n'
                     % (e(old["title"]), link, e(old.get("note", ""))))
        body += '  <section class="band"><div class="wrap">\n'
        body += band_head("Earlier editions", "Superseded versions",
                          "Kept for reference. Only the edition above is in force.")
        body += '    <ul class="superseded">\n' + rows + '    </ul>\n  </div></section>\n'

    return page(site, doc["url"], doc["title"],
                doc.get("summary") or ("%s. IAHR-APD." % doc["title"]), body)


# ---------------------------------------------------------------- pages
def doc_links(docs, kind, version=True):
    """One row per document: the page, its edition, and the PDF if there is one."""
    rows = ""
    for d in sorted((x for x in docs if x.get("kind") == kind),
                    key=lambda x: (x.get("order", 99), x["title"])):
        pdf = ('<a class="fmt" href="%s">PDF</a>' % e(d["pdf"])) if d.get("pdf") else ""
        ver = ('\n          <div class="ver">%s</div>' % e(d["version"])) \
            if version and d.get("version") else ""
        rows += ('        <li>\n          <div class="line"><a class="t" href="%s">%s</a>%s</div>%s\n        </li>\n'
                 % (e(d["url"]), e(d["title"]), pdf, ver))
    return '      <ul class="doclist">\n%s      </ul>\n' % rows
def build_home(site, congresses, news, events, documents, journal, awards, hero):
    nxt = congresses["next"]
    theme = e(nxt["theme"]) if nxt.get("theme") else "Theme to be announced by the Local Organising Committee."

    slides, dots = "", ""
    for i, sl in enumerate(hero["slides"]):
        slides += ('      <img src="%s" alt="" width="1800" height="760"%s data-place="%s" data-region="%s">\n'
                   % (e(sl["image"]), ' class="on"' if i == 0 else ' loading="lazy"',
                      e(sl["place"]), e(sl["region"])))
        dots += ('        <button type="button" data-slide="%d" aria-current="%s" '
                 'aria-label="%s"></button>\n' % (i, "true" if i == 0 else "false", e(sl["place"])))
    first = hero["slides"][0]

    news_items = ""
    for n in news[:4]:
        img = ('              <img class="thumb" src="%s" alt="" loading="lazy" width="720" height="405">\n'
               % e(n["image"])) if n.get("image") else ""
        news_items += ('            <li>%s              <span class="date">%s</span>\n'
                       '              <a class="title" href="/news/%s/">%s</a>\n'
                       '              <span class="meta">%s</span></li>\n'
                       % (img, pretty_date(n["date"]), e(n["slug"]), e(n["title"]),
                          inline(n.get("summary", ""))))

    ev = ""
    for x in events["events"][:3]:
        ev += ('          <div class="event"><div class="when"><b class="num">%s</b>'
               '<span class="num">%s</span></div>\n'
               '            <div><div class="what">%s</div><div class="where">%s</div></div></div>\n'
               % (e(x["month"]), e(x["year"]), e(x["title"]), e(x["detail"])))

    rows = ""
    for c in congresses["archive"][:6]:
        cls = ' class="next"' if c.get("next") else ""
        tag = '<span class="tag">Next</span>' if c.get("next") else ""
        th = e(c["theme"]) if c["theme"] else '<span class="gap">Theme to be announced</span>'
        rows += ('            <tr%s><td class="no">%s</td><td class="yr">%s</td>'
                 '<td class="place">%s%s</td><td class="theme">%s</td></tr>\n'
                 % (cls, e(c["number"]), e(c["year"] or "—"), e(c["location"]), tag, th))

    metrics = "".join('          <div class="row"><span>%s</span><b>%s</b></div>\n'
                      % (e(m["label"]), e(m["value"])) for m in journal["metrics"][:6])

    award_cards = ""
    for key, label in (("distinguished", "Distinguished Membership"),
                       ("heritage", "Heritage Award"),
                       ("best_paper", "Best Paper Award")):
        block = awards[key]
        lis = "".join('            <li><b class="num">%s</b><span>%s</span></li>\n'
                      % (e(r["year"]), "<br>".join(e(p["name"]) for p in r["people"]))
                      for r in block["recipients"][:3])
        award_cards += ('        <div class="award"><div class="since">Awarded biennially</div>'
                        '<h3>%s</h3>\n          <ul>\n%s          </ul></div>\n' % (label, lis))

    body = '  <section class="hero">\n'
    body += '    <div class="hero-slides" id="hero-slides" data-interval="%d">\n%s    </div>\n' % (
        int(hero.get("interval_seconds", 7)), slides)
    body += '    <canvas id="contours" aria-hidden="true"></canvas>\n'
    body += '''    <div class="wrap">
      <div>
        <div class="eyebrow">Regional Division &middot; Founded %s</div>
        <h1>%s</h1>
        <p class="lede">IAHR-APD brings together researchers and practitioners from more than twenty
        countries and economies to advance the science of hydraulics, build professional capacity in the
        region, and contribute regional expertise to the world's water challenges.</p>
        <div class="hero-actions">
          <a class="btn" href="/congresses/">%s APD Congress &rarr;</a>
          <a class="btn ghost" href="/congresses/#hosting">Host a Congress</a>
          <a class="btn ghost" href="/publications/">Submit to JHER</a>
        </div>
      </div>
      <aside class="record">
        <div class="head"><div class="eyebrow">Next Congress</div><div class="eyebrow num">%s</div></div>
        <div class="body">
          <h2>%s, %s</h2>
          <p class="theme">%s</p>
          <dl>
            <dt>Dates</dt><dd class="num">%s</dd>
            <dt>Host</dt><dd>%s</dd>
            <dt>Abstracts</dt><dd>%s</dd>
          </dl>
          <div class="countdown"><b id="days" data-opening="%s">&mdash;</b><span>days until the opening session</span></div>
        </div>
      </aside>
    </div>
    <div class="photocred">
      <div class="wrap">
        <b id="slide-place">%s</b><span id="slide-region">%s</span>
        <div class="dots" id="slide-dots">
%s        </div>
      </div>
    </div>
  </section>

  <section class="band tint">
    <div class="wrap">
      <div class="newsroom">
        <div class="col">
          <h3>Latest news</h3>
          <ul class="items">
%s          </ul>
        </div>
        <div class="col">
          <h3>Upcoming</h3>
%s        </div>
        <div class="col">
          <h3>Governing documents</h3>
%s        </div>
      </div>
    </div>
  </section>

  <section class="band">
    <div class="wrap">
%s      <div class="tablewrap">
        <table class="records">
          <thead><tr><th scope="col">No.</th><th scope="col">Year</th><th scope="col">Location</th><th scope="col">Theme</th></tr></thead>
          <tbody>
%s          </tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="band tint">
    <div class="wrap">
      <div class="split">
        <div>
          <div class="eyebrow">Division Journal</div>
          <h2 style="font-size:26px;margin-top:8px">%s</h2>
          <div class="prose" style="margin-top:14px"><p>%s</p></div>
          <div class="hero-actions" style="margin-top:24px">
            <a class="btn" href="/publications/">About the journal</a>
            <a class="btn ghost" href="%s">Read JHER &#8599;</a>
          </div>
        </div>
        <div class="sidecard">
          <div class="cap">Metrics &middot; %s</div>
%s        </div>
      </div>
    </div>
  </section>

  <section class="band">
    <div class="wrap">
%s      <div class="awards">
%s      </div>
    </div>
  </section>
''' % (e(site["founded"]), e(site["tagline"]), e(nxt["number"]), e(nxt["number"]),
       e(nxt["city"]), e(nxt["country"]), theme, e(nxt["dates"]), e(nxt["host"]),
       e(nxt["abstracts"]), e(nxt["opening"]),
       e(first["place"]), e(first["region"]), dots,
       news_items, ev, doc_links(documents, "statute", version=False),
       band_head("Record of Congresses",
                 "Twenty-five congresses since %s" % site["founded"], "",
                 ("/congresses/", "Full archive, 1st &ndash; 26th &rarr;")),
       rows,
       e(journal["title"]), inline(journal["body"][0]), e(site["links"]["jher"]),
       e(journal["metrics_year"]), metrics,
       band_head("Recognition", "APD Awards", "",
                 ("/awards/", "Statements, rules and full recipient lists &rarr;")),
       award_cards)

    return page(site, "/", site["short_name"],
                "IAHR-APD — the Asian and Pacific Division of the International Association for "
                "Hydro-Environment Engineering and Research. Congresses, awards, the Journal of "
                "Hydro-environment Research and news from the region.", body)


def build_about(site, documents):
    body = pagehead("The Division", "About IAHR-APD",
                    "A regional division of the International Association for Hydro-Environment "
                    "Engineering and Research, serving the Asian and Pacific regions since 1973.")
    body += '''  <section class="band tint"><div class="wrap">
    <div class="split">
      <div class="prose">
        <p>The IAHR Asian and Pacific Division &mdash; in short <strong>IAHR-APD</strong> &mdash; is a
        regional division of the International Association for Hydro-Environment Engineering and Research
        in the Asian and Pacific regions. The Division was founded in <strong>1973</strong>. All IAHR
        members residing in the regions are members of the Division.</p>
        <p>The Division exists to promote the science of hydraulics and its application across the region,
        to raise professional competence among those working on the hydrosphere, and to provide a standing
        forum where researchers and practitioners can exchange knowledge on problems that are specific to
        Asia and the Pacific &mdash; monsoon hydrology, typhoon and tsunami risk, sediment-laden rivers,
        deltas under subsidence, and rapidly urbanising catchments.</p>
      </div>
      <div class="sidecard">
        <div class="cap">At a glance</div>
        <div class="row"><span>Founded</span><b>1973</b></div>
        <div class="row"><span>Congresses held</span><b>25</b></div>
        <div class="row"><span>Executive Committee</span><b>15</b></div>
        <div class="row"><span>Journal</span><b>JHER</b></div>
        <div class="row"><span>Secretariat</span><b>KICT, Korea</b></div>
      </div>
    </div>
  </div></section>

  <section class="band"><div class="wrap">
    <div class="split wide">
      <div>
        <div class="eyebrow">Mandate</div>
        <h2 style="font-size:23px;margin-top:8px">Objectives of the Division</h2>
        <ol class="statements" style="margin-top:18px">
          <li>To promote the science of hydraulics and its application in all relevant fields in the geographic regions.</li>
          <li>To promote professional competence of individuals in the regions engaged in the development and application of the sciences to the hydrosphere.</li>
          <li>To contribute to the solution of regional problems in the field of hydraulics.</li>
          <li>To provide a forum of exchange of information among researchers and practitioners in the regional community.</li>
        </ol>
      </div>
      <div>
        <div class="eyebrow">Programme</div>
        <h2 style="font-size:23px;margin-top:8px">What the Division does</h2>
        <ul class="plainlist" style="margin-top:18px">
          <li>Organisational development of the Division's areas of endeavour</li>
          <li>Conduct of regional congresses and conferences</li>
          <li>Publication of monographs, congress proceedings and journal papers</li>
          <li>Co-operation and co-ordination with other IAHR divisions and technical committees</li>
          <li>A regional clearing house for information on hydraulics and its practical application</li>
        </ul>
      </div>
    </div>
  </div></section>

  <section class="band tint" id="statutes"><div class="wrap">
'''
    body += band_head("Statutes", "Laws, regulations and statements",
                      "Each document is published in full on this site. Only the edition currently in "
                      "force is listed; superseded editions are kept at the foot of each document.")
    body += doc_links(documents, "statute")
    body += '''  </div></section>

  <section class="band"><div class="wrap">
    <div class="band-head"><div><div class="eyebrow">History</div><h2>Milestones</h2></div></div>
    <ul class="timeline">
      <li><b>1973</b><div><div class="what">The Division is founded</div><div class="note">IAHR establishes a regional division for the Asian and Pacific regions.</div></div></li>
      <li><b>1990</b><div><div class="what">First By-Laws adopted</div><div class="note">Adopted by the Executive Committee in Beijing on 15 November 1990 and approved by the IAHR Council on 1 April 1991.</div></div></li>
      <li><b>2004</b><div><div class="what">By-Laws amended in Hong Kong</div><div class="note">Superseded by the revised edition of 2025.</div></div></li>
      <li><b>2007</b><div><div class="what">JHER launched</div><div class="note">The <em>Journal of Hydro-environment Research</em> begins publication with Elsevier, sponsored by the Korean Water Resources Association.</div></div></li>
      <li><b>2009</b><div><div class="what">Distinguished Membership Award established</div><div class="note">The statement of the award is approved in August 2009.</div></div></li>
      <li><b>2024</b><div><div class="what">24th APD Congress, Wuhan</div><div class="note">&ldquo;Water for a Changing Future&rdquo;, with the Heritage Award presented to Hankou Hydrological Station.</div></div></li>
      <li><b>2026</b><div><div class="what">25th APD Congress, Incheon</div><div class="note">&ldquo;Hydro-environments in the Era of Climate Change and AI&rdquo;, hosted in the Republic of Korea.</div></div></li>
    </ul>
  </div></section>
'''
    return page(site, "/about/", "About",
                "What IAHR-APD is, its objectives and programme, the By-Laws and award statements that "
                "govern it, and the Division's history since 1973.", body)


def build_governance(site, committee, meetings, documents):
    body = pagehead("How the Division is run", "Governance",
                    "The officers and Executive Committee of the Division, and the public record of its "
                    "meetings and annual reporting.")

    officers = ""
    for o in committee["officers"]:
        dept = "<br>%s" % e(o["department"]) if o.get("department") else ""
        officers += ('      <div class="feature">\n'
                     '        <img class="portrait" src="%s" width="420" height="525" alt="%s">\n'
                     '        <div>\n          <div class="role">%s</div>\n          <h3>%s</h3>\n'
                     '          <p class="aff">%s%s</p>\n          <div class="cty">%s</div>\n'
                     '        </div>\n      </div>\n'
                     % (e(o["photo"]), e(o["name"]), e(o["role"]), e(o["name"]),
                        e(o["affiliation"]), dept, e(o["country"])))

    body += '  <section class="band tint"><div class="wrap">\n'
    body += band_head("Officers · " + committee["term"], "Chair and Vice-Chair")
    body += '    <div class="feature-row">\n%s    </div>\n  </div></section>\n\n' % officers

    body += '  <section class="band" id="members"><div class="wrap">\n'
    body += band_head("Executive Committee · " + committee["term"], "Members",
                      "The Executive Committee is elected for a two-year term and meets at least once a "
                      "year, normally alongside an IAHR congress.")
    body += '    <div class="roster-grid">\n'
    body += "".join(person_card(m) for m in committee["members"])
    body += '    </div>\n'
    if committee.get("past_terms"):
        links = " &middot; ".join('<a href="/governance/">%s</a>' % e(t) for t in committee["past_terms"])
        body += '    <p class="sub" style="margin-top:22px">Past committees: %s</p>\n' % links
    body += '  </div></section>\n\n'

    inc = committee.get("incoming")
    if inc:
        rows = "".join('            <tr><td class="place">%s</td><td class="place">%s</td>'
                       '<td class="theme">%s</td><td class="yr">%s</td></tr>\n'
                       % (e(m["role"]), e(m["name"]), e(m["affiliation"]), e(m["country"]))
                       for m in inc["members"])
        body += '  <section class="band tint" id="incoming"><div class="wrap">\n'
        body += band_head("Elected · takes office " + inc["term"].split("–")[0].strip(),
                          "Executive Committee %s" % inc["term"], inc.get("note", ""))
        body += ('    <div class="tablewrap">\n      <table class="records">\n'
                 '        <thead><tr><th scope="col">Role</th><th scope="col">Name</th>'
                 '<th scope="col">Affiliation</th><th scope="col">Country</th></tr></thead>\n'
                 '        <tbody>\n%s        </tbody>\n      </table>\n    </div>\n'
                 '  </div></section>\n\n' % rows)

    body += '  <section class="band" id="reports"><div class="wrap">\n'
    body += band_head("Reporting", "Annual reports",
                      "Each year the Division reports its activity to the IAHR Council: congresses held "
                      "and planned, committee changes, awards presented, journal activity and regional "
                      "outreach. Each report is published in full on this site.")
    body += doc_links(documents, "report")
    body += '  </div></section>\n\n'

    body += '  <section class="band tint" id="meetings"><div class="wrap">\n'
    body += band_head("Record", "Executive Committee meetings",
                      "Meetings held in person alongside IAHR congresses, plus informal gatherings and "
                      "online sessions. Minutes are circulated to members on request.")
    rows = "".join('            <tr><td class="yr">%s</td><td class="place">%s</td>'
                   '<td class="place">%s</td><td class="theme">%s</td></tr>\n'
                   % (e(m["date"]), e(m["type"]), e(m["location"]), e(m["with"]))
                   for m in meetings["meetings"])
    body += ('    <div class="tablewrap">\n      <table class="records">\n'
             '        <thead><tr><th scope="col">Date</th><th scope="col">Type</th>'
             '<th scope="col">Location</th><th scope="col">Held with</th></tr></thead>\n'
             '        <tbody>\n%s        </tbody>\n      </table>\n    </div>\n  </div></section>\n' % rows)
    return page(site, "/governance/", "Governance",
                "The IAHR-APD Executive Committee for %s and the incoming committee, the Division's "
                "annual reports to the IAHR Council, and the record of committee meetings."
                % committee["term"], body)


def build_congresses(site, congresses, documents):
    nxt, latest = congresses["next"], congresses["latest"]
    theme = e(nxt["theme"]) if nxt.get("theme") else \
        "The Local Organising Committee will announce the congress theme and sub-themes, together with " \
        "the call for abstracts, during 2027."

    body = pagehead("Biennial regional congress", "IAHR-APD Congresses",
                    "Since 1973 the Division has convened a regional congress every two years, hosted in "
                    "turn by member institutions across Asia and the Pacific.")
    body += '''  <section class="band tint"><div class="wrap">
    <div class="split">
      <div>
        <div class="eyebrow">Next &middot; %s Congress</div>
        <h2 style="font-size:28px;margin-top:8px">%s, %s</h2>
        <p class="sub">%s. %s</p>
        <div class="hero-actions" style="margin-top:22px">
          <a class="btn" href="/contact/">Register interest</a>
          <a class="btn ghost" href="#hosting">Hosting a congress</a>
        </div>
      </div>
      <div class="sidecard">
        <div class="cap">Most recent &middot; %s Congress</div>
        <div class="pad"><strong style="color:var(--ink)">%s</strong><br>%s</div>
%s        <div class="row"><span>Award citations</span><b><a href="/awards/">Awards</a></b></div>
      </div>
    </div>
  </div></section>

  <section class="band" id="archive"><div class="wrap">
''' % (e(nxt["number"]), e(nxt["city"]), e(nxt["country"]), e(nxt["dates"]), theme,
       e(latest["number"]), e(latest["theme"]), e(latest["venue"]),
       "".join('        <div class="row"><span>%s</span><b>%s</b></div>\n'
               % (e(f["label"]), e(f["value"])) for f in latest.get("facts", [])))

    body += band_head("Complete record", "Congress archive, 1st – 26th",
                      "Rows marked as incomplete are gaps in the Division's own records. Corrections and "
                      "proceedings links from former host institutions are welcome.")
    rows = ""
    for c in congresses["archive"]:
        cls = ' class="next"' if c.get("next") else ""
        tag = '<span class="tag">Next</span>' if c.get("next") else ""
        if c["theme"]:
            th = e(c["theme"])
        elif c["year"]:
            th = '<span class="gap">Theme to be announced</span>'
        else:
            th = '<span class="gap">Year and theme not recorded</span>'
        rows += ('          <tr%s><td class="no">%s</td><td class="yr">%s</td>'
                 '<td class="place">%s%s</td><td class="theme">%s</td></tr>\n'
                 % (cls, e(c["number"]), e(c["year"] or "—"), e(c["location"]), tag, th))
    pack = doc_links(documents, "hosting", version=False)
    body += '''    <div class="tablewrap">
      <table class="records">
        <thead><tr><th scope="col">No.</th><th scope="col">Year</th><th scope="col">Location</th><th scope="col">Theme</th></tr></thead>
        <tbody>
%s        </tbody>
      </table>
    </div>
  </div></section>

  <section class="band tint" id="hosting"><div class="wrap">
    <div class="split">
      <div>
        <div class="eyebrow">For host institutions</div>
        <h2 style="font-size:23px;margin-top:8px">Hosting an IAHR-APD Congress</h2>
        <div class="prose" style="margin-top:14px">
          <p>Member institutions in the region are invited to propose hosting a future congress. Proposals
          are submitted to the Secretariat and considered by the Executive Committee, normally four years
          before the intended congress.</p>
          <p>A complete proposal covers the venue and dates, the proposed theme and sub-themes, the local
          organising committee, the budget and registration model, and the arrangements for publishing
          proceedings.</p>
        </div>
        <ol class="statements" style="margin-top:20px;border-top:2px solid var(--ink)">
          <li>Read the Guidelines for IAHR Regional Congresses issued by the IAHR Secretariat.</li>
          <li>Complete the proposal format and submit it to the APD Secretariat.</li>
          <li>Present the proposal to the Executive Committee at its next meeting.</li>
          <li>On approval, work through the congress working sheet with the Secretariat.</li>
        </ol>
      </div>
      <div>
        <div class="eyebrow">Hosting pack</div>
        <p class="sub" style="margin-top:8px;margin-bottom:14px">Each document is published in full on
        this site and can also be downloaded.</p>
%s        <p class="sub" style="margin-top:18px">Questions about hosting should go to the Secretariat
        &mdash; see <a href="/contact/">Contact</a>.</p>
      </div>
    </div>
  </div></section>
''' % (rows, pack)
    return page(site, "/congresses/", "Congresses",
                "Every IAHR-APD congress from the 1st to the 26th, the next congress in Wellington in "
                "2028, and how member institutions can propose to host one.", body)


def build_awards(site, awards, documents):
    latest = awards["latest"]
    statements = {d["slug"]: d for d in documents}
    links = {
        "distinguished": statements.get("distinguished-membership-award-statement"),
        "best_paper": statements.get("best-paper-award-rules"),
    }

    def slot(entry):
        if entry.get("photo"):
            return '<img class="avatar sm" src="%s" alt="%s">' % (e(entry["photo"]), e(entry["name"]))
        return '<div class="portrait-slot" aria-hidden="true">Photo</div>'

    def recipient(entry):
        return ('          <div class="editor">%s\n'
                '            <div><strong style="font-size:16px">%s</strong><br>%s</div>\n'
                '          </div>\n' % (slot(entry), e(entry["name"]), e(entry["affiliation"])))

    dma = recipient(latest["distinguished"])
    if latest.get("distinguished_2"):
        dma += recipient(latest["distinguished_2"])

    papers = "".join('          <li><div class="ttl">%s</div>\n'
                     '            <div class="aut">%s</div><div class="cty">%s</div></li>\n'
                     % (e(p["title"]), e(p["authors"]), e(p["country"])) for p in latest["papers"])

    body = pagehead("Recognition", "IAHR-APD Awards",
                    "The Division presents three awards at each regional congress: for distinguished "
                    "individual contribution, for hydraulic heritage in the region, and for the best "
                    "papers of the congress.")
    body += '  <section class="band tint"><div class="wrap">\n'
    body += band_head(latest["congress"], "%s recipients" % latest["year"], "",
                      ("/congresses/", "About the congress &rarr;"))
    body += ('    <div class="split wide">\n      <div>\n'
             '        <div class="sidecard">\n'
             '          <div class="cap">Distinguished Membership Award</div>\n'
             '%s        </div>\n'
             '        <div class="sidecard" style="margin-top:24px">\n'
             '          <div class="cap">Water Conservancy and Environmental Heritage Award</div>\n'
             '%s        </div>\n'
             '      </div>\n      <div>\n'
             '        <div class="eyebrow">Best Paper Award</div>\n'
             '        <ul class="papers" style="margin-top:12px;border-top:2px solid var(--ink)">\n'
             '%s        </ul>\n'
             '      </div>\n    </div>\n  </div></section>\n\n'
             % (dma, recipient(latest["heritage"]), papers))

    for i, key in enumerate(("distinguished", "heritage", "best_paper")):
        block = awards[key]
        tint = " tint" if i % 2 else ""
        doc = links.get(key)
        more = (doc["url"], "Read the statement and rules &rarr;") if doc else None
        body += '  <section class="band%s" id="%s"><div class="wrap">\n' % (tint, key.replace("_", "-"))
        body += band_head(block["eyebrow"], block["title"], block["intro"], more)
        body += laureate_list(block["recipients"])
        body += "  </div></section>\n\n"
    return page(site, "/awards/", "Awards",
                "The Distinguished IAHR-APD Membership Award, the Heritage Award and the Best Paper "
                "Award, with the full list of recipients since 2010.", body)


def build_news_index(site, news, events):
    items = ""
    for n in news:
        img = ('            <img class="thumb" src="%s" alt="" loading="lazy" width="720" height="405">\n'
               % e(n["image"])) if n.get("image") else ""
        items += ('          <li>%s            <span class="date">%s</span>\n'
                  '            <a class="title" href="/news/%s/">%s</a>\n'
                  '            <span class="meta">%s</span></li>\n'
                  % (img, pretty_date(n["date"]), e(n["slug"]), e(n["title"]),
                     inline(n.get("summary", ""))))
    ev = "".join('          <div class="event"><div class="when"><b class="num">%s</b>'
                 '<span class="num">%s</span></div>\n'
                 '            <div><div class="what">%s</div><div class="where">%s</div></div></div>\n'
                 % (e(x["month"]), e(x["year"]), e(x["title"]), e(x["detail"]))
                 for x in events["events"])

    body = pagehead("Bulletin", "News & Events",
                    "Announcements from the Division and the calendar of congresses, committee meetings "
                    "and regional events.")
    body += '''  <section class="band tint"><div class="wrap">
    <div class="split">
      <div>
        <div class="eyebrow">Announcements</div>
        <h2 style="font-size:23px;margin-top:8px">Latest news</h2>
        <ul class="items" style="margin-top:16px;border-top:2px solid var(--ink)">
%s        </ul>
      </div>
      <div class="sidecard">
        <div class="cap">Calendar</div>
        <div class="pad" style="padding-bottom:4px">
%s        </div>
      </div>
    </div>
  </div></section>
''' % (items, ev)
    return page(site, "/news/", "News & Events",
                "Announcements from IAHR-APD and the calendar of congresses, Executive Committee "
                "meetings and regional events.", body)


def build_news_item(site, item):
    body = pagehead("News · " + pretty_date(item["date"]).replace(" · ", "."),
                    item["title"], item.get("summary", ""))
    img = ('    <img class="newsimg" src="%s" alt="" width="1600" height="900">\n'
           % e(item["image"])) if item.get("image") else ""
    body += '  <section class="band tint"><div class="wrap">\n%s' % img
    body += ('    <div class="prose" style="font-size:16.5px;margin-top:22px">%s</div>\n'
             '    <p class="sub" style="margin-top:32px"><a href="/news/">&larr; All news</a></p>\n'
             '  </div></section>\n' % rich(item.get("body", "")))
    return page(site, "/news/%s/" % item["slug"], item["title"],
                item.get("summary", "")[:180], body)


def build_gallery(site, gallery):
    body = pagehead("Photographs", "Gallery",
                    "Congresses, Executive Committee meetings and technical visits, year by year.")
    nav = "".join('        <button type="button" data-year="y%s">%s</button>\n'
                  % (e(y["year"]), e(y["year"])) for y in gallery["years"])
    body = body.replace("  </div></section>\n\n",
                        '    <div class="yearnav" id="yearnav">\n%s    </div>\n  </div></section>\n\n' % nav, 1)

    for i, y in enumerate(gallery["years"]):
        alt = "%s, %s" % (y["title"], y["year"])
        shots = "".join("""        <button type="button" class="shot" data-full="%s" data-caption="%s"
                aria-label="Enlarge photograph from %s">
          <img src="%s" width="640" height="457" loading="lazy" alt="%s">
        </button>
""" % (e(p["image"]), e(p.get("caption") or alt), e(alt), e(p.get("thumb") or p["image"]),
       e(p.get("caption") or alt)) for p in y["photos"])
        body += """  <section class="band%s" id="y%s"><div class="wrap">
    <div class="yearhead"><b>%s</b><h2>%s</h2><span class="where">%s</span></div>
    <div class="gallery">
%s    </div>
  </div></section>

""" % (" tint" if i % 2 == 0 else "", e(y["year"]), e(y["year"]), e(y["title"]), e(y["where"]), shots)

    body += """  <section class="band"><div class="wrap">
    <p class="sub">Photographs from earlier congresses are held by the Secretariat and by former host
    institutions. Members who have images from past congresses are invited to send them to the
    <a href="/contact/">Secretariat</a> for the archive.</p>
  </div></section>
"""
    return page(site, "/gallery/", "Gallery",
                "Photographs from IAHR-APD congresses, Executive Committee meetings and technical "
                "visits, arranged by year.", body)


def build_membership(site, committee):
    ypn = next((m for m in committee["members"] if m["role"] == "YPN Member"), None)
    ypn_line = ("The Division holds a dedicated YPN seat on its Executive Committee, currently held by "
                "%s of %s." % (ypn["name"], ypn["affiliation"])) if ypn else ""
    body = pagehead("Joining the Division", "Membership",
                    "Membership of IAHR-APD follows automatically from membership of IAHR. There is no "
                    "separate application and no separate fee.")
    body += '''  <section class="band tint"><div class="wrap">
    <div class="split">
      <div>
        <div class="prose">
          <p><strong>All IAHR members residing in the Asian and Pacific regions are members of the
          Division.</strong> To join, you become a member of IAHR through the association's global
          secretariat; the regional division follows from your country of residence.</p>
          <p>IAHR offers individual, student, young professional and corporate membership. Current
          categories, rates and the application form are held by the IAHR global secretariat, and are
          the same wherever in the world you live.</p>
          <p>Division membership adds the biennial regional congress at member rates, eligibility for
          the APD awards, the Division's calls and announcements, and a route into the regional Young
          Professionals Network.</p>
        </div>
        <div class="hero-actions" style="margin-top:26px">
          <a class="btn" href="%s">Categories, rates and application &#8599;</a>
          <a class="btn ghost" href="/contact/">Ask the Secretariat</a>
        </div>
        <div class="band-head" style="margin-top:44px;margin-bottom:16px">
          <div><div class="eyebrow">Young Professionals</div><h2 style="font-size:23px">YPN in the Asia-Pacific</h2></div>
        </div>
        <p class="sub" style="margin-top:0">The IAHR Young Professionals Network connects students and
        early-career researchers across the region. %s</p>
      </div>
      <div>
        <div class="sidecard">
          <div class="cap">What Division membership adds</div>
          <div class="pad">
            <ul class="plainlist" style="font-size:14px">
              <li>Member rates at the biennial APD Congress</li>
              <li>Eligibility for the three APD awards</li>
              <li>Announcements and calls from the Division</li>
              <li>Regional Young Professionals Network</li>
            </ul>
          </div>
        </div>
        <div class="sidecard" style="margin-top:24px">
          <div class="cap">What IAHR membership adds</div>
          <div class="pad">
            <ul class="plainlist" style="font-size:14px">
              <li>The Journal of Hydraulic Research</li>
              <li>Hydrolink, the association's magazine</li>
              <li>Technical committee participation</li>
              <li>Member rates at IAHR World Congresses</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div></section>
''' % (e(site["links"]["iahr_membership"]), e(ypn_line))
    return page(site, "/membership/", "Membership",
                "How to join IAHR and the Asian and Pacific Division, what membership includes, and the "
                "regional Young Professionals Network.", body)


def build_contact(site):
    s = site["secretariat"]
    addr = "<br>".join(e(l) for l in s["address_lines"])

    people = ""
    for p in s.get("people", []):
        mail = ""
        if p.get("email"):
            mail = ('\n            <div class="mail">%s</div>' % e(p["email"]))
        note = ('\n            <div class="note">%s</div>' % e(p["note"])) if p.get("note") else ""
        people += ('          <div class="who-row">\n            <div class="role">%s</div>\n            <div class="nm">%s</div>\n            <div class="aff">%s</div>%s%s\n          </div>\n'
                   % (e(p["role"]), e(p["name"]), e(p.get("affiliation", "")), note, mail))

    topics = "".join("          <li>%s</li>\n" % e(t) for t in site.get("enquiry_topics", []))

    body = pagehead("Get in touch", "Contact",
                    "The Division's Secretariat is hosted by the Korea Institute of Civil Engineering and "
                    "Building Technology in Goyang, Republic of Korea.")
    body += '''  <section class="band tint"><div class="wrap">
    <div class="split">
      <div>
        <div class="eyebrow">Enquiries</div>
        <h2 style="font-size:23px;margin-top:8px">Write to the Secretariat</h2>
        <p class="sub">The Secretariat is the first point of contact for:</p>
        <ul class="plainlist" style="margin-top:14px">
%s        </ul>
        <div class="prose" style="margin-top:22px">
          <p>For membership, subscriptions and world congress matters, contact the IAHR global
          secretariat directly at <a href="%s">iahr.org</a>.</p>
        </div>
        <div class="hero-actions" style="margin-top:22px">
          <a class="btn ghost" href="/congresses/#hosting">Hosting a congress</a>
          <a class="btn ghost" href="/awards/">Award nominations</a>
        </div>
      </div>
      <div>
        <div class="sidecard">
          <div class="cap">IAHR-APD Secretariat</div>
          <div class="pad"><strong style="color:var(--ink)">%s</strong><br>%s</div>
        </div>
        <div class="sidecard" style="margin-top:24px">
          <div class="cap">Who to write to</div>
%s        </div>
      </div>
    </div>
  </div></section>
''' % (topics, e(site["links"]["iahr_global"]), e(s["host"]), addr, people)
    return page(site, "/contact/", "Contact",
                "How to reach the IAHR-APD Secretariat at KICT in Goyang, Republic of Korea.", body)


def build_publications(site, journal, congresses):
    metrics = "".join('          <div class="row"><span>%s</span><b>%s</b></div>\n'
                      % (e(m["label"]), e(m["value"])) for m in journal["metrics"])
    editors = ""
    for ed in journal["editors"]:
        interests = '<br><span class="spec">%s</span>' % e(ed["interests"]) if ed.get("interests") else ""
        editors += """          <div class="editor">
            <img class="avatar sm" src="%s" alt="%s">
            <div><strong>%s</strong><br>%s%s</div>
          </div>
""" % (e(ed["photo"]), e(ed["name"]), e(ed["name"]), e(ed["affiliation"]), interests)

    body = pagehead("Journal and proceedings", "Publications",
                    "The Division publishes through its house journal, through the proceedings of its "
                    "biennial congresses, and through the wider IAHR publishing programme.")
    body += """  <section class="band tint"><div class="wrap">
    <div class="split">
      <div>
        <div class="eyebrow">%s</div>
        <h2 style="font-size:26px;margin-top:8px">%s</h2>
        <div class="prose" style="margin-top:16px">%s</div>
        <div class="hero-actions" style="margin-top:26px">
          <a class="btn" href="%s">Read JHER &#8599;</a>
          <a class="btn ghost" href="%s">Submit a manuscript &#8599;</a>
        </div>
      </div>
      <div>
        <div class="sidecard">
          <div class="cap">Metrics &middot; %s</div>
%s        </div>
        <div class="sidecard" style="margin-top:24px">
          <div class="cap">Editors-in-Chief</div>
%s        </div>
      </div>
    </div>
  </div></section>

  <section class="band"><div class="wrap">
""" % (e(journal["eyebrow"]), e(journal["title"]),
       "\n".join("<p>%s</p>" % inline(p) for p in journal["body"]),
       e(site["links"]["jher"]), e(site["links"]["jher"]),
       e(journal["metrics_year"]), metrics, editors)

    body += band_head("Congress proceedings", "Proceedings archive",
                      "Proceedings are produced by each host institution. Where a permanent link exists "
                      "it is recorded here; earlier volumes are held by the Secretariat.")
    rows = ""
    for pr in congresses["proceedings"]:
        link = '<a href="%s">Online archive</a>' % e(pr["url"]) if pr.get("url") \
            else '<span class="gap">Held by the Secretariat</span>'
        rows += ('          <tr><td class="no">%s</td><td class="yr">%s</td>'
                 '<td class="place">%s</td><td class="theme">%s</td></tr>\n'
                 % (e(pr["number"]), e(pr["year"]), e(pr["host"]), link))
    body += """    <div class="tablewrap">
      <table class="records">
        <thead><tr><th scope="col">No.</th><th scope="col">Year</th><th scope="col">Host</th><th scope="col">Proceedings</th></tr></thead>
        <tbody>
%s        </tbody>
      </table>
    </div>
  </div></section>

  <section class="band tint"><div class="wrap">
""" % rows
    body += band_head("Also from IAHR", "Wider publishing programme")
    cards = "".join("""      <div class="person"><div class="role">%s</div><div class="who">%s</div>
        <div class="aff">%s</div><div class="country">%s</div></div>
""" % (e(o["kind"]), e(o["title"]), e(o["note"]), e(o["meta"])) for o in journal["other_publications"])
    body += '    <div class="leaders">\n%s    </div>\n  </div></section>\n' % cards
    return page(site, "/publications/", "Publications",
                "The Journal of Hydro-environment Research, the congress proceedings archive and the "
                "wider IAHR publishing programme.", body)


# ---------------------------------------------------------------- extras
def build_sitemap(paths):
    urls = "".join("  <url><loc>%s%s</loc></url>\n" % (SITE_URL, p) for p in paths)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' \
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % urls


def copy_tree(src, dst):
    if not os.path.isdir(src):
        return
    for root, _, files in os.walk(src):
        for fn in files:
            if fn.startswith("."):
                continue
            rel = os.path.relpath(os.path.join(root, fn), src)
            out = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            if fn.endswith(".css") and BASE:
                with open(os.path.join(root, fn), encoding="utf-8") as f:
                    text = f.read()
                with open(out, "w", encoding="utf-8") as f:
                    f.write(rebase_css(text))
            else:
                shutil.copy2(os.path.join(root, fn), out)


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)

    site = load("site.json")
    committee = load("committee.json")
    congresses = load("congresses.json")
    meetings = load("ec-meetings.json")
    awards = load("awards.json")
    journal = load("journal.json")
    events = load("events.json")
    gallery = load("gallery.json")
    hero = load("hero.json")
    documents = load_documents()
    for doc in documents:
        doc["pdf"] = ensure_pdf(doc)
    news = load_news()

    print("pages")
    write("/", build_home(site, congresses, news, events, documents, journal, awards, hero))
    write("/about/", build_about(site, documents))
    write("/governance/", build_governance(site, committee, meetings, documents))
    write("/congresses/", build_congresses(site, congresses, documents))
    write("/awards/", build_awards(site, awards, documents))
    write("/publications/", build_publications(site, journal, congresses))
    write("/news/", build_news_index(site, news, events))
    for item in news:
        write("/news/%s/" % item["slug"], build_news_item(site, item))
    write("/gallery/", build_gallery(site, gallery))
    write("/membership/", build_membership(site, committee))
    write("/contact/", build_contact(site))
    for doc in documents:
        write(doc["url"], build_document(site, doc))

    paths = ["/", "/about/", "/governance/", "/congresses/", "/awards/", "/publications/",
             "/news/", "/gallery/", "/membership/", "/contact/"] +             ["/news/%s/" % n["slug"] for n in news] + [d["url"] for d in documents]
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(build_sitemap(paths))
    with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE_URL)
    if CUSTOM_DOMAIN:
        with open(os.path.join(DIST, "CNAME"), "w", encoding="utf-8") as f:
            f.write(CUSTOM_DOMAIN + "\n")
        print("  CNAME -> %s" % CUSTOM_DOMAIN)
    # Stop GitHub Pages running the output through Jekyll.
    open(os.path.join(DIST, ".nojekyll"), "w").close()

    print("static and assets")
    copy_tree(STATIC, DIST)
    copy_tree(ASSETS, os.path.join(DIST, "assets"))

    total = sum(os.path.getsize(os.path.join(r, f))
                for r, _, fs in os.walk(DIST) for f in fs)
    print("\ndist/ built: %d files, %d KB" %
          (sum(len(fs) for _, _, fs in os.walk(DIST)), total // 1024))


if __name__ == "__main__":
    main()
