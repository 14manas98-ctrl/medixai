# fix_all.py — применяет ВСЕ изменения к medix_final.html
# Запуск: python fix_all.py
# Файл должен лежать в C:\MedixAI\

import os

path = 'public/medix_final.html'
if not os.path.exists(path):
    path = 'medix_final.html'
if not os.path.exists(path):
    print("ОШИБКА: файл не найден! Положи fix_all.py в папку C:\\MedixAI\\")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

ok = 0
fail = 0

def fix(old, new, desc):
    global html, ok, fail
    if old in html:
        html = html.replace(old, new)
        print(f"OK: {desc}")
        ok += 1
    else:
        print(f"SKIP: {desc} (уже применено или не найдено)")
        fail += 1

# ============================================================
# БЛОК 1: Казахские переводы (кезең → ауысым)
# ============================================================
fix("Кезеңде сәттілік! Сіз маңызды іс жасайсыз 🚑",
    "Ауысымда сәттілік! Сіз маңызды іс атқарып жатсыз 🚑",
    "Пожелание на каз")

fix("Кезеңді жабуды растайсыз ба?",
    "Ауысымды жабуды растайсыз ба?",
    "Подтверждение закрытия смены")

fix("Барлығы кезең бойы тіркеледі.",
    "Барлығы ауысым бойы тіркеледі.",
    "Фиксируется за смену")

fix("resetBtn:'🔄 Кезеңді жабу'",
    "resetBtn:'🔄 Ауысымды жабу'",
    "Кнопка закрытия смены KZ")

fix("mSub:'Кезеңдегі медикамент есебі'",
    "mSub:'Ауысымдағы медикамент есебі'",
    "Подзаголовок медикаментов KZ")

fix("d2:'Кезеңдегі кіріс және шығыс'",
    "d2:'Ауысымдағы кіріс және шығыс'",
    "Описание модуля медикаментов KZ")

fix(">0 ч 0 мин<",
    ">0 сағ 0 мин<",
    "Начальное время смены")

fix("el.textContent=`${h} ч ${m} мин`;",
    "el.textContent=`${h} сағ ${m} мин`;",
    "Функция времени смены")

fix("AI карта жасап жатқанда",
    "AI карта жасаған кезде",
    "Текст онбординга KZ")

fix("аз рутина, көп білім",
    "аз күнделікті жұмыс, көп білім",
    "Слоган KZ")

fix("Очистить приход",
    "Кірісті тазалау",
    "Очистить приход → KZ")

fix("Журнал остатков",
    "Қалдық журналы",
    "Журнал остатков → KZ")

fix("Очистить остатки",
    "Қалдықты тазалау",
    "Очистить остатки → KZ")

# ============================================================
# БЛОК 2: Удалить кнопку "Открыть в браузере" из бота
# ============================================================
fix("[{ text: '🌐 Открыть в браузере', url: 'https://medixai-production.up.railway.app/medix_final.html' }]",
    "",
    "Удалить кнопку браузера из бота")

# ============================================================
# БЛОК 3: Обновить домен на medixai.kz
# ============================================================
fix("'https://medixai-production.up.railway.app/medix_final.html'",
    "'https://www.medixai.kz/medix_final.html'",
    "Обновить домен в боте")

# ============================================================
# БЛОК 4: CSS для шаблонов
# ============================================================
tmpl_css = """
/* ============================================================
   TEMPLATES MODULE
============================================================ */
.tmpl-card{display:flex;align-items:center;gap:12px;padding:13px 14px;border-radius:13px;margin-bottom:7px;background:var(--card);border:1px solid var(--border);animation:fadeUp 0.35s cubic-bezier(.22,1,.36,1) both;cursor:pointer;transition:all 0.2s;}
.tmpl-card:hover{border-color:var(--card-hover-border);transform:translateX(3px);}
.tmpl-icon{width:38px;height:38px;border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0;background:linear-gradient(135deg,rgba(0,200,167,0.15),rgba(0,136,238,0.15));border:1px solid rgba(0,200,167,0.2);}
.tmpl-info{flex:1;min-width:0;}
.tmpl-name{font-size:13px;font-weight:600;color:var(--text1);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.tmpl-meta{font-size:10.5px;color:var(--sub);margin-top:2px;}
.tmpl-del{width:30px;height:30px;border-radius:8px;background:var(--med-minus-bg);border:1px solid var(--med-minus-border);color:var(--danger);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;transition:opacity 0.2s;}
.tmpl-del:hover{opacity:0.7;}
.save-tmpl-btn{display:flex;align-items:center;justify-content:center;gap:7px;margin:8px 0 0;padding:11px;border-radius:13px;border:1px solid rgba(0,200,167,0.25);background:rgba(0,200,167,0.07);color:var(--accent);font-size:12px;font-weight:700;cursor:pointer;transition:all 0.2s;}
.save-tmpl-btn:hover{background:rgba(0,200,167,0.13);}
.ci5{background:linear-gradient(135deg,#0d200a,#1a3a12);}
"""
fix('</style>', tmpl_css + '</style>', "CSS шаблонов")

