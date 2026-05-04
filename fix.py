with open('public/medix_final.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Заменить текст родничка на таблицу по возрасту
old_rodnik = '<div style="font-size:10px;color:var(--accent);line-height:1.6;padding:4px 2px;margin-top:4px;" id="norms-rodnik"></div>'

new_rodnik = '''<div style="margin-top:8px;border-radius:10px;overflow:hidden;border:1px solid var(--border);">
          <div style="background:var(--tag-bg);padding:6px 10px;font-size:9px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--sub);border-bottom:1px solid var(--border);" id="norms-rodnik-title"></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;padding:6px 10px;border-bottom:1px solid var(--border);"><span style="font-size:11px;color:var(--text1);">0–3 мес</span><span style="font-size:11px;font-weight:700;color:var(--accent);">2.5–3.0 см</span></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;padding:6px 10px;border-bottom:1px solid var(--border);"><span style="font-size:11px;color:var(--text1);">3–6 мес</span><span style="font-size:11px;font-weight:700;color:var(--accent);">2.0–2.5 см</span></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;padding:6px 10px;border-bottom:1px solid var(--border);"><span style="font-size:11px;color:var(--text1);">6–9 мес</span><span style="font-size:11px;font-weight:700;color:var(--accent);">1.5–2.0 см</span></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;padding:6px 10px;border-bottom:1px solid var(--border);"><span style="font-size:11px;color:var(--text1);">9–12 мес</span><span style="font-size:11px;font-weight:700;color:var(--warn);">0.5–1.0 см</span></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;padding:6px 10px;"><span style="font-size:11px;color:var(--text1);">12–18 мес</span><span style="font-size:11px;font-weight:700;color:var(--success);">закрыт</span></div>
        </div>'''

html = html.replace(old_rodnik, new_rodnik)

# Обновить заголовок родничка в JS
html = html.replace(
    "if(rodnikEl) rodnikEl.textContent = '🔵 ' + (t('normsRodnik')||'');",
    "const rodnikTitle = document.getElementById('norms-rodnik-title');\n  if(rodnikTitle) rodnikTitle.textContent = isKz ? 'ҮЛКЕН НҮКТЕ (БОЛЬШОЙ РОДНИЧОК)' : 'БОЛЬШОЙ РОДНИЧОК';"
)

with open('public/medix_final.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("OK")