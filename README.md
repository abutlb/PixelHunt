# 🎯 PixelHunt — Image Object Detection Pipeline

<div align="center">

```
██████╗ ██╗██╗  ██╗███████╗██╗     ██╗  ██╗██╗   ██╗███╗   ██╗████████╗
██╔══██╗██║╚██╗██╔╝██╔════╝██║     ██║  ██║██║   ██║████╗  ██║╚══██╔══╝
██████╔╝██║ ╚███╔╝ █████╗  ██║     ███████║██║   ██║██╔██╗ ██║   ██║   
██╔═══╝ ██║ ██╔██╗ ██╔══╝  ██║     ██╔══██║██║   ██║██║╚██╗██║   ██║   
██║     ██║██╔╝ ██╗███████╗███████╗██║  ██║╚██████╔╝██║ ╚████║   ██║   
╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   
```

**Detect · Annotate · Filter — Powered by YOLOv11**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![YOLOv11](https://img.shields.io/badge/YOLO-v11-orange?style=flat-square)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=flat-square&logo=opencv)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

</div>

---

## 📖 Overview

**PixelHunt** is a command-line object detection pipeline built on top of **YOLOv11** and **OpenCV**.  
Drop your images in a folder, pick a mode, and get instant results — annotated images, detailed Excel/CSV reports, or filtered outputs by class.

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🔍 **Mode 1 — Report** | Detect all objects and export a full Excel + CSV report |
| 🎨 **Mode 2 — Annotate** | Save images with bounding boxes and confidence labels |
| 🎯 **Mode 3 — Filter** | Extract only images containing specific classes |
| 📊 **Excel Reports** | 4 sheets: Raw Data · Class Summary · Per Image · Stats |
| 🌐 **RTL / LTR Support** | Full right-to-left support for Excel reports |
| 🎨 **Rich Terminal UI** | Progress bars, colored tables, and live stats |
| ⚡ **Multi-model** | Works with any YOLO `.pt` model (nano → extra-large) |

---

## 📁 Project Structure

```
pixelhunt/
│
├── pixelhunt.py          # Main script
├── requirements.txt      # Dependencies
├── README.md
│
├── images/               # 📥 Put your input images here
│   ├── photo1.jpg
│   ├── photo2.png
│   └── ...
│
└── output/               # 📤 Auto-generated results
    ├── reports/
    │   ├── pixelhunt_report_20260420_170000.xlsx
    │   └── pixelhunt_report_20260420_170000.csv
    ├── annotated/
    │   ├── photo1.jpg
    │   └── photo2.png
    └── filtered__car_plane/
        ├── photo1.jpg
        └── ...
```

---

## 🚀 Installation

```bash
# 1. Clone the repo
git clone https://github.com/abutlb/PixelHunt.git
cd PixelHunt

# 2. Install dependencies
pip install -r requirements.txt
```

**`requirements.txt`**
```
ultralytics
opencv-python
pandas
openpyxl
rich
```

---

## 🎮 Usage

### Basic Syntax
```bash
python pixelhunt.py --mode <1|2|3> [OPTIONS]
```

### All Options

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--mode` | | **required** | `1` Report · `2` Annotate · `3` Filter |
| `--images` | `-i` | `images/` | Input images folder |
| `--output` | `-o` | `output/` | Output folder |
| `--model` | `-m` | `yolo11n.pt` | YOLO model file |
| `--classes` | `-c` | — | Target classes for Mode 3 |
| `--format` | `-f` | `both` | `csv` · `excel` · `both` |
| `--conf` | | `0.25` | Confidence threshold `0.0–1.0` |
| `--dir` | | `RTL` | Report direction `RTL` · `LTR` |

---

## 📌 Examples

```bash
# Mode 1 — Full detection report (RTL Excel, default)
python pixelhunt.py --mode 1

# Mode 1 — LTR report + CSV only
python pixelhunt.py --mode 1 --dir LTR --format csv

# Mode 2 — Annotate all images
python pixelhunt.py --mode 2

# Mode 2 — Custom folders + stronger model
python pixelhunt.py --mode 2 -i ./photos -o ./results -m yolo11m.pt

# Mode 3 — Filter images containing cars or planes
python pixelhunt.py --mode 3 --classes car plane

# Mode 3 — Higher confidence threshold
python pixelhunt.py --mode 3 --classes person --conf 0.6
```

---

## 📊 Excel Report Structure

The generated `.xlsx` file contains **4 sheets**:

| Sheet | Contents |
|-------|----------|
| `Raw Detections` | Every detected object with coordinates, confidence, and image info |
| `Class Summary` | Per-class stats: count, images, avg/min/max confidence, avg size |
| `Per Image Summary` | Per-image stats: total objects, unique classes, avg confidence |
| `Stats Overview` | Global summary: totals, averages, generation timestamp |

> All sheets support **RTL layout** for Arabic/Hebrew workflows via `--dir RTL`.

---

## 🎨 Annotation Style

Bounding boxes use a **double-border style** with a filled label background:

```
┌─────────────────────┐
│  car  94%           │  ← filled color label
╔═════════════════════╗
║                     ║  ← outer colored border
║   detected object   ║
║                     ║
╚═════════════════════╝
```

Each class gets a **unique consistent color** across all images.

---

## 🤖 Supported Models

Any YOLOv11 `.pt` model works out of the box:

| Model | Speed | Accuracy |
|-------|-------|----------|
| `yolo11n.pt` | ⚡⚡⚡⚡⚡ | ⭐⭐ |
| `yolo11s.pt` | ⚡⚡⚡⚡ | ⭐⭐⭐ |
| `yolo11m.pt` | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| `yolo11l.pt` | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| `yolo11x.pt` | ⚡ | ⭐⭐⭐⭐⭐ |

Models are **auto-downloaded** by Ultralytics on first run.

---

## 🖼️ Supported Image Formats

`.jpg` · `.jpeg` · `.png` · `.bmp` · `.webp` · `.tiff` · `.tif`

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

<div align="center">
  Made with ❤️ using YOLOv11 · OpenCV · Rich
</div>
