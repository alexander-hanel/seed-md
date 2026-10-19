"""Check independent acceptance assertions using small, intentionally altered SQL data."""
import importlib.util,json,sqlite3,unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / 'seed'
spec=importlib.util.spec_from_file_location('reference',PACKAGE/'acceptance/reference.py')
reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)

def relationship_db():
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    db.executescript((PACKAGE/'contracts/schema.sql').read_text())
    db.execute("INSERT INTO corpora VALUES(1,'classic','samples','inputs/samples',NULL,'{}')")
    db.execute("INSERT INTO source_files VALUES(1,1,'scoped.cpp','test','utf-8',X'','complete')")
    names=['Left::Probe','Right::Probe','ReceiverA::Read','ReceiverB::Read','ISeedDevice::Read','FieldOnly::Probe','Shadowed']
    ids={name:i+1 for i,name in enumerate(names)}
    for name,did in ids.items():
        kind='field' if name=='FieldOnly::Probe' else 'method' if name.endswith('::Read') else 'function'
        db.execute('INSERT INTO declarations VALUES(?,1,?,?,?,?,?,1,1,0,1,?,\'{}\',\'[]\',\'test\',\'supported\')',
                   (did,name.split('::')[-1],name,name.casefold(),kind,'cpp','x'))
    cases=json.loads((PACKAGE/'acceptance/relationship-cases.json').read_text())['cases']
    for case in cases:
        sid=case['line'];db.execute('INSERT INTO candidate_sets VALUES(?,?)',(sid,'test-set-'+str(sid)))
        for name in case['targets']:
            db.execute("INSERT INTO candidate_declarations VALUES(?,?,'normalized_name')",(sid,ids[name]))
        db.execute('INSERT INTO usages VALUES(?,1,NULL,?,?,\'call\',?,1,\'[]\',?,?,?)',
                   (sid,case['name'],case.get('qualified_name'),sid,case.get('status','candidate'),json.dumps({'shadowed':case.get('shadowed',False)}),sid))
    return db,ids

class ReferenceContract(unittest.TestCase):
    def test_all_reference_values_have_source_material(self):
        self.assertEqual(reference.verify_assets(),7)

    def test_qualified_receiver_and_shadowing_baseline(self):
        db,_=relationship_db();self.assertEqual(reference.check_relationships(db),[])

    def test_qualified_name_does_not_expand_to_other_namespace(self):
        db,ids=relationship_db();db.execute("INSERT INTO candidate_declarations VALUES(2,?,'normalized_name')",(ids['Right::Probe'],))
        self.assertTrue(any(f['line']==2 and f['rule']=='eligible targets' for f in reference.check_relationships(db)))

    def test_known_receiver_rejects_other_type(self):
        db,ids=relationship_db();db.execute("INSERT INTO candidate_declarations VALUES(3,?,'normalized_name')",(ids['ReceiverB::Read'],))
        self.assertTrue(any(f['line']==3 for f in reference.check_relationships(db)))

    def test_shadowed_name_has_no_external_target(self):
        db,ids=relationship_db();db.execute("INSERT INTO candidate_declarations VALUES(7,?,'normalized_name')",(ids['Shadowed'],))
        self.assertTrue(any(f['line']==7 for f in reference.check_relationships(db)))

    def test_unknown_receiver_does_not_drop_alternatives(self):
        db,ids=relationship_db();db.execute('DELETE FROM candidate_declarations WHERE set_id=9 AND declaration_id=?',(ids['ReceiverB::Read'],))
        self.assertTrue(any(f['line']==9 for f in reference.check_relationships(db)))

    def test_calls_do_not_target_fields(self):
        db,ids=relationship_db();db.execute("INSERT INTO candidate_declarations VALUES(10,?,'normalized_name')",(ids['FieldOnly::Probe'],))
        self.assertTrue(any(f['line']==10 for f in reference.check_relationships(db)))

if __name__=='__main__':unittest.main()
