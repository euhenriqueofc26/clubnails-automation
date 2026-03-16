export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();
  try {
    const prompt = req.body.prompt;
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${process.env.GEMINI_API_KEY}`,
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
    res.status(200).json({ text });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
}
