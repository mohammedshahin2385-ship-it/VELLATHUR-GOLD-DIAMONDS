import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

loader_pattern = re.compile(r'(<div id="loader".*?</div>\s*</div>\s*</div>)', re.DOTALL)

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to replace 'images/IMG_1090.png' specifically within the loader section
    
    match = loader_pattern.search(content)
    if match:
        loader_block = match.group(1)
        new_loader_block = loader_block.replace('images/IMG_1090.png', 'Asset 3@3x (1).png')
        content = content.replace(loader_block, new_loader_block)
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Updated ' + file)
