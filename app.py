"""
GeoHazardMate AI - Flask backend
A domain-restricted chatbot powered by the Gemini API.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types

from chatbot_config import BOT_NAME, SYSTEM_PROMPT

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite"

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Add it to your .env file before starting the app."
    )

client = genai.Client(api_key=GEMINI_API_KEY)


@app.route("/")
def home():
    """Render the chat UI."""
    return render_template("index.html", bot_name=BOT_NAME)


@app.route("/chat", methods=["POST"])
def chat():
    """Receive a user message and return the model's reply."""
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a message before sending."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )
        reply_text = response.text.strip() if response and response.text else (
            "Sorry, I couldn't generate a response. Please try again."
        )
    except Exception as exc:  # noqa: BLE001
        reply_text = f"Something went wrong while contacting the AI service: {exc}"

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True)
