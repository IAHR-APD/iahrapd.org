# iahrapd.org

The website of the **IAHR Asian and Pacific Division**. A static site: plain
HTML generated from JSON content files by a single Python script, published to
GitHub Pages.

Editors do not need any of this — they use [Pages CMS](https://app.pagescms.org).
This file is for whoever maintains the code.

Korean handover notes for the Secretariat: [`docs/사무국-인수인계.md`](docs/사무국-인수인계.md)

## Build

```bash
python build.py
python -m http.server 8788 --directory dist
```

Python 3.9 or newer. **No packages to install** — standard library only. The
script reads `content/`, writes `dist/`, and copies `static/` and `assets/`
into it. `dist/` is not committed; it is rebuilt on every push.

Two environment variables, both set automatically by the workflow and both
unnecessary locally:

| Variable | Purpose |
|---|---|
| `BASE_PATH` | Sub-path the site is served under, e.g. `/iahrapd.org`. Empty at a domain root. |
| `SITE_URL` | Origin used for canonical URLs and the sitemap. |

Both are ignored once `custom_domain` is filled in `content/site.json`.

## Layout

```
content/          the site's text, as JSON. This is what the admin screen edits.
  site.json         name, Secretariat details, custom domain, external links
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
static/           copied to the site root as-is: styles.css, site.js, favicon
build.py          the generator, ~700 lines, commented
.pages.yml        what the admin screen shows and how it saves
tools/            one-off scripts used to create the first version of the site
```

Adding a page means adding a `build_*` function in `build.py` and one line in
`main()`. Adding a field means adding it to the JSON, to `build.py`, and to
`.pages.yml`.

## Publishing

`.github/workflows/deploy.yml` builds the site and publishes it to GitHub Pages
on every push to `main` — including the commits the admin screen makes. There
is no other service in the chain.

One-time repository setup:

- **Settings → Pages → Build and deployment → Source: GitHub Actions**
- The repository must be **public**, or the account needs GitHub Pro — Pages
  does not serve private repositories on the free plan.

### Custom domain

1. At the domain registrar, point `www.iahrapd.org` at `iahr-apd.github.io`
   with a CNAME record, and the apex `iahrapd.org` at GitHub's four A records
   (185.199.108–111.153).
2. Put `www.iahrapd.org` in `custom_domain` in `content/site.json`.

The build then writes a `CNAME` file and switches every link from
`/iahrapd.org/…` to `/…`. Nothing else changes.

## The admin screen

[Pages CMS](https://app.pagescms.org) — a free hosted editor. Editors sign in
with GitHub and open this repository; `.pages.yml` describes the forms. It
commits to `main`, which triggers the workflow above.

There is no separate user list: **write access to this repository is what grants
editing rights.**

If depending on pagescms.org is ever a concern, the same content can be edited
through GitHub's own web editor, or a self-hosted editor such as
[Decap CMS](https://decapcms.org) can be added — it needs a small OAuth proxy
of its own. A working Decap configuration and Cloudflare Worker are in this
repository's history at commit `b3d80d9`.

## Notes

- Content is plain JSON and Markdown. If this generator is ever replaced, the
  content carries over to any other static-site tool untouched.
- `build.py` escapes all content before writing it into HTML.
- The Contact page has no form and no server. If `secretariat.email` is set in
  `content/site.json` the page shows a mail link assembled in the browser from
  split parts, so the address is not plain text in the page source. Use a shared
  Secretariat address there, never a personal one.
- Everything works without JavaScript except the photograph lightbox and the
  congress countdown, both of which degrade to plain content.
