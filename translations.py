import json
from pathlib import Path

# مجلد ملفات الترجمة
TRANSLATIONS_DIR = Path(__file__).parent / "translations"


class ClassTranslator:
    """
    يقرأ ملفات الترجمة من مجلد translations/
    كل لغة = ملف JSON مستقل (ar.json, fr.json, ...)
    لإضافة لغة جديدة: أنشئ ملف <lang>.json في المجلد.
    """

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self._map: dict = {}

        if lang != "en":
            path = TRANSLATIONS_DIR / f"{lang}.json"
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    self._map = json.load(f)
            else:
                raise FileNotFoundError(
                    f"❌ ملف الترجمة غير موجود: {path}\n"
                    f"   اللغات المتاحة: {', '.join(self.available_languages())}"
                )

        # قاموس عكسي: مترجم → إنجليزي + إنجليزي → إنجليزي
        self._reversed: dict = {v.lower(): k for k, v in self._map.items()}
        self._reversed.update({k.lower(): k for k in self._map.keys()})

    # ─────────────────────────────────────────────
    #  الترجمة: إنجليزي → لغة المستخدم
    # ─────────────────────────────────────────────
    def translate(self, name: str) -> str:
        """إنجليزي → لغة المستخدم. يرجع الأصلي إن ما في ترجمة."""
        return self._map.get(name, name)

    def translate_display(self, name: str) -> str:
        """
        يرجع الاسم بالشكل: 'سيارة (car)' أو 'car' إن كانت en.
        مفيد لعرض التقارير والجداول.
        """
        if not self._map:
            return name
        translated = self._map.get(name, name)
        if translated != name:
            return f"{translated} ({name})"
        return name

    # ─────────────────────────────────────────────
    #  البحث العكسي: لغة المستخدم → إنجليزي
    # ─────────────────────────────────────────────
    def match_classes(self, tokens: list[str]) -> tuple[list[str], list[str]]:
        """
        يحل مشكلة الكلاسات المركبة من كلمتين مثل 'لوحة مفاتيح'.
        يجرب من أطول تركيبة للأقصر حتى يلقى تطابق.

        المدخل : ['لوحة', 'مفاتيح', 'سيارة']
        المخرج : (['keyboard', 'car'], [])
        """
        valid   = []
        invalid = []
        i       = 0

        while i < len(tokens):
            matched = False
            max_len = min(3, len(tokens) - i)
            for length in range(max_len, 0, -1):
                phrase  = " ".join(tokens[i : i + length])
                english = self._reversed.get(phrase.lower())
                if english:
                    valid.append(english)
                    i      += length
                    matched = True
                    break

            if not matched:
                invalid.append(tokens[i])
                i += 1

        return valid, invalid

    # ─────────────────────────────────────────────
    #  أدوات مساعدة
    # ─────────────────────────────────────────────
    @staticmethod
    def available_languages() -> list[str]:
        """يكتشف اللغات المتاحة تلقائياً من ملفات الـ JSON."""
        return ["en"] + [
            p.stem
            for p in sorted(TRANSLATIONS_DIR.glob("*.json"))
        ]

    def available_classes_display(self) -> str:
        """يرجع string جاهز للطباعة بكل الكلاسات بلغة المستخدم."""
        if not self._map:
            return "person, car, bicycle, ..."
        return "،  ".join(self._map.values())
