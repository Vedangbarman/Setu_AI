# Setu_AI: Technical Educational Assistant

## Overview
Setu_AI is a multimodal, domain-specific artificial intelligence application designed to assist students and developers with Computer Science concepts, specifically Data Structures and Algorithms (DSA) and Design and Analysis of Algorithms (DAA). 

Built as a high-performance microservice, Setu_AI leverages the Gemini 2.5 Flash API as its reasoning engine. It utilizes a custom Python backend to manage contextual session memory, enforce strict domain guardrails, and natively process documents and images without the latency overhead of traditional Vector Databases or LangChain architectures.

## Key Features
* **Multimodal Data Ingestion:** Natively processes multiple file types simultaneously (PDF, JPG, PNG) using direct byte-extraction into the API payload.
* **Domain-Specific Guardrails:** Engineered with strict system instructions that force the model to reject non-technical queries, ensuring the application remains exclusively focused on Computer Science.
* **Dynamic Localization:** Features a user-toggleable output engine that translates complex technical concepts into formal English, pure Hindi (Devanagari), or a natural Hinglish blend.
* **Contextual Memory Management:** Utilizes Streamlit session state to cache conversation history, allowing for continuous, context-aware follow-up queries.
* **Automated Documentation Export:** Compiles session interactions into formatted Markdown (`.md`) files for easy downloading and offline study.

## System Architecture
Setu_AI bypasses standard Retrieval-Augmented Generation (RAG) pipelines. Instead of chunking documents and storing them in a database, the application leverages the massive context window of the Gemini 2.5 Flash model. 

When a user uploads a document or image, the Python backend reads the raw bytes, maps the appropriate MIME type, and dynamically injects the binary data directly into the API payload alongside the user's prompt and the conversation history. This "Context Stuffing" methodology drastically reduces response latency and completely eliminates local computational bottlenecks.

## Technology Stack
* **Language:** Python 3.x
* **Frontend/State Management:** Streamlit
* **AI/LLM Integration:** Google GenAI SDK (`google-genai`)
* **Environment Management:** `python-dotenv`

## Installation and Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/Setu_AI.git](https://github.com/yourusername/Setu_AI.git)
   cd Setu_AI
