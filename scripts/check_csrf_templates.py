import os
import re

root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'templates')
missing = []
for dirpath, dirnames, filenames in os.walk(root):
    for fn in filenames:
        if not fn.endswith('.html'):
            continue
        path = os.path.join(dirpath, fn)
        with open(path, 'r', encoding='utf-8') as f:
            txt = f.read()
        # find any form with method POST (case-insensitive)
        forms = re.findall(r"<form[^>]*method=[\'\"]?POST[\'\"]?[^>]*>", txt, flags=re.IGNORECASE)
        if forms:
            if 'csrf_token' not in txt and "form.hidden_tag" not in txt:
                # record relative path from project root
                rel = os.path.relpath(path, os.getcwd())
                missing.append(rel.replace('\\', '/'))

print('Checked templates under:', root)
if missing:
    print('Templates with POST forms but no CSRF token:')
    for m in missing:
        print(' -', m)
    exit(1)
else:
    print('All templates with POST forms include CSRF token.')
    exit(0)
