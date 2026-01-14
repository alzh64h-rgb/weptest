```markdown
# نظام نسخ الملفات (versions)

فكرة بسيطة لحماية التعديلات: كل تعديل تحفظه كملف جديد داخل مجلد `versions/`، وملف `CURRENT` في جذر المستودع يشير إلى اسم الملف الفعّال الحالي.

الملفات المرفقة:
- `add_version.py` : ينسخ أي ملف إلى `versions/` مع طابع زمني ويحدّث `CURRENT`، ويخزن سجل في `versions/log.jsonl`.
  - مثال: `python add_version.py src/app.py --desc "fix-login-bug"`
  - لعرض السجل: `python add_version.py --list`
  - للرجوع إلى نسخة معينة حسب رقم السجل: `python add_version.py --rollback-index 3`
  - للرجوع إلى نسخة محددة بالاسم: `python add_version.py --rollback v20260101_121314_fix.py`

- `loader.py` : يحمل الملف المشار إليه في `CURRENT`. إن كان بايثون يحاول استدعاء `main()` إن وُجدت.
  - مثال تشغيل: `python loader.py`
  - لتشغيل كـ script: `python loader.py --run-as-script`
  - لاستدعاء دالة: `python loader.py --call some_function`

الممارسات المقترحة:
1. قبل كل تعديل كبير، شغّل `add_version.py` على الملف الذي ستعدّله — هذا سيحفظ نسخة احتياطية تلقائيًا.
2. بعد التأكد من التعديلات يمكنك إعادة حفظ نسخة جديدة بنفس الأسلوب.
3. عند حدوث خطأ: إما تعديل `CURRENT` يدوياً لإعادة اسم الملف السابق، أو استخدم `add_version.py --rollback-index N`.
4. يُفضّل استخدام Git أيضاً: commits صغيرة لكل خطوة + استخدام هذا النظام كطبقة حماية إضافية.

ملاحظة:
- السكربت أعلاه يناسب تعديل ملفات عامة؛ `loader.py` مفيد خاصة لملفات بايثون. يمكنك تعديل السكربت ليدعم لغات أو سلوك تشغيل آخر حسب مشروعك.
```