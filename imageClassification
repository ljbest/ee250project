import cv2
import sys
from ultralytics import YOLO


def detect_people(image_path: str):
    """
    Detects people in an image using YOLOv8.
    Outputs the count and location of each person found.
    """
  
    model = YOLO("yolov8n.pt")  # downloads automatically on first run

    image = cv2.imread(image_path)
    if image is None:
        sys.exit(1)

    img_height, img_width = image.shape[:2]
    print(f"Image size: {img_width}x{img_height} px\n")

   
    results = model(image, verbose=False)

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

    print("=" * 50)
    if len(people) == 0:
        print("No people detected in the image.")
        print("=" * 50)
        return

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

    output_path = "detected_people.jpg"
    cv2.imwrite(output_path, image)
    print(f"\nAnnotated image saved as: {output_path}")


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
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python detect_people.py <image_path>")
        print("Example: python detect_people.py photo.jpg")
        sys.exit(1)

    detect_people(sys.argv[1])
