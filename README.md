# 🥗 Calorie Tracker

A personal calorie tracking web app that runs locally on your machine. No cloud, no accounts, no nonsense.

## Features

- **Food Inventory** — maintain a list of food items with calories and protein per serving
- **Daily Log** — log meals by selecting items from your inventory with custom serving sizes
- **Calories Burnt** — input daily burn and see your net balance
- **Weekly Stats** — color-coded weekly view (🟢 deficit, 🔴 surplus) with week navigation

## Tech Stack

- **Backend:** Python + FastAPI
- **Database:** SQLite via SQLAlchemy
- **Frontend:** Vanilla HTML/CSS/JS (no build step)
- **Templates:** Jinja2

## Project Structure
calorie-tracker/
├── main.py # FastAPI app and all API routes
├── models.py # SQLAlchemy database models
├── database.py # DB connection and session management
├── templates/
│ └── index.html # Single-page frontend
├── static/ # Static assets (reserved for future use)
└── requirements.txt # Python dependencies


## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/calorie-tracker.git
cd calorie-tracker
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
uvicorn main:app --reload
```

### 5. Open in browser
http://localhost:8000


## Usage

1. Go to the **Inventory** tab and add your commonly eaten food items
2. Each day, go to **Daily Log**, select food items and servings to log your meals
3. Enter your **Calories Burnt** for the day and save
4. Check **Weekly Stats** to review your consumption and deficit/surplus over any week

## Data Storage

All data is stored locally in `calorie_tracker.db` (SQLite) in the project folder. This file is excluded from version control via `.gitignore`.

