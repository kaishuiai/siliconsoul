# SiliconSoul

اللغات:

- 简体中文 (افتراضي): README.md
- 简体中文: README.zh-CN.md
- 繁體中文: README.zh-TW.md
- English: README.en.md
- Русский: README.ru.md
- Tiếng Việt: README.vi.md
- Français: README.fr.md
- Español: README.es.md
- Italiano: README.it.md
- 日本語: README.ja.md
- 한국어: README.ko.md
- ᠮᠠᠨᠵᡠ ᡤᡳᠰᡠᠨ (Manchu): README.mnc.md
- ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ (Mongolian, traditional script): README.mn.md
- العربية: README.ar.md

## الاستخدام / القيمة / التموضع / نقاط التميّز

SiliconSoul هو نموذج أولي لمنتج دعم قرار متعدد الوكلاء (MOE) موجّه للمؤسسين والمديرين التشغيليين والمستثمرين وفرق الـCFO. يجمع بين إدخال عدة مستندات (PDF/Excel/PPT/Word) والاستدلال المتوازي لخبراء متعددين لإنتاج نتائج مدعومة بالأدلة، وقائمة منظمة بما ينقص من معلومات، وسجل قابل لإعادة التشغيل والمراجعة.

### القيمة

- إدخال متعدد المستندات → مخرجات قابلة لإعادة الاستخدام: خلاصة + أدلة + ما المطلوب استكماله
- تحليل نشاط/منتج فرعي مع تحقق واضح من النطاق وقواعد التوزيع (allocations)
- سير عمل قابل للإعادة: History و Replay و Diff وتصدير التقارير

### التموضع

- أداة تحليل ومراجعة، وليست نظام محاسبة ولا بديلًا عن ERP/BI
- مناسبة للعناية الواجبة، مراجعات الميزانية، التحليل التشغيلي، تحليل القطاعات، ودعم أبحاث الاستثمار

### نقاط التميّز

- رفع دفعات + وسوم غرض المستند (مالية/إيرادات قطاع/تكاليف/توزيعات/KPI/عقود وتسعير) مع تنظيم الأدلة حسب الغرض
- عند نقص المواد تعيد needs_structured (قائمة تحقق) مع أولويات
- صفحة History في الموقع الرئيسي تدعم فلترة CFO و replay/diff/download
- أمان صارم: لا يتم رفع tokens أو مفاتيح خاصة أو app id؛ يُنصح بتشغيل فحص الأمان قبل push

نظام دعم قرار متعدد الوكلاء (MOE)، ويتضمن:

- واجهة API خلفية بـ Python (aiohttp) + تنسيق الخبراء
- موقع رئيسي بـ React (Dashboard / Portfolio / KnowledgeBase / History)
- صفحة CFO بـ Streamlit (رفع عدة ملفات، تحليل نشاط/منتج فرعي، تصدير تقرير)

## بدء سريع (Docker Compose)

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

- الويب (React): غالبًا http://localhost:3000
- API: غالبًا http://localhost:8000/api
- CFO (Streamlit): http://localhost:8501 (يفتح من الموقع الرئيسي عبر رابط خارجي)

## تطوير محلي

### الخلفية

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

### الواجهة الأمامية

```bash
cd frontend
npm install
npm start
```

## الإعدادات والمعلومات الحساسة

يجب ألا يحتوي هذا المستودع على أي token / مفتاح خاص / app id. استخدم متغيرات البيئة أو ملفات إعداد محلية.

- لا تقم بعمل commit للملفات: `.env*` و `data/` و `logs/` و `*.db` و `*.key` و `*.pem` (مستثناة عبر .gitignore)
- يُنصح قبل الدفع: `./scripts/security_check.sh`
- مثال إعداد للواجهة: `frontend/.env.example`
- متغيرات شائعة (أسماء فقط، لا تضع القيم في المستودع):
  - `TUSHARE_TOKEN`: رمز Tushare
  - `SILICONSOUL_API_TOKENS`: تعيين رموز المصادقة للخلفية (لـ `/api/me`)
  - `REACT_APP_API_URL`: base url لواجهة API للموقع
  - `REACT_APP_CFO_URL`: رابط صفحة CFO الخارجية
  - `CFO_API_URL`: base url لواجهة API لصفحة CFO

## وثائق

- [سيناريو CFO](docs/cfo.md)
- [توثيق API](docs/api.md)
- [دليل التطوير](docs/development.md)
