# Admin sign-in worker

The admin screen at `/admin/` signs editors in with their GitHub account.
GitHub will not hand a token straight to a browser, so this small worker does
the exchange. It is set up **once** and then left alone.

You need a Cloudflare account (the same one that hosts the site) and permission
to create an OAuth app on the GitHub organisation.

## 1. Create the GitHub OAuth app

GitHub → your organisation → **Settings → Developer settings → OAuth Apps → New OAuth App**

| Field | Value |
|---|---|
| Application name | `IAHR-APD website admin` |
| Homepage URL | `https://www.iahrapd.org` |
| Authorization callback URL | `https://iahrapd-admin.<your-subdomain>.workers.dev/callback` |

Press **Register application**, then **Generate a new client secret**. Copy the
**Client ID** and the **Client secret** — the secret is shown only once.

## 2. Deploy the worker

Cloudflare dashboard → **Workers & Pages → Create → Worker**

- Name it `iahrapd-admin`
- **Deploy**, then **Edit code**, paste the contents of `worker.js`, **Deploy** again
- **Settings → Variables and Secrets**, add:
  - `GITHUB_CLIENT_ID` — plain text
  - `GITHUB_CLIENT_SECRET` — **encrypted / secret**

Note the worker address, e.g. `https://iahrapd-admin.example.workers.dev`.

## 3. Point the admin screen at it

In `static/admin/config.yml`, set:

```yaml
backend:
  name: github
  repo: iahr-apd/iahrapd.org
  branch: main
  base_url: https://iahrapd-admin.example.workers.dev
```

Commit that change. `https://www.iahrapd.org/admin/` will now sign people in.

## Who can edit

Anyone with **write access to the GitHub repository** can sign in and publish.
To add an editor, add their GitHub account as a collaborator on the repository.
To remove one, remove the collaborator. There are no separate CMS accounts to
keep track of.

## If you would rather not run a worker

[Pages CMS](https://pagescms.org) is a free hosted editor that works on any
GitHub repository with no infrastructure at all — sign in with GitHub, point it
at the repository, and edit the same files. The trade-off is a dependency on
someone else's service. The worker above keeps everything inside your own
accounts.
