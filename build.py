"""Build the translation payload using Python's standard library."""
import json
from pathlib import Path
import shutil
BASE = Path(__file__).resolve().parent

def build():
    output = BASE / 'build'
    output.mkdir(exist_ok=True)
    dictionary = json.loads((BASE / 'src/dictionary.json').read_text(encoding='utf-8'))
    dynamic = [line.split('\t') for line in (BASE / 'src/dynamic.tsv').read_text(encoding='utf-8').splitlines() if line.strip()]
    for name in ('zh-core.js', 'zh-renderer.js', 'zh-main.cjs'):
        source = (BASE / 'src' / name).read_text(encoding='utf-8')
        source = source.replace('__DICTIONARY__', json.dumps(dictionary, ensure_ascii=False))
        source = source.replace('__DYNAMIC__', json.dumps(dynamic, ensure_ascii=False))
        (output / name).write_text(source, encoding='utf-8')
    shutil.copyfile(BASE / 'src/zh-NOTICE.txt', output / 'zh-NOTICE.txt')
    print(f'Built {len(dictionary)} translations')

if __name__ == '__main__':
    build()
