// Publicly available links only. Never invent team contacts or GitHub repository URLs.
export const FOOTER_SECTIONS = [
 {title:'EXPLORE',links:[
  {label:'Mission overview',href:'#overview'},
  {label:'Regional investigation',href:'#global'},
  {label:'Upload NASA observations',href:'#investigate'},
  {label:'Results and trend charts',href:'#analysis'},
  {label:'Compare regions',href:'#compare'}]},
 {title:'DATA & SCIENCE',links:[
  {label:'NASA product catalogue',href:'#product-catalog'},
  {label:'Source provenance',href:'#sources'},
  {label:'Methods and limitations',href:'#sources'},
  {label:'NASA Giovanni',href:'https://giovanni.gsfc.nasa.gov/giovanni/',external:true},
  {label:'NASA GES DISC',href:'https://disc.gsfc.nasa.gov/',external:true},
  {label:'NASA POWER',href:'https://power.larc.nasa.gov/',external:true}]},
 {title:'PROJECT & RESOURCES',links:[
  {label:'NASA Space Apps challenge',href:'https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/',external:true},
  {label:'Natural Earth boundaries',href:'https://www.naturalearthdata.com/',external:true},
  {label:'NASA Earthdata Search',href:'https://search.earthdata.nasa.gov/',external:true},
  {label:'Monthly climatology',href:'#seasons'},
  {label:'Research product documentation',href:'#product-catalog'}]}
];
export const FOOTER_EXTERNAL=FOOTER_SECTIONS.flatMap(s=>s.links.filter(l=>l.external));
