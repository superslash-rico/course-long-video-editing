"""Install one complete Skill, or explicitly upgrade a recognized unchanged version with backup."""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
sys.dont_write_bytecode=True
from verify_package import verify

def digest(root):return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
def install(source,target_root,*,dry_run=False,upgrade=False,backup_root=None):
 source=source.resolve();target_root=target_root.expanduser().resolve();target=target_root/'course-long-video-editing';valid=verify(source)
 if not valid['ok']:return {'ok':False,'state':'invalid-source','errors':valid['errors']}
 if target==source:return {'ok':True,'state':'running-installed-copy','target':str(target)}
 if source in target.parents:return {'ok':False,'state':'target-inside-source'}
 if target.is_symlink():return {'ok':False,'state':'target-symlink-kept-for-review'}
 expected=digest(source);previous=None
 if target.exists():
  if not target.is_dir():return {'ok':False,'state':'existing-nondirectory-kept'}
  previous=digest(target)
  if previous==expected:return {'ok':True,'state':'already-installed-identical','target':str(target)}
  if not upgrade:return {'ok':False,'state':'existing-version-kept-no-overwrite','target':str(target)}
  old=verify(target)
  if not old['ok']:return {'ok':False,'state':'existing-modified-or-incomplete-kept','errors':old['errors']}
  accepted=json.loads((source/'PACKAGE.json').read_text()).get('upgradePolicy',{}).get('acceptedPreviousManifestSHA256',[])
  if hashlib.sha256((target/'assets/manifest.json').read_bytes()).hexdigest() not in accepted:return {'ok':False,'state':'unrecognized-previous-package-kept-for-review'}
  if backup_root is None:return {'ok':False,'state':'upgrade-needs-explicit-backup-root'}
  backup_root=backup_root.expanduser().resolve()
  if backup_root==target or target in backup_root.parents or backup_root==source or source in backup_root.parents:return {'ok':False,'state':'backup-must-be-outside-source-and-installed-skill'}
 if dry_run:return {'ok':True,'state':'dry-run-no-write','target':str(target),'upgrade':previous is not None}
 target_root.mkdir(parents=True,exist_ok=True)
 if previous is None:
  shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
  checked=verify(target);return {'ok':checked['ok'],'state':'installed-files-verified','target':str(target),'allFilesMatchSource':digest(target)==expected,'skillDiscovery':'requires-new-session-check'}
 backup_root.mkdir(parents=True,exist_ok=True);old_version=json.loads((target/'PACKAGE.json').read_text())['version'];stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup=backup_root/('course-long-video-editing-'+old_version+'-'+stamp)
 if backup.exists():return {'ok':False,'state':'backup-name-exists-no-write'}
 shutil.copytree(target,backup,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
 if digest(backup)!=previous:return {'ok':False,'state':'backup-readback-mismatch','backup':str(backup)}
 stage=Path(tempfile.mkdtemp(prefix='.course-skill-upgrade-',dir=target_root));new=stage/'new';retired=stage/'previous'
 try:
  shutil.copytree(source,new,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
  if digest(new)!=expected or digest(target)!=previous:return {'ok':False,'state':'concurrent-change-or-staging-mismatch-kept','backup':str(backup)}
  target.rename(retired)
  try:
   new.rename(target)
   checked=verify(target)
   if not checked['ok'] or digest(target)!=expected:raise RuntimeError('installed readback mismatch')
  except Exception:
   if target.exists():target.rename(stage/'failed-new')
   retired.rename(target);raise
  shutil.rmtree(retired)
  return {'ok':True,'state':'upgraded-backed-up-and-verified','target':str(target),'backup':str(backup),'allFilesMatchSource':True,'skillDiscovery':'requires-new-session-check'}
 finally:
  if not retired.exists():shutil.rmtree(stage)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target-root',type=Path);p.add_argument('--dry-run',action='store_true');p.add_argument('--upgrade',action='store_true');p.add_argument('--backup-root',type=Path);a=p.parse_args()
 source=Path(__file__).resolve().parents[1];target_root=a.target_root or Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'skills'
 try:out=install(source,target_root,dry_run=a.dry_run,upgrade=a.upgrade,backup_root=a.backup_root)
 except (OSError,ValueError,KeyError,RuntimeError) as exc:out={'ok':False,'state':'failed-preserving-existing-or-rollback','error':str(exc)}
 print(json.dumps(out,ensure_ascii=False,indent=2));return 0 if out['ok'] else 2
if __name__=='__main__':raise SystemExit(main())
