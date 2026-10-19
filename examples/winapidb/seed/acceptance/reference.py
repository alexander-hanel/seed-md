"""Independent source-backed acceptance checks; no reference implementation imports."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def load_cases():
    return json.loads((HERE/'reference-cases.json').read_text())['cases']

def verify_assets():
    fixtures=json.loads((HERE/'fixtures.json').read_text())
    for case in load_cases():
        for kind,hash_key in (('document','source_sha256'),('declaration','fixture_sha256')):
            source=case[kind];value=fixtures['files'][source['fixture_input']]
            raw=bytes.fromhex(value['hex']) if isinstance(value,dict) else value.encode()
            assert hashlib.sha256(raw).hexdigest()==source[hash_key], 'Changed reference source: '+case['name']
            text=raw.decode('utf-16') if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else raw.decode('utf-8-sig')
            if kind=='document':
                for field,value in source['expected'].items():
                    assert value is None or value in text, 'Unbacked field: '+field
                for member in source['parameters']:
                    assert member['source_heading'] in text, 'Unbacked member'
            else:assert source['signature'] in text, 'Unbacked declaration'
    contract=json.loads((HERE/'reference-cases.json').read_text())
    for notice in contract['notices']:
        content=fixtures['files'][notice['fixture_input']]
        raw=bytes.fromhex(content['hex']) if isinstance(content,dict) else content.encode()
        assert hashlib.sha256(raw).hexdigest()==notice['sha256'], 'Changed upstream notice'
    relationships=json.loads((HERE/'relationship-cases.json').read_text())
    lines=fixtures['files'][relationships['source']].splitlines()
    for case in relationships['cases']:
        assert case['name'] in lines[case['line']-1], 'Relationship case has no source occurrence'
    return len(load_cases())

def check_database(db, profile='fixtures', position_base=1, relationships=True):
    failures=[]
    def require(value,name,rule,detail):
        if not value:failures.append({'case':name,'rule':rule,'detail':detail})
    for case in load_cases():
        name=case['name'];doc=case['document'];decl=case['declaration']
        path=doc['fixture_source_path'] if profile=='fixtures' else doc['full_source_path']
        row=db.execute('SELECT * FROM documents WHERE source_path=?',(path,)).fetchone()
        require(row is not None,name,'document','Required source document missing')
        if row is not None:
            for field,expected in doc['expected'].items():
                require(row[field]==expected,name,'field:'+field,{'expected':expected,'actual':row[field]})
            members=list(db.execute("SELECT name,direction,optional,declared_type,position FROM members WHERE document_id=? AND kind='parameter' ORDER BY position,id",(row['id'],)))
            require([m['name'] for m in members]==[m['name'] for m in doc['parameters']],name,'parameter_order','Documented parameters missing/reordered')
            for actual,expected in zip(members,doc['parameters']):
                for field in ('direction','optional','declared_type','position'):
                    value=expected[field] if field!='position' else expected[field]-1+position_base
                    require(actual[field]==value,name,'parameter:'+expected['name']+'.'+field,{'expected':value,'actual':actual[field]})
        corpus=decl['fixture_corpus'] if profile=='fixtures' else decl['full_corpus']
        file_path=decl['fixture_path'] if profile=='fixtures' else decl['source_path']
        candidates=[]
        # Resolve the source by its primary key after indexed symbol lookup. This
        # avoids scanning entire corpora and works with arbitrary index names.
        for declaration in db.execute('SELECT * FROM declarations WHERE normalized_name=?',(name.casefold(),)):
            source=db.execute('SELECT path,sha256,corpus_id FROM source_files WHERE id=?',(declaration['file_id'],)).fetchone()
            if source is None:continue
            key=db.execute('SELECT key FROM corpora WHERE id=?',(source['corpus_id'],)).fetchone()[0]
            if key==corpus and source['path']==file_path:
                candidates.append({**dict(declaration),'sha256':source['sha256']})
        matching=[d for d in candidates if d['signature']==decl['signature'] and d['kind']==decl['kind']]
        require(bool(matching),name,'declaration','Required source-backed function signature missing or altered')
        expected_hash=decl['fixture_sha256'] if profile=='fixtures' else decl['source_sha256']
        for d in matching:
            require(d['sha256']==expected_hash,name,'header_identity','Pinned header/excerpt bytes differ; inspect acquisition identity')
        if relationships and row is not None and matching:
            require(any(db.execute('SELECT 1 FROM document_declarations WHERE document_id=? AND declaration_id=?',(row['id'],d['id'])).fetchone() for d in matching),name,'document_declaration','Required document/declaration relationship missing')
    return failures

def check_queries(query, profile='fixtures'):
    """query has the supplied Suite.query interface; expected data never comes from results."""
    failures=[]
    for case in load_cases():
        name=case['name'];doc=case['document'];decl=case['declaration']
        selector=doc['fixture_source_path'] if profile=='fixtures' else doc['full_source_path']
        corpus=decl['fixture_corpus'] if profile=='fixtures' else decl['full_corpus']
        def require(ok,rule):
            if not ok:failures.append({'case':name,'rule':rule})
        bundle=query('get',selector)
        require(bundle['primary_name']==name and bundle['header']==doc['expected']['header'],'get identity')
        lookup=query('lookup',name)
        require(any(d['source_path']==selector and d['primary_name']==name for d in lookup['documents']),'lookup exact document')
        declarations=query('declarations',name,['--corpus',corpus])
        require(any(d['signature']==decl['signature'] for d in declarations),'declarations source signature')
        arguments=query('arguments',selector)
        require([a['name'] for a in arguments]==[a['name'] for a in doc['parameters']],'arguments order')
        for actual,expected in zip(arguments,doc['parameters']):
            require(all(actual[k]==expected[k] for k in ('direction','optional','declared_type')),'arguments source attributes')
    return failures


def check_relationships(db):
    contract=json.loads((HERE/'relationship-cases.json').read_text());failures=[]
    for case in contract['cases']:
        rows=list(db.execute('''SELECT u.* FROM usages u JOIN source_files f ON f.id=u.file_id
            JOIN corpora c ON c.id=f.corpus_id WHERE c.key=? AND f.path=? AND u.line=? AND u.kind=?''',
            (contract['corpus'],contract['path'],case['line'],contract['kind'])))
        if len(rows)!=1:
            failures.append({'line':case['line'],'rule':'one observed call','actual_count':len(rows)});continue
        row=rows[0]
        for field in ('name','qualified_name','status'):
            if field in case and row[field]!=case[field]:failures.append({'line':case['line'],'rule':field})
        targets=[r[0] for r in db.execute('SELECT d.qualified_name FROM usage_declarations u JOIN declarations d ON d.id=u.declaration_id WHERE u.usage_id=?',(row['id'],))]
        if sorted(targets)!=sorted(case['targets']):failures.append({'line':case['line'],'rule':'eligible targets','expected':case['targets'],'actual':targets})
        if case.get('shadowed'):
            if not json.loads(row['evidence_json']).get('shadowed'):failures.append({'line':case['line'],'rule':'shadowing evidence'})
            if db.execute('SELECT 1 FROM usage_documents WHERE usage_id=?',(row['id'],)).fetchone():failures.append({'line':case['line'],'rule':'shadowed external document target'})
    return failures
