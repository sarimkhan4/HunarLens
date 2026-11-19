export const skillsPercent = value => typeof value === 'number' ? (value * 100).toFixed(1) + '%' : String(value);
export function formatSkillsEstimate(row) {
  if (typeof row.estimate !== 'number') return String(row.estimate);
  const range = row.reliability === 'mode unstable' ? 'mode unstable; bootstrap range ' : 'interval ';
  return skillsPercent(row.estimate) + ' · ' + range + skillsPercent(row.ci_low) + '–' + skillsPercent(row.ci_high) + (row.flag ? ' · ' + row.flag : '');
}
export function renderSkills(root, skills) {
  const $ = id => root.querySelector('#' + id);
  const pct = skillsPercent, show = formatSkillsEstimate;
  const one = (rows, group, category) => rows.find(row => row.group === group && row.category === category);
  const table = (id, headers, rows) => {
    const container = $(id); container.replaceChildren();
    const t = document.createElement('table');
    const head = t.createTHead().insertRow();
    headers.forEach(text => {const th = document.createElement('th'); th.scope = 'col'; th.textContent = text; head.appendChild(th);});
    const body = t.createTBody();
    rows.forEach(values => {const tr = body.insertRow(); values.forEach((value, index) => {
      const cell = index === 0 ? document.createElement('th') : document.createElement('td');
      if (index === 0) cell.scope = 'row';
      cell.textContent = value; tr.appendChild(cell);
    });});
    container.appendChild(t);
  };
  const bands = ['No formal','Below matric','Matric','Intermediate','Degree or above'];
  const unemployment = skills.unemployment_by_education;
  const noFormal = one(unemployment,'overall','No formal'), degree = one(unemployment,'overall','Degree or above');
  const trainingEmployed = one(skills.attainment_gap,'overall; employed','Training ever/current');
  const trainingUnemployed = one(skills.attainment_gap,'overall; unemployed','Training ever/current');
  const trainingGap = one(skills.attainment_difference,'overall','Training ever/current');
  const strict = [...skills.mismatch, ...skills.mismatch_sensitivity].filter(r => r.group.startsWith('overall; norm=') && r.group !== 'overall; norm=ISCO' && r.category === 'over');
  const strictValues = strict.map(r => r.estimate);
  const neet = one(skills.neet,'overall','not employed and not enrolled');
  const official = skills.neet_external[0];
  const kpis = [
    ['Unemployment by education',pct(noFormal.estimate)+' / '+pct(degree.estimate),'No formal (n='+noFormal.n+') / degree or above (n='+degree.n+')'],
    ['Training: unemployed / employed',pct(trainingUnemployed.estimate)+' / '+pct(trainingEmployed.estimate),'Difference: '+(trainingGap.difference*100).toFixed(1)+' percentage points'],
    ['Above typical education level',pct(Math.min(...strictValues))+'–'+pct(Math.max(...strictValues)),'Strict comparison across statistical norms; n='+strict[0].n],
    ['Approximate NEET / PBS NEET',pct(neet.estimate)+' / '+pct(official.estimate),'Different definitions · survey n='+neet.n]
  ];
  const kpiContainer = $('skills-kpis'); kpiContainer.replaceChildren();
  kpis.forEach(([title,value,note]) => {const card=document.createElement('article');card.className='card';
    const tag=document.createElement('span');tag.className='tag';tag.textContent=title.includes('PBS')?'Our analysis / Official survey':'Our analysis';card.appendChild(tag);
    const label=document.createElement('div');label.className='kpi-top';label.textContent=title;card.appendChild(label);
    const number=document.createElement('div');number.className='kpi-value';number.textContent=value;card.appendChild(number);
    const foot=document.createElement('div');foot.className='kpi-foot';foot.textContent=note;card.appendChild(foot);kpiContainer.appendChild(card);});
  const outcomes = skills.outcomes_by_education;
  const categories = ['employed matched','employed over','employed under','unemployed'];
  const labels = ['Employed: typical level','Employed: above typical','Employed: below typical','Unemployed'];
  const outcomeRows = bands.map(band => [band,...categories.map(category => {
    const row=one(outcomes,band,category); return show(row)+' (n='+row.positive_n+')';
  })]);
  table('skills-outcomes-table',['Education',...labels],outcomeRows);
  const chart=$('skills-outcomes');chart.replaceChildren();
  bands.forEach(band=>{const group=document.createElement('div');group.className='skills-bar-group';
    const title=document.createElement('strong');title.textContent=band;group.appendChild(title);
    const bar=document.createElement('div');bar.className='skills-stack';
    const values=document.createElement('div');values.className='skills-chart-values';
    categories.forEach((category,index)=>{const row=one(outcomes,band,category), segment=document.createElement('span');
      segment.className='skills-segment skills-segment-'+index;
      const value=typeof row.estimate==='number' ? pct(row.estimate) : String(row.estimate);
      segment.textContent=typeof row.estimate==='number'&&row.estimate>=.06 ? value : '';
      segment.title=labels[index]+': '+show(row)+'; n='+row.positive_n;
      segment.setAttribute('aria-label',segment.title);
      if(typeof row.estimate==='number')segment.style.flex='0 0 '+(row.estimate*100)+'%';
      else segment.hidden=true;
      const detail=document.createElement('span');detail.textContent=labels[index]+': '+value;values.appendChild(detail);
      bar.appendChild(segment);});group.appendChild(bar);group.appendChild(values);chart.appendChild(group);});
  const legend=document.createElement('div');legend.className='skills-legend';
  labels.forEach((label,index)=>{const item=document.createElement('span');item.className='skills-key skills-segment-'+index;item.textContent=label;legend.appendChild(item);});chart.appendChild(legend);
  const groups=[['overall','All youth'],['sex=1.0','Male'],['sex=2.0','Female'],['area=1.0','Rural'],['area=2.0','Urban']];
  function selector(id, options, render) {const select=$(id), old=select.value;select.replaceChildren();options.forEach(([value,label])=>{const option=document.createElement('option');option.value=value;option.textContent=label;select.appendChild(option);});if(options.some(([v])=>v===old))select.value=old;select.onchange=()=>render(select.value);render(select.value);}
  selector('skills-unemployment-group',groups,group=>table('skills-unemployment',['Education','Unemployed n','Labour-force n','Rate and interval'],unemployment.filter(r=>r.group===group).map(r=>[r.category,r.positive_n,r.n,show(r)])));
  selector('skills-graduate-group',groups,group=>table('skills-graduates',['Outcome','Outcome n','Labour-force n','Share and interval'],skills.graduate_absorption.filter(r=>r.group===group).map(r=>[r.category,r.positive_n,r.n,show(r)])));
  const attainmentGroups=[...new Set(skills.attainment_difference.map(row=>row.group))].map(group=>[group,(groups.find(([key])=>key===group)||[])[1]||group.replace('province=','Province ').replace('age_band=','Age ').replaceAll(', area=',', area ')]);
  selector('skills-attainment-group',attainmentGroups,group=>{
    const rows=skills.attainment_difference.filter(row=>row.group===group);
    const text=row=>typeof row.difference==='number'?(row.difference*100).toFixed(1)+' pp ('+(row.ci_low*100).toFixed(1)+' to '+(row.ci_high*100).toFixed(1)+' pp)':String(row.difference);
    table('skills-attainment-table',['Attainment','Employed n','Unemployed n','Difference and interval'],rows.map(row=>[row.category,row.employed_n,row.unemployed_n,text(row)]));
    const chart=$('skills-attainment-chart');chart.replaceChildren();
    const maximum=Math.max(...rows.map(row=>typeof row.difference==='number'?Math.abs(row.difference):0))||1;
    rows.forEach(row=>{const line=document.createElement('div');line.className='skills-gap-row';const label=document.createElement('span');label.textContent=row.category;const track=document.createElement('span');track.className='skills-gap-track';const bar=document.createElement('span');bar.className='skills-gap-fill';if(typeof row.difference==='number'){bar.style.width=(Math.abs(row.difference)/maximum*50)+'%';bar.style[row.difference<0?'right':'left']='50%';}track.appendChild(bar);const value=document.createElement('strong');value.textContent=text(row);line.append(label,track,value);chart.appendChild(line);});
  });
  const options=[['all','Strict: all employed'],['youth','Strict: youth only'],['within','Within one band: all employed'],['severe','Two or more bands above: all employed'],['isco','Normative ISCO']];
  selector('skills-definition',options,choice=>{
    const config={all:['overall; norm=all_15_plus','over','all_15_plus'],youth:['overall; norm=youth','over','youth'],isco:['overall; norm=ISCO','over','ISCO'],within:['all_15_plus','within one band','within one band'],severe:['all_15_plus','two or more bands above','two or more bands above']}[choice];
    const overall=choice==='within'||choice==='severe'?one(skills.mismatch_variants,config[0],config[1]):one([...skills.mismatch,...skills.mismatch_sensitivity],config[0],config[1]);
    $('skills-mismatch-overall').textContent='Overall: '+show(overall)+' · denominator n='+overall.n+' · cell n='+overall.positive_n;
    const rows=(choice==='within'||choice==='severe'?skills.mismatch_occupation_variants:skills.mismatch_by_occupation).filter(r=>r.group===config[2]);
    table('skills-mismatch',['Occupation group','Cell n','Denominator n','Share and uncertainty'],rows.map(r=>[r.category,r.positive_n,r.n,show(r)]));
  });
  const occupations=[...new Set(skills.education_occupation_matrix.map(row=>row.category).filter(category=>/^occupation \d+$/.test(category)))];
  table('skills-matrix',['Education',...occupations],bands.map(band=>[band,...occupations.map(occupation=>{const row=one(skills.education_occupation_matrix,band,occupation);return pct(row.estimate)+' (n='+row.positive_n+')';})]));
  $('skills-matrix').querySelectorAll('tbody tr').forEach((tr,index)=>{tr.querySelectorAll('td').forEach((td,column)=>{const row=one(skills.education_occupation_matrix,bands[index],occupations[column]);if(typeof row.estimate==='number')td.style.backgroundColor='rgba(29, 112, 131, '+Math.min(.24,row.estimate*.35)+')';});});
  table('skills-neet',['Survey group','Total n','Share and interval'],groups.map(([group,label])=>{const row=one(skills.neet,group,'not employed and not enrolled');return [label,row.n,show(row)];}));
}
