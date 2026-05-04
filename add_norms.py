import os

path = 'public/medix_final.html'
if not os.path.exists(path):
    path = 'medix_final.html'
if not os.path.exists(path):
    print("ERROR: file not found!")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

ok = 0

def fix(old, new, desc):
    global html, ok
    if old in html:
        html = html.replace(old, new, 1)
        print(f"OK: {desc}")
        ok += 1
    else:
        print(f"SKIP: {desc}")

# ============================================================
# 1. Добавить 2 новые вкладки в таб-бар калькулятора
# ============================================================
fix(
    '<div class="mtab" id="ct-shock" onclick="switchCalcTab(\'shock\')">⚡ <span id="ct-shock-lbl"></span></div>',
    '<div class="mtab" id="ct-shock" onclick="switchCalcTab(\'shock\')">⚡ <span id="ct-shock-lbl"></span></div>\n        <div class="mtab" id="ct-norms" onclick="switchCalcTab(\'norms\')">📊 <span id="ct-norms-lbl"></span></div>\n        <div class="mtab" id="ct-preg" onclick="switchCalcTab(\'preg\')">🤰 <span id="ct-preg-lbl"></span></div>',
    "Новые вкладки калькулятора"
)

# ============================================================
# 2. Добавить панели Нормы и Беременность после панели Шок-индекс
# ============================================================
norms_panel = """
    <!-- Панель: Нормы детей -->
    <div class="pane" id="cpane-norms">
      <div class="mid" id="norms-mid" style="padding:10px 14px;">
        <div style="font-size:9.5px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:var(--ex-label);margin-bottom:10px;" id="norms-title-lbl"></div>
        <!-- Таблица норм -->
        <div style="border-radius:12px;overflow:hidden;border:1px solid var(--border);margin-bottom:10px;">
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;background:var(--tag-bg);padding:7px 10px;border-bottom:1px solid var(--border);">
            <div style="font-size:9px;font-weight:700;color:var(--sub);" id="norms-col-age"></div>
            <div style="font-size:9px;font-weight:700;color:var(--sub);text-align:center;">ЧСС</div>
            <div style="font-size:9px;font-weight:700;color:var(--sub);text-align:center;">ЧДД</div>
            <div style="font-size:9px;font-weight:700;color:var(--sub);text-align:center;">АД сист.</div>
          </div>
          <div id="norms-rows"></div>
        </div>
        <div style="font-size:10px;color:var(--sub);line-height:1.6;padding:4px 2px;" id="norms-note"></div>
      </div>
    </div>

    <!-- Панель: Беременность -->
    <div class="pane" id="cpane-preg">
      <div class="mid" id="preg-mid" style="padding:10px 14px;">
        <div style="font-size:9.5px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:var(--ex-label);margin-bottom:10px;" id="preg-title-lbl"></div>
        <!-- Поле ввода ПМ -->
        <div style="margin-bottom:12px;">
          <div style="font-size:11px;font-weight:600;color:var(--text1);margin-bottom:6px;" id="preg-lmp-label"></div>
          <input type="date" id="preg-lmp-input" style="width:100%;padding:10px 14px;border-radius:11px;background:var(--inp);border:1.5px solid var(--border2);color:var(--text1);font-size:13px;font-family:'Inter',sans-serif;outline:none;" oninput="calcPreg()">
        </div>
        <div id="preg-results" style="display:none;">
          <!-- Срок -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px;">
            <div class="param-box" style="text-align:center;">
              <div class="param-label" id="preg-weeks-lbl"></div>
              <div class="param-val" id="preg-weeks" style="color:var(--accent);font-size:24px;"></div>
            </div>
            <div class="param-box" style="text-align:center;">
              <div class="param-label" id="preg-months-lbl"></div>
              <div class="param-val" id="preg-months" style="color:var(--accent);font-size:24px;"></div>
            </div>
          </div>
          <!-- ПДР -->
          <div style="padding:10px 13px;border-radius:11px;background:var(--card);border:1px solid var(--border);margin-bottom:8px;">
            <div style="font-size:9.5px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--sub);margin-bottom:4px;" id="preg-pdr-lbl"></div>
            <div style="font-size:16px;font-weight:700;color:var(--text1);" id="preg-pdr"></div>
          </div>
          <!-- Нормы по сроку -->
          <div style="padding:10px 13px;border-radius:11px;background:var(--card);border:1px solid var(--border);margin-bottom:8px;">
            <div style="font-size:9.5px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--sub);margin-bottom:8px;" id="preg-norms-lbl"></div>
            <div id="preg-norms-rows" style="display:flex;flex-direction:column;gap:6px;"></div>
          </div>
          <!-- Предупреждение -->
          <div id="preg-warn" style="display:none;" class="warn-item">
            <span class="warn-icon">⚠️</span>
            <span class="warn-text" id="preg-warn-text"></span>
          </div>
        </div>
        <div id="preg-empty" style="text-align:center;padding:30px 0;color:var(--sub);font-size:13px;" id="preg-empty-lbl"></div>
      </div>
    </div>
"""

