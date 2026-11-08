"""Portable teaching model: bounded SQLite outbox + idempotent receiver.

No actual MQTT, hardware access, OTA writing, or power-loss guarantees.
Run --help for the collect/flush/status workflow.
"""
import argparse
import json
import math
import pathlib
import sqlite3
import time
import uuid


class Outbox:
    def __init__(self, path, capacity=100):
        if type(capacity) is not int or capacity < 1:
            raise ValueError('capacity must be a positive integer')
        self.capacity = capacity
        self.db = sqlite3.connect(path, timeout=5)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('''CREATE TABLE IF NOT EXISTS outbox (
            id TEXT PRIMARY KEY, payload TEXT NOT NULL)''')
        self.db.commit()

    def close(self):
        self.db.close()

    def add(self, device, sequence, temperature, session):
        if not isinstance(device, str) or not 1 <= len(device) <= 64:
            raise ValueError('device length must be 1..64')
        if type(sequence) is not int or sequence < 0:
            raise ValueError('sequence must be a nonnegative integer')
        if not isinstance(session, str) or not 1 <= len(session) <= 64:
            raise ValueError('session length must be 1..64')
        if type(temperature) not in (int, float) or not math.isfinite(temperature) or not -100 <= temperature <= 200:
            raise ValueError('invalid temperature')
        key = json.dumps([device, session, sequence], separators=(',', ':'))
        payload = json.dumps(dict(schema=1, id=key, device=device, session=session,
                                  sequence=sequence, temperature=temperature,
                                  observed_unix_ms=time.time_ns()//1000000),
                             separators=(',', ':'), allow_nan=False)
        try:
            # Serializes capacity check + insertion, even across writer connections.
            self.db.execute('BEGIN IMMEDIATE')
            if self.db.execute('SELECT 1 FROM outbox WHERE id=?', (key,)).fetchone():
                self.db.rollback()
                return 'duplicate'
            if self.db.execute('SELECT COUNT(*) FROM outbox').fetchone()[0] >= self.capacity:
                self.db.rollback()
                return 'full'
            self.db.execute('INSERT INTO outbox VALUES (?,?)', (key, payload))
            self.db.commit()
            return 'accepted'
        except BaseException:
            self.db.rollback()
            raise

    def pending(self):
        return self.db.execute('SELECT COUNT(*) FROM outbox').fetchone()[0]

    def batch(self, limit=20):
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError('limit must be 1..1000')
        return self.db.execute('SELECT id,payload FROM outbox ORDER BY rowid LIMIT ?', (limit,)).fetchall()

    def ack(self, key):
        with self.db:
            self.db.execute('DELETE FROM outbox WHERE id=?', (key,))


class Receiver:
    """A second database models the remote service, not an MQTT broker."""
    def __init__(self, path):
        self.db = sqlite3.connect(path, timeout=5)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS received (id TEXT PRIMARY KEY,payload TEXT NOT NULL)')
        self.db.commit()

    def close(self):
        self.db.close()

    def accept(self, key, payload):
        with self.db:
            old = self.db.execute('SELECT payload FROM received WHERE id=?', (key,)).fetchone()
            if old:
                if old[0] != payload:
                    raise ValueError('id reused for different payload')
                return False
            self.db.execute('INSERT INTO received VALUES (?,?)', (key, payload))
            return True

    def count(self):
        return self.db.execute('SELECT COUNT(*) FROM received').fetchone()[0]


def flush(outbox, receiver, limit=20, fail_after_receive=False):
    acknowledged = 0
    for key, payload in outbox.batch(limit):
        receiver.accept(key, payload)
        if fail_after_receive:
            # Real process termination is tested separately through the CLI state.
            raise RuntimeError('simulated failure after receiver commit, before local ack')
        outbox.ack(key)
        acknowledged += 1
    return acknowledged


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', default='edge.db')
    parser.add_argument('--remote', default='receiver.db')
    parser.add_argument('--capacity', type=int, default=100)
    parser.add_argument('command', choices=['collect', 'flush', 'status'])
    parser.add_argument('--count', type=int, default=5)
    parser.add_argument('--fail-after-receive', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.count <= 1000:
        parser.error('--count must be 1..1000')
    outbox = Outbox(pathlib.Path(args.db), args.capacity)
    receiver = None
    try:
        if args.command == 'collect':
            session = uuid.uuid4().hex
            counts = {'accepted': 0, 'full': 0, 'duplicate': 0}
            for seq in range(args.count):
                result = outbox.add('sensor-01', seq, 20 + seq % 10, session)
                counts[result] += 1
            print(json.dumps(counts))
        elif args.command == 'flush':
            receiver = Receiver(args.remote)
            print(json.dumps({'acked': flush(outbox, receiver, args.count, args.fail_after_receive),
                              'remote_unique': receiver.count()}))
        print(json.dumps({'pending': outbox.pending()}))
    finally:
        if receiver is not None:
            receiver.close()
        outbox.close()


if __name__ == '__main__':
    main()
