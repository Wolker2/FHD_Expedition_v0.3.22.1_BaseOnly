#!/usr/bin/env python3
"""Independent SCR6/SCR8 structural inspector, derived from the game loader format.

Used to verify the recovered FHD_Expedition binary; not a general RSON decompiler.
"""
from pathlib import Path
import struct,json

class Reader:
 def __init__(self,b):self.b=b;self.p=0
 def get(self,f):
  n=struct.calcsize('<'+f);v=struct.unpack_from('<'+f,self.b,self.p)[0];self.p+=n;return v
 def i(self):return self.get('i')
 def u(self):return self.get('I')
 def f(self):return self.get('f')
 def flag(self):
  v=self.get('B');assert v in (0,1);return bool(v)
 def s(self):
  start=self.p
  while self.b[self.p:self.p+2]!=b'\0\0':
   self.p+=2
   if self.p>=len(self.b):raise ValueError(('string EOF',start))
  v=self.b[start:self.p].decode('utf-16le');self.p+=2;return v
 def fields(self,spec):return {k:getattr(self,t)() for k,t in spec}
 def seq(self,fn,label=''):
  n=self.i();assert 0<=n<10000,(label,self.p,n)
  return [fn() for _ in range(n)]

def parse(path):
 r=Reader(Path(path).read_bytes());d={};d['version']=r.u();d['local_offset']=r.u();assert d['version'] in (6,8)
 def var():
  x={'name':r.s(),'kind':r.get('B')};k=x['kind']
  if k in (1,2):x['value']=r.i() if k==1 else r.u()
  elif k==3:x['value']=r.get('d')
  elif k==4:x['value']=r.s()
  elif k==9:x['value']=r.seq(var)
  else:assert k in (0,5,6,7,8,10),k
  return x
 d['global_variables']=r.seq(var,'globals');d['global_code']=r.s()
 assert r.p==d['local_offset'],(r.p,d['local_offset'])
 d['local_variables']=r.seq(var,'locals');d['constellations']=r.i()
 def star():
  s=r.fields([('name','s'),('constellation','i')]);s.update(r.fields([('legacy_flag','flag')]) if d['version']<7 else {});s.update(r.fields([('reject_hostile','flag'),('protect','flag')]))
  s['constraints']=r.seq(lambda:r.fields([('star','i'),('min_distance','i'),('max_distance','i'),('black_hole','flag')]),'constraints')
  s['planets']=r.seq(lambda:r.fields([('name','s'),('race','u'),('owner','u'),('economy','u'),('government','u'),('min_orbit','i'),('max_orbit','i'),('dialog','s')]),'planets')
  s['ships']=r.seq(lambda:r.fields([('count','i'),('owner','u'),('types','u'),('player','flag'),('min_speed','i'),('max_speed','i'),('weapon','i'),('hook','i'),('free_space','i')]+([('legacy_pre_status0','i'),('legacy_pre_status1','i')]if d['version']<7 else[])+[('min_trader','i'),('max_trader','i'),('min_warrior','i'),('max_warrior','i'),('min_pirate','i'),('max_pirate','i')]+([('legacy_post_status0','i'),('legacy_post_status1','i')]if d['version']<7 else[])+[('min_strength','f'),('max_strength','f'),('stations','s')]),'ships')
  return s
 d['stars']=r.seq(star,'stars')
 def place():
  p=r.fields([('name','s'),('origin','s'),('kind','i')]);k=p['kind']
  if k==0:p.update(r.fields([('angle','f'),('distance','f'),('radius','i')]))
  elif k in (1,4):p.update(r.fields([('target','s'),('radius','i')]))
  elif k==2:p['target']=r.s()
  elif k in (3,5):p.update(r.fields([('target','s'),('distance','f'),('radius','i'),('angle','f')]))
  elif k==6:p.update(r.fields([('target','s'),('target2','s'),('radius','i')]))
  else:raise ValueError(k)
  return p
 d['places']=r.seq(place,'places')
 d['items']=r.seq(lambda:r.fields([('name','s'),('location','s'),('kind','i'),('type','i'),('weight','i'),('level','i'),('radius','i'),('owner','i'),('config','s')]),'items')
 d['groups']=r.seq(lambda:r.fields([('name','s'),('planet','s'),('state','i'),('owner','u'),('types','u'),('min_count','i'),('max_count','i'),('min_speed','i'),('max_speed','i'),('weapon','i'),('hook','i'),('free_space','i')]+([('legacy_before_player','i')]if d['version']<7 else[])+[('player','flag')]+([('legacy_after_player0','i'),('legacy_after_player1','i'),('legacy_after_player2','i'),('legacy_after_player3','i')]if d['version']<7 else[])+[('min_trader','i'),('max_trader','i'),('min_warrior','i'),('max_warrior','i'),('min_pirate','i'),('max_pirate','i'),('max_distance','i'),('dialog','s'),('min_strength','f'),('max_strength','f'),('stations','s')]),'groups')
 d['relations']=r.seq(lambda:r.fields([('group1','i'),('group2','i'),('relation12','i'),('relation21','i'),('min_balance','f'),('max_balance','f')]),'relations')
 for code in ('init_code','turn_code','dialog_code'):d[code]=r.s()
 def state():
  s=r.fields([('name','s'),('kind','i')]);s['target']=r.s() if s['kind'] not in (0,1) else ''
  s['enemies']=r.seq(r.s,'enemies')
  s.update(r.fields([('pickup','s'),('pickup_all','flag'),('dialog','s'),('action_code','s'),('entry_code','s'),('turn_code','s')]))
  return s
 d['states']=r.seq(state,'states')
 d['dialogs']=r.seq(lambda:r.fields([('name','s'),('code','s')]),'dialogs')
 d['messages']=r.seq(lambda:r.fields([('name','s'),('code','s')]),'messages')
 d['answers']=r.seq(lambda:r.fields([('name','s'),('answer_code','s'),('action_code','s')]),'answers')
 assert r.p==len(r.b)
 return d

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description='Inspect SCR version 8 into complete named fields and source text')
 p.add_argument('input',type=Path);p.add_argument('--output',type=Path)
 a=p.parse_args();result=json.dumps(parse(a.input),ensure_ascii=False,indent=2)+'\n'
 if a.output:a.output.write_text(result,encoding='utf-8')
 else:print(result,end='')
