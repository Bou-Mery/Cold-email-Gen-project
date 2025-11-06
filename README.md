# 💌 AI Cold Email Generator: LLM-Powered Personalized Job Outreach 🚀

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/49217022-c0f9-46be-8696-d62cff766f43" />


[![Version](https://img.shields.io/badge/version-3.0-blue.svg)](https://github.com/yourusername/cold-email-generator)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.0-orange.svg)](https://langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red.svg)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4.0-purple.svg)](https://www.trychroma.com/)

**AI Cold Email Generator** is an open-source, intelligent platform that automates **personalized cold email generation** by combining **web scraping**, **large language models (LLMs)**, **semantic portfolio matching**, and **AI-powered job discovery**.

💡 It reduces the email crafting time from *10–15 minutes* to *under 10 seconds*, while keeping the message **authentic and context-aware**.

---

## 📑 Table of Contents
- [🧠 Architecture Overview](#-architecture-overview)
- [🖥️ Application Modules](#️-application-modules)
- [⚙️ Technology Stack](#️-technology-stack)
- [🚀 Getting Started](#-getting-started)
- [🎯 Usage Guide](#-usage-guide)
- [🚀 Deployment](#-deployment)
- [🎥 Demo Video](#-demo-video)
- [🙌 Contributors](#-contributors)
- [📄 License](#-license)

---

## 🧠 Architecture Overview

<img width="2161" height="1562" alt="Image" src="https://github.com/user-attachments/assets/a1a65d5a-f733-43b6-b5df-f51de96fab7a" />
The system follows a modular AI-driven architecture:

- **Frontend:** Streamlit UI for interactive user experience.  
- **LLM Engine:** LangChain orchestration with Groq API (Llama 3.1).  
- **Vector Database:** ChromaDB for semantic portfolio–job matching.  
- **Web Scraper:** BeautifulSoup with retry and cleaning logic.  
- **Follow-up Generator:** Automated 3-step email campaign sequencer.

**Project Structure**
```
Cold-Email-Generator/
├── app/
│   ├── main.py             # Streamlit interface
│   ├── chains.py           # LangChain orchestration
│   ├── portfolio.py        # ChromaDB vector operations
│   ├── utils.py            # Web scraping & cleaning
│   └── rsrc/
│       └── links_portfolio.csv
├── vector_db/              # Persistent embeddings
├── tests/
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## 🖥️ Application Modules

### 🧭 Smart Job Discovery
- AI-powered job search across multiple job boards.
- Relevance scoring, deduplication, and semantic filtering.

### 🧠 Company Intelligence
- NLP-based analysis of company culture, values, and tech stack.

### 💬 Email Strategies
- Generates 3 email variants:
  - **Value-based** – Focus on impact  
  - **Solution-oriented** – Addresses company pain points  
  - **Storytelling** – Humanized, narrative approach  

### 📈 Success Prediction
- Each email is scored (0–100) with metrics:
  - Relevance  
  - Clarity  
  - Personalization  
  - Call-to-Action Strength

### 🔁 Automated Follow-ups
- Generates 3 follow-up emails (Day 3, 7, and 14) with progressive tone.

---

## ⚙️ Technology Stack

| Component | Technology |
|------------|-------------|
| **Frontend** | Streamlit |
| **AI Engine** | LangChain + Groq (Llama 3.1) |
| **Vector Database** | ChromaDB |
| **Web Scraping** | BeautifulSoup |
| **Deployment** | Streamlit Cloud |


---

## 🚀 Getting Started

### 🔧 Prerequisites
- Python 3.10+
- [Groq API Key](https://console.groq.com)
- 4GB RAM and stable internet connection

### 🧩 Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Bou-Mery/Cold-email-Gen-project.git
   cd Cold-email-Gen-project
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env`:
   ```env
   GROQ_API_KEY=gsk_your_key_here
   ```

5. **Add your portfolio**
   Edit `app/rsrc/links_portfolio.csv`:
   ```csv
   TechStack,Portfolio_Link
   "Python, FastAPI, PostgreSQL, Docker",https://github.com/you/api-project
   "React, TypeScript, Next.js",https://github.com/you/dashboard
   ```

6. **Run the application**
   ```bash
   streamlit run app/main.py
   ```

7. Open in browser: [http://localhost:8501](http://localhost:8501)

---

## 🎯 Usage Guide

### **Mode 1: Smart Discovery (Recommended)**
1. Enter your skills and location.  
2. View ranked job listings with match percentage.  
3. Select jobs and generate campaigns.  
4. Get full email sequences and performance analytics.

### **Mode 2: Direct URL Mode**
- Paste any job URL and instantly get:
  - 3 personalized email strategies  
  - Company research summary  
  - Success prediction & follow-up plan

---
## 🚀 Deployment

The application is deployed on **Streamlit Community Cloud**, providing free hosting with seamless GitHub integration.  
The deployment connects the GitHub repository to Streamlit Cloud, configures the **Groq API key** through the secure secrets management interface, and deploys the app with a single click.  
The platform automatically handles **containerization**, **HTTPS certificates**, and **persistent storage** for **ChromaDB embeddings**.

A live demo is available here 👉 [https://cold-email-gen3.streamlit.app](https://cold-email-gen3.streamlit.app)


## 🎥 Demo Video

🎬 **Watch the complete workflow:**
## 🎬 Demo Video

[Watch the demo video](./demofinal%20(1).mp4)



---

## 🙌 Contributors

- **Meryem Boukhrais** ([GitHub](https://github.com/Bou-Mery))  
- **Mohamed Hanine**  


---

## 📄 License

[MIT License](LICENSE)


---
