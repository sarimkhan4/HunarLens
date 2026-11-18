export default function({data, parentElement, setStateValue}) {
  const $ = id => parentElement.querySelector('#' + id);
  const root = parentElement;
  const active = root.activeElement;
  const focusId = active && active.id;
  let selection = null;
  try { if (active && active.selectionStart !== null) selection = [active.selectionStart, active.selectionEnd]; } catch (_) {}
  try {
  const sidebarNote=root.querySelector('.sidebar-bottom div');
  if(sidebarNote)sidebarNote.textContent='Frozen model · research use';
  root.querySelector('#page-explorer .sub').textContent='Explore the frozen model for youth aged 15–24 in the labour force. Association is not causation.';
  const pages = ['overview','explorer','performance','methodology'];
  const state = {...data.values};
  const results = data.result;
  function navigate(page) {
    pages.forEach(p => $('page-'+p).classList.toggle('active', p === page));
    root.querySelectorAll('[data-page]').forEach(b => {
      if (b.dataset.page === page) b.setAttribute('aria-current','page');
      else b.removeAttribute('aria-current');
    });
    $('crumb').textContent = ({overview:'Overview',explorer:'Profile explorer',performance:'Model performance',methodology:'Data & methodology'})[page];
  }
  root.querySelectorAll('[data-page]').forEach(b => b.onclick=()=>{navigate(b.dataset.page);setStateValue('page', b.dataset.page);});
  root.querySelectorAll('[data-goto]').forEach(b => b.onclick=()=>{navigate(b.dataset.goto);setStateValue('page', b.dataset.goto);});
  navigate(data.page);
  function send() {
    if (state.relationship_to_head === 1) {
      state.head_sex = state.sex;
      state.head_education = state.education_level;
    }
    setStateValue('profile', {...state});
  }
  const form=$('model-inputs');
  form.className='form-grid';
  form.style.gridColumn='1 / -1';
  data.fields.forEach(field=>{
    let div=form.querySelector('[data-field="'+field.name+'"]');
    if ((field.name === 'head_sex' || field.name === 'head_education') && state.relationship_to_head === 1) {
      if(div)div.remove();
      return;
    }
    const existing=Boolean(div);
    if (!div) div=document.createElement('div');
    div.className='field';
    div.dataset.field=field.name;
    const label=div.querySelector('label')||document.createElement('label');
    label.htmlFor='input-'+field.name;
    label.textContent=field.label;
    if(!existing)div.appendChild(label);
    let input=div.querySelector('input,select');
    if (field.options) {
      if(!input){
        input=document.createElement('select');
        for(const choice of field.options){
          const option=document.createElement('option');
          option.value=choice.value;
          option.textContent=choice.label;
          input.appendChild(option);
        }
      }
      input.value=state[field.name];
    } else {
      if(!input)input=document.createElement('input');
      input.type=field.name==='age'?'range':'number';
      input.min=field.range[0];input.max=field.range[1];input.step='1';input.value=state[field.name];
    }
    input.id='input-'+field.name;
    if (field.help) { input.title=field.help; input.setAttribute('aria-description',field.help); }
    input.onchange=()=>{ state[field.name]=input.value === '' ? null : Number(input.value); send(); };
    if(!existing)div.appendChild(input);
    if (field.name==='age') {
      div.style.gridColumn='1 / -1';
      const out=div.querySelector('.section-note')||document.createElement('span');out.className='section-note';out.textContent=String(state.age);
      input.oninput=()=>out.textContent=input.value;if(!existing)div.appendChild(out);
    }
    if(!existing)form.appendChild(div);
  });
  root.querySelectorAll('.example').forEach((button,index)=>{
    const examples=[
      {age:18,education_level:6,currently_enrolled:7},
      {},
      {age:22,sex:2,area:2,education_level:13,currently_enrolled:1}
    ];
    button.textContent=['Rural, enrolled','Rural, not enrolled','Urban graduate'][index];
    button.onclick=()=>{Object.assign(state,data.defaults,examples[index]);send();};
  });
  $('resetProfile').onclick=()=>{Object.assign(state,data.defaults);send();};
  const savedHost=root.host;
  const comparison=$('compareBox');
  $('clearProfile').hidden=savedHost.savedScore === undefined;
  comparison.hidden=savedHost.savedScore === undefined || results.errors.length>0;
  if(!comparison.hidden) comparison.textContent='Saved estimate: '+(savedHost.savedScore*100).toFixed(1)+'%. Current estimate: '+(results.probability*100).toFixed(1)+'%. Difference: '+((results.probability-savedHost.savedScore)*100).toFixed(1)+' percentage points.';
  $('saveProfile').disabled=results.errors.length>0;
  $('copyProfile').disabled=results.errors.length>0;
  $('saveProfile').onclick=()=>{savedHost.savedScore=results.probability;comparison.textContent='Estimate saved for this session only.';comparison.hidden=false;$('clearProfile').hidden=false;};
  $('clearProfile').onclick=()=>{delete savedHost.savedScore;comparison.hidden=true;$('clearProfile').hidden=true;};
  $('copyProfile').onclick=async()=>{
    const profile=data.fields.map(f=>{const control=$('input-'+f.name);if(!control)return null;return f.label+': '+(control.selectedOptions?control.selectedOptions[0].textContent:control.value);}).filter(Boolean).join(', ');
    const text='HunarLens model estimate: '+profile+' -> '+(results.probability*100).toFixed(1)+'%. Experimental, association not causation, not a decision tool.';
    try {await navigator.clipboard.writeText(text);comparison.textContent='Summary copied.';} catch (_) {comparison.textContent='Copy unavailable. Select and copy this summary: '+text;}
    comparison.hidden=false;
  };
  const resultCard=root.querySelector('#page-explorer article:nth-of-type(2)');
  $('multiple').nextElementSibling.textContent='Versus training-sample rate ('+(data.base_rate*100).toFixed(1)+'%)';
  $('flag').nextElementSibling.textContent=(data.threshold*100).toFixed(1)+'% follow-up threshold';
  let message=root.querySelector('#form-messages');
  if (!message) {message=document.createElement('div');message.id='form-messages';form.after(message);}
  message.replaceChildren();
  [...results.errors,...results.warnings].forEach((text,index)=>{
    const item=document.createElement('p');
    item.className=index<results.errors.length?'disclaimer':'callout';
    item.textContent=text;message.appendChild(item);
  });
  const resultIds=['band','probability','dotGrid','per100','multiple','flag','factors'];
  resultIds.forEach(id=>{
    if (['per100','multiple','flag'].includes(id)) $(id).parentElement.hidden=results.errors.length>0;
    else $(id).hidden=results.errors.length>0;
  });
  if(results.errors.length) {
    $('profileDesc').textContent='Correct the profile inputs to see an estimate.';
  } else {
    const p=results.probability,n=Math.round(p*100);
    $('profileDesc').textContent='Youth aged 15–24 in the labour force';
    $('probability').textContent=(p*100).toFixed(1)+'%';
    $('per100').textContent=n+' / 100';
    $('multiple').textContent=(p/data.base_rate).toFixed(1)+'×';
    $('flag').textContent=results.flagged?'Flagged':'Not flagged';
    const band=$('band');
    band.className='result-band '+({'Lower than most':'band-low','Elevated':'band-mid','High':'band-high'}[results.band]);
    band.textContent=results.band;
    $('dotGrid').innerHTML=Array.from({length:100},(_,i)=>'<i'+(i<n?' class="on"':'')+'></i>').join('');
    $('dotGrid').setAttribute('aria-label',n+' out of 100 squares highlighted');
    const factors=$('factors');
    factors.replaceChildren();
    results.changes.filter(row=>Math.abs(row.change)>=.0005).sort((a,b)=>Math.abs(b.change)-Math.abs(a.change)).forEach(row=>{
      const line=document.createElement('div');line.className='factor';
      const effect=relativeChange(row.change);
      line.textContent='Compared with the typical value, '+row.feature.replaceAll('_',' ')+' '+(effect>0?'raises':'lowers')+' the estimate by '+Math.abs(effect*100).toFixed(1)+' points';
      factors.appendChild(line);
    });
    if(!factors.children.length) factors.textContent='Each displayed change is smaller than 0.05 percentage points.';
  }
  resultCard.querySelectorAll('.extra-model-tools').forEach(node=>node.remove());
  if (!results.errors.length) {
    const extra=document.createElement('div');extra.className='extra-model-tools';
    const ruler=document.createElement('div');ruler.className='risk-ruler';
    ruler.setAttribute('role','img');ruler.setAttribute('aria-label',results.band+' band; higher than about '+Math.round(results.percentile)+' percent of validation youth');
    ruler.innerHTML='<span></span><span></span><span></span><i></i>';
    ruler.querySelector('i').style.left=Math.min(results.percentile,99.5)+'%';extra.appendChild(ruler);
    const labels=document.createElement('div');labels.className='risk-labels';labels.innerHTML='<span>Lower than most</span><span>Elevated</span><span>High</span>';extra.appendChild(labels);
    const text=document.createElement('p');text.className='section-note';text.textContent='Higher than about '+Math.round(results.percentile)+'% of youth in the validation sample.';extra.appendChild(text);
    const explore=document.createElement('details');explore.className='extra-section';explore.open=true;
    const summary=document.createElement('summary');summary.textContent='Explore one input';explore.appendChild(summary);
    const label=document.createElement('label');label.htmlFor='explore-choice';label.textContent='Input to explore';explore.appendChild(label);
    const select=document.createElement('select');select.id='explore-choice';
    data.fields.forEach(field=>{const option=document.createElement('option');option.value=field.name;option.textContent=field.label;select.appendChild(option);});
    select.value=data.explore;select.onchange=()=>setStateValue('explore',select.value);explore.appendChild(select);
    results.alternatives.forEach(row=>{const line=document.createElement('div');line.className='factor';
      const name=document.createElement('span');name.className='factor-name';name.textContent=row.label+(row.current?' · current':'');line.appendChild(name);
      const track=document.createElement('div');track.className='factor-track';const bar=document.createElement('div');bar.className='factor-fill';bar.style.width=(row.probability*100)+'%';track.appendChild(bar);line.appendChild(track);
      const value=document.createElement('span');value.textContent=(row.probability*100).toFixed(1)+'%'+(row.rare?' · rare':'');line.appendChild(value);
      line.title='Predicted probability '+(row.probability*100).toFixed(1)+'%';explore.appendChild(line);});
    const caveat=document.createElement('p');caveat.className='section-note';caveat.textContent='Changes are model associations, not causal effects. Rare combinations are less reliable.';explore.appendChild(caveat);extra.appendChild(explore);
    const explain=document.createElement('details');explain.className='extra-section';
    const head=document.createElement('summary');head.textContent='How the model uses information';explain.appendChild(head);
    data.importance.forEach(item=>{const line=document.createElement('div');line.className='factor';
      const name=document.createElement('span');name.className='factor-name';name.textContent=item.group;line.appendChild(name);
      const track=document.createElement('div');track.className='factor-track';track.style.position='relative';
      const bar=document.createElement('div');bar.className='factor-fill';bar.style.width=Math.max(0,Math.min(100,item.importance_mean/0.12*100))+'%';track.appendChild(bar);line.appendChild(track);
      const error=document.createElement('span');error.style.cssText='position:absolute;top:2px;height:3px;background:#17233d';error.style.left=Math.max(0,(item.importance_mean-item.importance_std)/0.12*100)+'%';error.style.width=Math.min(100,2*item.importance_std/0.12*100)+'%';track.appendChild(error);
      const value=document.createElement('span');value.textContent=item.importance_mean.toFixed(3)+' ± '+item.importance_std.toFixed(3);line.appendChild(value);explain.appendChild(line);});
    const explainNote=document.createElement('p');explainNote.className='section-note';explainNote.textContent='Decrease in validation average precision when each group is shuffled. Variation is across 20 shuffles; importance is not causation.';explain.appendChild(explainNote);extra.appendChild(explain);
    resultCard.appendChild(extra);
  }
  const survey=data.survey;
  const cards=root.querySelectorAll('#page-overview .kpi-value');
  ['youth_all','all_ages','youth_male','youth_female'].forEach((key,i)=>{cards[i].closest('.card').hidden=!(key in survey);if(key in survey)cards[i].textContent=(survey[key]*100).toFixed(1)+'%';});
  const chosen=[['Male',survey.youth_male],['Female',survey.youth_female],['Rural',survey.youth_rural],['Urban',survey.youth_urban],
    ...['15_19','20_24'].flatMap(age=>['male','female'].map(sex=>[age.replace('_','–')+' · '+sex,survey['unemployment_'+age+'_'+sex]]))].filter(([,v])=>Number.isFinite(v));
  const chart=$('ageChart');chart.removeAttribute('aria-label');
  chart.setAttribute('aria-label','Official unemployment rates for labour-force youth by age, sex and area');
  chart.innerHTML=chosen.map(([label,value])=>'<div class="metric-row"><span>'+label+'</span><div class="track"><div class="fill" style="width:'+(value*100)+'%"></div></div><strong>'+(value*100).toFixed(1)+'%</strong></div>').join('');
  chart.closest('.card').querySelector('h2').textContent='Youth unemployment by age, sex and area';
  chart.closest('.card').querySelector('.card-desc').textContent='Official weighted rate · ages 15–24';
  const chartLegend=chart.closest('.card').querySelector('.legend');if(chartLegend)chartLegend.remove();
  const chartInsight=chart.closest('.card').querySelector('.insight');if(chartInsight)chartInsight.textContent='Sex and area are separate comparisons. These are rates among youth in the labour force.';
  const part=$('participation');
  const ageKeys=['15_19','20_24'];
  const ageRows=ageKeys.filter(age=>['total','male','female'].every(sex=>['participation','unemployment'].every(kind=>kind+'_'+age+'_'+sex in survey)));
  part.closest('.card').hidden=ageRows.length===0;
  part.innerHTML=ageRows.map(age=>'<div class="metric-row"><span>'+age.replace('_','–')+'</span><div class="track"><div class="fill" style="width:'+(survey['participation_'+age+'_total']*100)+'%"></div></div><strong>'+(survey['participation_'+age+'_total']*100).toFixed(1)+'%</strong></div>').join('');
  const compare=$('groupCard');
  if(compare){compare.hidden=ageRows.length===0;const table=compare.querySelector('tbody');table.innerHTML=ageRows.map(age=>'<tr><td>'+age.replace('_','–')+'</td>'+['participation_'+age+'_total','unemployment_'+age+'_total','unemployment_'+age+'_male','unemployment_'+age+'_female'].map(key=>'<td>'+(survey[key]*100).toFixed(1)+'%</td>').join('')+'</tr>').join('');}
  const m=data.metrics['HGB F1'];
  const dummy=data.metrics['Stratified Dummy'];
  const perf=root.querySelectorAll('#page-performance .kpi-value');
  [Number(m.n).toLocaleString(),(m.prevalence*100).toFixed(1)+'%',((m.tp+m.fp)/m.n*100).toFixed(1)+'%',m.roc_auc.toFixed(3)].forEach((v,i)=>perf[i].textContent=v);
  const perfCards=root.querySelectorAll('#page-performance .grid.two');
  const outcome=perfCards[0].querySelectorAll('.card')[0];
  const values=[['Flagged youth',(m.tp+m.fp)/m.n],['Unemployed among flagged',m.precision],['Unemployed detected',m.recall]];
  outcome.querySelector('.metric-list').innerHTML=values.map(([label,v])=>'<div><div class="metric-row"><span>'+label+'</span><strong>'+(v*100).toFixed(1)+'%</strong></div><div class="track"><div class="fill" style="width:'+(v*100)+'%"></div></div></div>').join('');
  outcome.querySelector('.insight').textContent='Among unemployed youth, '+(m.recall*100).toFixed(1)+'% were flagged and '+((1-m.recall)*100).toFixed(1)+'% were missed. Of those flagged, '+(m.precision*100).toFixed(1)+'% were unemployed.';
  const core=perfCards[0].querySelectorAll('.card')[1];
  core.querySelector('.metric-list').innerHTML=[['F1',m.f1],['PR-AUC',m.pr_auc],['ROC-AUC',m.roc_auc]].map(([label,v])=>'<div class="metric-row"><span>'+label+'</span><div class="track"><div class="fill" style="width:'+(v*100)+'%"></div></div><strong>'+v.toFixed(3)+'</strong></div>').join('');
  const ci=data.confidence.find(r=>r.model_threshold==='HGB F1'&&r.metric==='f1');
  core.querySelector('.section-note').textContent='F1 95% interval: '+ci.lower_95.toFixed(3)+'–'+ci.upper_95.toFixed(3)+'. Dummy F1: '+dummy.f1.toFixed(3)+'. No-skill PR-AUC: '+m.prevalence.toFixed(3)+'.';
  const foot=root.querySelectorAll('#page-performance .kpi-foot');foot[1].textContent=m.positives.toLocaleString()+' of '+m.n.toLocaleString()+' youth';foot[2].textContent='At the selected threshold';
  const education=perfCards[1].querySelectorAll('.card')[1].querySelector('.metric-list');
  const ed=data.subgroups.filter(r=>r.subgroup.toLowerCase().includes('education')&&r.threshold==='f1');
  education.innerHTML=ed.map(r=>'<div class="metric-row"><span>'+r.value+' (n='+r.n+', positives='+r.positives+')</span><div class="track"><div class="fill" style="width:'+(r.recall*100)+'%"></div></div><strong>'+(r.recall*100).toFixed(1)+'%'+(r.positives<50?' †':'')+'</strong></div>').join('');
  perfCards[1].querySelectorAll('.card')[1].querySelector('.callout').textContent='† Fewer than 50 positives: unreliable. Differences are descriptive and do not establish causation.';
  const importance=$('importance');
  importance.innerHTML=data.importance.slice(0,5).map(r=>'<div class="metric-row"><span>'+r.group+'</span><div class="track"><div class="fill" style="width:'+Math.max(0,Math.min(100,r.importance_mean/0.12*100))+'%"></div></div><strong>'+r.importance_mean.toFixed(3)+'</strong></div>').join('');
  const impTitle=importance.closest('.card').querySelector('.card-desc');
  if(impTitle)impTitle.textContent='Decrease in validation average precision when inputs are shuffled';
  root.querySelectorAll('.generated-report').forEach(node=>node.remove());
  function addTable(title, rows) {
    const details=document.createElement('details');details.className='card generated-report';details.style.marginTop='16px';
    const summary=document.createElement('summary');summary.textContent=title;details.appendChild(summary);
    const wrap=document.createElement('div');wrap.className='table-wrap';
    const table=document.createElement('table'), keys=Object.keys(rows[0]||{}).filter(k=>!['tp','fp','tn','fn'].includes(k));
    const names={model_threshold:'Model and threshold',pr_auc:'PR-AUC',roc_auc:'ROC-AUC',cv_ap_mean:'CV PR-AUC',val_f1_best:'Validation F1',lift_10:'Top 10% lift',lift_20:'Top 20% lift',lower_95:'95% lower',upper_95:'95% upper',unreliable_fewer_than_50_positives:'Fewer than 50 positives'};
    const header=table.createTHead().insertRow();keys.forEach(k=>{const th=document.createElement('th');th.textContent=names[k]||k.replaceAll('_',' ').replace(/^./,c=>c.toUpperCase());header.appendChild(th);});
    const body=table.createTBody();rows.forEach(record=>{const tr=body.insertRow();keys.forEach(k=>{const td=tr.insertCell();const value=record[k];td.textContent=typeof value==='number'&&!Number.isInteger(value)?value.toFixed(3):String(value);});});
    wrap.appendChild(table);details.appendChild(wrap);root.querySelector('#page-performance').appendChild(details);
  }
  addTable('Model comparison · grouped CV and validation',data.experiments);
  addTable('Final test metrics · model and Dummy',data.test_table);
  addTable('95% grouped bootstrap confidence intervals',data.confidence);
  addTable('Subgroup performance · fewer than 50 positives is unreliable',data.subgroups);
  const pr=document.createElement('article');pr.className='card generated-report';pr.style.marginTop='16px';
  const prTitle=document.createElement('h2');prTitle.textContent='Final test precision–recall curve';pr.appendChild(prTitle);
  const prImage=document.createElement('img');prImage.src='data:image/png;base64,'+data.pr_curve;prImage.alt='Test precision–recall curve with the no-skill prevalence line';prImage.style.maxWidth='100%';pr.appendChild(prImage);
  root.querySelector('#page-performance').appendChild(pr);
  root.querySelectorAll('.source-pill').forEach(e=>e.textContent='Pakistan · National view');
  const method=root.querySelector('#page-methodology');
  if(!method.querySelector('.project-context')){
    const note=document.createElement('article');note.className='card project-context';note.style.marginTop='16px';
    const heading=document.createElement('h2');heading.textContent='Model sample, privacy and limitations';note.appendChild(heading);
    const description=document.createElement('p');description.textContent='The model covers youth aged 15–24 in the labour force, not all students. Unemployed people are available and either searched or have a job or business to start; the source data do not record whether that job begins within three months. The model and evaluation use unweighted records. Census features are constant within province or province and area. Enrolment patterns partly reflect selection into the labour-force sample. Subgroup performance varies. Inputs are not stored. HunarLens is not affiliated with or endorsed by PBS. Association is not causation, and the app is not a decision tool for individuals.';note.appendChild(description);
    method.appendChild(note);
  }
  $('downloadCsv').onclick=()=>{
    const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([indicatorCsv(data.overview)],{type:'text/csv'}));a.download='hunarlens-survey-indicators.csv';a.click();URL.revokeObjectURL(a.href);
  };
  if(focusId){const target=$(focusId);if(target){target.focus();if(selection)try{target.setSelectionRange(...selection);}catch(_){}}}
  } catch (error) {
    const message=document.createElement('div');message.setAttribute('role','alert');message.textContent='This page is temporarily unavailable. Please refresh or use the classic view.';root.appendChild(message);
  } finally { const shell=root.querySelector('.shell');if(shell)shell.style.visibility='visible'; }
}

export function relativeChange(change) { return -change; }
export function indicatorCsv(rows) {
  const lines=['Indicator,Our value,PBS value,Source,Difference,Status',...rows.map(r=>[r.indicator,r.our_value,r.pbs_value,r.source_url,r.difference,r.status].join(','))];
  return lines.join('\n');
}
