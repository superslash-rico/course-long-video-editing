// Deterministic source-local pen paths. No frame-to-frame randomness or media IDs.
export function handMarkLayers(mark, sourceWidth, sourceHeight, unit = 1) {
 const [x,y,w,h]=mark.rect??[];
 if(![x,y,w,h,sourceWidth,sourceHeight,unit].every(Number.isFinite)||Math.min(x,y)<0||Math.min(w,h,sourceWidth,sourceHeight,unit)<=0||x+w>sourceWidth||y+h>sourceHeight)throw new Error('Annotation must remain within its source image');
 const seed=String(mark.seed??`${mark.type}:${x}:${y}:${w}:${h}`);
 let state=2166136261;for(const c of seed)state=Math.imul(state^c.charCodeAt(0),16777619)>>>0;
 const rnd=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296;};
 const f=n=>Number(n.toFixed(3)),p=(a,b)=>`${f(x+a*w)} ${f(y+b*h)}`;
 const color=mark.color??(mark.type==='highlight'?'#FFE259':'#DA332C'),stroke=(mark.stroke??3)/unit;
 let d,thickness=stroke,opacity=1,blend;
 if(mark.type==='highlight'){
  d=`M${p(.015,.52)} C${p(.24,.47+rnd()*.06)} ${p(.68,.54-rnd()*.05)} ${p(.985,.50)}`;
  thickness=h*.76;opacity=.30;blend='multiply';
 }else if(mark.type==='underline'){
  d=`M${p(.012,.85)} C${p(.25,.76+rnd()*.06)} ${p(.65,.94-rnd()*.04)} ${p(.99,.83)}`;
 }else if(mark.type==='circle'){
  d=`M${p(.52,.08)} C${p(.84,.025)} ${p(.995,.22)} ${p(.97,.54)} C${p(.96,.88)} ${p(.71,.98)} ${p(.40,.94)} C${p(.09,.965)} ${p(.015,.75)} ${p(.03,.44)} C${p(.05,.15)} ${p(.30,.02)} ${p(.57,.075)}`;
 }else if(mark.type==='bracket'){
  d=`M${p(.16,.07)} Q${p(.035,.045)} ${p(.045,.24)} L${p(.035,.76)} Q${p(.04,.96)} ${p(.18,.93)} M${p(.82,.065)} Q${p(.97,.04)} ${p(.96,.25)} L${p(.97,.76)} Q${p(.95,.97)} ${p(.81,.93)}`;
 }else if(mark.type==='check'){
  d=`M${p(.08,.53)} Q${p(.22,.69)} ${p(.36,.89)} C${p(.53,.57)} ${p(.73,.22)} ${p(.95,.08)}`;
 }else if(mark.type==='frame'){
  // Legacy explicit UI-selection framing; not the default annotation language.
  d=`M${p(.02,.04)} L${p(.98,.04)} L${p(.98,.96)} L${p(.02,.96)} Z`;
 }else throw new Error('Unknown source annotation type');
 if(!Number.isFinite(thickness)||thickness<=0)throw new Error('Invalid pen width');
 const layers=[{d,color,strokeWidth:thickness,opacity,blend}];
 if(mark.type==='highlight')layers.push({d:`M${p(.02,.68)} Q${p(.52,.66)} ${p(.98,.69)}`,color,strokeWidth:h*.18,opacity:.13,blend});
 else layers.push({d,color,strokeWidth:thickness*.42,opacity:.28,offsetX:(rnd()-.5)*stroke*.6,offsetY:(rnd()-.5)*stroke*.6});
 return layers;
}
