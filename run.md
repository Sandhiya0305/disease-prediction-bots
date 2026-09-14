# Run – Disease Predictor Chatbot

## 1. Setup (once)
```powershell
Copy-Item .env.sample .env   # edit .env with your keys
pip install -r requirements.txt
npm install
```

If on Python 3.14:
```powershell
pip install "protobuf==5.28.3"
```

For ngrok (one-time, if using WhatsApp on phone):
```powershell
$env:NGROK_AUTHTOKEN="YOUR_TOKEN_HERE"
# or persist: [Environment]::SetEnvironmentVariable("NGROK_AUTHTOKEN","YOUR_TOKEN_HERE","User")
```

## 2. Backend – Terminal 1
```powershell
uvicorn main:app --reload
# open http://127.0.0.1:8000/docs
```

## 3. Frontend – Terminal 2
```powershell
npm run dev
# open http://localhost:3000
```

## 4. ngrok – Terminal 3 (only for phone/WhatsApp)
```powershell
ngrok http 8000
# copy https://xxxx.ngrok-free.app -> Twilio webhook: https://xxxx.ngrok-free.app/whatsapp
```
Twilio Console → Messaging → WhatsApp Sandbox → When a message comes in = `https://xxxx.ngrok-free.app/whatsapp` (POST) → join sandbox `join <code>` to `+1 4155238886` on your phone → chat.
