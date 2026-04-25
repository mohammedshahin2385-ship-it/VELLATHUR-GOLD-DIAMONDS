import glob
import re

files = glob.glob('*.html')
for f in files:
    if f == 'contact.html':
        continue
    
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace navbar link
    # Pattern looks for the "Contact Us" <a> tag in nav
    content = re.sub(r'(<a class="text-\[#F5F2EB\].*?)href="[^"]*?"(.*?>Contact Us</a>)', r'\1href="contact.html"\2', content)
    
    # Replace footer link
    # Pattern looks for "Contact Us" in footer
    content = re.sub(r'(<a class="text-\[#888888\].*?)href="[^"]*?"(.*?>Contact Us</a>)', r'\1href="contact.html"\2', content)

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
        
print("Updated all contact links globally.")
