export default async function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }
  if (req.method !== 'POST') return res.status(405).end();
  res.setHeader('Access-Control-Allow-Origin', '*');

  try {
    const prompt = req.body.messages[0].content;
    const apiKey = process.env.GEMINI_API_KEY;
    
    if (!apiKey) {
      return res.status(401).json({ error: { message: 'API Key não configurada. Configure GEMINI_API_KEY no Vercel.' } });
    }

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { maxOutputTokens: 1000, temperature: 0.8 }
        })
      }
    );
    const data = await response.json();
    if (!response.ok) throw new Error(data.error?.message || `Erro ${response.status}`);
    const text = data.candidates[0].content.parts[0].text.trim();
    res.status(200).json({ content: [{ text }] });
  } catch (e) {
    res.status(500).json({ error: { message: e.message } });
  }
}
