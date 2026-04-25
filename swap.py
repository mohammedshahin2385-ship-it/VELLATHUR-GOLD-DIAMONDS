import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

header_pattern = re.compile(
    r'<div class="flex flex-col items-center justify-center mt-1 text-center">\s*<span[^>]*>Vellathur</span>\s*<span[^>]*>Gold \& Diamonds</span>\s*</div>',
    re.DOTALL | re.IGNORECASE
)

footer_pattern = re.compile(
    r'<div[^>]*>Vellathur</div>\s*<div[^>]*>Gold \& Diamonds</div>',
    re.DOTALL | re.IGNORECASE
)

footer_amp_pattern = re.compile(
    r'<div[^>]*>Vellathur</div>\s*<div[^>]*>Gold &amp; Diamonds</div>',
    re.DOTALL | re.IGNORECASE
)

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original = content
    content = content.replace('Asset 3@3x (1).png', 'images/IMG_1090.png')
    content = header_pattern.sub('', content)
    content = footer_pattern.sub('', content)
    content = footer_amp_pattern.sub('', content)
    
    if content != original:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Updated ' + file)
