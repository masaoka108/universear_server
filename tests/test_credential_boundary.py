import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class CredentialBoundaryTests(unittest.TestCase):
    def test_tracked_files_have_no_private_key_headers_or_containers(self):
        files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        for name in filter(None, files):
            path = ROOT / name
            if not path.is_file():
                continue
            self.assertNotIn(b'PRIVATE KEY' + b'-----', path.read_bytes(), name)
            self.assertFalse(name.endswith(('.pfx', '.p12')), name)

    def test_git_and_docker_exclude_runtime_material(self):
        for name in ['.secret/stunnel/cert.pem', 'stunnel/new.key', 'stunnel/new.pfx', '.env.production']:
            subprocess.run(['git', 'check-ignore', '--no-index', '-q', name], cwd=ROOT, check=True)
        exclusions = (ROOT / '.dockerignore').read_text().splitlines()
        for name in ['.secret', 'for_bit_bucket', 'for_github', '**/*.key', '**/*.pfx']:
            self.assertIn(name, exclusions)

    def test_development_listener_is_local_and_uses_private_material(self):
        config = (ROOT / 'stunnel/dev_https').read_text()
        self.assertIn('cert = .secret/stunnel/cert.pem', config)
        self.assertIn('accept=127.0.0.1:8443', config)
        script = (ROOT / 'runserver').read_text()
        self.assertNotIn('0.0.0.0', script)
        self.assertIn('[ ! -r .secret/stunnel/cert.pem ]', script)

    def test_missing_tls_material_starts_no_processes(self):
        result = subprocess.run(['/bin/sh', './runserver'], cwd=ROOT, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b'Local TLS credentials are missing', result.stderr)

if __name__ == '__main__':
    unittest.main()
