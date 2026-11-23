# What: renders reports from aggregate tables and maintained narrative templates.
# Why: results remain traceable without reopening or rescoring test records.
# Viva: each statistical placeholder resolves to an existing table cell or calculation.
from __future__ import annotations
import ast
import hashlib
import json
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / 'reports/tables'
TEMPLATES = ROOT / 'scripts/report_templates'
OCCUPATIONS = ['Managers', 'Professionals', 'Technicians and associate professionals',
 'Clerical support workers', 'Service and sales workers',
 'Skilled agricultural, forestry and fishery workers', 'Craft and related trades workers',
 'Plant and machine operators and assemblers', 'Elementary occupations']
MODELS = {'logistic_regression': 'Logistic regression', 'random_forest': 'Random Forest',
          'hist_gradient_boosting': 'Histogram gradient boosting', 'dummy': 'Stratified Dummy'}


def load(name):
    return pd.read_csv(TABLES / f'{name}.csv', keep_default_na=False)


def fmt(value, style='d'):
    if style == 's':
        return str(value)
    try:
        n = float(value)
    except (ValueError, TypeError):
        return str(value) or '—'
    return {'i': lambda: f'{n:,.0f}', 'p': lambda: f'{100*n:.1f}%',
            'pp': lambda: f'{100*n:.1f}', 'pct_units': lambda: f'{n:.1f}%',
            'd': lambda: f'{n:.3f}'}[style]()


def label(value):
    text = str(value)
    for code, name in enumerate(OCCUPATIONS, 1):
        if text == f'occupation {code}':
            return name
    for old, new in {'sex=1.0': 'Male', 'sex=2.0': 'Female', 'area=1.0': 'Rural',
        'area=2.0': 'Urban', 'province=1.0': 'Khyber Pakhtunkhwa', 'province=2.0': 'Punjab',
        'province=3.0': 'Sindh', 'province=4.0': 'Balochistan',
        'all_15_plus': 'All employed adults', 'age_25_44': 'Employed mid-age adults',
        'norm=youth': 'norm=Employed youth', 'ISCO': 'Normative ISCO', 'overall': 'Overall'}.items():
        text = text.replace(old, new)
    return MODELS.get(text, 'Employed youth' if text == 'youth' else text)


def md_table(frame, columns, styles=None):
    styles = styles or {}
    lines = ['| ' + ' | '.join(columns.values()) + ' |', '| ' + ' | '.join(['---'] * len(columns)) + ' |']
    for _, row in frame.iterrows():
        cells = [fmt(row[c], styles[c]) if c in styles else label(row[c]) for c in columns]
        lines.append('| ' + ' | '.join(c.replace('|', '/').replace('\n', ' ') for c in cells) + ' |')
    return '\n'.join(lines)


