// Talks to FastAPI backend at http://localhost:8000
// Falls back to mock response if backend is not reachable.

export async function sendMessage(message: string, history: { role: string; content: string }[] = []): Promise<string> {
  const backendUrl = 'http://127.0.0.1:8000';
  try {
    const res = await fetch(`${backendUrl}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history }),
    });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(err);
    }
    const data = await res.json();
    return data.reply as string;
  } catch (e) {
    console.warn('Backend not reachable, using mock reply:', e);
    // Mock fallback for frontend-only demo (no API_KEY needed to see UI)
    await new Promise(r => setTimeout(r, 800));
    const lower = message.toLowerCase();
    if (lower.includes('fever') && lower.includes('cough')) {
      return `Based on your symptoms (fever, cough), potential conditions could include **Common Cold, Influenza, or Viral Fever**.\n\n⚠️ **Disclaimer:** This is NOT a medical diagnosis. Please consult a qualified healthcare professional for proper evaluation.`;
    }
    if (lower.includes('headache') || lower.includes('सिरदर्द')) {
      return `Headache and fatigue can be associated with many conditions (e.g., dehydration, viral illness, stress-related).\n\n⚠️ **Disclaimer:** This is for informational purposes only. Please consult a doctor if symptoms persist.`;
    }
    return `Thanks for describing: "${message}".\n\nIn a full setup this would call Gemini via the FastAPI backend ( /chat → Gemini ).\n\nPotential next steps: share duration, severity, and associated symptoms.\n\n⚠️ **Disclaimer:** I am not a medical professional. Always consult a qualified doctor for diagnosis or treatment.`;
  }
}
