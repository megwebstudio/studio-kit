#!/usr/bin/env python3
"""Fill README.md from README.template.md with the captured real outputs in assets/examples/.

  python3 tools/capture_examples.py && python3 tools/build_readme.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "README.template.md"), encoding="utf-8") as fh:
    text = fh.read()


def fill(m):
    path = os.path.join(ROOT, "assets", "examples", m.group(1) + ".txt")
    with open(path, encoding="utf-8") as fh:
        return fh.read().rstrip("\n")


text = re.sub(r"\{\{(\w+)\}\}", fill, text)
with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as fh:
    fh.write(text)
print("README.md written, %d lines" % text.count("\n"))