fix(
    '<!-- ================================================================\n     ONBOARDING MODAL',
    norms_panel + '\n<!-- ================================================================\n     ONBOARDING MODAL',
    "Панели Нормы и Беременность"
)

# ============================================================
# 3. Переводы KZ
# ============================================================
fix(
    "    wLabel:'САЛМАҚ',ageLabel:'ЖАС',sitLabel:'ЖАҒДАЙ',",
    """    wLabel:'САЛМАҚ',ageLabel:'ЖАС',sitLabel:'ЖАҒДАЙ',
    cTabNorms:'📊 Нормалар',cTabPreg:'\U0001f930 Жүктілік',
    normsTitle:'БАЛАЛАРДАҒЫ НОРМАЛАР',normsColAge:'ЖАС',normsNote:'* Нормалар шамамен. Жеке ерекшеліктерді ескеріңіз.',
    pregTitle:'\u0416\u04af\u043a\u0442\u0456\u043b\u0456\u043a \u043a\u0430\u043b\u044c\u043a\u0443\u043b\u044f\u0442\u043e\u0440\u044b',pregLmpLabel:'\u0421\u043e\u04a3\u0493\u044b \u0430\u0439\u044b\u0437 \u0431\u0430\u0441\u0442\u0430\u043b\u0493\u0430\u043d \u043a\u04af\u043d\u0456 (КА\u0411):',
    pregWeeksLbl:'\u0410\u041f\u0422\u0410 (\u0430\u043f\u0442\u0430)',pregMonthsLbl:'\u0410\u041f\u0422\u0410 (\u0430\u0439)',
    pregPdrLbl:'\u0411\u043e\u043b\u0436\u0430\u043b\u0493\u0430\u043d \u0442\u0443 \u043c\u0435\u0440\u0437\u0456\u043c\u0456 (\u0411\u0422\u041c):',
    pregNormsLbl:'\u041c\u0435\u0440\u0437\u0456\u043c\u0433\u0435 \u0441\u04d9\u0439\u043a\u0435\u0441 \u043d\u043e\u0440\u043c\u0430\u043b\u0430\u0440:',
    pregEmpty:'\u041a\u0410\u0411 \u043a\u04af\u043d\u0456\u043d \u0435\u043d\u0433\u0456\u0437\u0456\u04a3\u0456\u0437...',
    pregTooEarly:'\u041c\u0435\u0440\u0437\u0456\u043c \u0442\u044b\u043c \u0430\u0437. \u0416\u04af\u043a\u0442\u0456\u043b\u0456\u043a\u0442\u0456 \u0442\u0435\u043a\u0441\u0435\u0440\u0456\u04a3\u0456\u0437.',
    pregTooLate:'\u0424\u0438\u0437\u0438\u043e\u043b\u043e\u0433\u0438\u044f\u043b\u044b\u049b \u043c\u0435\u0440\u0437\u0456\u043c\u043d\u0435\u043d \u0430\u0441\u0430\u0434\u044b. \u0428\u044b\u043d\u0430\u044b \u0442\u0435\u043a\u0441\u0435\u0440\u0456\u04a3\u0456\u0437.',""",
    "Переводы KZ нормы+беременность"
)

# ============================================================
# 4. Переводы RU
# ============================================================
fix(
    "    wLabel:'ВЕС',ageLabel:'ВОЗРАСТ',sitLabel:'СИТУАЦИЯ',",
    """    wLabel:'ВЕС',ageLabel:'ВОЗРАСТ',sitLabel:'СИТУАЦИЯ',
    cTabNorms:'📊 Нормы',cTabPreg:'\U0001f930 Беременность',
    normsTitle:'НОРМЫ У ДЕТЕЙ',normsColAge:'ВОЗРАСТ',normsNote:'* Нормы ориентировочные. Учитывайте индивидуальные особенности.',
    pregTitle:'Калькулятор беременности',pregLmpLabel:'Дата последней менструации (ПМ):',
    pregWeeksLbl:'СРОК (нед)',pregMonthsLbl:'СРОК (мес)',
    pregPdrLbl:'Предполагаемая дата родов (ПДР):',
    pregNormsLbl:'Нормы по сроку:',
    pregEmpty:'Введите дату ПМ...',
    pregTooEarly:'Срок слишком мал. Проверьте беременность.',
    pregTooLate:'Срок превышает физиологический. Уточните данные.',""",
    "Переводы RU нормы+беременность"
)

