import re

files = ['d:/vellathur/profile.html', 'd:/vellathur/diamonds.html', 'd:/vellathur/22k_gold.html']

for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Clean up old anchor tag with logo
        content = re.sub(
            r'\s*<a href="home\.html" class="flex items-center flex-shrink-0 h-full">\s*<img src="Asset 3@3x \(1\)\.png"[^>]+>\s*</a>',
            '',
            content,
            flags=re.MULTILINE
        )
        
        # Make sure target header has the new flex-row logo syntax
        target_header_old = r'<a href="home\.html" class="flex flex-col items-center justify-center group whitespace-nowrap mt-1 text-center">'
        target_header_new = r"""<a href="home.html" class="flex flex-row items-center justify-center group whitespace-nowrap gap-3">
                <img src="Asset 3@3x (1).png" alt="Vellathur Logo" class="h-8 md:h-10 w-auto object-contain filter invert opacity-90 group-hover:opacity-100 transition-opacity" style="filter: invert(1) drop-shadow(0 0 5px rgba(204, 163, 101, 0.2));">
                <div class="flex flex-col items-center justify-center mt-1 text-center">"""
        
        content = re.sub(target_header_old, target_header_new.replace('\\', ''), content)
        
        # Re-attach closing div for header flex-column wrap
        target_header_end_old = r'<span class="font-label text-\[7px\] md:text-\[8px\] tracking-\[0\.35em\] text-\[#CCA365\] group-hover:text-\[#F5F2EB\] transition-colors uppercase leading-none ml-\[0\.35em\]">Gold &amp; Diamonds</span>\s*</a>'
        target_header_end_new = r"""<span class="font-label text-[7px] md:text-[8px] tracking-[0.35em] text-[#CCA365] group-hover:text-[#F5F2EB] transition-colors uppercase leading-none ml-[0.35em]">Gold & Diamonds</span>
                </div>
            </a>"""
        # wait `&amp;` vs `&`. It is `& Diamonds`. We use `Gold & Diamonds` in raw HTML. Let's just do `Gold & Diamonds</span>\s*</a>`
        content = re.sub(r'Gold & Diamonds</span>\s*</a>', r'Gold & Diamonds</span>\n                </div>\n            </a>', content)
        
        # Clean up old footer logo if it exists isolated
        content = re.sub(r'\s*<img src="Asset 3@3x \(1\)\.png" alt="Vellathur Logo" class="h-16 md:h-24 w-auto object-contain brightness-0 invert opacity-90">', '', content)
        
        # Prepend new logo in footer
        footer_old = r'<div class="flex flex-col items-center">\s*<div class="font-noto-serif text-2xl tracking-\[0\.3em\] text-\[#F5F2EB\] opacity-90 uppercase text-center mb-2">Vellathur</div>'
        footer_new = r"""<div class="flex flex-col items-center">
            <img src="Asset 3@3x (1).png" alt="Vellathur Logo" class="h-16 md:h-20 w-auto object-contain filter invert opacity-70 mb-4" style="filter: invert(1) drop-shadow(0 0 5px rgba(204, 163, 101, 0.1));">
            <div class="font-noto-serif text-2xl tracking-[0.3em] text-[#F5F2EB] opacity-90 uppercase text-center mb-2">Vellathur</div>"""
            
        content = re.sub(footer_old, footer_new.replace('\\', ''), content)
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
            
    except Exception as e:
        print(f"Failed on {f}: {e}")
