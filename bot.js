const TelegramBot = require('node-telegram-bot-api');

const TOKEN = '8684002127:AAHewwmYW0y4NOa5hn2yrnfqM-mGlBhMJkU';
const bot = new TelegramBot(TOKEN, {polling: true});

bot.onText(/\/start/, function(msg) {
  const chatId = msg.chat.id;
  const name = msg.from.first_name;
  bot.sendMessage(chatId, 'Салем ' + name + '! Мен Medix AI!', {
    reply_markup: {
      inline_keyboard: [[
        {text: 'Medix AI ашу', web_app: {url: 'https://14manas98-ctrl.github.io/medixai'}}
      ]]
    }
  });
});

bot.on('polling_error', function(error) {
  console.log(error.message);
});

console.log('Medix AI запущен!');