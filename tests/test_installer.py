"""Isolated fixtures only: never modifies the installed application."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('installer', Path(__file__).resolve().parents[1] / 'install.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.app = self.root / 'app'
        self.app.mkdir()
        (self.app / 'package.json').write_text(json.dumps({'productName':'GitHub Desktop','version':'3.6.6','main':'./main.js'}))
        (self.app / 'main.js').write_bytes(b'console.log("original");\n')
        (self.app / 'index.html').write_bytes(b'<html><head><script defer="defer" src="renderer.js"></script></head></html>')
        self.original = {p.name:p.read_bytes() for p in self.app.iterdir()}
        self.backup = self.root / 'backup'

    def snapshot(self):
        return {p.name:p.read_bytes() for p in self.app.iterdir()}

    def test_round_trip(self):
        m.install(self.app, self.backup)
        main = (self.app/'main.js').read_bytes()
        self.assertTrue(main.endswith(self.original['main.js']))
        html=(self.app/'index.html').read_text()
        self.assertLess(html.index('renderer.js'),html.index('zh-core.js'))
        self.assertLess(html.index('zh-core.js'),html.index('zh-renderer.js'))
        with self.assertRaises(ValueError): m.prepared(self.app)
        m.restore(self.app, self.backup)
        self.assertEqual(self.snapshot(),self.original)

    def test_update_and_tamper_refusal(self):
        m.install(self.app, self.backup)
        (self.app/'main.js').write_text('new upstream content')
        before=self.snapshot()
        with self.assertRaises(ValueError): m.restore(self.app,self.backup)
        self.assertEqual(before,self.snapshot())

    def test_bad_backup_refusal(self):
        m.install(self.app,self.backup)
        (self.backup/'main.js').write_text('corrupted')
        before=self.snapshot()
        with self.assertRaises(ValueError): m.restore(self.app,self.backup)
        self.assertEqual(before,self.snapshot())

    def test_wrong_version_refusal(self):
        (self.app/'package.json').write_text(json.dumps({'productName':'GitHub Desktop','version':'9.9.9','main':'./main.js'}))
        before=self.snapshot()
        with self.assertRaises(ValueError): m.install(self.app,self.backup)
        self.assertEqual(before,self.snapshot())
        self.assertFalse(self.backup.exists())

    def test_partial_install_rolls_back(self):
        original_save=m.save
        def broken_save(path,data):
            if path.name=='zh-core.js': raise OSError('simulated write failure')
            original_save(path,data)
        with patch.object(m,'save',side_effect=broken_save):
            with self.assertRaises(OSError): m.install(self.app,self.backup)
        self.assertEqual(self.original,self.snapshot())

    def test_partial_restore_rolls_back(self):
        m.install(self.app,self.backup)
        before=self.snapshot()
        original_save=m.save
        def broken_once(path,data):
            if path.name=='index.html' and data==self.original['index.html']:
                raise OSError('simulated write failure')
            original_save(path,data)
        with patch.object(m,'save',side_effect=broken_once):
            with self.assertRaises(OSError): m.restore(self.app,self.backup)
        self.assertEqual(before,self.snapshot())

    def test_unknown_layout_and_nested_backup_refusal(self):
        with self.assertRaises(ValueError): m.install(self.app,self.app/'backup')
        (self.app/'index.html').write_text('<head><script async src="renderer.js"></script></head>')
        with self.assertRaises(ValueError): m.prepared(self.app)

if __name__=='__main__': unittest.main()
