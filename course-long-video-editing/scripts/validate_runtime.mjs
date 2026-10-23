/** Local offline harness for the authored HTML components. Optional Playwright;
 * never installs packages, contacts a remote site, or drives the editor UI. */
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const args=process.argv.slice(2),get=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const skillRoot=path.resolve(get('--skill-root',path.join(path.dirname(fileURLToPath(import.meta.url)),'..'))),out=path.resolve(get('--output','runtime-evidence'));
let modulePath=get('--playwright-module',null),playwright;
try{playwright=modulePath?createRequire(import.meta.url)(path.resolve(modulePath)):createRequire(import.meta.url)('playwright');}catch{console.log(JSON.stringify({ok:null,state:'not-run',reason:'Playwright module unavailable; provide --playwright-module or record native-only checks'}));process.exit(3);}
fs.mkdirSync(out,{recursive:true});
const mime={'.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.html':'text/html','.json':'application/json','.ttf':'font/ttf'};
const server=http.createServer((req,res)=>{try{const u=new URL(req.url,'http://localhost'),p=path.resolve(skillRoot,'.'+decodeURIComponent(u.pathname));if(!p.startsWith(skillRoot+path.sep)||!fs.statSync(p).isFile())throw new Error('out of root');res.setHeader('Content-Type',mime[path.extname(p)]||'application/octet-stream');res.end(fs.readFileSync(p));}catch{res.statusCode=404;res.end('not found');}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const base=`http://127.0.0.1:${server.address().port}`;
let browser;const errors=[],checks=[];
try{
 browser=await playwright.chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(base+'/assets/components/course-stage/index.html');
 await page.addStyleTag({content:`@font-face{font-family:MiSans;src:url('${base}/assets/fonts/MiSans-Regular.ttf')}@font-face{font-family:MiSans;font-weight:700;src:url('${base}/assets/fonts/MiSans-Bold.ttf')}`});
 await page.evaluate(async(base)=>{
  const host=document.createElement('div');Object.assign(host.style,{position:'absolute',inset:'0',width:'1920px',height:'1080px'});document.body.replaceChildren(host);window.testHost=host;
  window.loadComponent=async(entry,values,viewport={width:1920,height:1080},seconds=24)=>{
   if(window.activeComponent)window.activeComponent.dispose();host.replaceChildren();
   const url=base+'/'+entry,parsed=new DOMParser().parseFromString(await(await fetch(url)).text(),'text/html'),dir=url.slice(0,url.lastIndexOf('/')+1);
   for(const style of parsed.querySelectorAll('style,link[rel="stylesheet"]')){const copy=style.cloneNode(true);if(copy.tagName==='LINK')copy.href=new URL(copy.getAttribute('href'),dir).href;host.append(copy);}
   const content=document.createElement('div');Object.assign(content.style,{position:'absolute',inset:'0'});for(const child of parsed.body.children)if(!['STYLE','LINK','SCRIPT'].includes(child.tagName))content.append(child.cloneNode(true));host.append(content);
   const script=parsed.querySelector('script[type="module"]');let entryUrl=script?.getAttribute('src');let mount;
   if(entryUrl)mount=(await import(new URL(entryUrl,dir).href)).default;
   else{const blob=URL.createObjectURL(new Blob([script.textContent.replace(/from\s+(['"])\.\/defaults.js\1/g,`from '${dir}defaults.js'`)],{type:'text/javascript'}));mount=(await import(blob)).default;URL.revokeObjectURL(blob);}
   const input=document.createElement('canvas');input.width=viewport.width;input.height=viewport.height;window.fixtureInput=input;
   window.drawInput=t=>{const c=input.getContext('2d');c.fillStyle='#274653';c.fillRect(0,0,input.width,input.height);c.fillStyle='#E802F8';c.fillRect((.1+.6*(t/8))*input.width,.35*input.height,.12*input.width,.3*input.height);c.fillStyle='#fff';c.font='bold 70px MiSans';c.fillText('合成输入 '+t.toFixed(2)+'s',80,140);};window.drawInput(0);
   window.activeComponent=await mount({root:content,props:values,input,viewport,timeline:{durationInSeconds:seconds,durationInFrames:Math.round(seconds*60),fps:60}});window.contentRoot=content;await document.fonts.ready;
  };
 },base);
 const load=async(entry,values={},seconds=24)=>page.evaluate(async({entry,values,seconds})=>window.loadComponent(entry,values,{width:1920,height:1080},seconds),{entry,values,seconds});
 const render=async(t,frame)=>page.evaluate(({t,frame})=>{window.drawInput(t);window.activeComponent.render({timeSeconds:t,frame:frame??Math.round(t*60),progress:t/24});}, {t,frame});
 const readable=async ids=>page.evaluate(ids=>{
  const hidden=[];for(const n of window.contentRoot.querySelectorAll('*')){let alpha=1;for(let p=n;p&&p!==window.contentRoot;p=p.parentElement)alpha*=Number(getComputedStyle(p).opacity);if(alpha<.05){hidden.push([n,n.style.pointerEvents]);n.style.pointerEvents='none';}}
  const bad=[];
  for(const id of ids){const el=window.contentRoot.querySelector(`[data-primary-id="${id}"]`);if(!el){bad.push(id+':missing');continue;}const range=document.createRange();range.selectNodeContents(el);for(const r of range.getClientRects()){
   if(r.x<4||r.y<4||r.right>1916||r.bottom>1020){bad.push(id+':outside-reading-frame');continue;}
   for(const x of [.2,.5,.8])for(const y of [.3,.7]){const hit=document.elementFromPoint(r.x+r.width*x,r.y+r.height*y);if(!(hit===el||el.contains(hit)))bad.push(id+':occluded');}
  }}
  for(const[n,value]of hidden)n.style.pointerEvents=value;return [...new Set(bad)];
 },ids);
 await load('assets/components/course-stage/index.html');
 for(const t of [0,2,5.5,10,14.8,18.9,21,23.5]){await render(t);await page.screenshot({path:path.join(out,`stage-${String(t).replace('.','_')}.png`)});}
 const paper=await page.evaluate(()=>[...window.contentRoot.querySelectorAll('.course-paper')].map(n=>({opacity:getComputedStyle(n).opacity,faceAlpha:getComputedStyle(n.querySelector('.course-paper-face')).backgroundColor,filter:n.querySelector('.course-paper-face').style.filter})));
 checks.push({check:'opaque-paper-faces',ok:paper.every(p=>!p.faceAlpha.startsWith('rgba(')),scope:'ordinary face alpha; reveal opacity checked separately'});
 for(const [t,ids]of [[5.5,['goalTitle','goalBody','goalDetail','ticket']],[11,['draftTitle','draftBody','draftDetail','ticket']],[21,['resultTitle','resultBody','resultNote']]]){await render(t);const issues=await readable(ids);checks.push({check:'primary-reading-clearance-'+t,ok:issues.length===0,issues});}
 await render(5.5);await page.evaluate(()=>{const n=window.contentRoot.querySelector('[data-primary-id="ticket"]').closest('.course-paper');window.savedTicketTop=n.style.top;n.style.top='-5px';});
 const badFixture=await readable(['goalBody','goalDetail']);checks.push({check:'negative-occlusion-regression-detected',ok:badFixture.some(x=>x.includes('occluded'))});await page.screenshot({path:path.join(out,'regression-occlusion-before.png')});
 await page.evaluate(()=>window.contentRoot.querySelector('[data-primary-id="ticket"]').closest('.course-paper').style.top=window.savedTicketTop);await page.screenshot({path:path.join(out,'regression-occlusion-after.png')});
 await render(10);const first=await page.screenshot();await render(2);await render(10);const second=await page.screenshot();checks.push({check:'out-of-order-seek',ok:first.equals(second)});
 const metrics=await page.evaluate(()=>[...window.contentRoot.querySelectorAll('.sheet-title,.sheet-body,.sheet-detail,.card-body')].map(n=>({text:n.textContent,rect:(r=>({x:r.x,y:r.y,width:r.width,height:r.height}))(n.getBoundingClientRect())})));fs.writeFileSync(path.join(out,'layout-metrics.json'),JSON.stringify(metrics,null,2));
 await load('assets/templates/identity-slash/speaker.html');await render(1.2);checks.push({check:'identity-default-mount',ok:await page.locator('.name').textContent()==='Rico'});
 await page.evaluate(()=>window.activeComponent.update({props:{name:'示范讲师',identity:'已确认身份',seconds:6}}));await render(2);checks.push({check:'identity-editable-copy',ok:await page.locator('.name').textContent()==='示范讲师'});await page.screenshot({path:path.join(out,'identity.png')});
 const q=JSON.parse(fs.readFileSync(path.join(skillRoot,'assets/templates/quote-highlight-follow/defaults.json'),'utf8'));await load('assets/templates/quote-highlight-follow/quote.html',q,5.2);await render(4.5);checks.push({check:'quote-exact-cues',ok:await page.locator('.q-hybrid').getAttribute('data-cue-status')==='exact'});await page.screenshot({path:path.join(out,'quote.png')});
 await load('assets/components/presenter-circle/effect.html',{seconds:8},8);await page.evaluate(()=>{window.drawInput(0);window.activeComponent.render({timeSeconds:0,frame:0,progress:0});});
 checks.push({check:'presenter-full-first',ok:await page.evaluate(()=>{const a=window.fixtureInput.getContext('2d').getImageData(0,0,1920,1080).data,b=window.contentRoot.querySelector('canvas').getContext('2d').getImageData(0,0,1920,1080).data;return a.every((v,i)=>v===b[i]);})});
 await page.evaluate(()=>{window.drawInput(4);window.activeComponent.render({timeSeconds:4,frame:240,progress:.5});});const middle=await page.screenshot();await page.screenshot({path:path.join(out,'circle-middle.png')});
 await page.evaluate(()=>{window.drawInput(5);window.activeComponent.render({timeSeconds:5,frame:300,progress:.625});});const next=await page.screenshot();checks.push({check:'presenter-live-input-changes',ok:!middle.equals(next)});
 await page.evaluate(()=>{window.drawInput(8);window.activeComponent.render({timeSeconds:8,frame:479,progress:1});});checks.push({check:'presenter-restores-current-input',ok:await page.evaluate(()=>{const a=window.fixtureInput.getContext('2d').getImageData(0,0,1920,1080).data,b=window.contentRoot.querySelector('canvas').getContext('2d').getImageData(0,0,1920,1080).data;return a.every((v,i)=>v===b[i]);})});
}catch(e){errors.push(String(e.stack||e));}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
const report={ok:!errors.length&&checks.every(x=>x.ok),checks,errors,scope:'Local Chromium layout/seek/input harness with bundled fonts; native rendering, human listening and physical colleague machines are separate.'};fs.writeFileSync(path.join(out,'runtime-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));process.exitCode=report.ok?0:2;
