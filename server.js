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

async function trackUser(req, endpoint) {
  const userId = req.body?.user_id;
  if (userId) {
    await redis.sadd('medix:unique_users', String(userId));
    await redis.incr('medix:total_requests');
    if (endpoint) await redis.incr('medix:endpoint:' + endpoint);
    const day = new Date().toISOString().slice(0, 10);
    await redis.incr('medix:day:' + day);
  }
}


app.get('/api/stats', async (req, res) => {
  try {
    const day = new Date().toISOString().slice(0, 10);
    const [users, total, karta, ai, calc, today] = await Promise.all([
      redis.scard('medix:unique_users'),
      redis.get('medix:total_requests'),
      redis.get('medix:endpoint:karta'),
      redis.get('medix:endpoint:ai'),
      redis.get('medix:endpoint:calc'),
      redis.get('medix:day:' + day),
    ]);
    res.json({
      unique_users: users || 0,
      total_requests: total || 0,
      karta: karta || 0,
      ai: ai || 0,
      calc: calc || 0,
      today: today || 0,
      uptime_hours: Math.floor(process.uptime() / 3600)
    });
  } catch(e) {
    console.error('Redis error:', e.message);
    res.json({unique_users: 0, total_requests: 0, karta: 0, ai: 0, calc: 0, today: 0, uptime_hours: Math.floor(process.uptime() / 3600), redis_error: e.message});
  }
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
  keyGenerator: (req) => req.body?.user_id ? String(req.body.user_id) : (req.headers['x-forwarded-for'] || req.ip),
});

// Лимит для карты вызова: 10 запросов в минуту по user_id или IP
const kartaLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 10,
  message: { error: 'Слишком много запросов карты. Подождите 1 минуту.' },
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.body?.user_id ? String(req.body.user_id) : (req.headers['x-forwarded-for'] || req.ip),
});

// Применяем общий лимит ко всем /api маршрутам
app.use('/api', generalLimiter);

// ─────────────────────────────────────────
// Статика
// ─────────────────────────────────────────
app.get('/', (req, res) => {
  res.redirect('https://14manas98-ctrl.github.io/medixai_landing/');
});
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
  trackUser(req, 'karta');
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
  trackUser(req, 'ai');
  console.log('Request /api/ai from user_id:', user_id || req.ip);

  try {
    const ANTHROPIC_KEY = process.env.ANTHROPIC_KEY;
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-6',
        max_tokens: max_tokens || 2500,
        stream: true,
        system: system,
        messages: messages,
        tools: [{ type: 'web_search_20250305', name: 'web_search' }]
      })
    });

    const reader = response.body.getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      res.write(value);
    }
    res.end();

  } catch (e) {
    console.error('Error /api/ai:', e.message);
    if (!res.headersSent) res.status(500).json({ error: e.message });
  }
});

