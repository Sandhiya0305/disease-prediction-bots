# Disease Predictor WhatsApp Chatbot

This is a backend-only FastAPI application that leverages the Google Gemini API to provide a multilingual (English, Hindi, Odia) disease prediction chatbot via WhatsApp, integrated with Twilio. The chatbot is designed to be friendly and helpful, focusing solely on predicting potential diseases based on user-provided symptoms, without offering any medical advice, prescriptions, or treatment plans.

## ✨ Features

*   **Multilingual Support:** Automatically detects and responds in English, Hindi, and Odia.
*   **Disease Prediction:** Utilizes the advanced reasoning capabilities of Google Gemini (`gemini-3-pro-preview`) to predict potential diseases based on symptoms.
*   **Friendly Conversation:** Designed to maintain an empathetic and reassuring tone with users.
*   **Strict Medical Disclaimer:** Explicitly trained to **NEVER** provide medical advice, prescriptions, diagnoses, or recommend treatments. Always advises users to consult a qualified healthcare professional.
*   **Twilio WhatsApp Integration:** Seamlessly connects with WhatsApp users through a Twilio phone number.
*   **Temporary Ngrok Deployment:** Instructions for quick local testing and temporary public exposure via Ngrok.

## ⚠️ Important Disclaimer

This chatbot is for **informational purposes only** and should **NOT** be used as a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified healthcare professional for any medical conditions or health concerns. The predictions made by this AI are not definitive diagnoses.

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.8+**
*   **pip** (Python package installer)
*   **Ngrok:** A tool to expose your local server to the internet. Download from [ngrok.com](https://ngrok.com/download).

### 1. Project Setup

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository-url>
    cd disease-predictor-chatbot
    ```
    *(Note: If you're downloading as a zip, just extract the contents.)*

2.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 2. Configure Environment Variables

Create a file named `.env` in the root directory of your project (same level as `main.py`). Copy the contents from `.env.sample` and fill in your credentials:

```ini
# .env file content (copy from .env.sample)

# Google Gemini API Key
# Get your API key from https://ai.google.dev/
API_KEY="YOUR_GEMINI_API_KEY"

# Twilio Account SID and Auth Token
# Find these in your Twilio console: https://www.twilio.com/console
TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN="your_twilio_auth_token_here"

# Your Twilio WhatsApp-enabled phone number
# Format: whatsapp:+1234567890
TWILIO_WHATSAPP_NUMBER="whatsapp:+14155238886" # Example, use your actual Twilio WhatsApp number
```

*   **`API_KEY`**: Obtain your Google Gemini API key from the Google AI Studio (ai.google.dev).
*   **`TWILIO_ACCOUNT_SID`** and **`TWILIO_AUTH_TOKEN`**: Find these on your Twilio Console Dashboard.
*   **`TWILIO_WHATSAPP_NUMBER`**: This is your Twilio number, formatted as `whatsapp:+1XXXXXXXXXX`. You need a Twilio number enabled for WhatsApp.

### 3. Run the FastAPI Backend

Open your terminal or command prompt and navigate to your project directory.

```bash
uvicorn main:app --reload
```

This will start the FastAPI server locally, usually on `http://127.0.0.1:8000`. Keep this terminal window open.

### 4. Expose with Ngrok (Temporary Deployment)

In a **new terminal window**, run Ngrok to create a public URL for your local FastAPI server:

```bash
ngrok http 8000
```

Ngrok will provide you with a forwarding URL (e.g., `https://your-random-subdomain.ngrok-free.app`). Copy the `https` URL.

### 5. Configure Twilio Webhook

1.  Go to your [Twilio Console](https://www.twilio.com/console).
2.  Navigate to **Phone Numbers** -> **Manage** -> **Active Numbers**.
3.  Select your WhatsApp-enabled Twilio phone number.
4.  Scroll down to the **Messaging** section.
5.  Under **A MESSAGE COMES IN**, set the webhook URL to your Ngrok `https` forwarding URL followed by `/whatsapp`.

    Example: `https://your-random-subdomain.ngrok-free.app/whatsapp`

6.  Ensure the method is set to **HTTP POST**.
7.  Click **Save**.

### 6. Usage

You can now send a WhatsApp message to your Twilio WhatsApp number. The chatbot will receive your message, process it with the Gemini API, and send a response back to your WhatsApp.

**Example Prompts:**

*   "I have a fever, cough, and body aches."
*   "मुझे सिरदर्द और थकान महसूस हो रही है।" (I am feeling headache and fatigue.)
*   "ମୋତେ ପେଟ ଦରଜ ଓ ବାନ୍ତି ଲାଗୁଛି।" (I am feeling stomach ache and nausea.)

Remember, the bot will always provide a disclaimer about consulting a doctor.

## 🧹 Cleaning Up (for Ngrok)

When you're done, simply close the Ngrok terminal window to stop exposing your local server. You'll also want to revert your Twilio webhook URL if you're not planning to keep the Ngrok tunnel active.

## License

This project is open-sourced under the MIT License. See the LICENSE file for details.