# ============================================================
# БЛОК 5: 5-я карточка на главном экране
# ============================================================
old_card = '      <div class="hcard" onclick="goTo(\'calc\')"><div class="ci ci4">🧮</div><div class="cinfo"><div class="ctit" id="h-t4"></div><div class="cdsc" id="h-d4"></div></div><div class="carr">›</div></div>'
new_card = old_card + '\n      <div class="hcard" onclick="goTo(\'templates\')"><div class="ci ci5">📁</div><div class="cinfo"><div class="ctit" id="h-t5"></div><div class="cdsc" id="h-d5"></div></div><div class="carr">›</div></div>'
fix(old_card, new_card, "5-я карточка шаблонов")

# ============================================================
# БЛОК 6: Экран шаблонов (вставить перед JOURNAL MODAL)
# ============================================================
tmpl_screen = """<!-- ================================================================
     SCREEN: TEMPLATES
================================================================ -->
<div class="screen" id="s-templates">
  <div class="blob b1"></div>
  <div class="inner">
    <div class="hdr">
      <div class="back-btn" onclick="goTo('home')">←</div>
      <div class="hdr-info"><div class="hdr-title" id="tmpl-title"></div><div class="hdr-sub" id="tmpl-sub"></div></div>
    </div>
    <div class="mid" id="tmpl-mid">
      <div id="tmpl-empty" class="empty-state" style="display:none;padding:60px 20px;"></div>
      <div id="tmpl-list"></div>
    </div>
    <div class="reset-btn" onclick="confirmClearTemplates()" id="tmpl-clear-btn" style="margin:0 14px 18px;display:none;"></div>
  </div>
</div>

"""
fix('<!-- ================================================================\n     JOURNAL MODAL',
    tmpl_screen + '<!-- ================================================================\n     JOURNAL MODAL',
    "Экран шаблонов")

# ============================================================
# БЛОК 7: Кнопка сохранения шаблона после карты
# ============================================================
fix('  html+=`<div class="time-info">${time} сек · </div>`;\n  document.getElementById(\'k-results\').innerHTML=html;',
    '  html+=`<div class="save-tmpl-btn" onclick="openSaveTemplate()">📁 <span id="k-save-tmpl-lbl"></span></div>`;\n  html+=`<div class="time-info">${time} сек · </div>`;\n  document.getElementById(\'k-results\').innerHTML=html;\n  setText(\'k-save-tmpl-lbl\', t(\'saveTmpl\'));',
    "Кнопка сохранить шаблон")

