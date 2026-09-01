/**
 * POST /api/contact  —  Cloudflare Pages Function
 *
 * Takes the enquiry form and emails it to the Secretariat. The recipient
 * address lives in the CONTACT_TO environment variable and is never sent to
 * the browser, so it does not appear in the page source and cannot be
 * harvested by address scrapers.
 *
 * Environment variables (Cloudflare dashboard → Settings → Variables):
 *   CONTACT_TO       who receives enquiries, e.g. secretariat@example.org
 *   CONTACT_FROM     verified sender, e.g. "IAHR-APD <website@iahrapd.org>"
 *   RESEND_API_KEY   API key from resend.com (free tier is ample)
 */

const MAX = { name: 200, email: 200, topic: 120, message: 8000 };

function clean(value, limit) {
  return String(value == null ? '' : value).replace(/\s+/g, ' ').trim().slice(0, limit);
}

function json(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
}

export async function onRequestPost({ request, env }) {
  let data;
  try {
    const type = request.headers.get('content-type') || '';
    if (type.includes('application/json')) {
      data = await request.json();
    } else {
      data = Object.fromEntries(await request.formData());
    }
  } catch {
    return json(400, { error: 'Could not read the form.' });
  }

  // Hidden field that only automated submissions fill in.
  if (clean(data.company, 50)) return json(204, {});

  const name = clean(data.name, MAX.name);
  const email = clean(data.email, MAX.email);
  const topic = clean(data.topic, MAX.topic) || 'Website enquiry';
  const message = String(data.message || '').trim().slice(0, MAX.message);

  if (!name || !email || !message) {
    return json(400, { error: 'Please give your name, email address and a message.' });
  }
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return json(400, { error: 'That email address does not look right.' });
  }

  if (!env.RESEND_API_KEY || !env.CONTACT_TO || !env.CONTACT_FROM) {
    console.error('contact: missing CONTACT_TO, CONTACT_FROM or RESEND_API_KEY');
    return json(500, { error: 'The contact form is not configured yet.' });
  }

  const sent = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      authorization: `Bearer ${env.RESEND_API_KEY}`,
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      from: env.CONTACT_FROM,
      to: [env.CONTACT_TO],
      reply_to: email,
      subject: `[iahrapd.org] ${topic} — ${name}`,
      text: `${message}\n\n—\nFrom: ${name} <${email}>\nSubject: ${topic}\nSent from the enquiry form on iahrapd.org`,
    }),
  });

  if (!sent.ok) {
    console.error('contact: mail provider returned', sent.status, await sent.text());
    return json(502, { error: 'The message could not be delivered. Please try again later.' });
  }
  return json(200, { ok: true });
}

export async function onRequest() {
  return json(405, { error: 'Use POST.' });
}
