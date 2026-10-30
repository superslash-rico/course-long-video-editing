# -*- coding: utf-8 -*-
"""Synthetic rejection tests for the material readiness gate, not aesthetics."""
import copy,json,struct,tempfile,zlib
from pathlib import Path
from material_priority import check_plan,digest,linked_plan

def png(path,alphas):
 def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
 pixels=b''.join(bytes([20,50,80,a]) for a in alphas)
 path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',len(alphas),1,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0'+pixels))+chunk(b'IEND',b''))

def main():
 results=[]
 with tempfile.TemporaryDirectory() as td:
  root=Path(td);(root/'receipt.txt').write_text('Synthetic opened official source fixture, not actual research')
  png(root/'cutout.png',[0,255,255,0]);png(root/'opaque.png',[255]*4);png(root/'empty.png',[0]*4)
  def file(n):return {'file':n,'sha256':digest(root/n)}
  base={'schemaVersion':2,'researchReceipts':[{'id':'r','query':'topic original source','sourceUrl':'https://example.test/original','accessedDate':'2026-10-30','result':'collected','evidence':file('receipt.txt')}],
   'assets':[{'id':'real','tier':'real','role':'evidence','sourceUrl':'https://example.test/original','rightsAndBoundary':'Synthetic test only',**file('receipt.txt')},{'id':'png','tier':'generated','role':'illustration','rightsAndBoundary':'Synthetic illustration fixture',**file('cutout.png'),'generationRecord':file('receipt.txt'),'visualReview':'Fixture declaration only'}],
   'scenes':[{'id':'s','goal':'Explain task','researchIds':['r'],'assetIds':['real','png'],'realAssessment':'Original examined','generatedAssessment':'Concept supplement','cameraPlan':{k:'Specific test plan' for k in ['opening','detail','hold','return','perspectiveAndDepth','motionPurpose']}}]}
  def test(name,mutate,ok):
   d=copy.deepcopy(base);mutate(d);p=root/'plan.json';p.write_text(json.dumps(d));r=check_plan(p);assert r['ok']==ok,(name,r);results.append({'name':name,'ok':True})
  test('real-plus-transparent-illustration-accepted',lambda d:None,True)
  test('no-real-research-rejected',lambda d:d.update(researchReceipts=[]),False)
  test('generated-as-evidence-rejected',lambda d:d['assets'][1].update(role='evidence'),False)
  test('opaque-png-rejected',lambda d:d['assets'][1].update(file('opaque.png')),False)
  test('explicit-user-background-exception-accepted',lambda d:d['assets'][1].update(**file('opaque.png'),fullBackgroundException={'reason':'Synthetic explicit user asks for full scene','requestEvidence':file('receipt.txt')}),True)
  test('background-exception-without-request-rejected',lambda d:d['assets'][1].update(**file('opaque.png'),fullBackgroundException={'reason':'Assumed background'}),False)
  test('empty-png-rejected',lambda d:d['assets'][1].update(file('empty.png')),False)
  test('stale-media-rejected',lambda d:d['assets'][1].update(sha256='0'*64),False)
  test('camera-checkbox-instead-of-plan-rejected',lambda d:d['scenes'][0].update(cameraPlan={}),False)
  test('tier-two-not-assessed-rejected',lambda d:d['scenes'][0].update(generatedAssessment=''),False)
  def pure_logic(d):
   d['assets']=[{'id':'logic','tier':'code','role':'relation','rightsAndBoundary':'Self-authored relation',**file('receipt.txt')}]
   d['scenes'][0].update(assetIds=['logic'],generatedAssessment='Photographs/cutouts would add no explanatory value to this relation',codeReason='Only arrows and exact labels represent the hierarchy')
  test('justified-pure-relation-after-research-accepted',pure_logic,True)
  def code_object(d):pure_logic(d);d['assets'][0]['role']='evidence'
  test('code-fake-evidence-rejected',code_object,False)
  p=root/'plan.json';p.write_text(json.dumps(base));assert linked_plan(file('plan.json'),root,['missing-scene']);results.append({'name':'scene-coverage-required','ok':True})
  assert linked_plan(None,root,['s']);results.append({'name':'missing-workflow-link-rejected','ok':True})
 print(json.dumps({'ok':True,'count':len(results),'tests':results,'scope':'Synthetic file, alpha and declaration checks; no real source, visual quality or user approval claim.'},indent=2))
if __name__=='__main__':main()
