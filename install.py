"""Version-gated installer for unpacked GitHub Desktop 3.6.6 resources.

No downloads, credentials, Git operations, signing changes, or ASAR rewriting.
Always run --check first. Stop GitHub Desktop before install/restore.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent
VERSION = '0.3.0'
APP_VERSION = '3.6.6'
PAYLOAD = ('zh-core.js', 'zh-main.cjs', 'zh-renderer.js', 'zh-NOTICE.txt')
ENTRY = ('main.js', 'index.html')
MANIFEST = 'manifest.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_app(app):
    if not app.is_dir() or app.is_symlink():
        raise ValueError('Expected an unpacked resources/app directory (not app.asar).')
    package = json.loads((app / 'package.json').read_text(encoding='utf-8'))
    if package.get('productName') != 'GitHub Desktop' or package.get('version') != APP_VERSION:
        raise ValueError('Only GitHub Desktop 3.6.6 is supported; refusing to modify this version.')
    if package.get('main') not in ('main.js', './main.js'):
        raise ValueError('Unknown main entry; adaptation is required.')
    for name in (*ENTRY, *PAYLOAD, 'package.json'):
        if (app / name).is_symlink():
            raise ValueError('Symlinked application files are not supported.')
    return package


def ensure_stopped():
    if sys.platform == 'darwin':
        result = subprocess.run(['pgrep', '-x', 'GitHub Desktop'], capture_output=True)
        if result.returncode == 0:
            raise ValueError('Quit GitHub Desktop before continuing.')
        if result.returncode != 1:
            raise ValueError('Could not check running processes.')
    elif sys.platform == 'win32':
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq GitHubDesktop.exe', '/FO', 'CSV', '/NH'], capture_output=True, text=True, check=True)
        if 'githubdesktop.exe' in result.stdout.lower():
            raise ValueError('Quit GitHub Desktop before continuing.')
    else:
        raise ValueError('Installation is supported only on macOS and Windows.')


def prepared(app):
    read_app(app)
    if any((app / name).exists() for name in PAYLOAD):
        raise ValueError('An existing patch was found. Restore it using its own matching backup first.')
    originals = {name: (app / name).read_bytes() for name in ENTRY}
    main = originals['main.js']
    html = originals['index.html'].decode('utf-8')
    if b'zh-main' in main or 'zh-renderer' in html or 'zh-core' in html:
        raise ValueError('An existing patch marker was found.')
    if main.startswith(b'#!') or main.startswith(b'\xef\xbb\xbf'):
        raise ValueError('Unexpected main entry encoding/layout.')
    renderer = re.findall(r'<script\b[^>]*\bsrc=["\']renderer\.js["\'][^>]*>\s*</script>', html, re.I)
    if len(renderer) != 1 or len(re.findall(r'</head\s*>', html, re.I)) != 1:
        raise ValueError('Unknown HTML layout; refusing to inject scripts.')
    if not re.search(r'\bdefer\b', renderer[0], re.I) or re.search(r'\basync\b|\btype\s*=', renderer[0], re.I):
        raise ValueError('Unsupported renderer loading order.')
    if re.search(r'content-security-policy', html, re.I):
        raise ValueError('HTML has a CSP that needs manual compatibility review; it will not be disabled.')
    suffix = '<script defer src="zh-core.js"></script><script defer src="zh-renderer.js"></script>'
    modified = {'main.js': b"require('./zh-main.cjs'); // desktop-local-zh v0.3.0\n" + main,
                'index.html': html.replace(renderer[0], renderer[0] + suffix).encode('utf-8')}
    for name in PAYLOAD:
        modified[name] = (BASE / 'build' / name).read_bytes()
    return originals, modified


def save(path, data):
    # Preserve the existing mode and replace each file atomically.
    temp = path.with_name(path.name + '.zh-tmp')
    if temp.exists():
        raise ValueError(f'Temporary file already exists: {temp}')
    try:
        with temp.open('xb') as handle:
            handle.write(data)
        if path.exists():
            shutil.copymode(path, temp)
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def validate_backup_path(app, backup):
    if backup == app or app in backup.parents or backup in app.parents:
        raise ValueError('Backup must be outside the application directory and not its ancestor.')


def install(app, backup):
    originals, modified = prepared(app)
    validate_backup_path(app, backup)
    backup.mkdir(parents=True, exist_ok=False)
    for name, data in originals.items():
        (backup / name).write_bytes(data)
    metadata = {'pluginVersion': VERSION, 'appVersion': APP_VERSION, 'appPath': str(app),
                'packageHash': digest((app / 'package.json').read_bytes()),
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'original': {name: digest(data) for name, data in originals.items()},
                'patched': {name: digest(data) for name, data in modified.items()}}
    (backup / MANIFEST).write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    changed = []
    try:
        # Recheck all inputs immediately before any mutation.
        for name, data in originals.items():
            if (app / name).read_bytes() != data:
                raise ValueError('Application changed while preparing the patch.')
        if any((app / name).exists() for name in PAYLOAD):
            raise ValueError('Application payload changed while preparing the patch.')
        for name, data in modified.items():
            save(app / name, data)
            changed.append(name)
    except Exception:
        for name in reversed(changed):
            if name in originals:
                save(app / name, originals[name])
            else:
                (app / name).unlink()
        raise
    print(f'Installed {VERSION}. Keep the private rollback backup: {backup}')


def restore(app, backup):
    read_app(app)
    validate_backup_path(app, backup)
    manifest = json.loads((backup / MANIFEST).read_text(encoding='utf-8'))
    if manifest.get('appPath') != str(app) or manifest.get('pluginVersion') != VERSION:
        raise ValueError('Backup belongs to another application path or patch version.')
    if set(manifest.get('original', {})) != set(ENTRY) or set(manifest.get('patched', {})) != set((*ENTRY, *PAYLOAD)):
        raise ValueError('Invalid backup manifest.')
    if digest((app / 'package.json').read_bytes()) != manifest['packageHash']:
        raise ValueError('Application package changed; refusing stale rollback.')
    for name, expected in manifest['patched'].items():
        if digest((app / name).read_bytes()) != expected:
            raise ValueError(f'Application file changed: {name}; refusing stale rollback.')
    originals = {name: (backup / name).read_bytes() for name in ENTRY}
    for name, data in originals.items():
        if digest(data) != manifest['original'][name]:
            raise ValueError('Backup integrity check failed.')
    patched = {name: (app / name).read_bytes() for name in (*ENTRY, *PAYLOAD)}
    changed = []
    try:
        for name, data in originals.items():
            save(app / name, data)
            changed.append(name)
        for name in PAYLOAD:
            (app / name).unlink()
            changed.append(name)
    except Exception:
        for name in reversed(changed):
            save(app / name, patched[name])
        raise
    print('Restored original English entry files. Backup retained.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'install', 'restore'])
    parser.add_argument('--app-dir', type=Path, required=True, help='Exact unpacked resources/app directory')
    parser.add_argument('--backup-dir', type=Path, help='New directory outside the app; required for install and restore')
    args = parser.parse_args()
    app = args.app_dir.expanduser().resolve()
    try:
        if args.action == 'check':
            prepared(app)
            print('Compatible unpatched 3.6.6 layout. No files changed.')
        else:
            if args.backup_dir is None:
                parser.error('--backup-dir is required')
            ensure_stopped()
            backup = args.backup_dir.expanduser().resolve()
            (install if args.action == 'install' else restore)(app, backup)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
