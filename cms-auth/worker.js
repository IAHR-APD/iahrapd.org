/**
 * GitHub OAuth for the admin screen — a Cloudflare Worker.
 *
 * Decap CMS signs editors in with their GitHub account. GitHub will not talk to
 * a browser directly, so this small worker sits in between. It holds no content
 * and stores nothing; it only exchanges a login code for a token.
 *
 * Deploy once, then never touch it again. See README.md in this folder.
 *
 * Environment variables (Worker → Settings → Variables):
 *   GITHUB_CLIENT_ID       from the GitHub OAuth app
 *   GITHUB_CLIENT_SECRET   from the GitHub OAuth app  (mark as secret)
 */

function page(status, content) {
  const body = `<!doctype html><html><body><script>
    (function () {
      function send() {
        window.opener.postMessage(
          'authorization:github:${status}:${JSON.stringify(content)}',
          '*'
        );
      }
      window.addEventListener('message', send, false);
      window.opener.postMessage('authorizing:github', '*');
    })();
  </script></body></html>`;
  return new Response(body, { headers: { 'content-type': 'text/html; charset=utf-8' } });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === '/auth') {
      const to = new URL('https://github.com/login/oauth/authorize');
      to.searchParams.set('client_id', env.GITHUB_CLIENT_ID);
      to.searchParams.set('scope', 'repo,user');
      to.searchParams.set('redirect_uri', `${url.origin}/callback`);
      return Response.redirect(to.toString(), 302);
    }

    if (url.pathname === '/callback') {
      const code = url.searchParams.get('code');
      if (!code) return page('error', { message: 'No code returned by GitHub.' });

      const res = await fetch('https://github.com/login/oauth/access_token', {
        method: 'POST',
        headers: { accept: 'application/json', 'content-type': 'application/json' },
        body: JSON.stringify({
          client_id: env.GITHUB_CLIENT_ID,
          client_secret: env.GITHUB_CLIENT_SECRET,
          code,
        }),
      });
      const data = await res.json();
      if (data.error || !data.access_token) {
        return page('error', { message: data.error_description || 'Sign-in failed.' });
      }
      return page('success', { token: data.access_token, provider: 'github' });
    }

    return new Response('IAHR-APD admin sign-in.', { status: 200 });
  },
};
