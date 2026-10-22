#!/usr/bin/env python3
"""Create a title-first course workspace and optionally copy explicitly classified files.

Standard library only. No network, ChatCut calls, speech edits or source-file moves.
The caller supplies the user-confirmed title, client-local date and file roles.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import shutil
import tempfile
import unicodedata

SKILL_ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ('原片', '片头', '片尾', '封面', '参考资料')
TRANSLATION = str.maketrans('/\\:*?"<>|', '／＼：＊？＂＜＞｜')


def portable_name(value, limit=240, preserve_suffix=False):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('A nonempty user-confirmed title or filename is required')
    original = unicodedata.normalize('NFC', value).strip()
    cleaned = re.sub(r'\s+', ' ', ''.join(' ' if ord(c)<32 else c for c in original.translate(TRANSLATION))).strip(' .')
    if not cleaned:
        raise ValueError('The title or filename has no usable characters')
    if len(cleaned.encode('utf-8')) > limit:
        suffix = Path(cleaned).suffix if preserve_suffix else ''
        if len(suffix.encode('utf-8'))>20:suffix=''
        tail='~'+hashlib.sha256(original.encode()).hexdigest()[:10]+suffix
        prefix=''
        for c in cleaned[:-len(suffix)] if suffix else cleaned:
            if len((prefix+c+tail).encode('utf-8'))>limit:break
            prefix+=c
        cleaned=prefix.rstrip()+tail
    return original, cleaned


def sha256(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(4*1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()


def signature(path):
    s=path.stat()
    return s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns


def classified_files(path):
    if path is None:return []
    data=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data,dict) or not isinstance(data.get('files'),list):
        raise ValueError('assets-json requires an object with a files array')
    result=[]
    for item in data['files']:
        if not isinstance(item,dict) or item.get('category') not in CATEGORIES:
            raise ValueError('Every supplied local file needs an explicit valid category')
        supplied=item.get('source')
        if not isinstance(supplied,str) or not supplied.strip():raise ValueError('source must be a local file path')
        source=Path(supplied).expanduser().resolve(strict=True)
        if not source.is_file():raise ValueError('List actual local files; enumerate supplied folders before import')
        relative=item.get('relativePath',source.name)
        if not isinstance(relative,str) or not relative or PureWindowsPath(relative).drive or relative.startswith(('/','\\')):
            raise ValueError('relativePath must stay inside its category')
        parts=relative.replace('\\','/').split('/')
        if any(x in {'','.','..'} for x in parts):raise ValueError('relativePath cannot escape or reset the category')
        relative=Path(*(portable_name(x,preserve_suffix=i==len(parts)-1)[1] for i,x in enumerate(parts)))
        result.append({'source':source,'sourceGiven':supplied,'category':item['category'],'relative':relative})
    return result


def save_record(path,data):
    if path.is_symlink():raise ValueError('Project record must not be a symlink')
    fd,name=tempfile.mkstemp(prefix='.course-record-',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            json.dump(data,stream,ensure_ascii=False,indent=2);stream.write('\n')
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)


def copy_file(item,root):
    source=item['source'];before=signature(source);digest=sha256(source)
    if signature(source)!=before:raise ValueError('Source changed while being read; retry after recording/download completes')
    base=root/item['category']/item['relative']
    category=root/item['category']
    if not base.resolve().is_relative_to(category.resolve()):raise ValueError('Destination resolves outside its category')
    base.parent.mkdir(parents=True,exist_ok=True)
    for ancestor in [base.parent,*base.parent.parents]:
        if ancestor==root:break
        if ancestor.is_symlink():raise ValueError('Destination directories cannot be symlinks')
    choices=[base]+[base.with_name(base.stem+'-'+digest[:n]+base.suffix) for n in [8,16,64]]
    for destination in choices:
        if destination.is_symlink():raise ValueError('Destination file cannot be a symlink')
        if destination.exists():
            if destination.is_file() and destination.stat().st_size==before[2] and sha256(destination)==digest:
                return destination,digest,'reused-identical'
            continue
        if shutil.disk_usage(root).free < before[2]+1024*1024:
            raise OSError('Insufficient free space for an independent copy; originals remain untouched')
        created_inode=None
        try:
            with destination.open('xb') as output:
                created_inode=os.fstat(output.fileno()).st_ino
                actual=hashlib.sha256()
                with source.open('rb') as incoming:
                    for chunk in iter(lambda:incoming.read(4*1024*1024),b''):
                        output.write(chunk);actual.update(chunk)
            if actual.hexdigest()!=digest or signature(source)!=before:
                raise ValueError('Copy did not match a stable source')
            shutil.copystat(source,destination)
            if sha256(destination)!=digest:raise ValueError('Destination checksum mismatch')
            return destination,digest,'copied'
        except FileExistsError:
            continue
        except Exception:
            if created_inode is not None and destination.exists() and destination.stat().st_ino==created_inode:
                destination.unlink()
            raise
    raise FileExistsError('All non-overwriting destination names are occupied; resolve this filename explicitly')


def initialize(workspace,title,date,assets_json=None,adopt_existing=False):
    original,folder_title=portable_name(title,limit=231)
    if not isinstance(date,str) or not re.fullmatch(r'\d{8}',date):raise ValueError('Use the client-local project creation date as YYYYMMDD')
    datetime.date(int(date[:4]),int(date[4:6]),int(date[6:]))
    workspace=workspace.expanduser().resolve(strict=True)
    if not workspace.is_dir() or workspace.is_relative_to(SKILL_ROOT):raise ValueError('Use the actual project workspace, outside the installed Skill package')
    inputs=classified_files(assets_json)
    root=workspace/(date+'-'+folder_title)
    if root.is_symlink():raise ValueError('Course project directory cannot be a symlink')
    if root.exists() and not root.is_dir():raise ValueError('Course project path is occupied by a file')
    record=root/'课程项目.json';log=root/'创作日志.md'
    for name in CATEGORIES:
        p=root/name
        if p.is_symlink() or (p.exists() and not p.is_dir()):raise ValueError('A required category is occupied or linked: '+name)
    existing=False
    if record.exists():
        if record.is_symlink():raise ValueError('Project record cannot be a symlink')
        data=json.loads(record.read_text(encoding='utf-8'))
        if not isinstance(data,dict):raise ValueError('Existing course project record must be an object')
        if data.get('courseTitle')!=original or data.get('directoryName')!=root.name or data.get('courseProjectRoot')!=str(root):
            raise ValueError('Existing project identity/location differs; resolve whether this is the same course before continuing')
        existing=True
    else:
        if root.exists() and any(p.name!='.DS_Store' for p in root.iterdir()) and not adopt_existing:
            raise ValueError('Unknown nonempty course directory; inspect it before using --adopt-existing')
        data=json.loads((SKILL_ROOT/'assets/records/project-intake-template.json').read_text(encoding='utf-8'))
        data.update(templateOnly=False,projectName=original,courseTitle=original,workspaceRoot=str(workspace),courseProjectRoot=str(root),projectCreatedDate=date,directoryName=root.name,intakeStage='awaiting-materials')
        data['lectureFacts']['title']=original
        data['materialOrganization']['status']='awaiting-materials'
    root.mkdir(exist_ok=True)
    for name in CATEGORIES:(root/name).mkdir(exist_ok=True)
    if log.is_symlink() or (log.exists() and not log.is_file()):raise ValueError('Course log path is occupied or linked')
    if not log.exists():
        with log.open('x',encoding='utf-8') as stream:
            stream.write(f'# {original} · 剪辑创作日志\n\n建档日期：{date[:4]}-{date[4:6]}-{date[6:]}（用户/客户端本地日期）。\n\n已建立独立课程目录和五类素材目录；尚未执行转写、粗剪或动画。素材分类/复制记录见课程项目.json，后续所有工作文件、预览和交付保存在本目录。最终上传标题另存，不自动改动目录名。\n')
    imported=[];errors=[]
    organization=data.setdefault('materialOrganization',{})
    if not isinstance(organization,dict):raise ValueError('Existing material organization must be an object')
    records=organization.setdefault('inputs',[])
    if not isinstance(records,list) or any(not isinstance(x,dict) for x in records):raise ValueError('Existing material records must be an array of objects')
    previous_errors=organization.get('pendingCopies',[])
    if not isinstance(previous_errors,list) or any(not isinstance(x,dict) for x in previous_errors):raise ValueError('Existing pending copies must be an array of objects')
    for item in inputs:
        try:
            destination,digest,action=copy_file(item,root)
            value={'sourcePath':str(item['source']),'sourceGiven':item['sourceGiven'],'destinationRelativePath':destination.relative_to(root).as_posix(),'category':item['category'],'bytes':destination.stat().st_size,'sha256':digest,'copyOrMove':'copy','action':action}
            if not any(x.get('sourcePath')==value['sourcePath'] and x.get('destinationRelativePath')==value['destinationRelativePath'] and x.get('sha256')==digest for x in records):records.append(value)
            imported.append(value)
        except (OSError,ValueError) as exc:
            errors.append({'sourcePath':str(item['source']),'category':item['category'],'reason':str(exc)})
    attempted={str(item['source']) for item in inputs}
    pending=[entry for entry in previous_errors if entry.get('sourcePath') not in attempted]+errors
    organization['pendingCopies']=pending
    organization['status']='needs-attention' if pending else 'provided-files-organized' if records else organization.get('status','awaiting-materials')
    initial_stages={'awaiting-materials','not-started','provided-materials-organized; validate-video-next'}
    if records and not pending and data.get('intakeStage') in initial_stages:data['intakeStage']='provided-materials-organized; validate-video-next'
    save_record(record,data)
    if inputs:
        with log.open('a',encoding='utf-8') as stream:
            stream.write(f'\n素材归档：本次核对{len(imported)}项，待处理{len(pending)}项。用户原文件保持；本次助手未执行原生剪辑。详细源/目标/摘要见课程项目.json。\n')
    return {'courseTitle':original,'projectDirectory':str(root),'directoryName':root.name,'createdOrReused':'reused' if existing else 'initialized','inputDirectories':{name:str(root/name) for name in CATEGORIES},'providedFilesOrganized':len(imported),'pendingCopies':pending,'sourceFilesMoved':False,'nativeEditingStarted':False,'nextAction':'resolve pending files before editing' if pending else 'continue this course using its saved state' if existing else 'validate original video then ask unknown rough-cut status' if records else 'remind user to place materials in the five categories'},not pending


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',required=True,type=Path)
    parser.add_argument('--title',required=True)
    parser.add_argument('--date',required=True,help='Client/user local project creation date, YYYYMMDD; reuse the original date for the same project')
    parser.add_argument('--assets-json',type=Path)
    parser.add_argument('--adopt-existing',action='store_true',help='Only after establishing that the unmarked directory belongs to this course')
    args=parser.parse_args()
    try:
        result,ok=initialize(args.workspace,args.title,args.date,args.assets_json,args.adopt_existing)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if ok else 2
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'ok':False,'error':str(exc),'nativeEditingStarted':False},ensure_ascii=False));return 2


if __name__=='__main__':raise SystemExit(main())
