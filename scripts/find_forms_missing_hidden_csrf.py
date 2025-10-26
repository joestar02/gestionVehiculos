import os, re
root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'templates')
problems = []
for dirpath, dirnames, filenames in os.walk(root):
    for fn in filenames:
        if not fn.endswith('.html'): continue
        path = os.path.join(dirpath, fn)
        with open(path, 'r', encoding='utf-8') as f:
            txt = f.read()
        # for each form tag, check inside if contains csrf_token and hidden input
        for m in re.finditer(r"(<form[^>]*method=[\'\"]?POST[\'\"]?[^>]*>)(.*?)(</form>)", txt, flags=re.IGNORECASE|re.DOTALL):
            form_open = m.group(1)
            form_body = m.group(2)
            # if csrf_token present but no name="csrf_token" field
            if '{{ csrf_token() }}' in form_body and 'name="csrf_token"' not in form_body and "name='csrf_token'" not in form_body:
                rel = os.path.relpath(path, os.getcwd()).replace('\\','/')
                problems.append((rel, form_open.strip()))
                break
print('Found', len(problems), 'forms with bare csrf_token and no hidden input:')
for p in problems:
    print(' -', p[0], 'form starts with:', p[1][:80])
if problems:
    exit(1)
else:
    exit(0)
