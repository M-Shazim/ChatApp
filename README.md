# ChatApp 🗨️

Welcome to **ChatApp** — a real-time messaging application built with Django and Django Channels, enabling both private and group chats seamlessly.

---

## 🖥️ Project Overview

ChatApp focuses on:

- Real-time communication between users
- Group chat rooms and private messaging
- Smooth, responsive web interface
- WebSocket-based updates without needing page reloads

The app includes:

- Live updating of messages
- Separate handling for group and private messages
- Basic user authentication and session handling

---

## 🚀 Tech Stack

- **Backend:** Django, Django Channels
- **Frontend:** HTML, CSS (basic styling)
- **Real-time Layer:** WebSockets via Django Channels
- **Database:** SQLite 

---

## ⚙️ Features

- Real-time group messaging
- Real-time private messaging
- Django Authentication for user management
- WebSocket support for instant updates
- Scalable architecture for future extensions

---

## 📂 Project Structure

```plaintext
chatapp/
  ├── chat/                 # Chat app (models, views, consumers)
  ├── users/                # User management (optional)
  ├── templates/
  │    └── chat/            # HTML templates for chat interfaces
  ├── static/               # Static files (CSS, JavaScript)
  ├── settings.py
  ├── urls.py
  ├── asgi.py               # ASGI application for WebSockets
  └── manage.py
README.md





