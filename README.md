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
![Languages](https://img.shields.io/badge/Languages-EN%20·%20AR%20·%20FR%20·%20ES-teal?style=flat-square)

</div>

---

## 📖 Overview

**PixelHunt** is a command-line object detection pipeline built on top of **YOLOv11** and **OpenCV**.  
Drop your images in a folder, pick a mode, and get instant results — annotated images, detailed Excel/CSV reports, or filtered outputs by class.

Now with **multi-language support** 🌍 — search, filter, and read reports in your own language.

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🔍 **Mode 1 — Report** | Detect all objects and export a full Excel + CSV report |
| 🎨 **Mode 2 — Annotate** | Save images with bounding boxes and confidence labels |
| 🎯 **Mode 3 — Filter** | Extract only images containing specific classes |
| 📊 **Excel Reports** | 4 sheets: Raw Data · Class Summary · Per Image · Stats |
| 🌐 **RTL / LTR Support** | Full right-to-left support for Excel reports |
| 🌍 **Multi-language** | Class names in EN · AR · FR · ES — search in your language |
| 🎨 **Rich Terminal UI** | Progress bars, colored tables, and live stats |
| ⚡ **Multi-model** | Works with any YOLO `.pt` model (nano → extra-large) |

---

## 📁 Project Structure

```
pixelhunt/
│
├── pixelhunt.py          # Main script
├── translations.py       # ClassTranslator — language engine
├── requirements.txt      # Dependencies
├── README.md
│
├── translations/         # 🌍 One file per language
│   ├── ar.json           # Arabic
│   ├── fr.json           # French
│   ├── es.json           # Spanish
│   └── zh.json           # Add your own!
│
├── images/               # 📥 Put your input images here
│   ├── photo1.jpg
│   └── ...
│
└── output/               # 📤 Auto-generated results
    ├── reports/
    │   ├── pixelhunt_report_20260420_170000.xlsx
    │   └── pixelhunt_report_20260420_170000.csv
    ├── annotated/
    │   ├── photo1.jpg
    │   └── ...
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
| `--lang` | | `en` | Output language `en` · `ar` · `fr` · `es` |

---

## 📌 Examples

```bash
# Mode 1 — Full detection report (default)
python pixelhunt.py --mode 1

# Mode 1 — Arabic report + RTL Excel
python pixelhunt.py --mode 1 --lang ar

# Mode 1 — French report + LTR + CSV only
python pixelhunt.py --mode 1 --lang fr --dir LTR --format csv

# Mode 2 — Annotate all images in Arabic
python pixelhunt.py --mode 2 --lang ar

# Mode 2 — Custom folders + stronger model
python pixelhunt.py --mode 2 -i ./photos -o ./results -m yolo11m.pt

# Mode 3 — Filter in English
python pixelhunt.py --mode 3 --classes car plane

# Mode 3 — Filter in Arabic (single word)
python pixelhunt.py --mode 3 --lang ar --classes سيارة طائرة

# Mode 3 — Filter in Arabic (multi-word class)
python pixelhunt.py --mode 3 --lang ar --classes لوحة مفاتيح سيارة

# Mode 3 — Higher confidence threshold
python pixelhunt.py --mode 3 --lang ar --classes شخص --conf 0.6
```

---

## 🌍 Multi-language Support

PixelHunt supports searching, filtering, and reporting in multiple languages.  
Class names appear in the format **`سيارة (car)`** in reports and annotated images.

### Supported Languages

| Code | Language | File |
|------|----------|------|
| `en` | English *(default)* | built-in |
| `ar` | Arabic — العربية | `translations/ar.json` |
| `fr` | French — Français | `translations/fr.json` |
| `es` | Spanish — Español | `translations/es.json` |

### ➕ Adding a New Language

1. Copy any existing file as a template:
```bash
cp translations/en.json translations/zh.json
```

2. Translate the **values** only — keep the keys in English:
```json
{
    "person": "人",
    "car": "汽车",
    "cat": "猫"
}
```

3. Run immediately — no code changes needed:
```bash
python pixelhunt.py --mode 1 --lang zh
```

> 💡 Want to contribute a translation? Open a **Pull Request** with your `.json` file — it's that simple!

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
> Class names appear **bilingual** (e.g. `سيارة (car)`) when using `--lang ar`.

---

## 🎨 Annotation Style

Bounding boxes use a **double-border style** with a filled label background:

```
┌─────────────────────┐
│  سيارة (car)  94%   │  ← bilingual label
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

## 🤝 Contributing

Contributions are welcome! The easiest way to contribute is by **adding a new language translation**:

1. Fork the repo
2. Add `translations/<lang>.json`
3. Open a Pull Request

For bugs or feature requests, open an [Issue](https://github.com/abutlb/PixelHunt/issues).

---

## 📜 License

MIT License — free to use, modify, and distribute for **personal and non-commercial use**.

For commercial licensing, contact: abutlb10015@gmail.com

---

<div align="center">
  Made with ❤️ using YOLOv11 · OpenCV · Rich
</div>
