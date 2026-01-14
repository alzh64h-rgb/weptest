#!/usr/bin/env python3
"""
add_version.py
نسخة بايثون بسيطة لإضافة نسخة من ملف إلى مجلد versions وتحديث المؤشر CURRENT.
Usage:
  python add_version.py path/to/source.ext --desc "short description"
  python add_version.py --list
  python add_version.py --rollback v20260101_121314_description.py
"""
import argparse
import os
import shutil
import datetime
import re
import json
import sys

VERSIONS_DIR = "versions"
CURRENT_FILE = "CURRENT"
LOG_FILE = os.path.join(VERSIONS_DIR, "log.jsonl")

def safe(s: str) -> str:
    return re.sub(r'[^A-Za-z0-9._-]', '_', s)[:100]

def ensure_dirs():
    os.makedirs(VERSIONS_DIR, exist_ok=True)

def add_version(src_path: str, desc: str = None):
    if not os.path.isfile(src_path):
        print(f"خطأ: الملف المصدر غير موجود: {src_path}", file=sys.stderr)
        sys.exit(2)
    ensure_dirs()
    base_ext = os.path.splitext(src_path)[1]
    stamp = datetime.datetime.utcnow().strftime("v%Y%m%d_%H%M%S")
    desc_safe = ("_" + safe(desc)) if desc else ""
    fname = f"{stamp}{desc_safe}{base_ext}"
    dst = os.path.join(VERSIONS_DIR, fname)
    shutil.copy2(src_path, dst)
    with open(CURRENT_FILE, "w", encoding="utf-8") as f:
        f.write(fname)
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "source": os.path.abspath(src_path),
        "stored": fname,
        "desc": desc or "",
    }
    with open(LOG_FILE, "a", encoding="utf-8") as lf:
        lf.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"تم حفظ النسخة: {dst}")
    print(f"المؤشر CURRENT محدث إلى: {fname}")
    return fname

def list_versions():
    if not os.path.exists(LOG_FILE):
        print("لا توجد نسخ محفوظة بعد.")
        return
    with open(LOG_FILE, "r", encoding="utf-8") as lf:
        for i, line in enumerate(lf, 1):
            try:
                obj = json.loads(line)
                print(f"{i:3d}: {obj.get('stored')}  | {obj.get('timestamp')} | {obj.get('desc')}")
            except Exception:
                print(f"{i:3d}: (سطر سجل تالف) {line.strip()}")

def rollback(to_name: str = None, index: int = None):
    if index is not None:
        # find by index in log
        if not os.path.exists(LOG_FILE):
            print("لا يوجد سجل للنسخ.", file=sys.stderr); sys.exit(3)
        with open(LOG_FILE, "r", encoding="utf-8") as lf:
            lines = lf.readlines()
        if index < 1 or index > len(lines):
            print("فهرس غير صالح.", file=sys.stderr); sys.exit(4)
        obj = json.loads(lines[index-1])
        to_name = obj.get("stored")
    if not to_name:
        print("يجب تحديد اسم النسخة أو فهرسها للرجوع إليه.", file=sys.stderr); sys.exit(5)
    path = os.path.join(VERSIONS_DIR, to_name)
    if not os.path.exists(path):
        print(f"النسخة المطلوبة غير موجودة: {path}", file=sys.stderr); sys.exit(6)
    with open(CURRENT_FILE, "w", encoding="utf-8") as f:
        f.write(to_name)
    print(f"تم الرجوع إلى: {to_name} (المؤشر CURRENT مُحدّث)")

def main():
    p = argparse.ArgumentParser(description="Version single file into versions/ and update CURRENT")
    p.add_argument("source", nargs="?", help="path to source file to save as new version")
    p.add_argument("--desc", help="short description to include in filename", default=None)
    p.add_argument("--list", action="store_true", help="list saved versions")
    p.add_argument("--rollback", help="rollback to named stored file (stored filename)")
    p.add_argument("--rollback-index", type=int, help="rollback to nth entry in the log (1-based)")
    args = p.parse_args()
    if args.list:
        list_versions()
        return
    if args.rollback or args.rollback_index:
        rollback(to_name=args.rollback, index=args.rollback_index)
        return
    if not args.source:
        p.print_help()
        return
    add_version(args.source, args.desc)

if __name__ == "__main__":
    main()