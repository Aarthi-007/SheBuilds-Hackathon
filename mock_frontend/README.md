# Klyros - Standalone Mock Frontend (Test Bench)

This directory (`mock_frontend/`) contains a **100% self-contained, isolated Mock Frontend Test Bench** built exclusively to test asset ingestion, Groq AI multimodal processing, 6-pillar content validation, and market trend intelligence.

---

## 🚀 How to Use

### Method 1: Via FastAPI Backend Server
Start the backend server:
```bash
cd d:\REC\backend
python app\main.py
```
Open your browser and navigate to:
👉 **`http://localhost:8000/mock/`**

---

### Method 2: Standalone Browser Launch
Simply double-click `d:\REC\mock_frontend\index.html` in your file explorer to open it in Chrome / Edge / Firefox!

---

## 🗑️ How to Delete when integrating Production Frontend

Because all test bench files are isolated exclusively inside the `mock_frontend/` folder:

1. **Delete the directory:**
   ```bash
   rm -rf mock_frontend
   ```
2. **Remove the optional static mount line in `backend/app/main.py`** (if added):
   ```python
   # App mount for mock_frontend
   ```

No backend models, database collections, or API routes will be affected!
