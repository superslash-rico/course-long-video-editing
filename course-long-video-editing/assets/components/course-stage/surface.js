// The 2D stacking boundary is outside the preserve-3d world. Ordinary paper
// remains opaque when dimmed; opacity is reserved for intentional reveal/exit.
export function createStage(root,{x=755,y=540,perspective=2500}={}){
 const doc=root.ownerDocument,layer=doc.createElement('div'),lens=doc.createElement('div'),world=doc.createElement('div');
 Object.assign(layer.style,{position:'absolute',inset:'0',zIndex:'10',isolation:'isolate'});
 Object.assign(lens.style,{position:'absolute',left:x+'px',top:y+'px',width:'1px',height:'1px',perspective:perspective+'px',perspectiveOrigin:'0px 0px',transformStyle:'preserve-3d'});
 Object.assign(world.style,{position:'absolute',width:'1px',height:'1px',transformStyle:'preserve-3d',transformOrigin:'0px 0px'});
 layer.append(lens);lens.append(world);root.append(layer);
 return{element:layer,world,render(p){world.style.transform=`scale(${p.s}) rotateX(${p.rx??0}deg) rotateY(${p.ry??0}deg) rotateZ(${p.rz??0}deg) translate(${-p.fx}px,${-p.fy}px)`;},dispose(){layer.remove();}};
}
export function createPaper(parent,{x=0,y=0,z=0,width=600,height=500,rotation=0,color='#FBF7FD',ink='#24182D'}={}){
 const doc=parent.ownerDocument,outer=doc.createElement('div'),shadow=doc.createElement('div');outer.className='course-paper';
 Object.assign(outer.style,{position:'absolute',left:x-width/2+'px',top:y-height/2+'px',width:width+'px',height:height+'px',transformStyle:'preserve-3d',transform:`translateZ(${z}px) rotateZ(${rotation}deg)`});
 Object.assign(shadow.style,{position:'absolute',inset:'-5px',borderRadius:'8px',background:'rgba(25,10,34,.50)',filter:'blur(15px)',transform:'translate3d(7px,10px,-18px)'});outer.append(shadow);
 [9,6,3].forEach((d,i)=>{const edge=doc.createElement('div');Object.assign(edge.style,{position:'absolute',inset:'0',borderRadius:'6px',background:['#CBB7D8','#DDD0E5','#EEE5F3'][i],transform:`translate3d(${-i}px,${i}px,${-d}px)`});outer.append(edge);});
 const face=doc.createElement('div'),content=doc.createElement('div');face.className='course-paper-face';content.className='course-paper-content';
 Object.assign(face.style,{position:'absolute',inset:'0',background:color,color:ink,borderRadius:'6px',boxShadow:'inset 0 0 0 1px #E0D3E8',backfaceVisibility:'hidden'});Object.assign(content.style,{position:'absolute',inset:'0'});face.append(content);outer.append(face);parent.append(outer);
 return{element:outer,face,content,set({reveal=1,tone=1,contentOpacity=1,pose}={}){outer.style.opacity=String(reveal);face.style.filter=tone<1?`brightness(${Math.max(.1,tone)})`:'';content.style.opacity=String(contentOpacity);if(pose)outer.style.transform=pose;},dispose(){outer.remove();}};
}
