# core/detector.py

from pathlib import Path
from datetime import datetime

import cv2
from ultralytics import YOLO

from translations import ClassTranslator


CLASS_COLORS = [
    (255,  56,  56), (255, 157, 151), (255, 112,  31),
    (255, 178,  29), (207, 210,  49), ( 72, 249,  10),
    (146, 204,  23), ( 61, 219, 134), ( 26, 147,  52),
    (  0, 212, 187), ( 44, 153, 168), (  0, 194, 255),
    ( 52,  69, 147), (100, 115, 255), (  0,  24, 236),
    (132,  56, 255), ( 82,   0, 133), (203,  56, 255),
    (255, 149, 200), (255,  55, 199),
]


def get_color(class_id: int) -> tuple:
    return CLASS_COLORS[class_id % len(CLASS_COLORS)]


def detect_image(
    model      : YOLO,
    img_path   : Path,
    conf       : float,
    translator : ClassTranslator,
    source_url : str | None = None,
) -> dict:
    """
    يشغل YOLO على صورة واحدة ويرجع dict جاهز للـ JSON.
    """
    img             = cv2.imread(str(img_path))
    h, w            = img.shape[:2]
    results         = model(str(img_path), conf=conf, verbose=False)[0]
    ts              = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    detections      = []

    for b in results.boxes:
        cls_id      = int(b.cls[0])
        cls_name    = model.names[cls_id]
        cls_display = translator.translate_display(cls_name)
        confidence  = float(b.conf[0])
        x1, y1, x2, y2 = map(int, b.xyxy[0])

        detections.append({
            "class_id"    : cls_id,
            "class_name"  : cls_display,
            "class_en"    : cls_name,
            "confidence"  : round(confidence, 4),
            "bbox"        : {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            "size_px"     : {"width": x2 - x1, "height": y2 - y1},
        })

    return {
        "image_name"   : img_path.name,
        "source_url"   : source_url,
        "image_size"   : {"width": w, "height": h},
        "detected_at"  : ts,
        "total_objects": len(detections),
        "detections"   : detections,
    }


def annotate_image(
    img_path   : Path,
    result     : dict,
    out_path   : Path,
    translator : ClassTranslator,
):
    """يرسم bounding boxes على الصورة ويحفظها."""
    img = cv2.imread(str(img_path))

    for det in result["detections"]:
        b     = det["bbox"]
        color = get_color(det["class_id"])
        label = f"  {det['class_name']}  {det['confidence']:.0%}  "

        cv2.rectangle(img, (b["x1"], b["y1"]), (b["x2"], b["y2"]), color, 3)
        cv2.rectangle(img, (b["x1"]+1, b["y1"]+1), (b["x2"]-1, b["y2"]-1), (255,255,255), 1)

        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img, (b["x1"], b["y1"] - th - 14), (b["x1"] + tw + 4, b["y1"]), color, -1)
        cv2.putText(img, label, (b["x1"] + 2, b["y1"] - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imwrite(str(out_path), img)
