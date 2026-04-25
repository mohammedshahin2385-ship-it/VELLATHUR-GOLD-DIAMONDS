import glob
import re

files = glob.glob('*.html')
for f in files:
    if f == 'about.html':
        continue
    
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace navbar link
    # Pattern looks for the "About Us" <a> tag in nav
    content = re.sub(r'(<a class="text-\[#F5F2EB\].*?)href="[^"]*?"(.*?>About Us</a>)', r'\1href="about.html"\2', content)

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
        
print("Updated all about links globally.")
