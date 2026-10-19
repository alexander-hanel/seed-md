#!/usr/bin/env python3
"""Author small source-backed acceptance assets from an explicitly supplied reference DB.
This is an authoring tool, not part of project construction or a database importer.
"""
import argparse,hashlib,json,re,sqlite3,html
import yaml  # Authoring dependency only; distributed acceptance uses stdlib.
from pathlib import Path

NAMES=('CreateFileA','CreateFileW','ReadFile','ReadFileEx','DeviceIoControl','IoCreateDevice','IoDeleteDevice')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def decode(raw):
    return raw.decode('utf-16') if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else raw.decode('utf-8-sig')
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--database',type=Path,required=True);parser.add_argument('--package',type=Path,required=True);parser.add_argument('--notices-root',type=Path,required=True);a=parser.parse_args()
    db=sqlite3.connect(a.database.resolve().as_uri()+'?mode=ro');db.row_factory=sqlite3.Row
    fixtures=json.loads((a.package/'acceptance/fixtures.json').read_text());cases=[];notices=[]
    for name in NAMES:
        doc=db.execute('SELECT d.*,f.raw,c.key AS corpus,c.revision FROM documents d JOIN source_files f ON f.id=d.file_id JOIN corpora c ON c.id=d.corpus_id WHERE d.id IN (SELECT document_id FROM aliases WHERE normalized_name=lower(?)) AND d.primary_name=? AND d.source_path LIKE ?',(name,name,('ddi/' if name.startswith('Io') else 'sdk/')+'%')).fetchone()
        if doc is None:raise ValueError('Reference document missing: '+name)
        raw=doc['raw'];text=decode(raw);assert sha(raw)==doc['source_sha256']
        corpus=doc['corpus'];relative=doc['source_path'].split('/',1)[1];fixture_corpus='reference-'+corpus
        doc_path=fixture_corpus+'/content/'+relative
        fixtures['files'][doc_path]={'hex':raw.hex()} # Exact original bytes, including line endings.
        front=re.match(r'\A---\r?\n(.*?)\r?\n(?:---|\.\.\.)(?:\r?\n|$)',text,re.S)
        assert front is not None
        metadata=yaml.safe_load(front[1])
        mapping={'uid':'UID','title':'title','header':'req.header','dll':'req.dll','library':'req.lib'}
        def scalar(value):
            if value is None or value=='':return None
            return json.dumps(value) if isinstance(value,list) else str(value)
        fields={field:scalar(metadata.get(key)) for field,key in mapping.items()}
        assert name in metadata['api_name'] and fields['uid'].split(':',1)[1].split('.',1)[1]==name
        fields['primary_name']=name
        for key,value in fields.items():assert doc[key]==value,(name,key,'reference field disagrees with source')
        members=[]
        for row in db.execute("SELECT m.*,s.heading,s.markdown FROM members m JOIN sections s ON s.id=m.section_id WHERE m.document_id=? AND m.kind='parameter' ORDER BY m.position",(doc['id'],)):
            assert row['heading'] in text and row['name'] in row['heading']
            flags=re.search(r'\[([^]]+)\]',row['heading']);flags=[x.strip().lower() for x in flags[1].split(',')] if flags else []
            direction=','.join(x for x in ('in','out') if x in flags) or None
            optional=1 if 'optional' in flags else 0 if 'required' in flags else None
            assert row['direction']==direction and row['optional']==optional
            explicit_type=re.search(r'^\s*Type:\s*(.+)$',row['markdown'],re.M|re.I)
            source_type=html.unescape(re.sub(r'<[^>]*>','',explicit_type[1])).strip().strip('`') if explicit_type else None
            assert row['declared_type']==source_type
            members.append({'name':row['name'],'direction':direction,'optional':optional,'declared_type':row['declared_type'],
                            'position':len(members)+1,'source_heading':row['heading']})
        decl=db.execute('SELECT d.*,f.raw,f.path,f.sha256,c.key AS corpus FROM declarations d JOIN source_files f ON f.id=d.file_id JOIN corpora c ON c.id=f.corpus_id WHERE d.normalized_name=lower(?) AND d.kind=\'function\' ORDER BY d.id LIMIT 1',(name,)).fetchone()
        assert decl is not None
        source=decode(decl['raw']).encode('utf-8');signature=decl['signature'];assert sha(decl['raw'])==decl['sha256']
        assert source[decl['byte_start']:decl['byte_end']].decode('utf-8')==signature
        # Preserve the upstream header's leading copyright comment alongside the excerpt.
        prefix=decode(decl['raw'])[:3000]
        comments=re.findall(r'/\*[\s\S]*?\*/|(?m:^//[^\n]*(?:\n//[^\n]*)*)',prefix)
        banner=next((c for c in comments if 'copyright' in c.casefold()),'')
        header_text=(banner+'\n' if banner else '')+signature+'\n'
        hcorpus='reference-'+('wdk-headers' if name.startswith('Io') else 'sdk-headers');header_path=hcorpus+'/include/'+name+'.h'
        fixtures['files'][header_path]=header_text
        cases.append({'name':name,'document':{'full_source_path':doc['source_path'],'fixture_source_path':fixture_corpus+'/'+relative,
                      'fixture_input':doc_path,'source_id':'SRC-DDI-DOCS' if corpus=='ddi' else 'SRC-SDK-DOCS',
                      'source_path':relative,'source_sha256':sha(raw),'revision':doc['revision'],'expected_sources':{**mapping,'primary_name':'UID symbol selecting an explicit api_name'},'expected':fields,'parameters':members},
                      'declaration':{'source_id':'SRC-WDK-HEADERS' if name.startswith('Io') else 'SRC-SDK-HEADERS',
                      'source_path':decl['path'],'source_sha256':decl['sha256'],'full_corpus':decl['corpus'],
                      'source_span':{'byte_start':decl['byte_start'],'byte_end':decl['byte_end'],'line_start':decl['line_start'],'line_end':decl['line_end']},
                      'fixture_corpus':hcorpus,'fixture_input':header_path,'fixture_path':name+'.h','signature':signature,'fixture_sha256':sha(header_text.encode()),'name':name,'kind':'function'}})
    for corpus,filename in [('sdk','MicrosoftDocs-LICENSE'),('sdk','MicrosoftDocs-LICENSE-CODE'),('ddi','DriverDocs-LICENSE')]:
        raw=(a.notices_root/filename).read_bytes()
        target='reference-'+corpus+'/'+('LICENSE-CODE' if filename.endswith('-CODE') else 'LICENSE')
        fixtures['files'][target]={'hex':raw.hex()}
        notices.append({'fixture_input':target,'source_id':'SRC-'+corpus.upper()+'-DOCS','source_path':target.split('/',1)[1],'sha256':sha(raw)})
    for corpus in ('sdk','ddi'):
        key='reference-'+corpus
        if not any(x['key']==key for x in fixtures['config']['docs']):fixtures['config']['docs'].append({'key':key,'path':'inputs/'+key+'/content','repository':'inputs/'+key})
    for family in ('sdk','wdk'):
        key='reference-'+family+'-headers'
        if not any(x['key']==key for x in fixtures['config']['headers']):fixtures['config']['headers'].append({'key':key,'path':'inputs/'+key+'/include','package':'SEED.Reference.Excerpts','version':'1.0','include_version':'excerpts'})
    report={'description':'Source-backed compatibility examples. Document bytes are retained exactly; header declarations are exact verified source slices with retained copyright comments. Expected values were checked against the source, not blindly copied from generated output.',
            'identity_policy':'Reference IDs and absolute local paths are excluded. Full runs need not match historical Git commits. A changed source contract must be reported, not silently exempted.',
            'cases':cases,'notices':notices}
    (a.package/'acceptance/reference-cases.json').write_text(json.dumps(report,indent=2)+'\n')
    (a.package/'acceptance/fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
    print(json.dumps({'cases':len(cases),'parameter_expectations':sum(len(c['document']['parameters']) for c in cases),'notices':len(notices),'fixture_bytes':(a.package/'acceptance/fixtures.json').stat().st_size}))
if __name__=='__main__':main()