// ─────────────────────────────────────────
// /api/calc — Калькулятор доз
// Модель: Haiku (структурированные расчёты, дешевле)
// ─────────────────────────────────────────
app.post('/api/calc', aiLimiter, async (req, res) => {
  const { system, messages, max_tokens, tools, user_id } = req.body;
  trackUser(req, 'calc');
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
  const bot = new TelegramBot(BOT_TOKEN, { webHook: { port: false } });
bot.setWebHook(`https://medixai-production.up.railway.app/bot${BOT_TOKEN}`);
app.post(`/bot${BOT_TOKEN}`, (req, res) => {
  bot.processUpdate(req.body);
  res.sendStatus(200);
});

  bot.onText(/\/start/, async function(msg) {

    const chatId = msg.chat.id;
    const name = msg.from.first_name;
    await redis.sadd('medix:unique_users', String(msg.from.id));

    bot.sendMessage(chatId,
      `👋 Добро пожаловать в Medix AI, ${name}!\n\n🗂 *Карта вызова* — AI заполнит за секунды\n💊 *Медикаменты* — учёт расхода за смену\n🤖 *AI чат* — протоколы и дозировки\n🧮 *Калькулятор* — детские дозы и шок-индекс\n\nОткрывай и пробуй! 👇`,
      {
        parse_mode: 'Markdown',
        reply_markup: {
          inline_keyboard: [
            [
              { text: '🚑 Открыть Medix AI', web_app: { url: 'https://medixai-production.up.railway.app/medix_final.html' } }
            ]
          ]
        }
      }
    );
  });

  bot.on('error', function(error) {
    console.log('Bot error:', error.message);
  });

  console.log('Telegram bot started!');
} else {
  console.log('BOT_TOKEN not found, bot not started');
}

// ─────────────────────────────────────────
// ACCESS BOT — приём заявок на Medix AI
// ─────────────────────────────────────────
const ACCESS_BOT_TOKEN = process.env.ACCESS_BOT_TOKEN;
const ADMIN_CHAT_ID = process.env.ADMIN_CHAT_ID;

if (ACCESS_BOT_TOKEN) {
  const accessBot = new TelegramBot(ACCESS_BOT_TOKEN, { polling: true });
  const userState = {};

  accessBot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    userState[chatId] = { step: 'language' };
    accessBot.sendMessage(chatId,
      `👋 Сәлем! / Привет!\n\n🏥 *Medix AI* — скорой жәрдем бригадалары үшін цифрлық көмекші\n\nТілді таңдаңыз / Выберите язык:`,
      { parse_mode: 'Markdown', reply_markup: { inline_keyboard: [[
        { text: '🇰🇿 Қазақша', callback_data: 'lang_kaz' },
        { text: '🇷🇺 Русский', callback_data: 'lang_rus' }
      ]]}}
    );
  });

  accessBot.on('callback_query', (query) => {
    const chatId = query.message.chat.id;
    const data = query.data;
    if (!userState[chatId]) userState[chatId] = {};
    accessBot.answerCallbackQuery(query.id);

    if (data === 'lang_kaz' || data === 'lang_rus') {
      userState[chatId].lang = data === 'lang_kaz' ? 'kaz' : 'rus';
      userState[chatId].step = 'name';
      const isKaz = userState[chatId].lang === 'kaz';
      accessBot.sendMessage(chatId, isKaz ? '✅ Қазақ тілі!\n\nАтыңызды жазыңыз 👇' : '✅ Русский язык!\n\nНапишите ваше имя 👇');
    }
    else if (data.startsWith('prof_')) {
      userState[chatId].profession = data.replace('prof_', '');
      userState[chatId].step = 'city';
      const isKaz = userState[chatId].lang === 'kaz';
      accessBot.sendMessage(chatId, isKaz ? '🏙 Қалаңызды жазыңыз 👇' : '🏙 Напишите ваш город 👇');
    }
  });

  accessBot.on('message', (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text;
    if (!text || text.startsWith('/')) return;
    if (!userState[chatId]) return;
    const state = userState[chatId];
    const isKaz = state.lang === 'kaz';

    if (state.step === 'name') {
      userState[chatId].name = text;
      userState[chatId].step = 'profession';
      accessBot.sendMessage(chatId,
        isKaz ? `Сәлем, *${text}*! 👋\n\nМамандығыңызды таңдаңыз:` : `Привет, *${text}*! 👋\n\nВыберите профессию:`,
        { parse_mode: 'Markdown', reply_markup: { inline_keyboard: [
          [{ text: '🚑 Фельдшер', callback_data: 'prof_Фельдшер' }, { text: '👨‍⚕️ Врач', callback_data: 'prof_Врач' }],
          [{ text: '🎓 Студент', callback_data: 'prof_Студент' }, { text: '👩‍⚕️ Медсестра', callback_data: 'prof_Медсестра' }]
        ]}}
      );
    }
    else if (state.step === 'city') {
      userState[chatId].city = text;
      userState[chatId].step = 'done';

      accessBot.sendMessage(chatId,
        isKaz
          ? `✅ *Өтінішіңіз қабылданды!*\n\n🚑 Medix AI-ды қазір ашыңыз 👇`
          : `✅ *Заявка принята!*\n\n🚑 Открывай Medix AI прямо сейчас 👇`,
        { parse_mode: 'Markdown', reply_markup: { inline_keyboard: [
          [{ text: '🚑 Открыть Medix AI', url: 'https://t.me/iikomek_bot?start=open' }],
          
        ]}}
      );
      if (ADMIN_CHAT_ID) {
        const username = msg.from.username;
        const userLink = username
          ? `@${username}`
          : `[Написать](tg://user?id=${chatId})`;
        const noUsernameNote = username ? '' : '\n⚠️ У пользователя нет username — используй кнопку ниже';
        accessBot.sendMessage(ADMIN_CHAT_ID,
          `🔔 *Новая заявка!*\n\n👤 ${state.name}\n💼 ${state.profession}\n🏙 ${text}\n🌐 ${isKaz ? 'Казахский' : 'Русский'}\n📱 ${userLink}\n🆔 \`${chatId}\`${noUsernameNote}`,
          {
            parse_mode: 'Markdown',
            reply_markup: username ? undefined : {
              inline_keyboard: [[
                { text: '💬 Написать пользователю', url: `tg://user?id=${chatId}` }
              ]]
            }
          }
        );
      }
    }
  });

  console.log('Access bot started!');
} else {
  console.log('ACCESS_BOT_TOKEN not found');
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
