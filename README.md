<h1>🧠 EchoPilot – The Voice Assistant That Actually Listens</h1>

<p>
Meet <b>EchoPilot</b> — a real-time voice assistant that <i>actually listens while it talks</i>!  
Built using <b>Deepgram STT/TTS</b> and <b>Groq LLaMA 3.1</b>, it brings a near-human conversation experience with live interruption (barge-in), contextual memory, and intelligent response grounding.
</p>

<h2>✨ Features</h2>
<ul>
  <li>🎙️ <b>Live Speech Recognition</b> – Powered by Deepgram’s real-time STT API.</li>
  <li>🗣️ <b>Natural Voice Output</b> – Converts LLM responses to speech using Deepgram TTS.</li>
  <li>💬 <b>Barge-In Support</b> – Interrupt the assistant mid-sentence, and it instantly listens again!</li>
  <li>🧠 <b>Conversational Memory</b> – Stores recent context from <code>conversation_log.txt</code> for more natural replies.</li>
  <li>🌐 <b>Context-Aware Responses</b> – Uses live web-fetched context for accurate, grounded answers.</li>
  <li>⚡ <b>Multi-threaded Audio Handling</b> – Smooth, latency-free performance during real-time speech.</li>
</ul>

<h2>🧩 Tech Stack</h2>
<p>
Python • Deepgram API • Groq LLaMA 3.1 • WebSocket • pyaudio • sounddevice • BeautifulSoup • dotenv
</p>

<h2>📂 Repository Structure</h2>
<pre>
├── task_llm.py           # Main script: Handles LLM queries, STT, TTS, and interruptions
├── requirements.txt      # Dependencies for setup
├── conversation_log.txt  # Memory file storing past dialogue
├── .gitignore            # Standard Git ignore rules
</pre>

<h2>🚀 Getting Started</h2>

<h3>1️⃣ Clone the Repository</h3>
<pre>
git clone https://github.com/Niklaus2003/EchoPilot-The-Voice-Assistant-That-Actually-Listens.git
cd EchoPilot-The-Voice-Assistant-That-Actually-Listens
</pre>

<h3>2️⃣ Install Requirements</h3>
<pre>
pip install -r requirements.txt
</pre>

<h3>3️⃣ Set Environment Variables</h3>
<p>Create a <code>.env</code> file in the root directory:</p>
<pre>
DEEPGRAM_API_KEY=your_deepgram_api_key
GROQ_API_KEY=your_groq_api_key
</pre>

<h3>4️⃣ Run the Assistant</h3>
<pre>
python task_llm.py
</pre>

<h2>💡 How It Works</h2>
<ol>
  <li>EchoPilot listens continuously using Deepgram’s real-time STT API.</li>
  <li>Transcribed speech is processed by Groq’s LLaMA 3.1 for intelligent reasoning.</li>
  <li>Responses are converted to natural speech using Deepgram TTS.</li>
  <li>If you interrupt by speaking during playback, it instantly stops and starts listening again!</li>
</ol>

<h2>🔮 Future Enhancements</h2>
<ul>
  <li>🌍 Multilingual support for global interactions</li>
  <li>🎧 Improved emotion-aware voice synthesis</li>
  <li>🧩 Integration with a 3D avatar for expressive conversations</li>
  <li>💾 Persistent conversation memory via database</li>
  <li>🖥️ Web-based interface for easy interaction</li>
</ul>

<h2>📜 License</h2>
<p>MIT License – Open for exploration, learning, and contribution.</p>