# ============================================================
# 5. renderAll — добавить новые вкладки
# ============================================================
fix(
    "  setText('ct-dose-lbl',t('cTabDose'));setText('ct-shock-lbl',t('cTabShock'));",
    "  setText('ct-dose-lbl',t('cTabDose'));setText('ct-shock-lbl',t('cTabShock'));\n  setText('ct-norms-lbl',t('cTabNorms'));setText('ct-preg-lbl',t('cTabPreg'));\n  renderNormsPanel();renderPregPanel();",
    "renderAll новые вкладки"
)

# ============================================================
# 6. switchCalcTab — добавить norms и preg
# ============================================================
fix(
    """function switchCalcTab(tab){
  calcTab=tab;
  document.getElementById('cpane-dose').classList.toggle('active',tab==='dose');
  document.getElementById('cpane-shock').classList.toggle('active',tab==='shock');
  document.getElementById('ct-dose').classList.toggle('on',tab==='dose');
  document.getElementById('ct-shock').classList.toggle('on',tab==='shock');
}""",
    """function switchCalcTab(tab){
  calcTab=tab;
  ['dose','shock','norms','preg'].forEach(t=>{
    const p=document.getElementById('cpane-'+t);
    const b=document.getElementById('ct-'+t);
    if(p) p.classList.toggle('active',t===tab);
    if(b) b.classList.toggle('on',t===tab);
  });
}""",
    "switchCalcTab расширен"
)

