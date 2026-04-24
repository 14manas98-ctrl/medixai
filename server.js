const express = require('express');
const rateLimit = require('express-rate-limit');
const app = express();

app.use(express.json());

// ─────────────────────────────────────────
// CORS
// ─────────────────────────────────────────
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  res.header('Access-Control-Allow-Methods', 'POST, OPTIONS');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// ─────────────────────────────────────────
// RATE LIMITING — защита от злоупотреблений
// ─────────────────────────────────────────

// Общий лимит: 100 запросов за 15 минут с одного IP
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { error: 'Слишком много запросов. Подождите 15 минут.' },
  standardHeaders: true,
  legacyHeaders: false,
});

// Лимит для AI запросов: 20 запросов в минуту
const aiLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 20,
  message: { error: 'Слишком много AI запросов. Подождите 1 минуту.' },
  standardHeaders: true,
  legacyHeaders: false,
});

// Лимит для карты вызова: 10 запросов в минуту
const kartaLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 10,
  message: { error: 'Слишком много запросов карты. Подождите 1 минуту.' },
  standardHeaders: true,
  legacyHeaders: false,
});

// Применяем общий лимит ко всем /api маршрутам
app.use('/api', generalLimiter);

// ─────────────────────────────────────────
// Статика
// ─────────────────────────────────────────
app.use(express.static('public'));

// ─────────────────────────────────────────
// Общая функция вызова Anthropic API
// ─────────────────────────────────────────
async function callAnthropic(body) {
  const ANTHROPIC_KEY = process.env.ANTHROPIC_KEY;
  if (!ANTHROPIC_KEY) {
    throw new Error('ANTHROPIC_KEY не настроен на сервере');
  }
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
// Модель: Haiku (структурированная задача, дешевле)
// max_tokens: 4096 (фикс бага обрыва JSON)
// ─────────────────────────────────────────
app.post('/api/karta', kartaLimiter, async (req, res) => {
  const { prompt, system, messages } = req.body;
  console.log('Request /api/karta from:', req.ip);
  try {
    let body;
    if (messages) {
      body = {
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 4096,
        system: system,
        messages: messages
      };
    } else {
      body = {
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 4096,
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
// /api/ai — Медицинский AI чат
// Модель: Sonnet (сложные клинические вопросы)
// ─────────────────────────────────────────
app.post('/api/ai', aiLimiter, async (req, res) => {
  const { system, messages, max_tokens } = req.body;
  console.log('Request /api/ai from:', req.ip);
  try {
    const data = await callAnthropic({
      model: 'claude-sonnet-4-6',
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
// /api/calc — Калькулятор доз
// Модель: Haiku (структурированные расчёты, дешевле)
// ─────────────────────────────────────────
app.post('/api/calc', aiLimiter, async (req, res) => {
  const { system, messages, max_tokens, tools } = req.body;
  console.log('Request /api/calc from:', req.ip);
  try {
    const body = {
      model: 'claude-haiku-4-5-20251001',
      max_tokens: max_tokens || 2000,
      system: system,
      messages: messages
    };
    if (tools) body.tools = tools;
    const data = await callAnthropic(body);
    res.json(data);
  } catch (e) {
    console.error('Error /api/calc:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// ─────────────────────────────────────────
// TELEGRAM BOT
// ─────────────────────────────────────────
const TelegramBot = require('node-telegram-bot-api');
const BOT_TOKEN = process.env.BOT_TOKEN;

if (BOT_TOKEN) {
  const bot = new TelegramBot(BOT_TOKEN, { polling: true });

  bot.onText(/\/start/, function(msg) {
    const chatId = msg.chat.id;
    const name = msg.from.first_name;
    bot.sendMessage(chatId, 'Салем ' + name + '! Мен Medix AI!', {
      reply_markup: {
        inline_keyboard: [[
          {
            text: '🚑 Medix AI ашу',
            web_app: { url: 'https://medixai-production.up.railway.app/medix_final.html' }
          }
        ]]
      }
    });
  });

  bot.on('polling_error', function(error) {
    console.log('Bot error:', error.message);
  });

  console.log('Telegram bot started!');
} else {
  console.log('BOT_TOKEN not found, bot not started');
}

// ─────────────────────────────────────────
// Запуск сервера
// ─────────────────────────────────────────
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`MedixAI server running on port ${PORT}`);
  console.log('Rate limiting: ENABLED');
  console.log('Security: ACTIVE');
});