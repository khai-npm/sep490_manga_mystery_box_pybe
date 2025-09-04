# 🚀 Manga Mystery Box - Backend (Python WebSocket Service)

Real-time data service communication portal  

- **SWAGGER UI**  
[![Render Version](https://img.shields.io/badge/Render-Live-blue)](https://sep490-manga-mystery-box-pybe.onrender.com/)  
[![API Dev](https://img.shields.io/badge/API-mmb.io.vn-green)](https://api.mmb.io.vn/) *(only avaible at development stage)*

---

## 📦 Installation

Clone project:

```bash
git clone https://github.com/khai-npm/sep490_manga_mystery_box_pybe.git
cd sep490_manga_mystery_box_pybestage
```

🔹 Option 1: Install and Run with Docker

Build the image from Dockerfile:
```bash
docker build -t mmb-backend .
docker run -d -p 8000:8000 --name mmb-backend mmb-backend
```

🔹 Option 2: Install and Run with Python

Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```
- install dependencies
```bash
pip install -r requirements.txt
```
-run project
```bash
python run.py
```


The service will be available at: http://localhost:8000
🛠️ Technologies Used

    Python 3.x

    WebSocket

    FastAPI (Swagger UI)

    Docker
