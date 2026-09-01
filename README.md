# ☁️ CloudTalk

### Serverless AI Chatbot Powered by Cloud Computing

CloudTalk is an AI-powered chatbot application built using **Python, Streamlit, Vercel Serverless Functions, Groq AI, and Supabase**.

The application demonstrates how a modern AI chatbot can use **serverless cloud computing** to process user requests while storing conversation history in a cloud database.

---

## 📌 Project Overview

Traditional chatbot applications may require a continuously running backend server.

CloudTalk uses a **serverless architecture**, where the backend runs as a cloud function only when a request is received.

The user interacts with the Streamlit frontend, which sends the conversation to a REST API hosted on Vercel. The serverless backend communicates with Groq AI to generate the response and Supabase to store the conversation history.

---

## 🎯 Objectives

The main objectives of CloudTalk are:

- Build an AI-powered chatbot.
- Demonstrate serverless cloud computing.
- Deploy the backend using Vercel.
- Integrate an external AI service using Groq.
- Store chat history using Supabase.
- Provide persistent conversations.
- Create a simple and user-friendly chatbot interface.

---

## ✨ Features

### 🤖 AI Chatbot

CloudTalk uses Groq AI to generate intelligent responses to user questions.

### ☁️ Serverless Backend

The backend is deployed as a Vercel Serverless Function.

There is no traditional continuously running backend server.

### 🗄️ Persistent Chat History

Conversations are stored in Supabase PostgreSQL.

Messages remain available even after refreshing the application.

### 🔑 Session Management

Each conversation receives a unique session ID and chat ID.

This allows CloudTalk to associate messages with the correct conversation.

### 🔄 Conversation Context

CloudTalk sends the conversation history to the AI model, allowing the chatbot to understand previous messages.

### 🧹 Clear Chat

Users can clear the current conversation and start a new session.

### 🌐 REST API

The frontend communicates with the cloud backend using HTTP REST API requests.

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │      USER            │
                    │                      │
                    │  Sends Chat Message  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   STREAMLIT          │
                    │   FRONTEND           │
                    │                      │
                    │   Python + UI        │
                    └──────────┬───────────┘
                               │
                         REST API Request
                               │
                               ▼
                    ┌──────────────────────┐
                    │      VERCEL          │
                    │                      │
                    │ Serverless Function  │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
          ┌─────────────────┐   ┌─────────────────┐
          │    GROQ AI      │   │    SUPABASE     │
          │                 │   │                 │
          │ Generate AI     │   │ Store Chats &   │
          │ Response        │   │ Messages        │
          └────────┬────────┘   └────────┬────────┘
                   │                     │
                   └──────────┬──────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │    VERCEL API        │
                    │                      │
                    │ Returns AI Response  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    STREAMLIT         │
                    │                      │
                    │ Display Response     │
                    └──────────────────────┘