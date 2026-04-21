const express = require('express');
const app = express();

app.use(express.json());

// CORS
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  res.header('Access-Control-Allow-Methods', 'POST, OPTIONS');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// Статика — отдаём файлы из папки public/
app.use(express.static('public'));

// ─────────────────────────────────────────
// Общая функция вызова Anthropic API
// ─────────────────────────────────────────
async function callAnthropic(body) {
  const ANTHROPIC_KEY = process.env.ANTHROPIC_KEY;
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': ANTHROPIC_KEY,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify(body)
  });
  return await response.json();
}

// ─────────────────────────────────────────
// /api/karta — Карта вызова
// ─────────────────────────────────────────
app.post('/api/karta', async (req, res) => {
  const { prompt, system, messages } = req.body;
  console.log('Request /api/karta');
  try {
    // Поддержка старого формата (prompt) и нового (system + messages)
    let body;
    if (messages) {
      body = {
        model: 'claude-sonnet-4-5',
        max_tokens: 2000,
        system: system,
        messages: messages
      };
    } else {
      body = {
        model: 'claude-sonnet-4-5',
        max_tokens: 2000,
        messages: [{ role: 'user', content: prompt }]
      };
    }
    const data = await callAnthropic(body);
    res.json(data);
  } catch (e) {
    console.error('Error /api/karta:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// ─────────────────────────────────────────
// /api/ai — Медицинский AI чат (с web_search)
// ─────────────────────────────────────────
app.post('/api/ai', async (req, res) => {
  const { system, messages, max_tokens } = req.body;
  console.log('Request /api/ai');
  try {
    const data = await callAnthropic({
      model: 'claude-sonnet-4-5',
      max_tokens: max_tokens || 1500,
      system: system,
      messages: messages,
      tools: [{ type: 'web_search_20250305', name: 'web_search' }]
    });
    res.json(data);
  } catch (e) {
    console.error('Error /api/ai:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// ─────────────────────────────────────────
// /api/calc — Калькулятор доз (с web_search)
// ─────────────────────────────────────────
app.post('/api/calc', async (req, res) => {
  const { system, messages, max_tokens, tools } = req.body;
  console.log('Request /api/calc');
  try {
    const body = {
      model: 'claude-sonnet-4-5',
      max_tokens: max_tokens || 2000,
      system: system,
      messages: messages
    };
    // Передаём tools если есть (web_search)
    if (tools) body.tools = tools;
    const data = await callAnthropic(body);
    res.json(data);
  } catch (e) {
    console.error('Error /api/calc:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// ─────────────────────────────────────────
// Запуск сервера
// ─────────────────────────────────────────
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`MedixAI server running on port ${PORT}`);
});
