"""Offline authoring checks for the WinAPIDB draft package."""
from pathlib import Path
import re
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parents[1] / 'seed'


class PackageContract(unittest.TestCase):
    def test_schema_and_dictionary(self):
        db=sqlite3.connect(':memory:');sql=(PACKAGE/'contracts/schema.sql').read_text();db.executescript(sql)
        text=(PACKAGE/'contracts/data-dictionary.md').read_text()
        names=re.findall(r'CREATE (?:VIRTUAL )?(?:TABLE|VIEW)\s+(\w+)',sql,re.I)
        for name in names:
            section=text.split(f'## `{name}`\n',1)[1].split('\n## ',1)[0]
            self.assertEqual([r[1] for r in db.execute(f'pragma table_info({name})')],re.findall(r'^\| `([^`]+)` \|',section,re.M),name)
        self.assertEqual(db.execute("select type from sqlite_master where name='usage_declarations'").fetchone()[0],'view')
        db.execute("insert into corpora values(1,'h','headers','inputs/h',NULL,'{}')")
        db.execute("insert into source_files values(1,1,'x.h','digest','utf-8',X'','complete')")
        db.execute("insert into candidate_sets values(1,'example-set-signature')")
        for i in range(128):
            db.execute("insert into declarations values(?,1,'Shared','Shared','shared','function','cpp',1,1,0,1,'x','{}','[]','fixture','supported')",(i+1,))
            db.execute("insert into candidate_declarations values(1,?,'normalized_name')",(i+1,))
            db.execute("insert into usages values(?,1,NULL,'Shared',NULL,'text_reference',1,1,'[]','textual','{}',1)",(i+1,))
        self.assertEqual(db.execute('select count(*) from usage_declarations').fetchone()[0],16384)
        self.assertEqual(db.execute('select count(*) from candidate_declarations').fetchone()[0],128)
        self.assertFalse(db.execute('pragma foreign_key_check').fetchall())

    def test_bundled_runner_matches(self):
        self.assertEqual((PACKAGE/'acceptance/bounded.py').read_bytes(),(ROOT/'scripts/run_bounded.py').read_bytes())

if __name__ == '__main__': unittest.main()
