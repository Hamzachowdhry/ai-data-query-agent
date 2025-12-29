# 🤖 AI-Powered Retention Query Agent

An AI-driven analytics agent that enables non-technical campaign managers
to explore customer retention data using natural language queries.

## 🎯 Problem
Campaign and retention teams depend heavily on engineering teams for:
- customer segmentation
- campaign audience extraction
- retention metric analysis

This creates bottlenecks and slows down campaign execution.

## 💡 Solution
I designed and deployed an AI-powered query agent that:
- converts natural language questions into SQL
- performs semantic search over customer and campaign data
- returns actionable insights in real time

## 🧠 Architecture
- **LLM**: GPT-4 via LangChain
- **Semantic Search**: Pinecone
- **Backend**: FastAPI
- **UI**: Gradio (no-code, self-serve)
- **Database**: SQL
- **Deployment**: Docker + Cloud Run

## 🚀 Key Features
- Natural language → SQL query generation
- Customer segmentation via AI
- Self-serve analytics for campaign managers
- Exportable user lists
- Retention metric visualization

## 📉 Impact
- Reduced engineering dependency
- Cut campaign turnaround time by **~70%**
- Improved campaign experimentation velocity

## ⚙️ Local Setup
```bash
pip install -r requirements.txt
python api/main.py
python app.py
