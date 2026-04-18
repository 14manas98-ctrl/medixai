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
  const GEMINI_KEY = process.env.GEMINI_KEY;
  
  console.log('Request received, key exists:', !!GEMINI_KEY);
  
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }]
        })
      }
    );
    
    const data = await response.json();
    console.log('Gemini status:', response.status);
    console.log('Gemini data:', JSON.stringify(data).substring(0, 200));
    
    if (data.error) {
      console.error('Gemini error:', data.error.message);
      return res.status(500).json({ error: data.error.message });
    }
    
    res.json({ text: data.candidates[0].content.parts[0].text });
  } catch (e) {
    console.error('Server error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Medix AI сервер запущен на порту ${PORT}`));