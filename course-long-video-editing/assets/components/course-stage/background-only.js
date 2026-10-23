import {defaults} from './defaults.js';
import {createBackground} from './background.js';
export default function mount({root,props,viewport}){let p={...defaults,...(props||{})};const bg=createBackground(root.querySelector('.bg-host'),{width:viewport.width,height:viewport.height,id:'background-only'});return{update({props}){p={...defaults,...(props||{})};},render(){bg.render(p,{s:p.cameraScale??.77,fx:p.cameraX??0,fy:p.cameraY??0},.77);},dispose(){bg.dispose();}};}
