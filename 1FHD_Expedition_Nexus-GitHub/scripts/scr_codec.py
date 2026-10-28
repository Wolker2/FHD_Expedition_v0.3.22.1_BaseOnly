#!/usr/bin/env python3
"""Build recovered FHD_Expedition SCR6/SCR8 directly from editable RSON + typed field layout.

SCR6/SCR8 stores source text, not VM bytecode. The game compiles that text on load.
This encoder serializes the complete recovered runtime model. It does not
implement RScript's general visual-graph compiler for arbitrary projects.
"""
from pathlib import Path
import argparse,json,struct

FORMATS={'u8':'B','bool':'B','i32':'i','u32':'I','f32':'f','f64':'d'}
VAR_TYPES={'Int':1,'Dword':2,'Float':3,'Str':4}

def object_index(scene):
    if scene.get('FileID')!=573785173 or scene.get('FileVersion')!=8:
        raise ValueError('Expected RSON FileID 573785173, version 8')
    index={}
    for group in scene['Visual.Objects']:
        for collection in group.values():
            if not isinstance(collection,list):continue
            for item in collection:
                number=item['#']
                if number in index:raise ValueError('Duplicate object ID '+str(number))
                index[number]=item
    for item in index.values():
        if item['Parent']!=-1 and item['Parent'] not in index:
            raise ValueError('Invalid Parent on object '+str(item['#']))
    for link in scene['Visual.Links']:
        if link['Begin'] not in index or link['End'] not in index:
            raise ValueError('Dangling visual link')
    return index

def as_text(value):
    if isinstance(value,list):
        if not all(isinstance(s,str)for s in value):raise ValueError('Code must contain strings')
        return '\n'.join(value)
    if not isinstance(value,str):raise ValueError('String field expected')
    return value

def encode(scene,layout):
    if layout['format']!='srhd-recovered-scr-layout-v1':raise ValueError('Unknown field layout')
    objects=object_index(scene);out=bytearray();marks={};patches=[]
    def get(reference):return objects[reference[0]][reference[1]]
    def string(value):
        value=as_text(value)
        if '\0' in value:raise ValueError('Embedded NUL in string')
        return value.encode('utf-16le')+b'\0\0'
    for record in layout['records']:
        kind=record[0]
        if kind=='mark':
            if record[1] in marks:raise ValueError('Duplicate marker')
            marks[record[1]]=len(out);continue
        if kind=='offset':patches.append((len(out),record[1]));out.extend(bytes(4));continue
        if kind=='concat_wstr':
            out.extend(string(''.join(as_text(get(r))for r in record[1])));continue
        value=get(record[1:]) if len(record)==3 else record[1]
        if kind in ('wstr','lines'):out.extend(string(value))
        elif kind=='vartype':out.extend(bytes([VAR_TYPES[value]]))
        elif kind in FORMATS:
            if kind=='bool':
                if not isinstance(value,bool):raise ValueError('Boolean field expected')
                value=int(value)
            elif kind.startswith('f'):value=float(value)
            else:value=int(value)
            out.extend(struct.pack('<'+FORMATS[kind],value))
        else:raise ValueError('Unknown layout primitive '+kind)
    for offset,marker in patches:struct.pack_into('<I',out,offset,marks[marker])
    return bytes(out)

def build(source,layout_path):
    return encode(json.loads(Path(source).read_text('utf-8-sig')),
                  json.loads(Path(layout_path).read_text('utf-8-sig')))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--layout',type=Path)
    a=p.parse_args();layout=a.layout or a.source.with_suffix('.layout.json')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(build(a.source,layout))
    print('SCR6/SCR8 built:',a.output)
