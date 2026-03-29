# 🏢 Seatify: AI-Powered Smart Library Occupancy System

Seatify is an end-to-end computer vision solution designed to optimize library seat management. Using **YOLOv8** for real-time chair detection and a modern **React** dashboard, it provides library users and staff with instantaneous occupancy analytics, reservation capabilities, and utility monitoring (Power Sockets).

## 🚀 Key Features

*   **Real-time AI Detection**: YOLOv8-powered monitoring with temporal smoothing for stable results.
*   **Intelligent Reservation**: Marks seats as "Reserved" if textbooks, laptops, or bottles are detected.
*   **Interactive Floor Maps**: Subject-wise mapping for Anna Centenary Library (Levels 1-8).
*   **Staff Mode**: Secure authentication (`admin`) to manually override and reserve seats.
*   **Historical Analytics**: SQLite-backed tracking for Peak/Quiet hours and Heatmaps.
*   **Utility Tracking**: Real-time power socket availability monitoring.

---

## 🛠️ Project Structure

```bash
/seatify
├── .gitignore              # Global git exclusions
├── smart-library-seats     # Python Backend & AI Engine
│   ├── cam1/               # YOLO inference scripts & weights
│   ├── server/             # Flask API & SQLite (seatify.db)
│   └── requirements.txt    # Python dependencies
└── seatify-dashboard       # React Frontend
    ├── src/                # Dashboard components
    └── package.json        # Frontend dependencies
```

---

## 🔧 Setup & Installation

### 1. Backend (AI & API)
```powershell
cd smart-library-seats
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python server/app.py
```

### 2. AI Inference Engine (Camera 1)
```powershell
# In a new terminal
cd smart-library-seats
.\venv\Scripts\activate
python cam1\run_inference.py
```

### 3. Frontend Dashboard
```powershell
# In a new terminal
cd seatify-dashboard
npm install
npm start
```

---

## 📊 Tech Stack
*   **Inference**: YOLOv8, OpenCV, Ultralytics
*   **Backend**: Flask (Python), SQLite
*   **Frontend**: React.js, Lucide Icons, Vanilla CSS (Glassmorphism)
*   **Communication**: REST API (Cors-enabled)

---

## 📝 Credentials (Staff Mode)
*   **Username**: `admin`
*   **Password**: `admin123`
