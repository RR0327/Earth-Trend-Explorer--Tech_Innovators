// Equirectangular projection only. Country geometry is provided by real Natural Earth GeoJSON.
export function geometryToSvgPath(geometry,width=400,height=220){
 if(!geometry || !['Polygon','MultiPolygon'].includes(geometry.type))return '';
 const polys=geometry.type==='Polygon'?[geometry.coordinates]:geometry.coordinates;
 const projected=[];
 for(const poly of polys){
  for(const ring of poly){
   if(!Array.isArray(ring) || ring.length<4)continue;
   const positions=ring.filter(p=>Array.isArray(p)&&Number.isFinite(p[0])&&Number.isFinite(p[1])&&p[0]>=-180&&p[0]<=180&&p[1]>=-90&&p[1]<=90);
   if(positions.length<4)continue;
   const point=p=>[+(((p[0]+180)/360)*width).toFixed(2),+(((90-p[1])/180)*height).toFixed(2)];
   const segments=[];
   let segment=[];
   let previous=null;
   for(const current of positions){
    if(previous && Math.abs(current[0]-previous[0])>180){if(segment.length>2)segments.push(segment);segment=[];}
    segment.push(point(current));previous=current;
   }
   if(segment.length>2)segments.push(segment);
   for(const s of segments)projected.push('M '+s.map(p=>p.join(' ')).join(' L ')+' Z');
  }
 }
 return projected.join(' ');
}
