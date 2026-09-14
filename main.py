"""
FastAPI backend for Disease Predictor WhatsApp Chatbot
- Gemini powered disease prediction (multilingual: English, Hindi, Odia)
- Twilio WhatsApp webhook
- /chat endpoint for frontend
"""
import os
from typing import List, Optional

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Twilio optional
try:
    from twilio.rest import Client as TwilioClient
    from twilio.twiml.messaging_response import MessagingResponse
except Exception as e:
    print(f"[Twilio] Import failed (will run without WhatsApp): {e}")
    TwilioClient = None
    MessagingResponse = None

# Gemini optional
try:
    import google.generativeai as genai
except Exception as e:
    print(f"[Gemini] Import failed (will run with mock replies): {e}")
    genai = None

API_KEY = os.getenv("API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

SYSTEM_PROMPT = """You are a friendly, empathetic Disease Predictor assistant.
You support English, Hindi (हिंदी), and Odia (ଓଡ଼ିଆ). Automatically detect the user's language and respond in the SAME language.

Your task:
- Based on symptoms described, suggest 2-4 POSSIBLE conditions that could match, with brief explanation.
- Ask 1-2 follow-up questions if info is insufficient.
- Keep tone reassuring and helpful.

CRITICAL RULES:
- NEVER provide prescriptions, dosage, treatment plans, or definitive diagnosis.
- NEVER claim certainty. Use phrasing like "could be associated with", "possible conditions include".
- ALWAYS include a disclaimer: "This is for informational purposes only. Please consult a qualified healthcare professional."
- If user asks for prescription/treatment, politely decline and advise to see a doctor.
- If symptoms seem emergency (chest pain, severe bleeding, difficulty breathing, etc.), advise immediate medical attention.
"""

app = FastAPI(title="Disease Predictor Chatbot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
model = None
MODEL_CANDIDATES = [
    "models/gemini-3.8-flash",
    "models/gemini-3.7-flash",
    "models/gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-3.7-flash",
]
if genai and API_KEY:
    try:
        # Strip quotes if present
        clean_key = API_KEY.strip().strip('"').strip("'")
        genai.configure(api_key=clean_key)
        for model_name in MODEL_CANDIDATES:
            try:
                model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
                print(f"[Gemini] Using model: {model_name}")
                break
            except Exception as e:
                print(f"[Gemini] Failed {model_name}: {e}")
                continue
        if model is None:
            # Fallback without system_instruction for older SDKs
            for model_name in MODEL_CANDIDATES:
                try:
                    model = genai.GenerativeModel(model_name)
                    print(f"[Gemini] Using model (no system prompt): {model_name}")
                    break
                except Exception as e:
                    continue
    except Exception as e:
        print(f"[Gemini] Configure failed: {e}")
else:
    if not API_KEY:
        print("[Gemini] No API_KEY set - will use mock responses")
    if not genai:
        print("[Gemini] google-generativeai not installed")

# Twilio client
twilio_client = None
if TwilioClient and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    try:
        twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("[Twilio] Client initialized")
    except Exception as e:
        print(f"[Twilio] Init failed: {e}")
else:
    print("[Twilio] Not configured (set TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN to enable)")


def get_gemini_reply(user_message: str, history: Optional[List[dict]] = None) -> str:
    """Call Gemini or return mock reply if not configured."""
    global model
    if model:
        # Build prompt with history
        prompt = user_message
        if history:
            convo = "\n".join([f"{h.get('role')}: {h.get('content')}" for h in history[-6:]])
            prompt = f"Conversation history:\n{convo}\n\nCurrent user message: {user_message}\n\nRemember: auto-detect language (English/Hindi/Odia) and include disclaimer."
        else:
            prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}"

        # Try current model, on 404 fallback to other candidates
        tried = []
        for attempt_model_name in [None] + MODEL_CANDIDATES:
            try:
                cur_model = model
                if attempt_model_name is not None and attempt_model_name not in tried:
                    tried.append(attempt_model_name)
                    print(f"[Gemini] Fallback trying model: {attempt_model_name}")
                    cur_model = genai.GenerativeModel(attempt_model_name, system_instruction=SYSTEM_PROMPT)
                    model = cur_model  # update global
                response = cur_model.generate_content(prompt)
                text = response.text.strip() if response.text else "Sorry, I couldn't generate a response."
                if "consult" not in text.lower() and "healthcare" not in text.lower():
                    text += "\n\n⚠️ Disclaimer: This is for informational purposes only. Please consult a qualified healthcare professional."
                return text
            except Exception as e:
                err_str = str(e)
                print(f"[Gemini] Error with {attempt_model_name or 'current'}: {err_str}")
                if "404" in err_str and "is not found" in err_str and attempt_model_name is None:
                    continue  # try next candidate
                if "404" in err_str:
                    continue
                # For non-404 errors, break after first retry
                if attempt_model_name is None:
                    continue
                else:
                    return f"Gemini error: {e}. Mock fallback: Based on '{user_message}', possible conditions could include viral illness or common cold. ⚠️ Please consult a doctor. This is not a medical diagnosis."
        # All attempts failed
        return f"Gemini error: all models failed. Mock fallback: Based on '{user_message}', possible conditions could include viral illness or common cold. ⚠️ Please consult a doctor. This is not a medical diagnosis."
    else:
        # Mock logic for demo without API key
        lower = user_message.lower()
        if "fever" in lower and "cough" in lower:
            return "Based on fever + cough, possible conditions include **Common Cold, Influenza, or Viral Fever**. Please share duration and other symptoms.\n\n⚠️ Disclaimer: This is NOT a medical diagnosis. Please consult a qualified healthcare professional."
        if "headache" in lower or "सिरदर्द" in user_message:
            return "Headache & fatigue can be linked to dehydration, viral illness, stress, or lack of sleep. Stay hydrated and rest.\n\n⚠️ Disclaimer: For informational purposes only. See a doctor if it persists."
        if "ପେଟ" in user_message or "pet" in lower and "dard" in lower:
            return "ପେଟ ଦରଜ ଓ ବାନ୍ତି ବିଭିନ୍ନ କାରଣରୁ ହୋଇପାରେ (ଗ୍ୟାଷ୍ଟ୍ରାଇଟିସ୍, ଫୁଡ୍ ପଏଜନିଂ ଇତ୍ୟାଦି)।\n\n⚠️ ବିଜ୍ଞପ୍ତି: ଏହା କେବଳ ସୂଚନା ପାଇଁ। ଦୟାକରି ଡାକ୍ତରଙ୍କ ପରାମର୍ଶ ନିଅନ୍ତୁ।"
        return f"Thanks for sharing: \"{user_message}\"\n\nBased on this, I would need more details to suggest possible conditions. Possible next steps: mention duration, severity, fever, pain location.\n\n⚠️ Disclaimer: This is for informational purposes only. Please consult a qualified healthcare professional. (Mock reply — set GEMINI_API_KEY for real AI response)"


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = None

class ChatResponse(BaseModel):
    reply: str


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Disease Predictor Chatbot",
        "gemini_configured": bool(model),
        "twilio_configured": bool(twilio_client),
        "endpoints": ["/health", "/chat", "/whatsapp", "/docs"]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "gemini": bool(model), "twilio": bool(twilio_client)}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    reply = get_gemini_reply(req.message, req.history)
    return ChatResponse(reply=reply)

# Compatibility alias for frontend that may call /predict
@app.post("/predict", response_model=ChatResponse)
async def predict(req: ChatRequest):
    return await chat(req)

@app.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(default=""),
    From: str = Form(default=""),
    To: str = Form(default=""),
):
    # Twilio sends form-encoded
    # If not provided via Form parsing, try raw body
    if not Body:
        form = await request.form()
        Body = form.get("Body", "") or form.get("body", "")
        From = form.get("From", From)
    print(f"[WhatsApp] From {From}: {Body}")
    reply_text = get_gemini_reply(Body)

    # Try to send via Twilio API if configured, otherwise use TwiML
    if MessagingResponse:
        resp = MessagingResponse()
        resp.message(reply_text)
        return PlainTextResponse(str(resp), media_type="application/xml")
    else:
        # Fallback JSON
        return JSONResponse({"reply": reply_text})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
