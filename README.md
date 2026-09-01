# iahrapd.org

The website of the **IAHR Asian and Pacific Division**. A static site: plain
HTML generated from JSON content files by a single Python script.

Editors do not need any of this — they use the admin screen at `/admin/`.
This file is for whoever maintains the code.

Korean handover notes for the Secretariat: [`docs/사무국-인수인계.md`](docs/사무국-인수인계.md)

## Build

```bash
python build.py
```

Python 3.9 or newer. **No packages to install** — standard library only. The
script reads `content/`, writes `dist/`, and copies `static/` and `assets/`
into it. `dist/` is not committed; it is rebuilt on every deploy.

To look at the result locally:

```bash
python -m http.server 8788 --directory dist
```

## Layout

```
content/          the site's text, as JSON. This is what the admin screen edits.
  site.json         name, Secretariat details, external links
  committee.json    Executive Committee
  congresses.json   next congress, archive, proceedings
  awards.json       the three awards and every recipient
  journal.json      JHER
  documents.json    By-Laws, award statements, annual reports
  ec-meetings.json  committee meeting record
  events.json       calendar
  gallery.json      photographs grouped by year
  news/*.json       one file per news item
assets/           images. Portraits, gallery photographs, logos, hero montage.
static/           copied to the site root as-is: styles.css, site.js, favicon, /admin
build.py          the generator, ~700 lines, commented
functions/        Cloudflare Pages Functions — currently just the contact form
cms-auth/         the GitHub sign-in worker for the admin screen
tools/            one-off scripts used to create the first version of the site
```

Adding a page means adding a `build_*` function in `build.py` and one line in
`main()`. Adding a field means adding it to the JSON, to `build.py`, and to
`static/admin/config.yml`.

## Hosting

Cloudflare Pages, connected to this repository:

| Setting | Value |
|---|---|
| Build command | `python3 build.py` |
| Build output directory | `dist` |
| Root directory | *(repository root)* |

Environment variables, for the contact form:

| Name | Value |
|---|---|
| `CONTACT_TO` | where enquiries go — **never** put this in the page |
| `CONTACT_FROM` | verified sender, e.g. `IAHR-APD <website@iahrapd.org>` |
| `RESEND_API_KEY` | secret, from resend.com |

`PYTHON_VERSION` can be set to `3.12` if the default build image is older.

The site is entirely static, so it can be served from anywhere — GitHub Pages,
a university web server, an S3 bucket. Only the contact form needs Cloudflare
(or an equivalent serverless function).

## The admin screen

`/admin/` runs [Decap CMS](https://decapcms.org). It commits directly to this
repository, which triggers a rebuild and a deploy. Setup instructions and the
alternative to running your own sign-in worker are in
[`cms-auth/README.md`](cms-auth/README.md).

## Notes

- Content is plain JSON and Markdown. If this generator is ever replaced, the
  content carries over to any other static-site tool untouched.
- `build.py` escapes all content before writing it into HTML.
- The contact recipient address exists only as a server-side environment
  variable. It is not in the repository, the built HTML or the JavaScript.
- Everything works without JavaScript except the photograph lightbox and the
  congress countdown, both of which degrade to plain content.
