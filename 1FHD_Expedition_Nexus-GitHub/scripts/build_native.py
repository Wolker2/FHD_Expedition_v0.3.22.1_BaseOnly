#!/usr/bin/env python3
"""Build the inspectable x86 assembly into a deterministic PE32 DLL.

GNU as/ld/objcopy/nm/objdump and Python standard library only. No prebuilt
DLL, extracted code bytes or opaque PE header blob is used as an input.
"""
from pathlib import Path
import json,re,struct,subprocess

def align(value,size):return (value+size-1)//size*size
def run(*args):subprocess.run([str(x)for x in args],check=True,capture_output=True)

def build(source,output):
    source=Path(source);output=Path(output);profile=json.loads((source/'pe_profile.json').read_text())
    if profile['format']!='srhd-native-pe32-v1':raise ValueError('Unknown PE profile')
    work=source/'build';work.mkdir(exist_ok=True)
    obj=work/'native.o';elf=work/'native.elf'
    run('as','--32',source/'expedition_native.S','-o',obj)
    run('ld','-melf_i386','-T',source/'link.ld',obj,'-o',elf)
    sections={}
    for section in ('text','data','dosstub'):
        target=work/(section+'.bin');run('objcopy','-O','binary','--only-section=.'+section,elf,target);sections[section]=target.read_bytes()
    if sections['data']!=bytes(profile['data_virtual_size']):raise ValueError('Only zero-initialized native globals are supported by this profile')
    image_base=profile['image_base'];text=sections['text'];text_rva=0x1000;rdata_rva=0x2000;data_rva=0x3000;reloc_rva=0x4000
    if len(text)>4096:raise ValueError('Native code exceeds the fixed section layout')
    symbols={}
    for line in subprocess.check_output(['nm','-n',str(elf)],text=True).splitlines():
        parts=line.split()
        if len(parts)==3:symbols[parts[2]]=int(parts[0],16)
    if symbols['GalaxyPointer']!=image_base+data_rva or symbols['ProbeAddFunction']!=image_base+data_rva+4:raise ValueError('Native global layout changed')
    names=profile['exports'];count=len(names);rdata=bytearray(40)
    name_offset=len(rdata);rdata.extend(profile['dll_name'].encode('ascii')+b'\0');rdata.extend(bytes(align(len(rdata),4)-len(rdata)))
    functions=len(rdata)
    for name in names:rdata.extend(struct.pack('<I',symbols[name]-image_base))
    pointers=len(rdata);rdata.extend(bytes(4*count));ordinals=len(rdata)
    for index in range(count):rdata.extend(struct.pack('<H',index))
    for index,name in enumerate(names):
        struct.pack_into('<I',rdata,pointers+index*4,rdata_rva+len(rdata));rdata.extend(name.encode('ascii')+b'\0')
    struct.pack_into('<IIHH7I',rdata,0,0,0,0,0,rdata_rva+name_offset,1,count,count,rdata_rva+functions,rdata_rva+pointers,rdata_rva+ordinals)
    relocations=[];active=False
    for line in subprocess.check_output(['objdump','-r',str(obj)],text=True).splitlines():
        if line.startswith('RELOCATION RECORDS FOR '):active=line=='RELOCATION RECORDS FOR [.text]:'
        match=re.match(r'^([0-9a-fA-F]+)\s+R_386_32\s+',line)
        if active and match:relocations.append(text_rva+int(match[1],16))
    pages={}
    for rva in sorted(relocations):pages.setdefault(rva&~0xFFF,[]).append(0x3000|(rva&0xFFF))
    reloc=bytearray()
    for page,entries in sorted(pages.items()):
        if len(entries)%2:entries.append(0)
        reloc.extend(struct.pack('<II',page,8+2*len(entries)));reloc.extend(struct.pack('<'+'H'*len(entries),*entries))
    stub=sections['dosstub'];pe_offset=64+len(stub);dos=bytearray(64)
    struct.pack_into('<14H',dos,0,0x5A4D,pe_offset,1,0,4,0,0,0,0,0,0,0,0x40,0);struct.pack_into('<I',dos,60,pe_offset)
    file_align=profile['file_alignment'];section_align=profile['section_alignment'];header_size=align(pe_offset+24+224+4*40,file_align)
    text_size=align(len(text),file_align);rdata_size=align(len(rdata),file_align);reloc_size=align(len(reloc),file_align)
    optional=bytearray(224)
    struct.pack_into('<HBB',optional,0,0x10B,*profile['linker_version'])
    struct.pack_into('<9I',optional,4,text_size,rdata_size+reloc_size,0,0,text_rva,0,image_base,section_align,file_align)
    struct.pack_into('<6H',optional,40,*profile['os_version'],*profile['image_version'],*profile['subsystem_version'])
    struct.pack_into('<4I',optional,52,0,align(reloc_rva+len(reloc),section_align),header_size,0)
    struct.pack_into('<2H',optional,68,profile['subsystem'],profile['dll_characteristics'])
    struct.pack_into('<6I',optional,72,profile['stack_reserve'],profile['stack_commit'],profile['heap_reserve'],profile['heap_commit'],0,16)
    struct.pack_into('<2I',optional,96,rdata_rva,len(rdata));struct.pack_into('<2I',optional,136,reloc_rva,len(reloc))
    coff=struct.pack('<HHIIIHH',0x14C,4,profile['coff_timestamp'],0,0,224,profile['coff_characteristics'])
    table=bytearray()
    records=[('.text',len(text),text_rva,text_size,header_size,0x60000020),('.rdata',len(rdata),rdata_rva,rdata_size,header_size+text_size,0x40000040),('.data',profile['data_virtual_size'],data_rva,0,0,0xC0000040),('.reloc',len(reloc),reloc_rva,reloc_size,header_size+text_size+rdata_size,0x42000040)]
    for name,size,rva,raw_size,pointer,flags in records:
        table.extend(struct.pack('<8s6I2HI',name.encode('ascii'),size,rva,raw_size,pointer,0,0,0,0,flags))
    data=bytes(dos)+stub+b'PE\0\0'+coff+optional+table
    data+=bytes(header_size-len(data))
    data+=text+bytes([profile['text_padding']])*(text_size-len(text))
    data+=rdata+bytes(rdata_size-len(rdata))+reloc+bytes(reloc_size-len(reloc))
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(data)
    return data

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();build(a.source,a.output);print('DLL built:',a.output)
