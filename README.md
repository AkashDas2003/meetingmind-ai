# 🎙️ MeetingMind AI

> **Transcribe. Summarise. Chat. Export.** — Your intelligent meeting assistant powered by local & cloud AI.

---

## 🚀 What This Tool Does

MeetingMind AI takes any meeting recording and turns it into structured, actionable intelligence — in English, Hindi, or Hinglish.

| Feature | Description |
|--------|-------------|
| 🎬 **Flexible Input** | Accepts any YouTube URL or local audio/video file |
| 🇬🇧 **English Transcription** | Powered by OpenAI Whisper running fully locally (free) |
| 🇮🇳 **Hindi & Hinglish Transcription** | Powered by Sarvam AI for accurate Indic language support |
| 📋 **Meeting Summary** | Full meeting summarised in clean bullet points |
| ✅ **Action Items** | Extracted with owner and deadline for each item |
| 🧠 **Key Decisions** | All important decisions made during the meeting |
| ❓ **Open Questions** | Follow-ups and unresolved questions captured automatically |
| 💬 **Chat with Meeting** | Ask anything about your meeting using RAG + ChromaDB |
| 📄 **Export Report** | Download the full analysis as PDF or TXT |

---

## 🛠️ Tech Stack

```
MeetingMind AI
├── 🐍 Python                        → Backend & AI pipeline
├── 🎤 OpenAI Whisper (local)        → English transcription (free, offline)
├── 🌐 Sarvam AI                     → Hindi & Hinglish transcription
├── 🔗 LangChain LCEL                → Modern AI pipeline orchestration
├── 🤖 Mistral AI (free API)         → Summarisation & extraction LLM
├── 🗄️ ChromaDB                      → Vector database for RAG
├── 🤗 HuggingFace Embeddings (local)→ Embedding generation (free, offline)
└── ⚛️  React.js                      → Frontend UI
```

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- [Sarvam AI API Key](https://sarvam.ai)
- [Mistral AI API Key](https://mistral.ai)
- `ffmpeg` installed on your system

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/meetingmind-ai.git
cd meetingmind-ai
```

### 2. Set Up Python Backend
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory:
```env
SARVAM_API_KEY=your_sarvam_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
```

### 4. Set Up React Frontend
```bash
cd frontend
npm install
npm run dev
```

### 5. Start the Backend Server
```bash
python app.py
```

---

## 🧑‍💻 Usage

### Option A — YouTube URL
1. Paste any YouTube meeting/call URL into the input field
2. Select language: **English**, **Hindi**, or **Hinglish**
3. Click **Analyse Meeting**

### Option B — Upload File
1. Upload any `.mp3`, `.mp4`, `.wav`, `.m4a`, or `.webm` file
2. Select language
3. Click **Analyse Meeting**

### Chat with Your Meeting
Once transcribed, use the **Chat** tab to ask questions like:
- *"Who is responsible for the marketing report?"*
- *"What was decided about the product launch date?"*
- *"List all deadlines mentioned in the meeting."*

### Export
Click **Export** to download your full meeting report as **PDF** or **TXT**.

---

## 🗂️ Project Structure

```
meetingmind-ai/
├── app.py                  # FastAPI/Flask backend entry point
├── transcriber/
│   ├── whisper_engine.py   # English transcription via Whisper
│   └── sarvam_engine.py    # Hindi/Hinglish via Sarvam AI
├── analyser/
│   ├── summariser.py       # Bullet-point meeting summary
│   ├── action_items.py     # Action item extraction
│   ├── decisions.py        # Key decisions extraction
│   └── questions.py        # Open questions extraction
├── rag/
│   ├── embedder.py         # HuggingFace embeddings
│   ├── vectorstore.py      # ChromaDB setup & queries
│   └── chat.py             # RAG chat pipeline (LangChain LCEL)
├── exporter/
│   ├── pdf_export.py       # PDF report generation
│   └── txt_export.py       # TXT report generation
├── frontend/               # React.js UI
│   ├── src/
│   └── public/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🌐 Supported Languages

| Language | Engine | Cost |
|----------|--------|------|
| English | OpenAI Whisper (local) | Free |
| Hindi | Sarvam AI | API (free tier available) |
| Hinglish | Sarvam AI | API (free tier available) |

---

## 💡 Key Design Decisions

- **Whisper runs locally** — no data sent to OpenAI, fully private for English meetings.
- **HuggingFace embeddings run locally** — no cost for vector generation.
- **ChromaDB is local** — your meeting data never leaves your machine.
- **Mistral free API** — powerful LLM without OpenAI pricing.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper)
- [Sarvam AI](https://sarvam.ai)
- [LangChain](https://langchain.com)
- [Mistral AI](https://mistral.ai)
- [ChromaDB](https://trychroma.com)
- [HuggingFace](https://huggingface.co)

---

Built with ❤️ for productive teams everywhere.