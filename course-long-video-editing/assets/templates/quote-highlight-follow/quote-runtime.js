const clamp=n=>Math.max(0,Math.min(1,n));
const ease=n=>1-Math.pow(1-clamp(n),3);
const escape=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
function hash(s){let n=5381;for(let i=0;i<s.length;i++)n=((n*33)^s.charCodeAt(i))>>>0;return n.toString(16);}

export default function mount({root,props}){
 const card=root.querySelector('.q-hybrid'),wash=root.querySelector('.q-atmosphere'),copy=root.querySelector('.q-copy'),linesHost=root.querySelector('.q-lines');
 let values=props,tokens=[],cueStatus='exact';
 function bind(){
  card.style.fontFamily=values.font;card.style.color=values.textColor;
  const sourceLines=String(values.text).split('\n');
  const keywords=String(values.keywords).split(/[,，]/).map(x=>x.trim()).filter(Boolean).sort((a,b)=>b.length-a.length);
  const pattern=keywords.length?new RegExp('('+keywords.map(escape).join('|')+')','g'):null;
  let cues;try{cues=JSON.parse(values.cues);}catch{cues=[];}
  const total=Math.max(1,Number(values.seconds)),speechEnd=Math.max(.4,total-.42);
  linesHost.replaceChildren();tokens=[];cueStatus='exact';
  sourceLines.forEach((text,row)=>{
   const line=document.createElement('div');line.className='q-line';line.style.fontSize=(row===0?values.leadSize:values.mainSize)+'px';line.style.fontWeight=row===0?'400':'700';
   let rowCues=Array.isArray(cues)?cues.filter(c=>c.row===row).sort((a,b)=>a.from-b.from):[];
   const valid=rowCues.length&&rowCues[0].from===0&&rowCues[rowCues.length-1].to===text.length&&rowCues.every((c,i)=>c.from>=0&&c.to>c.from&&c.to<=text.length&&c.start<=c.end&&(!i||c.from===rowCues[i-1].to));
   if(!valid){cueStatus='fallback';rowCues=[{from:0,to:text.length,start:row*.28,end:speechEnd}];}
   for(const cue of rowCues){
    const word=document.createElement('span');word.className='q-word';
    const parts=pattern?text.slice(cue.from,cue.to).split(pattern):[text.slice(cue.from,cue.to)];
    const marks=[];
    for(const part of parts){if(!part)continue;if(keywords.includes(part)){
     const mark=document.createElement('span');mark.className='q-mark';
     const bg=document.createElement('span');bg.className='q-mark-bg';bg.style.backgroundColor=values.markerColor;
     const ink=document.createElement('span');ink.className='q-mark-ink';ink.textContent=part;
     mark.append(bg,ink);word.append(mark);marks.push({bg,ink});
    }else{const plain=document.createElement('span');plain.textContent=part;word.append(plain);}}
    line.append(word);tokens.push({element:word,start:Number(cue.start),end:Number(cue.end),marks});
   }
   linesHost.append(line);
  });
  const gradient=root.querySelector('radialGradient');const gradientId='q-fade-'+hash(String(values.text)+values.bgColor);gradient.setAttribute('id',gradientId);root.querySelector('.q-wash').setAttribute('fill','url(#'+gradientId+')');
  for(const stop of root.querySelectorAll('stop'))stop.setAttribute('stop-color',values.bgColor);
  root.querySelector('.q-leader').style.backgroundColor=values.accentColor;root.querySelector('.q-progress>span').style.backgroundColor=values.accentColor;
  card.dataset.cueStatus=cueStatus;
 }
 bind();
 return {
  update({props}){values=props;bind();},
  render({timeSeconds}){
   const t=Math.max(0,timeSeconds),duration=Math.max(1,Number(values.seconds));
   const enter=ease(t/.28),exit=ease((t-(duration-.35))/.35),opacity=enter*(1-exit);
   wash.style.opacity=String((values.transparentBackground?0:clamp(Number(values.bgOpacity)))*opacity);
   copy.style.opacity=String(opacity);copy.style.transform=`translateY(${(1-enter)*10-exit*4}px)`;
   root.querySelector('.q-leader').style.transform=`scaleX(${ease(t/.36)})`;
   root.querySelector('.q-progress>span').style.transform=`scaleX(${clamp(t/(duration-.42))})`;
   for(const token of tokens){
    const begun=t>=token.start,active=begun&&t<token.end,p=ease((t-token.start)/.22);
    token.element.style.opacity=String(begun?.35+.65*p:.22);
    token.element.style.color=active?values.activeColor:values.textColor;
    token.element.style.transform=`translateY(${begun?(1-p)*5:0}px) scale(${active?1.012:1})`;
    for(const mark of token.marks){mark.bg.style.opacity=String(begun?1:0);mark.bg.style.transform=`rotate(-.6deg) scaleX(${.95+.05*p})`;mark.ink.style.color=begun?values.inkColor:values.textColor;}
   }
  },
  dispose(){tokens=[];}
 };
}
