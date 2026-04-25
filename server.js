const express = require('express');
const rateLimit = require('express-rate-limit');
const app = express();

app.use(express.json());

// ─────────────────────────────────────────
// SECURITY — helmet
// ─────────────────────────────────────────
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
// СЧЁТЧИК УНИКАЛЬНЫХ ПОЛЬЗОВАТЕЛЕЙ
// ─────────────────────────────────────────
const { Redis } = require('@upstash/redis');

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
});

async function trackUser(req) {
  const userId = req.body?.user_id;
  if (userId) {
    await redis.sadd('medix:unique_users', String(userId));
  }
}

app.get('/api/stats', async (req, res) => {
  const count = await redis.scard('medix:unique_users');
  res.json({
    unique_users: count,
    uptime_hours: Math.floor(process.uptime() / 3600)
  });
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

// Лимит для AI запросов: 20 запросов в минуту по user_id или IP
const aiLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 20,
  message: { error: 'Слишком много AI запросов. Подождите 1 минуту.' },
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.body?.user_id ? String(req.body.user_id) : req.ip,
});

// Лимит для карты вызова: 10 запросов в минуту по user_id или IP
const kartaLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 10,
  message: { error: 'Слишком много запросов карты. Подождите 1 минуту.' },
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.body?.user_id ? String(req.body.user_id) : req.ip,
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
// Модель: Sonnet (главный продукт, качество важно)
// max_tokens: 4096 (фикс бага обрыва JSON)
// ─────────────────────────────────────────
app.post('/api/karta', kartaLimiter, async (req, res) => {
  const { prompt, system, messages, user_id } = req.body;
  trackUser(req);
  console.log('Request /api/karta from user_id:', user_id || req.ip);
  try {
    let body;
    if (messages) {
      body = {
        model: 'claude-sonnet-4-6',
        max_tokens: 4096,
        system: system,
        messages: messages
      };
    } else {
      body = {
        model: 'claude-sonnet-4-6',
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
  const { system, messages, max_tokens, user_id } = req.body;
  trackUser(req);
  console.log('Request /api/ai from user_id:', user_id || req.ip);
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
  const { system, messages, max_tokens, tools, user_id } = req.body;
  trackUser(req);
  console.log('Request /api/calc from user_id:', user_id || req.ip);
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

  bot.onText(/\/start/, async function(msg) {

    const chatId = msg.chat.id;
    const name = msg.from.first_name;
    await redis.sadd('medix:unique_users', String(msg.from.id));

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
  console.log('Rate limiting: ENABLED (by user_id + IP)');
  console.log('Security: ACTIVE');
});