def context():
    values, ledger = {}, {}
    def add(key, value, source, style='d'):
        if hasattr(value, 'item'):
            value = value.item()
        values[key] = fmt(value, style)
        ledger[key] = {'value': value, 'source': source, 'format': style}
    def cell(key, table, query, col, style='d'):
        selected = load(table).query(query) if query else load(table)
        assert len(selected) == 1, (key, len(selected))
        add(key, selected.iloc[0][col], {'table': table, 'query': query, 'column': col}, style)
    for prefix, model in [('test','HGB F1'), ('screen','HGB screening'), ('dummy','Stratified Dummy')]:
        for col in ['n','positives','tn','fp','fn','tp','f1','precision','recall','pr_auc','roc_auc','accuracy','prevalence','lift_10','lift_20','threshold']:
            cell(f'{prefix}_{col}', 'test_metrics', f'model_threshold == "{model}"', col, 'i' if col in ['n','positives','tn','fp','fn','tp'] else 'd')
        for col in ['precision','recall','prevalence']:
            cell(f'{prefix}_{col}_pct','test_metrics',f'model_threshold == "{model}"',col,'p')
    for metric in ['f1','pr_auc','precision','recall','roc_auc','lift_10']:
        for bound in ['lower_95','upper_95']:
            cell(f'{metric}_{bound}','test_bootstrap_ci',f'model_threshold == "HGB F1" and metric == "{metric}"',bound)
    cell('bootstrap_repeats','test_bootstrap_ci','model_threshold == "HGB F1" and metric == "f1"','repeats','i')
    for i, row in load('row_waterfall').iterrows():
        add(f'waterfall_{i}',row['rows'],{'table':'row_waterfall','row':i,'column':'rows'},'i')
    split = load('split_summary')
    add('sample_n',split.rows.sum(),{'table':'split_summary','operation':'sum(rows)'},'i')
    add('sample_positive',split.positives.sum(),{'table':'split_summary','operation':'sum(positives)'},'i')
    add('sample_prevalence',split.positives.sum()/split.rows.sum(),{'table':'split_summary','operation':'sum(positives)/sum(rows)'},'p')
    for group in ['all_ages','youth_all','youth_male','youth_female','youth_rural','youth_urban']:
        for col in ['unemployment_rate','pbs_unemployment_rate']:
            cell(f'{group}_{col}','label_reproduction',f'group == "{group}"',col,'p')
    for col in ['employed','unemployed','labour_force']:
        add(f'national_{col}',load('label_reproduction').query('group == "all_ages"').iloc[0][col]/1e6,{'table':'label_reproduction','column':col,'query':'group == "all_ages"','divide':1e6})
    for prefix, group in [('future','all_ages'),('waiting','S5C5_1_all'),('waiting_unemployed','S5C5_1_unemployed')]:
        for col in ['records','weighted_count']:
            cell(f'{prefix}_{col}','future_starters_diagnostic',f'group == "{group}"',col,'i')
    for prefix, model in [('lr','logistic_regression'),('rf','random_forest'),('hgb','hist_gradient_boosting')]:
        for exp in ['E1','E2','E3','E4']:
            for col in ['cv_ap_mean','cv_ap_std','val_ap','val_f1']:
                cell(f'{prefix}_{exp}_{col}','experiments',f'model == "{model}" and exp_id == "{exp}"',col)
        row = load('generalization_gap').query(f'model == "{model}"').iloc[0]
        add(f'{prefix}_gap',row.train_ap-row.cv_ap,{'table':'generalization_gap','model':model,'operation':'train_ap-cv_ap'})
    add('cv_difference',ledger['rf_E3_cv_ap_mean']['value']-ledger['hgb_E3_cv_ap_mean']['value'],{'operation':'rf_E3_cv_ap_mean-hgb_E3_cv_ap_mean'})
    for method in ['raw','sigmoid']:
        for col in ['brier','ece_10_fixed_bins']:
            cell(f'{method}_{col}','calibration_validation',f'method == "{method}"',col)
    cell('val_f1','validation_thresholds','threshold_type == "f1"','f1')
    for prefix, band in [('lowedu','No formal'),('degree','Degree or above')]:
        for col in ['n','positive_n','estimate','ci_low','ci_high']:
            cell(f'{prefix}_{col}','skills_unemployment_by_education',f'group == "overall" and category == "{band}"',col,'i' if col in ['n','positive_n'] else 'p')
    cell('degree_female','skills_unemployment_by_education','group == "sex=2.0" and category == "Degree or above"','estimate','p')
    for category,key in [('Employed: groups 1–4','graduate_upper'),('Employed: groups 5–9','graduate_other'),('Unemployed','graduate_unemployed')]:
        cell(key,'skills_graduate_absorption',f'group == "overall" and category == "{category}"','estimate','p')
    for prefix, table, query in [('strict_adult','skills_mismatch','group == "overall; norm=all_15_plus" and category == "over"'),('strict_youth','skills_mismatch_sensitivity','group == "overall; norm=youth" and category == "over"'),('normative','skills_mismatch_sensitivity','group == "overall; norm=ISCO" and category == "over"'),('tolerance','skills_mismatch_variants','group == "all_15_plus" and category == "within one band"'),('severe','skills_mismatch_variants','group == "all_15_plus" and category == "two or more bands above"'),('neet','skills_neet','group == "overall"')]:
        for col in ['n','positive_n','estimate','ci_low','ci_high']:
            cell(f'{prefix}_{col}',table,query,col,'i' if col in ['n','positive_n'] else 'p')
    cell('neet_pbs','skills_neet_external','','estimate','p')
    for col in ['difference','ci_low','ci_high']:
        row = load('skills_attainment_difference').query('group == "overall" and category == "Training ever/current"').iloc[0]
        add(f'training_{col}',abs(float(row[col])),{'table':'skills_attainment_difference','query':'group == "overall" and category == "Training ever/current"','column':col,'operation':'absolute'},'pp')
    for group, key in [('overall; employed','training_employed'),('overall; unemployed','training_unemployed')]:
        cell(key,'skills_attainment_gap',f'group == "{group}" and category == "Training ever/current"','estimate','p')
    for feature in ['Education','Enrolment','Geography','Sex']:
        cell(f'importance_{feature}','grouped_permutation_importance',f'group == "{feature}"','importance_mean')
    cell('without_enrolment','feature_group_ablation','model == "hist_gradient_boosting" and ablation == "full_without_currently_enrolled"','cv_ap_mean')
    for group, key in [('Enrolled','enrolled'),('Not enrolled','not_enrolled')]:
        for col in ['n','unemployed','unemployment_rate']:
            cell(f'{key}_{col}','enrolment_train_summary',f'enrolment == "{group}"',col,'p' if col == 'unemployment_rate' else 'i')
    for group,key in [('No formal education','noformal_test'),('Intermediate','intermediate_test'),('Degree or higher','degree_test'),('Female','female_test'),('Male','male_test')]:
        for col in ['n','positives','recall','flag_rate']:
            cell(f'{key}_{col}','test_subgroups',f'value == "{group}" and threshold == "f1"',col,'i' if col in ['n','positives'] else 'p')
    for key,table,col in [('max_missing','feature_missingness','missing_rate'),('max_scan','single_feature_scan','mean_pr_auc'),('reproduction_max','skills_reproduction','difference_pp')]:
        add(key,load(table)[col].max(),{'table':table,'operation':f'max({col})'},'p' if key == 'max_missing' else 'd')
    for i in [0,2]:
        add(f'learning_{i}',load('grouped_learning_curve').iloc[i].cv_ap_mean,{'table':'grouped_learning_curve','row':i,'column':'cv_ap_mean'})
    for col in ['n','coverage','mean','minimum','maximum']:
        cell(f'shift_{col}','skills_model_shift','scenario == "education" and grouping == "overall"',col,'i' if col == 'n' else ('p' if col == 'coverage' else 'pp'))
    metadata = json.loads((ROOT/'models/metadata.json').read_text())
    for key in ['high_min','elevated_min']:
        add(key,metadata['risk_bands'][key],{'file':'models/metadata.json','key':f'risk_bands.{key}'})
    add('model_kib',(ROOT/'models/final_pipeline.joblib').stat().st_size/1024,{'file':'models/final_pipeline.joblib','operation':'bytes/1024'})
    add('feature_count',len(metadata['feature_names']),{'file':'models/metadata.json','operation':'len(feature_names)'},'i')
    evidence=json.loads((ROOT/'docs/report_reference_evidence.json').read_text())['pbs_households']
    add('households',int(re.search(r'[\d,]+',evidence['text']).group().replace(',','')),evidence,'i')
    for name, code in [('waiting_young','1.0'),('illness_young','2.0')]:
        frame=load('absence_code_by_age')
        row=frame.loc[frame.iloc[:,0].astype(float).eq(float(code))].iloc[0]
        add(name,row['15-24'],{'table':'absence_code_by_age','code':code,'column':'15-24'},'i')
    # Read implemented search choices without importing executable modelling code.
    tree=ast.parse((ROOT/'scripts/compare_models.py').read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ['N_ITER_RF','N_ITER_HGB']:
            add(node.targets[0].id.lower(),ast.literal_eval(node.value),{'file':'scripts/compare_models.py','constant':node.targets[0].id},'i')
    search=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='search_space')
    spaces=[ast.literal_eval(n.value) for n in ast.walk(search) if isinstance(n,ast.Return)]
    spaces.sort(key=lambda space: 0 if 'model__C' in space else (1 if 'model__n_estimators' in space else 2))
    for model,space in zip(['Logistic regression','Random Forest','HGB'],spaces):
        for parameter,choices in space.items():
            add(f'search_{model}_{parameter}',json.dumps(choices),{'file':'scripts/compare_models.py','function':'search_space','model':model,'parameter':parameter},'s')
    return values,ledger