# ============================================================
# 7. JS функции Нормы и Беременность
# ============================================================
norms_js = """
// ================================================================
// NORMS & PREGNANCY
// ================================================================
const CHILD_NORMS = [
  {age:'0–1 мес',  ageKz:'0–1 ай',   hr:'110–170', rr:'40–60', bp:'60–80'},
  {age:'1–6 мес',  ageKz:'1–6 ай',   hr:'100–160', rr:'35–48', bp:'70–90'},
  {age:'6–12 мес', ageKz:'6–12 ай',  hr:'100–150', rr:'30–45', bp:'80–95'},
  {age:'1–2 года', ageKz:'1–2 жас',  hr:'90–140',  rr:'25–35', bp:'85–100'},
  {age:'3–5 лет',  ageKz:'3–5 жас',  hr:'80–120',  rr:'22–30', bp:'90–105'},
  {age:'6–10 лет', ageKz:'6–10 жас', hr:'70–110',  rr:'18–25', bp:'95–110'},
  {age:'11–15 лет',ageKz:'11–15 жас',hr:'60–100',  rr:'15–20', bp:'100–120'},
];

function renderNormsPanel(){
  const isKz = lang==='kz';
  const titleEl = document.getElementById('norms-title-lbl');
  const colAge = document.getElementById('norms-col-age');
  const noteEl = document.getElementById('norms-note');
  if(titleEl) titleEl.textContent = t('normsTitle');
  if(colAge) colAge.textContent = t('normsColAge');
  if(noteEl) noteEl.textContent = t('normsNote');
  const rows = document.getElementById('norms-rows');
  if(!rows) return;
  rows.innerHTML = CHILD_NORMS.map((r,i)=>`
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;padding:7px 10px;border-bottom:${i<CHILD_NORMS.length-1?'1px solid var(--border)':'none'};">
      <div style="font-size:12px;font-weight:600;color:var(--text1);">${isKz?r.ageKz:r.age}</div>
      <div style="font-size:12px;text-align:center;color:var(--danger);">${r.hr}</div>
      <div style="font-size:12px;text-align:center;color:var(--accent);">${r.rr}</div>
      <div style="font-size:12px;text-align:center;color:var(--warn);">${r.bp}</div>
    </div>
  `).join('');
}

function renderPregPanel(){
  const isKz = lang==='kz';
  const els = {
    title: document.getElementById('preg-title-lbl'),
    lmpLbl: document.getElementById('preg-lmp-label'),
    weeksLbl: document.getElementById('preg-weeks-lbl'),
    monthsLbl: document.getElementById('preg-months-lbl'),
    pdrLbl: document.getElementById('preg-pdr-lbl'),
    normsLbl: document.getElementById('preg-norms-lbl'),
    emptyLbl: document.getElementById('preg-empty'),
  };
  if(els.title) els.title.textContent = t('pregTitle');
  if(els.lmpLbl) els.lmpLbl.textContent = t('pregLmpLabel');
  if(els.weeksLbl) els.weeksLbl.textContent = t('pregWeeksLbl');
  if(els.monthsLbl) els.monthsLbl.textContent = t('pregMonthsLbl');
  if(els.pdrLbl) els.pdrLbl.textContent = t('pregPdrLbl');
  if(els.normsLbl) els.normsLbl.textContent = t('pregNormsLbl');
  if(els.emptyLbl) els.emptyLbl.textContent = t('pregEmpty');
  // re-calc if date already entered
  const inp = document.getElementById('preg-lmp-input');
  if(inp && inp.value) calcPreg();
}

function calcPreg(){
  const inp = document.getElementById('preg-lmp-input');
  if(!inp||!inp.value) return;
  const lmp = new Date(inp.value);
  const today = new Date();
  const diffMs = today - lmp;
  const diffDays = Math.floor(diffMs / 86400000);
  const weeks = Math.floor(diffDays / 7);
  const days = diffDays % 7;
  const months = (diffDays / 30.44).toFixed(1);
  const isKz = lang==='kz';

  const resultsEl = document.getElementById('preg-results');
  const emptyEl = document.getElementById('preg-empty');
  const warnEl = document.getElementById('preg-warn');
  const warnText = document.getElementById('preg-warn-text');

  if(weeks < 4){
    if(resultsEl) resultsEl.style.display='none';
    if(emptyEl) emptyEl.style.display='block';
    if(emptyEl) emptyEl.textContent = t('pregTooEarly');
    return;
  }
  if(weeks > 42){
    if(resultsEl) resultsEl.style.display='none';
    if(emptyEl) emptyEl.style.display='block';
    if(emptyEl) emptyEl.textContent = t('pregTooLate');
    return;
  }

  if(emptyEl) emptyEl.style.display='none';
  if(resultsEl) resultsEl.style.display='block';

  // Срок
  const weeksEl = document.getElementById('preg-weeks');
  const monthsEl = document.getElementById('preg-months');
  if(weeksEl) weeksEl.textContent = weeks + (days>0 ? '+'+days : '');
  if(monthsEl) monthsEl.textContent = months;

  // ПДР (Негеле: ПМ + 280 дней)
  const pdr = new Date(lmp.getTime() + 280*86400000);
  const pdrEl = document.getElementById('preg-pdr');
  if(pdrEl) pdrEl.textContent = pdr.toLocaleDateString(isKz?'kk-KZ':'ru-RU', {day:'numeric',month:'long',year:'numeric'});

  // Нормы по сроку
  const normsEl = document.getElementById('preg-norms-rows');
  if(normsEl){
    // ВДМ = срок недель - 4 (с 16 нед), примерно
    let vdm = '—', okr = '—', fhr = '120–160 уд/мин';
    if(weeks >= 16 && weeks <= 40){
      vdm = `${weeks - 2}–${weeks + 2} см`;
      okr = `${weeks * 2 + 50}–${weeks * 2 + 60} см`;
    }
    const normsData = [
      {lbl: isKz?'ЖСЖ ұрықта':'ЧСС плода', val: fhr, color:'var(--danger)'},
      {lbl: isKz?'Жатыр дүнінің биіктігі (ЖДБ)':'Высота дна матки (ВДМ)', val: vdm, color:'var(--accent)'},
      {lbl: isKz?'Іш айналымы':'Окружность живота', val: okr, color:'var(--warn)'},
    ];
    normsEl.innerHTML = normsData.map(n=>`
      <div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid var(--border);">
        <div style="font-size:12px;color:var(--text2);">${n.lbl}</div>
        <div style="font-size:13px;font-weight:700;color:${n.color};">${n.val}</div>
      </div>
    `).join('');
  }

  // Предупреждения
  if(warnEl && warnText){
    if(weeks >= 37){
      warnEl.style.display='flex';
      warnText.textContent = isKz?'Мерзімді жүктілік. Туу кез-келген уақытта басталуы мүмкін.':'Доношенная беременность. Роды могут начаться в любой момент.';
    } else if(weeks < 22){
      warnEl.style.display='flex';
      warnText.textContent = isKaz?'Ерте мерзімдегі жүктілік. Акушер-гинеколог консультациясы қажет.':'Ранний срок. Необходима консультация акушера-гинеколога.';
    } else {
      warnEl.style.display='none';
    }
  }
}

"""

fix(
    '// ================================================================\n// INIT',
    norms_js + '// ================================================================\n// INIT',
    "JS функции Нормы и Беременность"
)

# ============================================================
with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\\n{'='*50}")
print(f"Готово! Применено: {ok}/7")
print(f"Файл: {path}")
