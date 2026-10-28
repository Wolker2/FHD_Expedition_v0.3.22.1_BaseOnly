from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,unittest,zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import compile_source,resource_audit,load,INSTALL_PREFIX
from scr_codec import encode as encode_scr
from inspect_scr import parse
from build_native import build as build_native

class SourceTests(unittest.TestCase):
    def test_all_original_hashes_and_resource_references(self):
        files,configs=compile_source();expected=load(ROOT/'original-file-sha256.json')
        self.assertEqual({k:hashlib.sha256(v).hexdigest()for k,v in files.items()},expected)
        self.assertEqual(len(files),11)
        self.assertEqual(resource_audit(files,configs),{'cache_references_checked':6,'missing':[]})

    def test_both_script_formats_accept_source_edits_and_relocate_offsets(self):
        for name,version,locals_ in [('FHD_Expedition',8,2),('FHD_Expedition_Intro',6,3)]:
            source=ROOT/'source/script';scene=load(source/(name+'.rson'));layout=load(source/(name+'.layout.json'))
            for group in scene['Visual.Objects']:
                for item in group.get('Operations',[]):
                    if item['Name']=='global_code':item['Code'].insert(0,'// source edit test')
            data=encode_scr(scene,layout)
            with tempfile.TemporaryDirectory()as folder:
                path=Path(folder)/'script.scr';path.write_bytes(data);model=parse(path)
            self.assertEqual(model['version'],version)
            self.assertGreater(model['local_offset'],28)
            self.assertTrue(model['global_code'].startswith('// source edit test\n'))
            self.assertEqual(len(model['local_variables']),locals_)

    def test_embedded_dat_code_is_an_active_input(self):
        original,_=compile_source()
        with tempfile.TemporaryDirectory()as folder:
            target=Path(folder);shutil.copytree(ROOT/'source',target/'source',ignore=shutil.ignore_patterns('build'))
            path=target/'source/CFG/Rus/Lang.json';data=load(path)
            block=next(e['value']for e in data['root']['entries']if e['kind']=='block'and e['name']=='Script')
            def change(block):
                for e in block['entries']:
                    if e['kind']=='block':
                        if change(e['value']):return True
                    elif '('in e['value']and ';'in e['value']:
                        e['value']+=' // source edit test';return True
                return False
            self.assertTrue(change(block))
            path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            files,_=compile_source(target)
        self.assertEqual([k for k in files if files[k]!=original[k]],['CFG/Rus/Lang.dat'])

    def test_native_exports_with_40_mock_engine_checks(self):
        emulator=os.environ.get('FHD_QEMU_I386')or shutil.which('qemu-i386')
        self.assertTrue(emulator,'qemu-i386 is required for native behavioral tests')
        with tempfile.TemporaryDirectory()as folder:
            work=Path(folder);source=ROOT/'source/native'
            build_native(source,work/'native.dll')
            commands=[['as','--32',str(ROOT/'tests/native_fixture.S'),'-o',str(work/'fixture.o')],
                      ['objcopy','--remove-section=.dosstub',str(source/'build/native.o'),str(work/'native-test.o')],
                      ['ld','-melf_i386','--entry=_start',str(work/'fixture.o'),str(work/'native-test.o'),'-o',str(work/'fixture.elf')],
                      [emulator,str(work/'fixture.elf')]]
            for command in commands:
                result=subprocess.run(command,capture_output=True,text=True)
                self.assertEqual(result.returncode,0,'Command: '+repr(command)+'\n'+result.stdout+result.stderr)

    def test_complete_build_without_precompiled_inputs(self):
        with tempfile.TemporaryDirectory()as folder:
            target=Path(folder)
            for name in ['scripts','source']:shutil.copytree(ROOT/name,target/name,ignore=shutil.ignore_patterns('__pycache__','build'))
            shutil.copy2(ROOT/'original-file-sha256.json',target/'original-file-sha256.json')
            self.assertFalse(any(p.suffix in('.dll','.lib','.scr','.dat','.gi','.o','.elf','.bin')for p in target.rglob('*')if p.is_file()))
            result=subprocess.run([sys.executable,str(target/'scripts/build.py'),'--strict-original'],cwd=target,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+'\n'+result.stderr)
            expected=load(ROOT/'original-file-sha256.json')
            with zipfile.ZipFile(target/'dist/FHD_Expedition_FROM_SOURCE.zip')as z:
                self.assertIsNone(z.testzip());self.assertEqual(len(z.namelist()),11)
                for name,digest in expected.items():self.assertEqual(hashlib.sha256(z.read(INSTALL_PREFIX+name)).hexdigest(),digest)

if __name__=='__main__':unittest.main()
