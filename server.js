const express = require('express');
const app = express();
 
app.use(express.json());
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  res.header('Access-Control-Allow-Methods', 'POST, OPTIONS');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});
 
app.use(express.static('public'));
 
app.post('/api/karta', async (req, res) => {
  const { prompt } = req.body;
  const ANTHROPIC_KEY = process.env.ANTHROPIC_KEY;
 
  console.log('Request received, key exists:', !!ANTHROPIC_KEY);
 
  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-6',
        max_tokens: 1500,
        messages: [{ role: 'user', content: prompt }]
      })
    });
 
    const data = await response.json();
    console.log('Anthropic status:', response.status);
 
    if (data.error) {
      console.error('Anthropic error:', data.error.message);
      return res.status(500).json({ error: data.error.message });
    }
 
    res.json({ text: data.content[0].text });
  } catch (e) {
    console.error('Server error:', e.message);
    res.status(500).json({ error: e.message });
  }
});
 
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Medix AI сервер запущен на порту ${PORT}`));
 