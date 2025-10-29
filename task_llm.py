import os
import time
import json
import threading
from datetime import datetime
import requests
import websocket
import pyaudio
import sounddevice as sd
import soundfile as sf
import tempfile
from bs4 import BeautifulSoup
from deepgram import DeepgramClient, SpeakOptions
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VOICE_MODEL = "aura-asteria-en"

if not DEEPGRAM_API_KEY or not GROQ_API_KEY:
    raise ValueError("API keys for Deepgram and Groq must be set in the .env file.")

# --- Trigger Words ---
TRIGGER_WORD = "alexa"
EXIT_TRIGGER_WORDS = ["exit", "goodbye", "stop"]
TRANSCRIPT_RESULT = {"text": ""}
MAX_TTS_LENGTH = 2000
LOG_FILE = "conversation_log.txt"
MEMORY_LINES = 6

# --- Fetch Context ---
def fetch_deepgram_privacy_text():
    url = "https://developers.deepgram.com/trust-security/data-privacy-compliance"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    lines = [line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()]
    return "\n".join(lines)

# --- Timestamped Logging ---
def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def log_message(speaker, message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp()} {speaker}: {message}\n")

def get_recent_memory():
    if not os.path.exists(LOG_FILE):
        return ""
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[-MEMORY_LINES:])

# --- WebSocket Events for STT ---
def on_message(ws, message):
    data = json.loads(message)
    if "channel" in data:
        alt = data["channel"]["alternatives"]
        if alt and alt[0]["transcript"]:
            TRANSCRIPT_RESULT["text"] = alt[0]["transcript"]
            time.sleep(0.5)
            ws.close()

def on_error(ws, error):
    print("WebSocket Error:", error)

def on_close(ws, *_):
    print("🎤 Done Listening.")

def record_and_send(ws):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    try:
        while ws.keep_running:
            data = stream.read(CHUNK, exception_on_overflow=False)
            ws.send(data, opcode=websocket.ABNF.OPCODE_BINARY)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def transcribe():
    TRANSCRIPT_RESULT["text"] = ""
    url = (
        "wss://api.deepgram.com/v1/listen?language=en&punctuate=true&interim_results=false"
        "&encoding=linear16&sample_rate=16000&channels=1"
    )
    ws = websocket.WebSocketApp(
        url,
        header=[f"Authorization: Token {DEEPGRAM_API_KEY}"],
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.start()
    while not ws.sock or not ws.sock.connected:
        time.sleep(0.1)
    record_and_send(ws)
    ws_thread.join()
    return TRANSCRIPT_RESULT["text"].strip().lower()

# --- Ask LLM (Groq) ---
def ask_llm(user_query, context):
    print("🌐 Asking LLM...")
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    memory = get_recent_memory()
    prompt = f"""You are a helpful assistant answering questions strictly based on the context below.
If the answer cannot be found in the context, respond: "I couldn't find that information."

Context:
{context}

Recent conversation:
{memory}

User question: {user_query}
"""
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        print("LLM Error:", response.text)
        return None

# --- TTS with Interrupt ---
def speak_text_with_trigger(text):
    if len(text) > MAX_TTS_LENGTH:
        text = text[:MAX_TTS_LENGTH]
    try:
        deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)
        options = SpeakOptions(model=VOICE_MODEL)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            filename = tmp_file.name

        deepgram.speak.v("1").save(filename, {"text": text}, options)
        data, samplerate = sf.read(filename)
        stop_event = threading.Event()

        def play():
            sd.play(data, samplerate=samplerate)
            while sd.get_stream().active:
                if stop_event.is_set():
                    sd.stop()
                    break
                time.sleep(0.1)
            os.remove(filename)

        def interrupt_listener():
            while not stop_event.is_set():
                phrase = transcribe()
                if TRIGGER_WORD in phrase:
                    print(f"🛑 Trigger word '{TRIGGER_WORD}' detected.")
                    stop_event.set()

        t1 = threading.Thread(target=play)
        t2 = threading.Thread(target=interrupt_listener)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        return stop_event.is_set()
    except Exception as e:
        print("TTS Error:", e)
        return False

# --- Main Chat Loop ---
def main():
    context_text = fetch_deepgram_privacy_text()
    print("💬 Ask me about Deepgram's privacy & data policy.")
    while True:
        print("\n🎤 Listening...")
        user_input = transcribe()
        if not user_input:
            continue
        print("🧍 You:", user_input)
        log_message("user", user_input)
        if any(word in user_input for word in EXIT_TRIGGER_WORDS):
            speak_text_with_trigger("Goodbye!")
            break
        reply = ask_llm(user_input, context_text)
        if reply:
            print("🤖 Assistant:", reply)
            log_message("assistant", reply)
            interrupted = speak_text_with_trigger(reply)
            if interrupted:
                print("🔁 Restarting conversation...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Exiting...")
