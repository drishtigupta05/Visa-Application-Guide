from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

SCALE_DOWN_URL = "https://api.scaledown.xyz/compress/raw/"
API_KEY = os.getenv("SCALEDOWN_API_KEY")

FULL_CONTEXT = """US Visa Application Guide:
- Types: Tourist (B-2), Student (F-1), Work (H-1B).
- Steps: Fill DS-160 form online, pay fee, schedule interview at embassy.
- Requirements: Valid passport, photo, proof of ties to home country, financial support.
- Common questions: What is DS-160? It's the online nonimmigrant visa application form.
- Tips: Be honest, prepare documents, practice interview questions."""

compressed_cache = None

def get_compressed():
    global compressed_cache
    if compressed_cache is not None:
        return compressed_cache

    payload = {
        "context": FULL_CONTEXT,
        "prompt": "USA tourist visa questions",
        "scaledown": {"rate": "auto"}
    }
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}

    try:
        r = requests.post(SCALE_DOWN_URL, json=payload, headers=headers, timeout=12)
        r.raise_for_status()
        data = r.json()
        compressed_cache = data.get("compressed_context", FULL_CONTEXT)
        return compressed_cache
    except:
        return FULL_CONTEXT


@app.route("/api/compress_once", methods=["GET"])
def compress_once():
    return jsonify({"compressed": get_compressed()})


@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "").lower().strip()

    compressed = get_compressed()

    # Extremely naive keyword matching (this is the best we can do without LLM)
    keywords = {
        "ds-160": "DS-160 is the online nonimmigrant visa application form.",
        "documents": "Valid passport, recent photo, proof of ties to home country, financial documents.",
        "interview": "Schedule at US embassy/consulate. Be honest, show intent to return home.",
        "tourist": "B-2 visa. Prove strong ties to home country and temporary visit intent.",
        "fee": "Pay visa application fee before interview.",
        "ties": "Proof of job, family, property or other strong connections to home country."
    }

    answer = "I don't have enough information to answer that precisely. Please ask about DS-160, documents, interview, tourist visa, fees or ties to home country."
    for k, v in keywords.items():
        if k in question:
            answer = v + "\n\nCompressed knowledge base excerpt:\n" + compressed[:400] + "..."
            break

    return jsonify({"reply": answer})


if __name__ == "__main__":
    app.run(port=5000, debug=True)