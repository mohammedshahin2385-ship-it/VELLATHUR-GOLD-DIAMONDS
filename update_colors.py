import os
import re

files_to_update = ['home.html', 'about.html', 'collections.html', 'contact.html', 'diamonds.html', '22k_gold.html', 'profile.html', 'kia-header.css', 'scroll-animate.css', 'update_all.py', 'revert_nav.py']

replacements = {
    r'(?i)#050505': '#0C0808',
    r'(?i)#121412': '#0C0808',
    r'rgba\(9,\s*9,\s*9,\s*0\.92\)': 'rgba(12, 8, 8, 0.92)',
    
    r'(?i)#0A0A0A': '#1A1313',
    r'(?i)#141414': '#1A1313',
    r'(?i)#1C1C1C': '#1A1313',
    r'(?i)#1A1A1A': '#1A1313',
    r'rgba\(18,\s*20,\s*18,\s*0\.8\)': 'rgba(26, 19, 19, 0.8)',
    
    r'(?i)#1A472A': '#CCA365',
    r'(?i)#004225': '#CCA365',
    r'(?i)#9c8a67': '#CCA365',
    r'(?i)#98d4ac': '#CCA365',
    r'(?i)#d3c5ad': '#CCA365',
    r'(?i)rgba\(152,\s*212,\s*172,': 'rgba(204, 163, 101,',
    r'(?i)rgba\(211,\s*197,\s*173,': 'rgba(204, 163, 101,',
    
    r'(?i)#333533': '#5E1C24',
    r'(?i)#00522B': '#5E1C24',
    
    r'(?i)#F5F5F5': '#F5F2EB',
    r'(?i)#F1F1F1': '#F5F2EB',
    r'(?i)#E0E0E0': '#F5F2EB',
    r'(?i)#e2e3df': '#F5F2EB',
    r'(?i)#ffffff': '#F5F2EB',
}

for root, _, files in os.walk('.'):
    for f in files:
        if f.endswith('.html') or f.endswith('.css') or f.endswith('.js') or f.endswith('.py'):
            if f in ['update_colors.py']:
                continue
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            new_content = content
            for old, new_col in replacements.items():
                new_content = re.sub(old, new_col, new_content)
                
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Updated {f}")
