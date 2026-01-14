#!/usr/bin/env python3
"""
loader.py
يحمل الملف المشار إليه في CURRENT من مجلد versions ويشغّله.
- إذا كان الملف بايثون (.py): سيحاول استيراده كـ module ونداء الدالة main() إذا وُجدت.
- يمكن استخدام --run-as-script لتشغيله عبر runpy.run_path (مثل تنفيذ كسكربت مستقل).
Usage:
  python loader.py            # يحاول استيراد وتشغيل main() إذا كانت موجودة
  python loader.py --call func_name  # يستدعي دالة func_name من الموديول المحمّل
  python loader.py --run-as-script  # ينفّذ الملف كسكربت
"""
import os
import sys
import importlib.util
import runpy
import argparse

VERSIONS_DIR = "versions"
CURRENT_FILE = "CURRENT"

def get_current_path():
    if not os.path.exists(CURRENT_FILE):
        print("لا يوجد ملف CURRENT. حدّثه أولًا باستخدام add_version.py", file=sys.stderr)
        sys.exit(2)
    name = open(CURRENT_FILE, encoding="utf-8").read().strip()
    path = os.path.join(VERSIONS_DIR, name)
    if not os.path.exists(path):
        print(f"الملف المشار إليه غير موجود: {path}", file=sys.stderr)
        sys.exit(3)
    return path

def load_python_module(path):
    spec = importlib.util.spec_from_file_location("active_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--call", help="call a function from the loaded module (e.g. main)")
    p.add_argument("--run-as-script", action="store_true", help="execute the file as a script")
    args = p.parse_args()

    path = get_current_path()
    ext = os.path.splitext(path)[1].lower()

    if args.run_as_script:
        runpy.run_path(path, run_name="__main__")
        return

    if ext == ".py":
        mod = load_python_module(path)
        if args.call:
            fn = getattr(mod, args.call, None)
            if not callable(fn):
                print(f"الدالة {args.call} غير موجودة أو غير قابلة للاستدعاء في الموديول.", file=sys.stderr)
                sys.exit(4)
            result = fn()
            if result is not None:
                print("نتيجة الاستدعاء:", result)
        else:
            # حاول استدعاء main() إن وجدت
            if hasattr(mod, "main") and callable(mod.main):
                mod.main()
            else:
                print("لا توجد دالة main() في الموديول؛ تم تحميله فقط.")
    else:
        print("الملف ليس بايثون. استخدم --run-as-script لتشغيله كسكربت أو افتحه يدوياً.", file=sys.stderr)
        sys.exit(5)

if __name__ == "__main__":
    main()