"""Offline behavior checks: no real keys, images, or API requests."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/glm-vision/scripts/vision.py'
spec = importlib.util.spec_from_file_location('vision', SCRIPT)
vision = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vision)


class VisionTests(unittest.TestCase):
    def run_cli(self, responses=(), env=None, extra=()):
        stdout, stderr = io.StringIO(), io.StringIO()
        args = ['vision.py', '--images', 'https://example.invalid/image.png', *extra]
        with patch.dict(os.environ, env or {}, clear=True), patch.object(sys, 'argv', args), \
                patch.object(vision, 'call_api', side_effect=responses) as call, \
                patch.object(vision.time, 'sleep') as sleep, \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                status = vision.main()
            except SystemExit as exc:
                status = exc.code
        return status, stdout.getvalue(), stderr.getvalue(), call, sleep

    def test_missing_credentials_never_calls_api(self):
        status, out, _, call, _ = self.run_cli()
        self.assertEqual(status, 1)
        self.assertEqual(out, '')
        call.assert_not_called()

    def test_rate_limit_switches_model(self):
        status, out, _, call, sleep = self.run_cli([
            (None, {'kind': 'overload', 'message': 'HTTP 429'}),
            ({'choices': [{'message': {'content': 'recognized'}}]}, None),
        ], {'ZHIPU_API_KEY': 'test-only'})
        self.assertEqual((status, out), (0, 'recognized\n'))
        self.assertEqual([c.args[2]['model'] for c in call.call_args_list],
                         ['glm-4.6v-flash', 'glm-4.1v-thinking-flash'])
        sleep.assert_not_called()

    def test_auth_failure_skips_provider(self):
        status, out, _, call, _ = self.run_cli([
            (None, {'kind': 'auth', 'message': 'HTTP 401'}),
            ({'choices': [{'message': {'content': 'fallback'}}]}, None),
        ], {'ZHIPU_API_KEY': 'test-only', 'SILICONFLOW_API_KEY': 'test-only'})
        self.assertEqual((status, out), (0, 'fallback\n'))
        self.assertEqual([c.args[0] for c in call.call_args_list], ['zhipu', 'siliconflow'])

    def test_single_model_retry_is_bounded(self):
        status, out, _, call, sleep = self.run_cli([
            (None, {'kind': 'transient', 'message': 'timeout'}),
            (None, {'kind': 'transient', 'message': 'timeout'}),
        ], {'ZHIPU_API_KEY': 'test-only'}, ['--model', 'zhipu/custom'])
        self.assertEqual((status, out, call.call_count), (1, '', 2))
        sleep.assert_called_once_with(3)

    def test_invalid_local_image_fails_before_api(self):
        with tempfile.TemporaryDirectory() as directory:
            status, _, _, call, _ = self.run_cli(extra=['--images', str(Path(directory) / 'missing.png')])
            self.assertEqual(status, 2)
            call.assert_not_called()

    def test_invalid_provider_and_numeric_arguments(self):
        for args in (['--model', 'unknown/model'], ['--max-tokens', '0'], ['--temperature', 'nan']):
            with self.subTest(args=args):
                status, _, _, call, _ = self.run_cli(extra=args)
                self.assertEqual(status, 2)
                call.assert_not_called()

    def test_timeout_and_invalid_json_are_classified(self):
        with patch.object(vision.urllib.request, 'urlopen', side_effect=TimeoutError()):
            self.assertEqual(vision.call_api('zhipu', 'test-only', {})[1]['kind'], 'transient')
        with patch.object(vision.urllib.request, 'urlopen') as request:
            request.return_value.__enter__.return_value.read.return_value = b'not json'
            self.assertEqual(vision.call_api('zhipu', 'test-only', {})[1]['kind'], 'transient')

    def test_http_diagnostics_do_not_echo_secret_or_response(self):
        secret = 'test-only-sensitive-value'
        error = urllib.error.HTTPError('https://example.invalid', 401, 'bad', {},
                                       io.BytesIO(json.dumps({'error': {'message': secret}}).encode()))
        with patch.object(vision.urllib.request, 'urlopen', side_effect=error):
            _, result = vision.call_api('zhipu', secret, {})
        self.assertEqual(result['kind'], 'auth')
        self.assertNotIn(secret, result['message'])

    def test_local_encoding_and_final_answer_only(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / 'image.png'
            image.write_bytes(b'fake-image')
            self.assertEqual(vision.build_image_part(str(image), 'zhipu')['image_url']['url'], 'ZmFrZS1pbWFnZQ==')
            self.assertTrue(vision.build_image_part(str(image), 'siliconflow')['image_url']['url'].startswith('data:image/png;base64,'))
        self.assertIsNone(vision.extract_text({'choices': [{'message': {'reasoning_content': 'reasoning only'}}]}))
        self.assertIsNone(vision.extract_text({'choices': [{'message': {'content': []}}]}))


if __name__ == '__main__':
    unittest.main()
