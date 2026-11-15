// Geographic polygon selection utilities: coordinates are WGS84 [longitude,latitude].
import {validateBounds} from './geography.mjs';
export function validatePolygon(points){
 if(!Array.isArray(points)||points.length<4||points.length>26)throw Error('Provide 3–25 polygon vertices and close the polygon.');
 if(points.some(p=>!Array.isArray(p)||p.length!==2||p.some(n=>typeof n!=='number'||!Number.isFinite(n))))throw Error('Invalid WGS84 polygon coordinates.');
 if(points[0][0]!==points.at(-1)[0]||points[0][1]!==points.at(-1)[1])throw Error('Polygon must be closed.');
 const distinct=new Set(points.slice(0,-1).map(p=>p.join(',')));
 if(distinct.size<3)throw Error('Polygon requires three distinct points.');
 const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
 const bbox=[Math.min(...xs),Math.min(...ys),Math.max(...xs),Math.max(...ys)];validateBounds(bbox);
 if(bbox[2]-bbox[0]>25||bbox[3]-bbox[1]>25)throw Error('Polygon extent cannot exceed 25 degrees per axis.');
 let twiceArea=0;for(let i=1;i<points.length;i++)twiceArea+=points[i-1][0]*points[i][1]-points[i][0]*points[i-1][1];
 if(Math.abs(twiceArea)<1e-9)throw Error('Polygon has zero area.');
 return {bbox,polygon:points};
}
export function closePolygon(points){return validatePolygon([...points,points[0]]);}
export function mapPointFromClient(clientX,clientY,rect,view){
 if(!rect||!(rect.width>0&&rect.height>0))throw Error('Map dimensions unavailable');
 const x=view.x+(clientX-rect.left)/rect.width*view.width;
 const y=view.y+(clientY-rect.top)/rect.height*view.height;
 const lon=Math.max(-180,Math.min(180,(x/400)*360-180));
 const lat=Math.max(-90,Math.min(90,90-(y/220)*180));
 return [Number(lon.toFixed(4)),Number(lat.toFixed(4))];
}
export function zoomMap(view,multiplier){const width=Math.min(400,Math.max(20,view.width/multiplier));const height=width*220/400;return {x:Math.max(0,Math.min(400-width,view.x+(view.width-width)/2)),y:Math.max(0,Math.min(220-height,view.y+(view.height-height)/2)),width,height};}
export function panMap(view,dx,dy){return {...view,x:Math.max(0,Math.min(400-view.width,view.x+dx)),y:Math.max(0,Math.min(220-view.height,view.y+dy))};}

// Preview size without accepting or silently clipping an invalid research polygon.
export function polygonExtent(vertices){
 if(!Array.isArray(vertices)||vertices.length<2)return null;
 const xs=vertices.map(p=>p[0]),ys=vertices.map(p=>p[1]);
 return {width:Math.max(...xs)-Math.min(...xs),height:Math.max(...ys)-Math.min(...ys)};
}
// NASA POWER is point-based, so it can use a point even if a draft region is too large
// for operator-approved area extraction. Never represent this as a polygon mean.
export function pointCenterFromSelection(bounds,draft=[]){
 let b=bounds;
 if(Array.isArray(draft)&&draft.length>=2){
  const xs=draft.map(p=>p[0]),ys=draft.map(p=>p[1]);
  b=[Math.min(...xs),Math.min(...ys),Math.max(...xs),Math.max(...ys)];
 }
 if(!Array.isArray(b)||b.length!==4||b.some(n=>!Number.isFinite(n)))throw Error('Valid point bounds required');
 return {lon:(b[0]+b[2])/2,lat:(b[1]+b[3])/2};
}
