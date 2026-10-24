import {defaults} from './defaults.js';
import {createBackground} from './background.js';
import {cameraAt,validateShots,phase,mix} from './camera.js';
import {createStage,createPaper} from './surface.js';
// Self-authored teaching illustration. Replace copy for each lesson; no source
// screenshot, scientific claim, person, narration, or saved project ID is built in.
export default async function mount({root,props,timeline}){
 let p={...defaults,...(props||{})},shots;
 const scene=root.querySelector('.course-scene'),chrome=root.querySelector('.course-chrome'),footer=root.querySelector('.course-source');
 const bg=createBackground(scene,{id:'course-stage'}),stage=createStage(scene),doc=scene.ownerDocument;
 const plate=createPaper(stage.world,{width:1420,height:860});
 const left=createPaper(stage.world,{x:-350,y:-20,z:30,width:640,height:500,rotation:-1.4});
 const right=createPaper(stage.world,{x:350,y:-20,z:36,width:640,height:500,rotation:1.4});
 const ticket=createPaper(stage.world,{x:-350,y:220,z:130,width:570,height:190});
 const finalSheet=createPaper(stage.world,{x:0,y:80,z:155,width:1170,height:430});
 function block(parent,className,text){const n=doc.createElement('div');n.className=className;n.textContent=text;parent.append(n);return n;}
 const baseLayout=block(plate.content,'sheet-layout',''),baseTitle=block(baseLayout,'sheet-title',''),baseNote=block(baseLayout,'sheet-label','');
 function column(paper){const layout=block(paper.content,'sheet-layout','');return{layout,label:block(layout,'sheet-label',''),title:block(layout,'sheet-title sheet-accent',''),body:block(layout,'sheet-body',''),detail:block(layout,'sheet-detail','')};}
 const a=column(left),b=column(right),small=block(ticket.content,'card-layout',''),ticketLabel=block(small,'sheet-label',''),ticketBody=block(small,'card-body sheet-accent','');
 const finish=block(finalSheet.content,'sheet-layout',''),finishLabel=block(finish,'sheet-label',''),finishTitle=block(finish,'sheet-title sheet-accent',''),finishBody=block(finish,'sheet-body',''),finishNote=block(finish,'sheet-detail','');
 finish.style.width='835px';
 const primaryNodes={goalTitle:a.title,goalBody:a.body,goalDetail:a.detail,draftTitle:b.title,draftBody:b.body,draftDetail:b.detail,ticket:ticketBody,resultTitle:finishTitle,resultBody:finishBody,resultNote:finishNote};for(const [id,n] of Object.entries(primaryNodes))n.setAttribute('data-primary-id',id);
 function bind(){
  shots=validateShots(JSON.parse(p.cameraJSON),p.seconds);scene.style.fontFamily=p.font;root.querySelector('.eyebrow').textContent=p.eyebrow;root.querySelector('h1').textContent=p.title;root.querySelector('.course-note').textContent=p.note;footer.textContent=p.sourceNote;
  baseTitle.textContent=p.sheetTitle;baseNote.textContent=p.sheetNote;
  a.label.textContent=p.leftLabel;a.title.textContent=p.leftTitle;a.body.textContent=p.leftBody;a.detail.textContent=p.leftDetail;
  b.label.textContent=p.rightLabel;b.title.textContent=p.rightTitle;b.body.textContent=p.rightBody;b.detail.textContent=p.rightDetail;
  ticketLabel.textContent=p.ticketLabel;ticketBody.textContent=p.ticketA;finishLabel.textContent=p.resultLabel;finishTitle.textContent=p.resultTitle;finishBody.textContent=p.resultBody;finishNote.textContent=p.resultNote;
  scene.style.setProperty('--course-accent',p.accentColor);
  for(const n of scene.querySelectorAll('.sheet-accent'))n.style.color=p.accentColor;
 }
 await doc.fonts.load(`700 60px "${p.font}"`);bind();
 return{update({props}){p={...defaults,...(props||{})};bind();},render({timeSeconds}){
  const t=Math.max(0,timeSeconds),cam=cameraAt(t,shots,p.readingPushStrength),move=phase(t,p.moveAt,p.moveAt+.42),result=phase(t,p.resultAt,p.resultAt+.46),oldInk=1-phase(t,p.resultAt-.18,p.resultAt+.16);
  bg.render(p,cam,.77);stage.render(cam);chrome.style.opacity=String(phase(t,.08,.5)*(1-phase(cam.s,.87,.96)));footer.style.opacity=String(phase(t,.6,1));
  left.set({tone:1-.28*move,contentOpacity:1-.35*move});right.set({tone:1,contentOpacity:.38+.62*move});
  ticket.set({pose:`translate3d(${mix(0,700,move)}px,0,${130+result*20}px) rotateZ(${mix(-1.3,1.3,move)}deg)`,reveal:1-result});ticketBody.textContent=move>.5?p.ticketB:p.ticketA;
  a.layout.style.opacity=String(oldInk);b.layout.style.opacity=String(oldInk);finalSheet.set({reveal:result});finish.style.opacity=String(phase(t,p.resultAt+.30,p.resultAt+.65));
 },dispose(){bg.dispose();stage.dispose();}};
}
