"""Build platform ZIPs from an explicit allowlist; never include local backups."""
import hashlib
from pathlib import Path
import subprocess
import sys
import zipfile

BASE = Path(__file__).resolve().parents[1]
VERSION = '0.3.0'
subprocess.run([sys.executable, str(BASE / 'build.py')], check=True)
files = [BASE / name for name in ('README.md','LICENSE','CONTRIBUTING.md','CHANGELOG.md','build.py','install.py','package.json','package-lock.json')]
for folder in ('src','build','docs','licenses','tests','scripts'):
    files.extend(p for p in (BASE / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
files = sorted(files)
dest = BASE / 'dist'
dest.mkdir(exist_ok=True)
checks = []
for platform, doc in [('macOS','macos.md'), ('Windows','windows.md')]:
    target = dest / f'GitHub-Desktop-Chinese-{platform}-{VERSION}.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(BASE).as_posix()
            info = zipfile.ZipInfo(f'GitHub-Desktop-Chinese-{VERSION}/{relative}',(2026,9,27,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info,path.read_bytes())
        info = zipfile.ZipInfo(f'GitHub-Desktop-Chinese-{VERSION}/START-HERE.txt',(2026,9,27,0,0,0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info,f'{platform}: 请先阅读 docs/{doc}\n本包包含源码与构建文件，需要 Python 3.9+。Windows 尚未实机验证。\n'.encode('utf-8'))
    checks.append(f'{hashlib.sha256(target.read_bytes()).hexdigest()}  {target.name}')
(dest / 'SHA256SUMS.txt').write_text('\n'.join(checks)+'\n',encoding='utf-8')
print('\n'.join(checks))
