// Section anchors match this single-page React application's real IDs.
// Only verified public HTTPS resource links open in a new tab.
export const FOOTER_SECTIONS = [
  { title: 'Explore', links: [
    { label: 'Home', href: '#overview' },
    { label: 'Explore Earth', href: '#global' },
    { label: 'Regional Comparison', href: '#compare' },
    { label: 'Research Library', href: '#research' },
  ] },
  { title: 'Resources', links: [
    { label: 'NASA', href: 'https://www.nasa.gov/', external: true },
    { label: 'NASA POWER', href: 'https://power.larc.nasa.gov/', external: true },
    { label: 'NASA Giovanni', href: 'https://giovanni.gsfc.nasa.gov/', external: true },
    { label: 'Natural Earth', href: 'https://www.naturalearthdata.com/', external: true },
  ] },
];
export const FOOTER_EXTERNAL = FOOTER_SECTIONS.flatMap(section => section.links.filter(link => link.external));
