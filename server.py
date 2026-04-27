
import cv2
from PIL import Image
import os
import time
from flask import Flask, Response, json, render_template
from werkzeug.utils import secure_filename
from flask import request
from flask_socketio import SocketIO, emit
from os import path, getcwd
import time
import os
import base64
import io
import sys
from ultralytics import YOLO


def detect_people(image_path: str):
    """
    Detects people in an image using YOLOv8.
    Outputs the count and location of each person found.
    """

    # ── Load model ──────────────────────────────────────────────────────────
    print("Loading YOLO model...")
    model = YOLO("yolov8n.pt")  # downloads automatically on first run

    # ── Load image ──────────────────────────────────────────────────────────
    image = cv2.imread("./static/"+image_path)
    if image is None:
        print("=" * 50)
        print(f"❌ Error: Could not load image from '{image_path}'")
        print("Check the filename is correct and the file exists.")
        print("=" * 50)
        sys.exit(1)

    img_height, img_width = image.shape[:2]
    print(f"Image size: {img_width}x{img_height} px\n")

    # ── Run detection ────────────────────────────────────────────────────────
    results = model(image, verbose=False)

    # ── Filter for people only (YOLO class 0 = person) ──────────────────────
    people = []
    for result in results:
        for box in result.boxes:
            if int(box.cls) == 0:  # class 0 is 'person'
                confidence = float(box.conf)
                if confidence >= 0.4:  # confidence threshold
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    people.append({
                        "confidence": confidence,
                        "x1": x1, "y1": y1,
                        "x2": x2, "y2": y2,
                        "width": x2 - x1,
                        "height": y2 - y1,
                        "center_x": (x1 + x2) // 2,
                        "center_y": (y1 + y2) // 2,
                    })

    # ── Print results ────────────────────────────────────────────────────────
    print("=" * 50)
    if len(people) == 0:
        print("✅ Detection complete.")
        print("👤 No people found in the image.")
        print("=" * 50)
        return 0

    print(f"People detected: {len(people)}")
    print("=" * 50)

    for i, person in enumerate(people, start=1):
        region = get_region(
            person["center_x"], person["center_y"],
            img_width, img_height
        )
        print(f"\nPerson {i}:")
        print(f"  Confidence     : {person['confidence']:.1%}")
        print(f"  Bounding box   : top-left ({person['x1']}, {person['y1']})  "
              f"bottom-right ({person['x2']}, {person['y2']})")
        print(f"  Size           : {person['width']}x{person['height']} px")
        print(f"  Center         : ({person['center_x']}, {person['center_y']})")
        print(f"  Region         : {region}")

    print("\n" + "=" * 50)

    # ── Save annotated image ─────────────────────────────────────────────────
    for i, person in enumerate(people, start=1):
        x1, y1, x2, y2 = person["x1"], person["y1"], person["x2"], person["y2"]

        # Draw bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Label with person number and confidence
        label = f"Person {i} ({person['confidence']:.0%})"
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        label_y = y1 - 10 if y1 - 10 > 10 else y1 + 20

        # Background rectangle for label
        cv2.rectangle(
            image,
            (x1, label_y - label_size[1] - 4),
            (x1 + label_size[0], label_y + 4),
            (0, 255, 0), -1
        )
        cv2.putText(
            image, label, (x1, label_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2
        )

    output_path = "./static/"+"detected_people_"+image_path
    cv2.imwrite(output_path, image)
    print(f"\nAnnotated image saved as: {output_path}")
    
    return len(people)


def get_region(cx: int, cy: int, img_w: int, img_h: int) -> str:
    """
    Divides the image into a 3x3 grid and returns which region
    the center point falls in (e.g. 'top-left', 'center', 'bottom-right').
    """
    col = cx / img_w
    row = cy / img_h

    if col < 1/3:
        h_pos = "left"
    elif col < 2/3:
        h_pos = "center"
    else:
        h_pos = "right"

    if row < 1/3:
        v_pos = "top"
    elif row < 2/3:
        v_pos = "middle"
    else:
        v_pos = "bottom"

    if v_pos == "middle" and h_pos == "center":
        return "center"
    if v_pos == "middle":
        return h_pos
    return f"{v_pos}-{h_pos}"


# ── Entry point ──────────────────────────────────────────────────────────────
#if __name__ == "__main__":
#    if len(sys.argv) < 2:
#        print("Usage: python detect_people.py <image_path>")
#        print("Example: python detect_people.py photo.jpg")
#        sys.exit(1)
#
#    detect_people(sys.argv[1])
#    detect_people(sys.argv[1])








app = Flask(__name__,template_folder='./')
socketio = SocketIO(app, logge=True)

host_ip = "0.0.0.0"


cameras = {}

@app.route('/disconnect', methods=['POST'])
def disconnect():
    if request.is_json:
        data = request.get_json()
        name = data
        if name not in cameras:
            return f"{name} does not exist", 400
        else:
            del cameras[name]
            return f"removed {name} from cameras", 200
    return "Invalid Request", 400
    
@app.route('/camera')
def video_feed():
    return render_template('camera.html')
@app.route('/camera/list')
def print_cameras():
#    print(cameras.items())
    active_cameras = {key:"static/../detected_people_"+value["name"] for key, value in cameras.items() if value["people"] >= 1}

    return render_template('camera_list.html', camera_list=active_cameras)
    
@app.route('/camera/get', methods=['POST'])
def get_camera_image():
    if request.is_json:
        data = request.get_json()
        name = data["camera_name"]+'.jpg';
        
        if name not in cameras:
            cameras[name] = {"name":name}
        
        
        with open("./static/"+name, 'wb') as file:
            file.write(base64.decodebytes(bytes(data["image"][23:],'utf-8')))
        
        
        cameras[name]["people"] = detect_people(name)
        
        
        
        return "got image", 200
    return "Invalid Request", 400
    
app.run(host=host_ip, port=5000, debug=False, threaded=False,ssl_context='adhoc')
