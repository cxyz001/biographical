/** Local HTTP contract exercise. In-memory data; no authentication or persistence. */
import http from 'node:http';
import { pathToFileURL } from 'node:url';

export function createService() {
  const tickets = new Map();
  let nextId = 1;
  return http.createServer(async (req, res) => {
    function reply(status, data) {
      res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
      res.end(JSON.stringify(data));
    }
    async function body() {
      let size = 0;
      const parts = [];
      for await (const part of req) {
        size += part.length;
        if (size > 8192) throw Object.assign(new Error('body too large'), { status: 413 });
        parts.push(part);
      }
      try {
        const value = JSON.parse(Buffer.concat(parts).toString('utf8'));
        if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error();
        return value;
      } catch { throw Object.assign(new Error('JSON object required'), { status: 400 }); }
    }
    try {
      const url = new URL(req.url, 'http://localhost');
      if (url.pathname === '/api/tickets' && req.method === 'GET') {
        return reply(200, { items: [...tickets.values()] });
      }
      if (url.pathname === '/api/tickets' && req.method === 'POST') {
        const input = await body();
        if (typeof input.title !== 'string' || !input.title.trim() || input.title.trim().length > 120) {
          return reply(422, { code: 'INVALID_TITLE', message: 'title must contain 1..120 characters' });
        }
        const item = { id: nextId++, title: input.title.trim(), status: 'open', version: 1 };
        tickets.set(item.id, item);
        return reply(201, item);
      }
      const match = /^\/api\/tickets\/(\d+)$/.exec(url.pathname);
      if (match && req.method === 'PATCH') {
        const input = await body();
        if (!Number.isSafeInteger(input.version) || !['open', 'done'].includes(input.status)) {
          return reply(422, { code: 'INVALID_UPDATE' });
        }
        const current = tickets.get(Number(match[1]));
        if (!current) return reply(404, { code: 'NOT_FOUND' });
        // No await between comparison and replacement: atomic only in this process.
        if (input.version !== current.version) return reply(409, { code: 'VERSION_CONFLICT', current });
        const updated = { ...current, status: input.status, version: current.version + 1 };
        tickets.set(current.id, updated);
        return reply(200, updated);
      }
      reply(404, { code: 'NOT_FOUND' });
    } catch (error) {
      if (!res.headersSent && !res.destroyed) reply(error.status ?? 500, { code: error.status ? 'BAD_REQUEST' : 'INTERNAL_ERROR' });
    }
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const port = Number(process.env.PORT ?? 3088);
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('invalid PORT');
  createService().listen(port, '127.0.0.1', () => console.log(`API: http://127.0.0.1:${port}/api/tickets`));
}
