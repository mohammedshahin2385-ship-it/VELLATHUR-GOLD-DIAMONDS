import glob
import re
import os

files = glob.glob("*.html")
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove data-i18n attributes that target nav or footer items
    new_content = re.sub(r'\sdata-i18n="(nav|footer)_[^"]+"', '', content)
    
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Updated {f}")
    else:
        print(f"No changes for {f}")
