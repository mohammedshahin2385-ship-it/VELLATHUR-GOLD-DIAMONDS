import re
import glob

files = glob.glob('*.html')
pattern = re.compile(r'<!-- Language Switch Global -->.*?</div>\s*<div class="hidden md:flex flex-col items-end mr-2">', re.DOTALL)

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if pattern.search(content):
        new_content = pattern.sub(r'<div class="hidden md:flex flex-col items-end mr-2">', content)
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Reverted in {f}")