def skills_table(name,query=None):
    frame=load(name)
    if query: frame=frame.query(query)
    cols={c:t for c,t in [('group','Population / norm'),('category','Outcome / education'),('n','Denominator n'),('positive_n','Cell n'),('estimate','Weighted share'),('ci_low','Lower bound'),('ci_high','Upper bound'),('reliability','Reliability'),('flag','Disclosure / reliability'),('bootstrap_median','Bootstrap median'),('bootstrap_bias','Bootstrap bias')] if c in frame}
    return md_table(frame,cols,{'n':'i','positive_n':'i',**{c:'p' for c in ['estimate','ci_low','ci_high','bootstrap_median','bootstrap_bias']}})


def tables():
    out={}
    out['splits_table']=md_table(load('split_summary'),{'split':'Partition','rows':'Youth n','positives':'Unemployed n','prevalence':'Prevalence'},{'rows':'i','positives':'i','prevalence':'p'})
    frame=load('generalization_gap'); frame['gap']=frame.train_ap-frame.cv_ap
    out['gap_table']=md_table(frame,{'model':'Tuned model','train_ap':'Train AP','cv_ap':'CV AP','validation_ap':'Validation AP','gap':'Train minus CV'},{c:'d' for c in ['train_ap','cv_ap','validation_ap','gap']})
    out['comparison_table']=md_table(load('experiments').query('exp_id == "E4" or exp_id == "E0"'),{'model':'Model','cv_ap_mean':'CV AP','cv_ap_std':'Fold SD','val_ap':'Validation AP','val_f1':'Validation F1'},{c:'d' for c in ['cv_ap_mean','cv_ap_std','val_ap','val_f1']})
    rows=[]
    for _,r in load('test_metrics').iterrows():
        row={'model':r.model_threshold}
        for col in ['f1','precision','recall','pr_auc','roc_auc','lift_10']:
            ci=load('test_bootstrap_ci').query('model_threshold == @r.model_threshold and metric == @col').iloc[0]
            row[col]=f'{r[col]:.3f} [{ci.lower_95:.3f}, {ci.upper_95:.3f}]'
        rows.append(row)
    out['test_table']=md_table(pd.DataFrame(rows),{'model':'Model / operating point','f1':'F1 [95% CI]','precision':'Precision [95% CI]','recall':'Recall [95% CI]','pr_auc':'AP [95% CI]','roc_auc':'ROC-AUC [95% CI]','lift_10':'Top-decile lift [95% CI]'})
    out['education_table']=skills_table('skills_unemployment_by_education','group == "overall"')
    out['graduate_table']=skills_table('skills_graduate_absorption','group == "overall"')
    out['subgroup_table']=md_table(load('test_subgroups'),{'subgroup':'Grouping','value':'Population','threshold':'Operating point','n':'Youth n','positives':'Unemployed n','flag_rate':'Flagged share','precision':'Precision','recall':'Recall','unreliable_fewer_than_50_positives':'Unreliable'},{'n':'i','positives':'i','flag_rate':'p','precision':'d','recall':'d'})
    blocks=[]
    for i,name in enumerate(['skills_unemployment_by_education','skills_graduate_absorption','skills_mismatch','skills_mismatch_sensitivity','skills_mismatch_variants','skills_mismatch_by_occupation','skills_mismatch_occupation_variants','skills_outcomes_by_education','skills_neet','skills_degree_type','skills_training_by_occupation'],1):
        blocks.append(f'### Table A{i}. {name.removeprefix("skills_").replace("_"," ").capitalize()}\n\n'+skills_table(name)+f'\n\nSource: [{name}.csv](../reports/tables/{name}.csv). Bounds are PSU-bootstrap percentile bounds. Rows labelled mode unstable show the bootstrap range. A dash denotes a structural zero; n<30 denotes primary suppression.\n')
    out['skills_appendices']='\n'.join(blocks)
    modes=load('skills_occupation_modes'); modes['occupation']=modes.occupation.map(lambda n:OCCUPATIONS[int(float(n))-1])
    out['modes_table']=md_table(modes,{'norm':'Reference population','occupation':'Occupation','mode_label':'Modal education','n':'Reference n'},{'n':'i'})
    out['reproduction_table']=md_table(load('skills_reproduction'),{'indicator':'Published indicator','n':'Cell n','our_value':'Calculated share','pbs_value':'PBS share','difference_pp':'Absolute gap (pp)','status':'Check'},{'n':'i','our_value':'pct_units','pbs_value':'pct_units','difference_pp':'d'})
    out['stability_table']=md_table(load('skills_mode_stability').query('reliability == "mode unstable"'),{'norm':'Norm','occupation':'Occupation code','band_label':'Resampled modal band','reference_n':'Reference n','replicate_share':'Resample share','change_share':'Mode-change share','reliability':'Reliability'},{'occupation':'i','reference_n':'i','replicate_share':'p','change_share':'p'})
    params=json.loads(load('experiments').query('exp_id == "E3" and model == "hist_gradient_boosting"').iloc[0].best_params)
    out['parameters_table']=md_table(pd.DataFrame([{'parameter':k.removeprefix('model__').replace('_',' '),'value':'None' if v is None else fmt(v)} for k,v in params.items()]),{'parameter':'Hyperparameter','value':'Saved value'})
    inventory=[]
    for path in sorted((ROOT/'tests').glob('test_*.py')):
        names=[n.name for n in ast.walk(ast.parse(path.read_text(encoding='utf-8'))) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
        descriptions=[re.sub(r'\bgate\b','tolerance',n.removeprefix('test_').replace('_',' ')) for n in names]
        inventory.append(f'- **{path.name}**: '+'; '.join(descriptions)+'.')
    out['test_inventory']='\n'.join(inventory)
    out['shift_table']=md_table(load('skills_model_shift'),{'scenario':'Substitution','grouping':'Grouping','group':'Population','n':'Covered n','coverage':'Coverage','mean':'Mean change (pp)','minimum':'Code minimum (pp)','maximum':'Code maximum (pp)','ci_low':'Lower bound (pp)','ci_high':'Upper bound (pp)','flag':'Reliability'},{'n':'i','coverage':'p',**{c:'pp' for c in ['mean','minimum','maximum','ci_low','ci_high']}})
    return out


def render_reports():
    values,ledger=context(); values.update(tables())
    choices=[]
    for key,item in ledger.items():
        if key.startswith('search_'):
            choices.append({'model':item['source']['model'],'parameter':item['source']['parameter'].removeprefix('model__').replace('_',' '),'choices':', '.join('None' if v is None else (v if isinstance(v,str) else fmt(v)) for v in json.loads(item['value']))})
    values['search_table']=md_table(pd.DataFrame(choices),{'model':'Model','parameter':'Search parameter','choices':'Implemented choices'})
    for name in ['decisions','features','references']:
        values[name]=(TEMPLATES/f'{name}.md').read_text(encoding='utf-8')
    text=(ROOT/'docs/process/skills_gap_plan.md').read_text(encoding='utf-8')
    values['definition']='Skills gap, as measurable'+text.split('"Skills gap, as measurable')[1].split('"')[0]
    reports={}
    for name,template in [('project_report.md','full.md'),('report_short.md','short.md')]:
        text=(TEMPLATES/template).read_text(encoding='utf-8')
        for _ in range(3): text=re.sub(r'\{\{(\w+)\}\}',lambda m:values[m[1]],text)
        reports[name]=text
    return reports,ledger


def architecture_figure():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    fig,ax=plt.subplots(figsize=(12,6)); ax.set(xlim=(0,12),ylim=(0,6)); ax.axis('off')
    boxes=[(.2,2.4,'Official PBS files\nDownload and audit'),(3.2,4,'Modelling path\nAllowlist · household splits\nTraining-only pipeline'),(3.2,.8,'Survey-analysis path\nWeights · occupation modes\nPSU bootstrap'),(6.3,4,'Frozen model\nValidation thresholds\nSaved test summaries'),(6.3,.8,'Aggregate survey tables\nCounts · uncertainty\nDisclosure flags'),(9.3,2.4,'Streamlit dashboard\nModel + static tables\nNative fallback')]
    for x,y,text in boxes:
        ax.add_patch(FancyBboxPatch((x,y),2.5,1.25,boxstyle='round,pad=0.1',facecolor='#E3E8F5',edgecolor='#1D2B64'))
        ax.text(x+1.25,y+.625,text,ha='center',va='center',fontsize=10,color='#1F2933')
    for a,b in [(0,1),(0,2),(1,3),(2,4),(3,5),(4,5)]:
        x,y,_=boxes[a]; xx,yy,_=boxes[b]
        ax.annotate('',xy=(xx-.1,yy+.625),xytext=(x+2.6,y+.625),arrowprops={'arrowstyle':'->','color':'#1D2B64','lw':1.7})
    ax.set_title('HunarLens: separate prediction and survey-analysis paths',fontsize=15,pad=12)
    fig.tight_layout(); fig.savefig(ROOT/'reports/figures/report_architecture.png',dpi=200,bbox_inches='tight'); plt.close(fig)


def word_counts(reports):
    body=reports['project_report.md'].split('## Abstract\n')[1].split('## References')[0]
    prose='\n'.join(line for line in body.splitlines() if not line.startswith(('|','![','<!--')))
    return {'main_prose':len(prose.split()),'abstract':len(body.split('## 1.')[0].split()),'short_total':len(reports['report_short.md'].split())}


def main():
    reports,ledger=render_reports()
    for name,text in reports.items(): (ROOT/'docs'/name).write_text(text,encoding='utf-8')
    (TABLES/'report_numbers.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    figures=re.findall(r'!\[([^]]+)\]\(([^)]+)\)',reports['project_report.md'])
    (ROOT/'docs/report_figures.md').write_text('# Report figures\n\n'+'\n'.join(f'- [{caption}]({path})' for caption,path in figures)+'\n',encoding='utf-8')
    architecture_figure()
    print(word_counts(reports))
    print('Model SHA-256:',hashlib.sha256((ROOT/'models/final_pipeline.joblib').read_bytes()).hexdigest())


if __name__=='__main__':
    main()
