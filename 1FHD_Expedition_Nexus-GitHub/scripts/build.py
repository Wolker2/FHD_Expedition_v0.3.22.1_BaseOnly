#!/usr/bin/env python3
"""Build all 11 FHD_Expedition runtime files from editable source, without binaries.

Python 3.10+ and GNU binutils; standard-library Python only. No Windows tools or game installation.
"""
from pathlib import Path
import argparse,hashlib,json,platform,sys,zipfile,zlib
from dat_codec import encode as encode_dat,decode as decode_dat
from gi_codec import encode as encode_gi,decode as decode_gi
from scr_codec import build as build_scr
from build_native import build as build_native

ROOT=Path(__file__).resolve().parent.parent
INSTALL_PREFIX='Mods/FHD_MODS/FHD_Expedition/'
def load(path):return json.loads(Path(path).read_text('utf-8-sig'))
def sha(data):return hashlib.sha256(data).hexdigest()
def walk(block,path=''):
    for e in block['entries']:
        name=path+'.'+e['name']if path else e['name']
        if e['kind']=='block':yield from walk(e['value'],name)
        else:yield name,e['value']

def compile_source(root=ROOT):
    source=root/'source';files={};configs={}
    for path in sorted((source/'CFG').rglob('*.json')):
        name=path.relative_to(source).with_suffix('.dat').as_posix();tree=load(path)
        files[name]=encode_dat(tree);configs[name]=tree
        if decode_dat(files[name],tree['format'])!=tree:raise ValueError('DAT roundtrip failed: '+name)
    for script in ['FHD_Expedition','FHD_Expedition_Intro']:
        files['DATA/Script/'+script+'.scr']=build_scr(source/'script'/(script+'.rson'),source/'script'/(script+'.layout.json'))
    files['DATA/FHDExpeditionNative.dll']=build_native(source/'native',root/'dist/FHDExpeditionNative.dll')
    for path in sorted((source/'DATA/UI').glob('*.json')):
        tree=load(path);name='DATA/UI/'+path.stem+'.gi';files[name]=encode_gi(tree)
        if decode_gi(files[name])!=tree:raise ValueError('GI roundtrip failed: '+name)
    files['ModuleInfo.txt']=(source/'ModuleInfo.txt').read_bytes().decode('utf-8').encode('cp1251')
    return files,configs

def resource_audit(files,configs):
    refs=[]
    for alias,value in walk(configs['CFG/CacheData.dat']['root']):
        path=value.replace('\\','/')
        if path.startswith(INSTALL_PREFIX):
            refs.append({'alias':alias,'path':path,'present':path[len(INSTALL_PREFIX):]in files})
    return {'cache_references_checked':len(refs),'missing':[x for x in refs if not x['present']]}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--strict-original',action='store_true');a=p.parse_args()
    files,configs=compile_source();expected=load(ROOT/'original-file-sha256.json')
    if set(files)!=set(expected):raise SystemExit('Runtime file list does not match the reference manifest')
    hashes={k:sha(v)for k,v in sorted(files.items())};different=[k for k in hashes if hashes[k]!=expected[k]]
    if a.strict_original and different:raise SystemExit('Original hash mismatch: '+repr(different))
    audit=resource_audit(files,configs)
    if audit['missing']:raise SystemExit('Referenced resources missing: '+repr(audit['missing']))
    out=ROOT/'dist';out.mkdir(exist_ok=True);archive=out/'FHD_Expedition_FROM_SOURCE.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for path,data in sorted(files.items()):
            info=zipfile.ZipInfo(INSTALL_PREFIX+path,date_time=(2026,10,28,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(archive)as z:
        if z.testzip():raise SystemExit('ZIP integrity failure')
    report={'runtime_files':len(files),'source_derived_files':len(files),'prebuilt_runtime_files_used':False,
            'byte_identical_to_original':not different,'different_files':different,
            'dat_files':3,'script_files':2,'native_dlls':1,'gi_images':4,'resource_audit':audit,
            'python':platform.python_version(),'zlib':zlib.ZLIB_RUNTIME_VERSION,
            'sha256':hashes,'package_sha256':sha(archive.read_bytes()),
            'rscript_executed':False,'game_executed':False,'native_source':'reconstructed x86 assembly',
            'original_script_issue':'FHD_Expedition_Intro SCR6 dialog_code contains four opening braces and five closing braces; original bytes preserved.'}
    (out/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS:',len(files),'runtime files built from source;',len(files)-len(different),'original hashes match')
    print('CacheData references:',audit['cache_references_checked'],'present; missing:',len(audit['missing']))
    print('Package:',archive)

if __name__=='__main__':main()
