# Boardgame Tool 🎲

## Overview

BoardGameTool is a full-stack web application for creating and managing board game matches.
(currently supporting **Kingdom Builder**).

The application allows authenticated users to:
- Create new matches
- Assign players
- Enter task-based scores
- Automatically calculate total results
- Persist match data in a database for statistics

This project demonstrates backend architecture, authentication, database modeling, and frontend-backend integration.

---

## 📦 Tech Stack

### Backend
- Python 3.10+
- FastAPI
- SQLAlchemy
- PostgreSQL (recommended) or SQLite
- JWT Authentication

### Frontend
- Plain HTML / CSS / JavaScript
- No external JS frameworks
- REST API communication via Fetch

### Authentication

This application uses **JWT (JSON Web Tokens)** for authentication.

## Database
- **Database:** SQLite (default)  
  *(can be replaced with PostgreSQL or MySQL)*
- **ORM:** SQLAlchemy
- **Migrations:** Not implemented (tables are created via models)---

## ✅ Requirements

Make sure the following software is installed:

- **Python ≥ 3.10**
- **pip**
- **Git**
- Optional: **PostgreSQL**

Check versions:
```bash
python --version
pip --version


🎮 Match Creation Flow (Kingdom Builder Example)

1. Select number of players
2. Choose players using autocomplete
3. Start match
4. Map and tasks are generated automatically
5. Enter task scores
6. Total score updates live
7. Save results