import os

files = ['home.html', 'collections.html', '22k_gold.html', 'diamonds.html', 'profile.html']

nav_target = """        <nav class="hidden lg:flex gap-6 items-center font-noto-serif text-[10px] tracking-[0.15em] uppercase justify-center flex-1">
            <a class="text-[#F5F2EB] hover:text-[#CCA365] border-b border-transparent hover:border-[#CCA365] transition-colors py-1" href="home.html">Home</a>
            <a class="text-[#F5F2EB] hover:text-[#CCA365] border-b border-transparent hover:border-[#CCA365] transition-colors py-1" href="#">About Us</a>
            <a class="text-[#F5F2EB] hover:text-[#CCA365] border-b border-transparent hover:border-[#CCA365] transition-colors py-1" href="collections.html">Collections</a>
            <a class="text-[#F5F2EB] hover:text-[#CCA365] border-b border-transparent hover:border-[#CCA365] transition-colors py-1" href="#">New Arrivals</a>
            <a class="text-[#F5F2EB] hover:text-[#CCA365] border-b border-transparent hover:border-[#CCA365] transition-colors py-1" href="#">Contact Us</a>
        </nav>
        <div class="flex-none flex items-center justify-end gap-5 ml-auto">
            <div class="hidden md:flex flex-col items-end mr-2">"""

nav_replace = """        <nav class="hidden lg:flex gap-6 items-center font-noto-serif text-[10px] tracking-[0.15em] uppercase justify-center flex-1">
            <a class="text-[#F5F2EB] hover:text-[#CCA365] border-b border-transparent hover:border-[#CCA365] transition-colors py-1" href="home.html" data-i18n="nav_home">Home</a>
            <a class="text-[#F5F2EB] hover:text-[#CCA365] border-b border-transparent hover:border-[#CCA365] transition-colors py-1" href="#" data-i18n="nav_about">About Us</a>
            <a class="text-[#F5F2EB] hover:text-[#CCA365] border-b border-transparent hover:border-[#CCA365] transition-colors py-1" href="collections.html" data-i18n="nav_collections">Collections</a>
            <a class="text-[#F5F2EB] hover:text-[#CCA365] border-b border-transparent hover:border-[#CCA365] transition-colors py-1" href="#" data-i18n="nav_new_arrivals">New Arrivals</a>
            <a class="text-[#F5F2EB] hover:text-[#CCA365] border-b border-transparent hover:border-[#CCA365] transition-colors py-1" href="#" data-i18n="nav_contact_us">Contact Us</a>
        </nav>
        <div class="flex-none flex items-center justify-end gap-5 ml-auto">
            
            <div class="hidden md:flex flex-col items-end mr-2">"""

footer_links_target = """<div class="flex flex-wrap justify-center gap-x-12 gap-y-6 font-manrope text-[10px] tracking-[0.2em] uppercase">
        <a class="text-[#888888] hover:text-[#CCA365] transition-colors cursor-none" href="#">Privacy Policy</a>
        <a class="text-[#888888] hover:text-[#CCA365] transition-colors cursor-none" href="#">Terms of Service</a>
        <a class="text-[#888888] hover:text-[#CCA365] transition-colors cursor-none" href="#">Ethical Sourcing</a>
        <a class="text-[#888888] hover:text-[#CCA365] transition-colors cursor-none" href="#">Contact Us</a>
    </div>"""

footer_links_replace = """<div class="flex flex-wrap justify-center gap-x-12 gap-y-6 font-manrope text-[10px] tracking-[0.2em] uppercase">
        <a class="text-[#888888] hover:text-[#CCA365] transition-colors cursor-none" href="#" data-i18n="footer_privacy">Privacy Policy</a>
        <a class="text-[#888888] hover:text-[#CCA365] transition-colors cursor-none" href="#" data-i18n="footer_terms">Terms of Service</a>
        <a class="text-[#888888] hover:text-[#CCA365] transition-colors cursor-none" href="#" data-i18n="footer_ethical">Ethical Sourcing</a>
        <a class="text-[#888888] hover:text-[#CCA365] transition-colors cursor-none" href="#" data-i18n="footer_contact">Contact Us</a>
    </div>"""

for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace Navbar
        if nav_target in content:
            content = content.replace(nav_target, nav_replace)
        else:
            print(f"[{f}] Warning: NAV target not found exactly.")
            
        # Replace Footer Links
        if footer_links_target in content:
            content = content.replace(footer_links_target, footer_links_replace)
        else:
            print(f"[{f}] Warning: Footer Links target not found exactly.")
            
        # Add script tag before </body>
        if "<script src=\"i18n.js\"></script>" not in content:
            content = content.replace("</body>", "<script src=\"i18n.js\"></script>\n</body>")
            
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"[{f}] Processed successfully.")
