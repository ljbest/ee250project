# EE250 IoT Security Camera System

A distributed IoT security camera system that uses YOLOv8 computer vision to detect people across multiple camera feeds and alerts viewers in real time via a web interface.

---

## Overview

This system allows an arbitrary number of phone or webcam clients to act as security cameras, streaming snapshots to a central Flask server. The server uses YOLOv8 to detect people in each snapshot and serves a live dashboard to viewer clients showing only cameras that have active person detections.

---

## Features

- 📷 **Multi-camera support** — any number of devices can register as cameras
- 👤 **Person detection** — YOLOv8n runs inference on each camera snapshot
- 🖥️ **Live viewer dashboard** — shows live feeds only from cameras with people detected
- 🌐 **Browser-based** — both camera and viewer clients run entirely in the browser
- 🔒 **HTTPS** — required for browser camera access, enabled via ad-hoc SSL

---

## Project Structure

```
ee250project/
├── server.py               # Flask server — handles camera registration, image processing, routing
├── imageClassification.py  # YOLOv8 person detection script (standalone image input)
├── camera.html             # Camera client — captures and streams snapshots from browser
├── camera_list.html        # Viewer dashboard — displays feeds from cameras with detections
└── install                 # Dependency installation script
```

---

## Requirements

- Python 3.11+
- pip

---

## Installation

**Clone the repository:**
```bash
git clone https://github.com/ljbest/ee250project.git
cd ee250project
```

**Set up a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

**Install dependencies:**
```bash
pip install flask flask-socketio ultralytics opencv-python pillow pyopenssl
```

---

## Running the System

### 1. Start the server
```bash
python server.py
```
The server runs on `https://0.0.0.0:5000` with ad-hoc HTTPS enabled.

> **Note:** Your browser will show a `net::ERR_CERT_AUTHORITY_INVALID` warning due to the self-signed certificate. Click "Advanced" and proceed — this is expected behavior in a development environment.

---

### 2. Open a camera client
On any device connected to the same network, open a browser and navigate to:
```
https://<server-ip>:5000/camera
```
You will be prompted to enter a name for the camera. Once named, the client will begin sending a snapshot to the server every 2 seconds. The server runs YOLOv8 inference on each snapshot to count people.

---

### 3. Open the viewer dashboard
On any device, navigate to:
```
https://<server-ip>:5000/camera/list
```
This page displays live snapshots from all cameras that currently have one or more people detected.

---

## Standalone Image Classification

To run person detection on a single image without the full server:

```bash
python imageClassification.py <image_path>
```

**Example:**
```bash
python imageClassification.py photo.jpg
```

**Output:**
```
Image size: 1280x720 px

==================================================
People detected: 2
==================================================

Person 1:
  Confidence     : 94%
  Bounding box   : top-left (112, 45)  bottom-right (289, 430)
  Size           : 177x385 px
  Center         : (200, 237)
  Region         : left

Person 2:
  Confidence     : 88%
  Bounding box   : top-left (540, 60)  bottom-right (710, 440)
  Size           : 170x380 px
  Center         : (625, 250)
  Region         : center

Annotated image saved as: detected_people.jpg
```

An annotated copy of the image with bounding boxes drawn around each detected person is saved as `detected_people.jpg`.

---

## How It Works

### Computer Vision
YOLOv8n (You Only Look Once, nano variant) performs single-pass object detection on each camera snapshot. YOLO divides the image into a grid and simultaneously predicts bounding boxes, confidence scores, and class probabilities in one forward pass through a convolutional neural network. Only detections of class `person` with a confidence score above 40% are counted.

### Camera Client
The camera client (`camera.html`) uses the browser's HTML5 MediaDevices API to access the device camera. Every 2 seconds it captures a snapshot, encodes it as a base64 JPEG, and POSTs it to the server along with the camera name. The camera name is collected via a JavaScript `prompt` on page load and bundled with each snapshot to ensure it is always defined before transmission begins.

### Server
The Flask server (`server.py`) exposes the following endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/camera` | GET | Serves the camera client page |
| `/camera/list` | GET | Serves the viewer dashboard |
| `/camera/get` | POST | Receives snapshots, runs YOLO, stores results |
| `/connect` | POST | Registers a new camera |
| `/disconnect` | POST | Removes a camera from the registry |

### Viewer Dashboard
The viewer dashboard (`camera_list.html`) is rendered server-side using Flask's `render_template`, which passes a filtered list of cameras with a person count greater than zero. The HTML is dynamically populated with the latest snapshot from each active camera.

---

## Known Limitations

- The self-signed SSL certificate will trigger a browser warning on first visit
- The server currently stores camera data in memory — restarting the server clears all registered cameras
- Snapshot transmission every 2 seconds introduces slight latency in detections

---

## Authors

Lindsay Best — EE250 IoT Project
