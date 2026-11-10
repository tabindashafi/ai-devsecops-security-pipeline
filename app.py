
from flask import Flask, request, jsonify
import os
import requests
chatbot_prompt = os.environ.get(
    "CHATBOT_SYSTEM_PROMPT",
    "You are a helpful AI chatbot."
)

from validate import validate_input, detect_injection, scan_output

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:1b"


@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>TechCorp AI Assistant</title>
    </head>
    <body>
        <h1>TechCorp AI Assistant</h1>

        <textarea id="message" placeholder="Ask me anything..."
        style="width:700px;height:150px;font-size:18px;"></textarea>
        <button onclick="sendMessage()">Send</button>

        <h3>AI Response:</h3>
        <pre id="response"></pre>

        <script>
        async function sendMessage() {
            const message = document.getElementById("message").value;

            const result = await fetch("/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({message: message})
            });

            const data = await result.json();

            document.getElementById("response").textContent =
                data.response || data.error;
        }
        </script>
    </body>
    </html>
    """


@app.route("/chat", methods=["POST"])
def chat():

    # Layer 1: Input validation
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")

    valid, validation_message = validate_input(user_message)

    if not valid:
        return jsonify({"error": validation_message}), 400

    # Layer 2: Prompt injection detection
    detected, detection_message = detect_injection(user_message)

    if detected:
        return jsonify({
            "error": "Request blocked by prompt injection defence."
        }), 400

    # Send accepted prompt to Ollama
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": user_message}
                ],
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()
        ai_response = response.json()["message"]["content"]

    except (requests.RequestException, KeyError, ValueError):
        return jsonify({
            "error": "Unable to obtain a response from Ollama."
        }), 502

    # Layer 3: Output scanning
    suspicious, scan_message = scan_output(ai_response)

    if suspicious:
        return jsonify({
            "response": "Response blocked by output security scanner."
        })

    return jsonify({"response": ai_response})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)