# ============================================================
# БЛОК 8: Переводы KZ — добавить t5, saveTmpl и др.
# ============================================================
fix("    hFoot:'MEDIX AI · ЖМЖ Қазақстан',",
    "    hFoot:'MEDIX AI · ЖМЖ Қазақстан',\n    t5:'\u04ae\u043b\u0433\u0456\u043b\u0435\u0440',d5:'\u0421\u0430\u049b\u0442\u0430\u043b\u0493\u0430\u043d \u0448\u0430\u049b\u044b\u0440\u0443 \u043a\u0430\u0440\u0442\u0430\u043b\u0430\u0440\u044b',\n    saveTmpl:'\u04ae\u043b\u0433\u0456 \u0440\u0435\u0442\u0456\u043d\u0434\u0435 \u0441\u0430\u049b\u0442\u0430\u0443',\n    tmplTitle:'\u04ae\u043b\u0433\u0456\u043b\u0435\u0440',tmplSub:'\u0421\u0430\u049b\u0442\u0430\u043b\u0493\u0430\u043d \u043a\u0430\u0440\u0442\u0430\u043b\u0430\u0440 \u00b7 \u041e\u0444\u0444\u043b\u0430\u0439\u043d',\n    tmplEmpty:'\u04ae\u043b\u0433\u0456\u043b\u0435\u0440 \u0436\u043e\u049b. \u041a\u0430\u0440\u0442\u0430 \u0436\u0430\u0441\u0430\u043f, \u04af\u043b\u0433\u0456 \u0440\u0435\u0442\u0456\u043d\u0434\u0435 \u0441\u0430\u049b\u0442\u0430\u04a3\u044b\u0437.',\n    tmplClear:'\u0411\u0430\u0440\u043b\u044b\u049b \u04af\u043b\u0433\u0456\u043b\u0435\u0440\u0434\u0456 \u0442\u0430\u0437\u0430\u043b\u0430\u0443',\n    tmplSavePlh:'\u04ae\u043b\u0433\u0456 \u0430\u0442\u0430\u0443\u044b (\u043c\u044b\u0441\u0430\u043b\u044b: \u041e\u041a\u0421, \u0410\u043d\u0430\u0444\u0438\u043b\u0430\u043a\u0441\u0438\u044f)',",
    "Переводы KZ для шаблонов")

# ============================================================
# БЛОК 9: Переводы RU — добавить t5, saveTmpl и др.
# ============================================================
fix("    hFoot:'MEDIX AI · СМП Казахстан',",
    "    hFoot:'MEDIX AI · СМП Казахстан',\n    t5:'\u0428\u0430\u0431\u043b\u043e\u043d\u044b',d5:'\u0421\u043e\u0445\u0440\u0430\u043d\u0451\u043d\u043d\u044b\u0435 \u043a\u0430\u0440\u0442\u044b \u0432\u044b\u0437\u043e\u0432\u0430',\n    saveTmpl:'\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043a\u0430\u043a \u0448\u0430\u0431\u043b\u043e\u043d',\n    tmplTitle:'\u0428\u0430\u0431\u043b\u043e\u043d\u044b',tmplSub:'\u0421\u043e\u0445\u0440\u0430\u043d\u0451\u043d\u043d\u044b\u0435 \u043a\u0430\u0440\u0442\u044b \u00b7 \u041e\u0444\u0444\u043b\u0430\u0439\u043d',\n    tmplEmpty:'\u0428\u0430\u0431\u043b\u043e\u043d\u043e\u0432 \u043d\u0435\u0442. \u0421\u043e\u0437\u0434\u0430\u0439\u0442\u0435 \u043a\u0430\u0440\u0442\u0443 \u0438 \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u0435 \u043a\u0430\u043a \u0448\u0430\u0431\u043b\u043e\u043d.',\n    tmplClear:'\u041e\u0447\u0438\u0441\u0442\u0438\u0442\u044c \u0432\u0441\u0435 \u0448\u0430\u0431\u043b\u043e\u043d\u044b',\n    tmplSavePlh:'\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0448\u0430\u0431\u043b\u043e\u043d\u0430 (\u043d\u0430\u043f\u0440\u0438\u043c\u0435\u0440: \u041e\u041a\u0421, \u0410\u043d\u0430\u0444\u0438\u043b\u0430\u043a\u0441\u0438\u044f)',",
    "Переводы RU для шаблонов")

# ============================================================
# БЛОК 10: renderAll — t5 и шаблоны
# ============================================================
fix("  setText('h-t4',t('t4'));setText('h-d4',t('d4'));",
    "  setText('h-t4',t('t4'));setText('h-d4',t('d4'));\n  setText('h-t5',t('t5'));setText('h-d5',t('d5'));",
    "renderAll t5")

fix("  setText('h-foot',t('hFoot'));",
    "  setText('h-foot',t('hFoot'));\n  setText('tmpl-title',t('tmplTitle'));setText('tmpl-sub',t('tmplSub'));\n  const cb=document.getElementById('tmpl-clear-btn');if(cb)cb.textContent='\U0001f5d1\ufe0f '+t('tmplClear');\n  renderTemplatesList();",
    "renderAll шаблоны")

# ============================================================
# БЛОК 11: goTo — templates
# ============================================================
fix("  if(screen==='meds'){renderMedSubTabs();renderRashodList();renderPrihodList();updateShiftTime();}",
    "  if(screen==='meds'){renderMedSubTabs();renderRashodList();renderPrihodList();updateShiftTime();}\n  if(screen==='templates'){renderTemplatesList();}",
    "goTo templates")

