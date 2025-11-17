# FastAPI Project Setup

## Prerequisites

- **Python**: `>= 3.10`
- **Framework**: FastAPI
- **Server**: Uvicorn

---

## Setup Instructions

### 1. Create a Virtual Environment

#### Windows
```bash
py -m venv .venv
```

#### Linux / macOS
```bash
python3 -m venv .venv
```

### 2. Activate the Virtual Environment

#### Windows
```bash
.venv\Scripts\activate
```

#### Linux / macOS
```bash
source .venv/bin/activate
```

### 3. Install Dependencies

Ensure you have a `requirements.txt` file with the required packages:

```bash
pip install -r requirements.txt
```

### 4. Run the FastAPI Application

Use Uvicorn to run your FastAPI app. Replace `app.main` with the correct path to your FastAPI instance if needed:

```bash
uvicorn app.main:app --reload
```

---



