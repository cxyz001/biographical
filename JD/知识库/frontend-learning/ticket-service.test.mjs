import { test } from 'node:test';
import assert from 'node:assert/strict';
import { once } from 'node:events';
import { createService } from './ticket-service.mjs';

async function fixture(t) {
  const server = createService();
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  t.after(() => new Promise(resolve => { server.close(resolve); server.closeAllConnections(); }));
  const base = `http://127.0.0.1:${server.address().port}`;
  return async (path, method = 'GET', value) => {
    const response = await fetch(base + path, { method, headers: { 'Content-Type': 'application/json' },
      body: value === undefined ? undefined : JSON.stringify(value) });
    return { status: response.status, value: await response.json() };
  };
}

test('create, list and update follow the public HTTP contract', async t => {
  const call = await fixture(t);
  const created = await call('/api/tickets', 'POST', { title: '  Repair pump  ' });
  assert.equal(created.status, 201);
  assert.deepEqual(created.value, { id: 1, title: 'Repair pump', status: 'open', version: 1 });
  assert.equal((await call('/api/tickets')).value.items.length, 1);
  const updated = await call('/api/tickets/1', 'PATCH', { version: 1, status: 'done' });
  assert.equal(updated.value.version, 2);
  assert.equal(updated.value.status, 'done');
});

test('concurrent updates with the same version cannot silently overwrite', async t => {
  const call = await fixture(t);
  await call('/api/tickets', 'POST', { title: 'one' });
  const results = await Promise.all(['done', 'open'].map(status => call('/api/tickets/1', 'PATCH', { version: 1, status })));
  assert.deepEqual(results.map(x => x.status).sort(), [200, 409]);
  assert.equal((await call('/api/tickets')).value.items[0].version, 2);
});

test('untrusted input cannot set IDs, versions or arbitrary statuses', async t => {
  const call = await fixture(t);
  for (const title of ['', ' ', 42, 'x'.repeat(121)]) {
    assert.equal((await call('/api/tickets', 'POST', { title })).status, 422);
  }
  const item = await call('/api/tickets', 'POST', { title: 'valid', id: 99, version: 9 });
  assert.equal(item.value.id, 1);
  assert.equal(item.value.version, 1);
  assert.equal((await call('/api/tickets/1', 'PATCH', { version: 1, status: 'admin' })).status, 422);
});

test('body limit and missing resources produce controlled errors', async t => {
  const call = await fixture(t);
  assert.equal((await call('/api/tickets', 'POST', { title: 'x'.repeat(9000) })).status, 413);
  assert.equal((await call('/api/tickets', 'POST', [])).status, 400);
  assert.equal((await call('/api/tickets/99', 'PATCH', { version: 1, status: 'done' })).status, 404);
  assert.equal((await call('/missing')).status, 404);
});
