# app.py

import json
import uuid
from pathlib import Path

import gradio as gr
from ultralytics import YOLO

from core.detector   import detect_image, annotate_image
from core.downloader import load_urls_from_file, images_from_urls
from core.reporter   import save_json, save_excel, save_csv
from translations    import ClassTranslator

# ── تحميل النموذج مرة واحدة ──
MODEL      = YOLO("yolo11n.pt")
LANGUAGES  = ClassTranslator.available_languages()
OUTPUT_DIR = Path("gradio_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ════════════════════════════════════════════════
#   CSS مخصص
# ════════════════════════════════════════════════

CUSTOM_CSS = """
/* ── الخط العام ── */
* { font-family: 'Segoe UI', Tahoma, sans-serif; }

/* ── البانر ── */
.banner-box {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 16px;
    padding: 32px 24px;
    text-align: center;
    margin-bottom: 8px;
    border: 1px solid #e94560;
}
.banner-box h1 {
    color: #e94560 !important;
    font-size: 2.2em !important;
    margin: 0 0 6px 0 !important;
    letter-spacing: 2px;
}
.banner-box p  { color: #a8b2d8 !important; margin: 4px 0 !important; font-size: 1em; }
.banner-box .sub { color: #64ffda !important; font-size: 0.9em; }

/* ── بطاقات الأقسام ── */
.section-card {
    background: #f8faff;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 20px 8px 20px;
    margin-bottom: 12px;
}
.section-title {
    font-size: 1.05em;
    font-weight: 700;
    color: #1e40af;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── زر التشغيل ── */
.run-btn {
    background: linear-gradient(90deg, #e94560, #0f3460) !important;
    color: white !important;
    font-size: 1.15em !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    padding: 14px !important;
    border: none !important;
    width: 100%;
    letter-spacing: 1px;
    transition: opacity 0.2s;
}
.run-btn:hover { opacity: 0.88 !important; }

/* ── زر التحميل ── */
.download-btn button {
    background: linear-gradient(90deg, #059669, #065f46) !important;
    color: white !important;
    font-size: 1.05em !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    border: none !important;
    width: 100% !important;
    margin-top: 8px;
}

/* ── بطاقة النتيجة ── */
.result-stat {
    background: linear-gradient(135deg, #1e40af, #3b82f6);
    color: white;
    border-radius: 10px;
    padding: 14px 10px;
    text-align: center;
    font-size: 1.5em;
    font-weight: 800;
}
.result-stat span { display: block; font-size: 0.45em; font-weight: 400; opacity: 0.85; margin-top: 2px; }

/* ── الـ Gallery ── */
.gallery-wrap img {
    cursor: zoom-in;
    border-radius: 8px;
    transition: transform 0.2s;
}

/* ── tooltip / hint ── */
.hint-box {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 0.88em;
    color: #78350f;
    margin: 6px 0 10px 0;
}

/* ── Accordion ── */
.tips-accordion { border: 1.5px dashed #cbd5e1 !important; border-radius: 10px !important; }
"""

# ════════════════════════════════════════════════
#   دالة الكشف
# ════════════════════════════════════════════════

def run_detection(
    images_input,
    urls_text,
    urls_file,
    lang,
    conf,
    output_format,
    annotate,
):
    translator = ClassTranslator(lang=lang)
    results    = []
    ann_paths  = []

    run_dir = OUTPUT_DIR / uuid.uuid4().hex[:8]
    run_dir.mkdir(parents=True)

    try:
        sources = []

        if images_input:
            for img in images_input:
                sources.append((None, Path(img)))

        if urls_text and urls_text.strip():
            urls = [u.strip() for u in urls_text.strip().splitlines() if u.strip()]
            for url, path in images_from_urls(urls, run_dir / "from_urls"):
                sources.append((url, path))

        if urls_file is not None:
            file_urls = load_urls_from_file(Path(urls_file))
            for url, path in images_from_urls(file_urls, run_dir / "from_file"):
                sources.append((url, path))

        if not sources:
            msg = "❌ No images or URLs provided! / لم يتم تقديم أي صور أو روابط"
            return None, None, 0, 0, msg

        ann_dir = run_dir / "annotated"
        ann_dir.mkdir()

        for source_url, img_path in sources:
            result = detect_image(MODEL, img_path, conf, translator, source_url)
            results.append(result)

            if annotate:
                ann_path = ann_dir / f"ann_{img_path.name}"
                annotate_image(img_path, result, ann_path, translator)
                if ann_path.exists():
                    ann_paths.append(str(ann_path))

        if not results:
            return None, None, 0, 0, "❌ No results!"

        # ── حفظ المخرجات ──
        out_dir = run_dir / "reports"
        out_dir.mkdir()

        json_path  = save_json(results, out_dir / "results.json")
        excel_path = None
        csv_path   = None

        if output_format in ("excel", "both"):
            excel_path = save_excel(results, out_dir / "results.xlsx")
        if output_format in ("csv", "both"):
            csv_path = save_csv(results, out_dir / "results.csv")

        # ── اختيار ملف التحميل ──
        if output_format == "excel" and excel_path:
            download_file = str(excel_path)
        elif output_format == "csv" and csv_path:
            download_file = str(csv_path)
        else:
            download_file = str(json_path)

        if not Path(download_file).exists():
            download_file = None

        # ── إحصائيات ──
        total_imgs = len(results)
        total_objs = sum(r["total_objects"] for r in results)

        # ── JSON preview ──
        preview = json.dumps(
            {
                "total_images" : total_imgs,
                "total_objects": total_objs,
                "sample"       : results[:2],
            },
            ensure_ascii=False,
            indent=2,
        )

        return ann_paths or None, download_file, total_imgs, total_objs, preview

    except Exception as e:
        import traceback
        error_msg = f"❌ Error:\n{str(e)}\n\n{traceback.format_exc()}"
        return None, None, 0, 0, error_msg


# ════════════════════════════════════════════════
#   Gradio UI
# ════════════════════════════════════════════════

with gr.Blocks(title="🎯 PixelHunt") as demo:

    # ── البانر ──
    gr.HTML("""
    <div class="banner-box">
        <h1>🎯 PixelHunt</h1>
        <p><b>Object Detection Pipeline — Powered by YOLOv11</b></p>
        <p class="sub">
            كشف الأجسام · التعليق التوضيحي · التصفية
            &nbsp;|&nbsp;
            Detect · Annotate · Filter
        </p>
    </div>
    """)

    # ── دليل الاستخدام السريع ──
    with gr.Accordion("📖 Quick Guide / دليل الاستخدام", open=False, elem_classes="tips-accordion"):
        gr.HTML("""
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; padding:12px;">

            <div style="background:#f0f9ff; border-radius:10px; padding:14px;">
                <b style="color:#0369a1;">📥 Input / المدخلات</b><br><br>
                <b>Upload Images:</b> ارفع صور مباشرة من جهازك<br><br>
                <b>Image URLs:</b> الصق روابط صور من الإنترنت (رابط لكل سطر)<br><br>
                <b>URLs File:</b> ارفع ملف <code>.txt</code> أو <code>.csv</code> أو <code>.json</code>
                يحتوي على قائمة روابط
            </div>

            <div style="background:#f0fdf4; border-radius:10px; padding:14px;">
                <b style="color:#15803d;">⚙️ Settings / الإعدادات</b><br><br>
                <b>Language:</b> لغة أسماء الكلاسات في النتائج<br><br>
                <b>Confidence:</b> دقة الكشف — كلما زاد كلما قل عدد النتائج لكن بدقة أعلى<br><br>
                <b>Output Format:</b> صيغة ملف النتائج للتحميل<br><br>
                <b>Annotate:</b> رسم مربعات على الصور
            </div>

            <div style="background:#fefce8; border-radius:10px; padding:14px;">
                <b style="color:#a16207;">📊 Output Formats / صيغ المخرجات</b><br><br>
                <b>JSON:</b> افتراضي — مناسب للمطورين والـ API<br><br>
                <b>CSV:</b> مناسب لـ Excel العادي<br><br>
                <b>Excel:</b> تقرير كامل بـ 4 صفحات مع إحصائيات<br><br>
                <b>Both:</b> CSV + Excel معاً
            </div>

            <div style="background:#fdf4ff; border-radius:10px; padding:14px;">
                <b style="color:#7e22ce;">💡 Tips / نصائح</b><br><br>
                • الصور الواضحة تعطي نتائج أفضل<br><br>
                • ابدأ بـ Confidence = 0.25 ثم عدّل<br><br>
                • لو النموذج ما كشف شيء جرب تخفض الـ Confidence<br><br>
                • يمكنك الجمع بين رفع الصور والروابط معاً
            </div>

        </div>
        """)

    # ── الصف الرئيسي ──
    with gr.Row(equal_height=False):

        # ════ العمود الأيسر: المدخلات ════
        with gr.Column(scale=1):

            # -- رفع الصور --
            gr.HTML('<div class="section-title">📸 Upload Images / رفع الصور</div>')
            images_input = gr.File(
                label="Drag & drop images here / اسحب الصور هنا",
                file_count="multiple",
                file_types=["image"],
            )

            # -- روابط --
            gr.HTML('<div class="section-title">🔗 Image URLs / روابط الصور</div>')
            gr.HTML('<div class="hint-box">📌 ضع رابطاً واحداً في كل سطر — Paste one URL per line</div>')
            urls_text = gr.Textbox(
                label="",
                placeholder="https://example.com/image1.jpg\nhttps://example.com/image2.jpg",
                lines=3,
            )

            # -- ملف روابط --
            gr.HTML('<div class="section-title">📄 URLs File / ملف الروابط</div>')
            gr.HTML('<div class="hint-box">📌 يقبل ملفات .txt · .csv · .json تحتوي على قائمة روابط</div>')
            urls_file = gr.File(
                label="",
                file_types=[".txt", ".csv", ".json"],
            )

            gr.HTML("<hr style='margin:16px 0; border-color:#e2e8f0;'>")

            # -- الإعدادات --
            gr.HTML('<div class="section-title">⚙️ Settings / الإعدادات</div>')

            with gr.Row():
                lang = gr.Dropdown(
                    choices=LANGUAGES,
                    value="en",
                    label="🌍 Language / اللغة",
                    info="لغة أسماء الكلاسات في النتائج",
                )
                conf = gr.Slider(
                    minimum=0.1, maximum=0.95,
                    value=0.25, step=0.05,
                    label="🎯 Confidence / الدقة",
                    info="0.25 مناسب للبداية",
                )

            output_format = gr.Radio(
                choices=[
                    ("JSON  —  للمطورين والـ API", "json"),
                    ("CSV   —  جداول بيانات",      "csv"),
                    ("Excel —  تقرير كامل",        "excel"),
                    ("Both  —  CSV + Excel",       "both"),
                ],
                value="json",
                label="📊 Output Format / صيغة المخرجات",
            )

            annotate = gr.Checkbox(
                label="🎨 Annotate images / رسم مربعات على الصور",
                value=True,
                info="يحفظ نسخة من الصور مع تحديد الأجسام المكتشفة",
            )

            run_btn = gr.Button(
                "🚀  Run Detection  |  ابدأ الكشف",
                elem_classes="run-btn",
            )

        # ════ العمود الأيمن: المخرجات ════
        with gr.Column(scale=1):

            gr.HTML('<div class="section-title">📊 Results / النتائج</div>')

            # -- إحصائيات --
            with gr.Row():
                stat_imgs = gr.Number(
                    label="📸 Images Processed / الصور",
                    value=0,
                    interactive=False,
                )
                stat_objs = gr.Number(
                    label="📦 Objects Detected / الأجسام",
                    value=0,
                    interactive=False,
                )

            gr.HTML("<hr style='margin:12px 0; border-color:#e2e8f0;'>")

            # -- زر التحميل الواضح --
            gr.HTML('<div class="section-title">💾 Download Report / تحميل التقرير</div>')
            gr.HTML('<div class="hint-box">⬇️ بعد الكشف اضغط الزر لتحميل ملف النتائج</div>')
            download_btn = gr.File(
                label="📥 Click to Download / اضغط للتحميل",
                elem_classes="download-btn",
                interactive=False,
            )

            gr.HTML("<hr style='margin:12px 0; border-color:#e2e8f0;'>")

            # -- الصور المشروحة --
            gr.HTML('<div class="section-title">🖼️ Annotated Images / الصور المشروحة</div>')
            gr.HTML('<div class="hint-box">🔍 اضغط على أي صورة لعرضها بالحجم الكامل</div>')
            ann_gallery = gr.Gallery(
                label="",
                columns=2,
                height=380,
                object_fit="contain",   # ✅ يعرض الصورة كاملة بدون قص
                preview=True,           # ✅ يفتح lightbox عند الضغط
                elem_classes="gallery-wrap",
            )

            gr.HTML("<hr style='margin:12px 0; border-color:#e2e8f0;'>")

            # -- JSON preview --
            gr.HTML('<div class="section-title">📋 JSON Preview / معاينة النتائج</div>')
            json_preview = gr.Code(
                label="",
                language="json",
                lines=14,
            )

    # ── ربط الزر ──
    run_btn.click(
        fn=run_detection,
        inputs=[
            images_input, urls_text, urls_file,
            lang, conf, output_format, annotate,
        ],
        outputs=[ann_gallery, download_btn, stat_imgs, stat_objs, json_preview],
    )

    # ── Footer ──
    gr.HTML("""
        <div style="
            margin-top: 32px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            border-radius: 16px;
            border-top: 3px solid #e94560;
            padding: 32px 24px 24px 24px;
            text-align: center;
        ">

            <!-- الشعار -->
            <div style="font-size:1.6em; font-weight:900; letter-spacing:3px; color:#e94560; margin-bottom:4px;">
                🎯 PIXELHUNT
            </div>
            <div style="color:#64ffda; font-size:0.85em; margin-bottom:24px; letter-spacing:1px;">
                Object Detection Pipeline · خط أنابيب كشف الأجسام
            </div>

            <!-- الأدوات المستخدمة -->
            <div style="display:flex; justify-content:center; gap:12px; flex-wrap:wrap; margin-bottom:24px;">

                <a href="https://github.com/ultralytics/ultralytics" target="_blank" style="
                    text-decoration:none;
                    background:#1e293b;
                    border:1px solid #e94560;
                    border-radius:20px;
                    padding:6px 16px;
                    color:#e94560;
                    font-size:0.82em;
                    font-weight:600;
                    transition:all 0.2s;
                ">⚡ YOLOv11</a>

                <a href="https://opencv.org" target="_blank" style="
                    text-decoration:none;
                    background:#1e293b;
                    border:1px solid #3b82f6;
                    border-radius:20px;
                    padding:6px 16px;
                    color:#3b82f6;
                    font-size:0.82em;
                    font-weight:600;
                ">👁️ OpenCV</a>

                <a href="https://www.gradio.app" target="_blank" style="
                    text-decoration:none;
                    background:#1e293b;
                    border:1px solid #8b5cf6;
                    border-radius:20px;
                    padding:6px 16px;
                    color:#8b5cf6;
                    font-size:0.82em;
                    font-weight:600;
                ">🎨 Gradio</a>

                <a href="https://pandas.pydata.org" target="_blank" style="
                    text-decoration:none;
                    background:#1e293b;
                    border:1px solid #10b981;
                    border-radius:20px;
                    padding:6px 16px;
                    color:#10b981;
                    font-size:0.82em;
                    font-weight:600;
                ">🐼 Pandas</a>

                <a href="https://www.python.org" target="_blank" style="
                    text-decoration:none;
                    background:#1e293b;
                    border:1px solid #f59e0b;
                    border-radius:20px;
                    padding:6px 16px;
                    color:#f59e0b;
                    font-size:0.82em;
                    font-weight:600;
                ">🐍 Python 3.10+</a>

            </div>

            <!-- فاصل -->
            <div style="border-top:1px solid #1e3a5f; margin: 0 10% 20px 10%;"></div>

            <!-- الروابط -->
            <div style="display:flex; justify-content:center; gap:24px; flex-wrap:wrap; margin-bottom:20px;">

                <a href="https://github.com/abutlb/PixelHunt" target="_blank" style="
                    text-decoration:none;
                    color:#a8b2d8;
                    font-size:0.85em;
                    display:flex;
                    align-items:center;
                    gap:5px;
                ">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="#a8b2d8">
                        <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577
                        0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.335-1.755
                        -1.335-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236
                        1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466
                        -1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176
                        0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405
                        2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23
                        1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22
                        0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295
                        24 12c0-6.63-5.37-12-12-12"/>
                    </svg>
                    GitHub
                </a>

                <a href="https://github.com/abutlb/PixelHunt/issues" target="_blank" style="
                    text-decoration:none; color:#a8b2d8; font-size:0.85em;
                    display:flex; align-items:center; gap:5px;
                ">🐛 Report Issue / بلّغ عن مشكلة</a>

                <a href="https://github.com/abutlb/PixelHunt/blob/main/README.md" target="_blank" style="
                    text-decoration:none; color:#a8b2d8; font-size:0.85em;
                    display:flex; align-items:center; gap:5px;
                ">📖 Docs / التوثيق</a>

            </div>

            <!-- Copyright -->
            <div style="color:#4a5568; font-size:0.78em; letter-spacing:0.5px;">
                © 2026 PixelHunt &nbsp;·&nbsp; MIT License &nbsp;·&nbsp;
                Made with <span style="color:#e94560;">❤️</span> by
                <a href="https://github.com/abutlb" target="_blank"
                   style="color:#64ffda; text-decoration:none; font-weight:600;">
                    @abutlb
                </a>
            </div>

        </div>
        """)



if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Soft(primary_hue="blue"),
        css=CUSTOM_CSS,
        ssr_mode=False
    )
