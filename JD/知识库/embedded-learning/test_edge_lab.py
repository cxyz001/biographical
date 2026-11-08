import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from edge_lab import Outbox, Receiver, flush


class ReliabilityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.local = self.root/'local.db'
        self.remote = self.root/'remote.db'
        self.box = Outbox(self.local, capacity=2)
        self.receiver = Receiver(self.remote)

    def tearDown(self):
        self.box.close()
        self.receiver.close()
        self.tmp.cleanup()

    def add(self, seq=0):
        return self.box.add('sensor', seq, 23.5, 'boot-1')

    def test_capacity_rejection_and_reuse(self):
        self.assertEqual(self.add(0), 'accepted')
        self.assertEqual(self.add(1), 'accepted')
        self.assertEqual(self.add(2), 'full')
        flush(self.box, self.receiver)
        self.assertEqual(self.add(2), 'accepted')

    def test_duplicate_and_restart_session(self):
        self.add()
        self.assertEqual(self.add(), 'duplicate')
        self.assertEqual(self.box.add('sensor', 0, 24, 'boot-2'), 'accepted')
        self.assertEqual(self.box.pending(), 2)

    def test_validation(self):
        for temperature in [float('nan'), float('inf'), -101, 201, True, 'bad']:
            with self.assertRaises(ValueError):
                self.box.add('sensor', 0, temperature, 'boot-1')
        with self.assertRaises(ValueError): self.box.add('', 0, 20, 'boot-1')
        with self.assertRaises(ValueError): self.box.add('sensor', -1, 20, 'boot-1')
        with self.assertRaises(ValueError): self.box.batch(0)
        with self.assertRaises(ValueError): Outbox(self.root/'invalid.db', 0)
        self.assertEqual(self.box.pending(), 0)

    def test_reopen_retains_pending(self):
        self.add()
        self.box.close()
        self.box = Outbox(self.local, capacity=2)
        self.assertEqual(self.box.pending(), 1)
        self.assertEqual(flush(self.box, self.receiver), 1)
        self.assertEqual(self.receiver.count(), 1)

    def test_receive_before_ack_failure_and_retry(self):
        self.add()
        with self.assertRaises(RuntimeError): flush(self.box, self.receiver, fail_after_receive=True)
        self.assertEqual(self.receiver.count(), 1)
        self.assertEqual(self.box.pending(), 1)
        self.assertEqual(flush(self.box, self.receiver), 1)
        self.assertEqual(self.receiver.count(), 1)
        self.assertEqual(self.box.pending(), 0)

    def test_conflicting_payload_does_not_ack(self):
        self.add()
        key, payload = self.box.batch()[0]
        self.receiver.accept(key, payload+' ')
        with self.assertRaises(ValueError): flush(self.box, self.receiver)
        self.assertEqual(self.box.pending(), 1)

    def test_cli_failed_process_then_new_process_recovery(self):
        self.add()
        cmd = [sys.executable, str(pathlib.Path(__file__).with_name('edge_lab.py')),
               '--db', str(self.local), '--remote', str(self.remote), 'flush']
        failed = subprocess.run(cmd+['--fail-after-receive'], capture_output=True, text=True, timeout=10)
        self.assertNotEqual(failed.returncode, 0)
        recovered = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        lines = [json.loads(x) for x in recovered.stdout.splitlines()]
        self.assertEqual(lines[0]['remote_unique'], 1)
        self.assertEqual(lines[1]['pending'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
