# LegacyTree

LegacyTree is a family story preservation platform that helps users record, summarize, and map their life stories. Using AI, LegacyTree transforms conversations and memories into beautifully summarized chapters, illustrated memories, and interactive maps that can be shared across generations.

## Features

- **Record Stories:** Upload audio, images, or type transcripts to capture memories.
- **AI Summarization:** Automatically summarize stories and generate meaningful titles and themes.
- **AI Illustration:** Generate AI-powered illustrations for each story.
- **Memory Map:** Visualize stories on an interactive map based on their locations.
- **Guided Story Chat:** Chat with an AI interviewer to help narrate and record stories.
- **Speech-to-Text & Text-to-Speech:** Convert between speech and text in multiple languages.
- **Database Storage:** All stories are stored securely in a local SQLite database.

## Tech Stack

- **Frontend:** Streamlit ([app.py](app.py))
- **Backend:** FastAPI ([backend/main.py](backend/main.py))
- **Database:** SQLite ([backend/legacytree.db](backend/legacytree.db))
- **AI Models:** HuggingFace Transformers, Stable Diffusion, Whisper, gTTS
- **Geocoding:** geopy


## Project Structure

- `app.py` — Streamlit frontend application
- `backend/` — FastAPI backend and all core services
    - `main.py` — FastAPI app and API endpoints
    - `database.py` — Database setup and session management
    - `models.py` — SQLAlchemy models
    - `schemas.py` — Pydantic schemas
    - `geocoding.py` — Location geocoding service
    - `summarization.py` — AI summarization and theme classification
    - `image_generation.py` — AI illustration generation
    - `speech_service.py` — Speech-to-text and text-to-speech services
    - `requirements.txt` — Backend dependencies
