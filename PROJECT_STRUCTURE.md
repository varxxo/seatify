# Seatify Project Structure

```
seatify/
│
├── system_design_report.md.resolved      # System design documentation
│
├── seatify-dashboard/                    # React frontend dashboard
│   ├── package.json                      # npm dependencies
│   ├── README.md                         # Dashboard documentation
│   │
│   ├── public/                           # Static assets
│   │   ├── index.html
│   │   ├── library_zone.jpg
│   │   ├── manifest.json
│   │   └── robots.txt
│   │
│   └── src/                              # React source code
│       ├── App.css                       # Main app styles
│       ├── App.js                        # Main app component
│       ├── App.test.js                   # App tests
│       ├── index.css                     # Global styles
│       ├── index.js                      # Entry point
│       ├── logo.svg
│       ├── reportWebVitals.js
│       └── setupTests.js
│
└── smart-library-seats/                  # Backend ML/inference system
    ├── BRANCHING.md                      # Git branching strategy
    ├── CONTRIBUTING.md                   # Contribution guidelines
    ├── README.md                         # Main documentation
    ├── seat_logs.csv                     # Seat activity logs
    ├── yolov8n.pt                        # YOLOv8 nano model weights
    │
    ├── cam1/                             # Camera 1 inference modules
    │   ├── config.yaml                   # Camera configuration
    │   ├── run_inference.py              # Inference runner script
    │   ├── seats_cam1.json               # Seat mapping for cam1
    │   └── video_inference.py            # Video processing inference
    │
    ├── docs/                             # Documentation (empty)
    │
    ├── models/                           # ML models storage (empty)
    │
    ├── seatify/                          # Package modules
    │   └── smart-library-seats/
    │       └── tools/                    # Utility modules
    │
    ├── server/                           # Backend Flask server
    │   ├── app.py                        # Flask application
    │   ├── seat_logs.csv                 # Server-side logs
    │   └── storage.json                  # Data storage
    │
    ├── tools/                            # Utility scripts
    │   ├── camera_reference.jpg          # Reference image
    │   ├── draw_seat_map.py              # Seat mapping visualization
    │   ├── extract_frame.py              # Frame extraction tool
    │   ├── library_video.mp4             # Sample/reference video
    │   ├── library_zone.jpg              # Library zone reference
    │   └── output_preview.jpg            # Sample output
    │
    └── web/                              # Web resources (empty)
```

## Project Overview

### Frontend (seatify-dashboard/)
- **Type**: React JavaScript application
- **Purpose**: Dashboard UI for displaying seat occupancy information
- **Key Files**: 
  - `src/App.js` - Main React component
  - `public/index.html` - HTML entry point

### Backend (smart-library-seats/)
- **Type**: Python Flask server with ML inference
- **Purpose**: Computer vision-based seat occupancy detection
- **Key Components**:
  - **Server** (`server/app.py`) - Flask API backend
  - **Inference** (`cam1/`) - Camera-specific ML inference
  - **Tools** (`tools/`) - Utility scripts for processing
  - **Models** - YOLOv8n model for object detection

## Technology Stack

- **Frontend**: React.js
- **Backend**: Python Flask
- **ML Framework**: YOLOv8 (for seat detection)
- **Configuration**: YAML, JSON