# ============================================================
# БЛОК 12: JS функции шаблонов
# ============================================================
tmpl_js = """// ================================================================
// TEMPLATES
// ================================================================
let savedTemplates=[];
function loadTemplates(){try{return JSON.parse(localStorage.getItem('medix_templates_v1')||'[]');}catch(e){return[];}}
function saveTemplatesData(){localStorage.setItem('medix_templates_v1',JSON.stringify(savedTemplates));}
savedTemplates=loadTemplates();

function openSaveTemplate(){
  const name=prompt(t('tmplSavePlh'));
  if(!name||!name.trim()) return;
  const resultsEl=document.getElementById('k-results');
  const tmpl={id:Date.now(),name:name.trim(),lang:lang,ptype:ptype,html:resultsEl.innerHTML,date:new Date().toLocaleDateString('ru',{day:'2-digit',month:'2-digit',year:'2-digit'})};
  savedTemplates.unshift(tmpl);
  if(savedTemplates.length>50) savedTemplates=savedTemplates.slice(0,50);
  saveTemplatesData();
  alert(lang==='kz'?'\u04ae\u043b\u0433\u0456 \u0441\u0430\u049b\u0442\u0430\u043b\u0434\u044b!':'\u0428\u0430\u0431\u043b\u043e\u043d \u0441\u043e\u0445\u0440\u0430\u043d\u0451\u043d!');
}

function renderTemplatesList(){
  const list=document.getElementById('tmpl-list');
  const empty=document.getElementById('tmpl-empty');
  const clearBtn=document.getElementById('tmpl-clear-btn');
  if(!list) return;
  savedTemplates=loadTemplates();
  if(!savedTemplates.length){
    list.innerHTML='';
    if(empty){empty.style.display='block';empty.textContent=t('tmplEmpty');}
    if(clearBtn) clearBtn.style.display='none';
    return;
  }
  if(empty) empty.style.display='none';
  if(clearBtn) clearBtn.style.display='flex';
  list.innerHTML=savedTemplates.map((tmpl,i)=>`<div class="tmpl-card" onclick="openTemplate(${i})"><div class="tmpl-icon">\U0001f4cb</div><div class="tmpl-info"><div class="tmpl-name">${tmpl.name}</div><div class="tmpl-meta">${tmpl.lang==='kz'?'\u049a\u0410\u0417':'\u0420\u0423\u0421'} \u00b7 ${tmpl.date}</div></div><div class="tmpl-del" onclick="event.stopPropagation();deleteTemplate(${i})">\u2715</div></div>`).join('');
}

function openTemplate(idx){
  const tmpl=savedTemplates[idx];
  if(!tmpl) return;
  goTo('karta');
  document.getElementById('k-welcome').style.display='none';
  document.getElementById('k-results').innerHTML=tmpl.html;
  document.getElementById('k-results').style.display='block';
  setText('k-save-tmpl-lbl',t('saveTmpl'));
}

function deleteTemplate(idx){
  if(!confirm(lang==='kz'?'\u04ae\u043b\u0433\u0456\u043d\u0456 \u0436\u043e\u044e?':'\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0448\u0430\u0431\u043b\u043e\u043d?')) return;
  savedTemplates.splice(idx,1);
  saveTemplatesData();
  renderTemplatesList();
}

function confirmClearTemplates(){
  if(!confirm(lang==='kz'?'\u0411\u0430\u0440\u043b\u044b\u049b \u04af\u043b\u0433\u0456\u043b\u0435\u0440\u0434\u0456 \u0442\u0430\u0437\u0430\u043b\u0430\u0443\u0434\u044b \u0440\u0430\u0441\u0442\u0430\u0439\u0441\u044b\u0437 \u0431\u0430?':'\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0432\u0441\u0435 \u0448\u0430\u0431\u043b\u043e\u043d\u044b?')) return;
  savedTemplates=[];
  saveTemplatesData();
  renderTemplatesList();
}

"""
fix('// ================================================================\n// INIT',
    tmpl_js + '// ================================================================\n// INIT',
    "JS функции шаблонов")

# ============================================================
# Сохранить
# ============================================================
with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n{'='*50}")
print(f"Готово! Применено: {ok}, пропущено: {fail}")
print(f"Файл сохранён: {path}")
