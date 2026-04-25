import glob
import re

files = glob.glob('*.html')
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Replace the location icon href in all footers
    # Current: <a class="text-[#CCA365] opacity-60 hover:opacity-100 transition-opacity" href="#"><span class="material-symbols-outlined">location_on</span></a>
    # Updated: <a class="text-[#CCA365] opacity-60 hover:opacity-100 transition-opacity" href="https://share.google/yWGdoJM0EdQTshnyn" target="_blank"><span class="material-symbols-outlined">location_on</span></a>
    
    pattern1 = r'<a class="(text-\[#CCA365\].*?)" href="#"><span class="material-symbols-outlined">location_on</span></a>'
    replacement1 = r'<a class="\1" href="https://share.google/yWGdoJM0EdQTshnyn" target="_blank"><span class="material-symbols-outlined">location_on</span></a>'
    content = re.sub(pattern1, replacement1, content)

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print("Linked the Google Maps URL to Location Footer Icon.")
