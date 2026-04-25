import re

# Read collections.html to use as boilerplate
with open('collections.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract everything before <main
head_nav = re.split(r'<main', content)[0]

# Extract everything after </main>
footer_scripts = re.split(r'</main>', content)[1]

# In Navbar, ensure Collections is no longer active
head_nav = head_nav.replace('border-b-2 border-[#CCA365] transition-colors py-1" href="collections.html"', 'border-b border-transparent hover:border-[#CCA365] transition-colors py-1" href="collections.html"')

# In Navbar, make About Us active
head_nav = re.sub(r'<a class="text-\[#F5F2EB\].*?href=".*?".*?>About Us</a>', '<a class="text-[#F5F2EB] hover:text-[#CCA365] border-b-2 border-[#CCA365] transition-colors py-1" href="about.html">About Us</a>', head_nav)

about_main = """<main class="w-full relative z-10 flex flex-col bg-surface text-on-surface items-center min-h-screen">
    <!-- About Hero Section -->
    <section class="w-full relative pt-40 pb-20 px-6 overflow-hidden flex flex-col items-center justify-center text-center">
        <!-- Glow aesthetic -->
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-surface to-background w-full h-full pointer-events-none"></div>
        
        <span class="font-label text-xs tracking-[0.3em] uppercase text-secondary mb-6 relative z-10">Our Story</span>
        <h1 class="font-noto-serif text-5xl md:text-7xl mb-8 leading-tight tracking-tight text-white drop-shadow-md relative z-10 max-w-4xl">
            About Vellathur <br/><span class="italic text-primary">Gold & Diamonds</span>
        </h1>
    </section>

    <!-- Legacy of Trust -->
    <section class="max-w-4xl mx-auto px-6 md:px-12 py-24 border-t border-[#5E1C24]/50 text-center relative z-10">
        <h2 class="font-noto-serif text-3xl lg:text-5xl text-on-surface mb-8">Our Legacy of Trust</h2>
        <p class="font-body text-lg md:text-xl text-on-surface-variant leading-relaxed max-w-3xl mx-auto">
            Located in the heart of <span class="text-[#F5F2EB]">Tirur</span>, Vellathur Gold & Diamonds has established itself as a premier destination for those who seek purity, elegance, and transparency in every gram. For years, we have been more than just a jewellery showroom; we are a part of your family’s most cherished celebrations.
        </p>
        <p class="font-body text-lg md:text-xl text-on-surface-variant leading-relaxed max-w-3xl mx-auto mt-6">
            Our commitment to excellence is reflected in our exclusive focus on <span class="text-secondary font-bold tracking-wider">BIS 916 Hallmarked Gold</span>, ensuring that every piece you take home is a valuable asset for generations to come.
        </p>
    </section>

    <!-- Craftsmanship & Collection -->
    <section class="w-full bg-[#1A1313] py-24 relative z-10 border-t border-[#5E1C24]/50">
        <div class="max-w-7xl mx-auto px-6 md:px-12">
            <div class="text-center mb-16">
                <span class="font-label text-xs tracking-[0.2em] uppercase text-outline-variant mb-3 block">— Curated Perfection</span>
                <h2 class="font-noto-serif text-4xl lg:text-5xl text-on-surface">Craftsmanship & Collection</h2>
                <p class="font-body text-lg text-on-surface-variant mt-4 max-w-2xl mx-auto">At Vellathur, we bridge the gap between timeless tradition and contemporary flair.</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <!-- Wedding Wonders -->
                <div class="bg-surface-variant/30 border border-[#5E1C24]/60 p-10 hover:border-primary/50 transition-colors duration-500 group">
                    <span class="material-symbols-outlined text-[32px] text-tertiary mb-6 group-hover:scale-110 transition-transform duration-500">favorite</span>
                    <h3 class="font-noto-serif text-2xl text-[#F5F2EB] mb-4">Wedding Wonders</h3>
                    <p class="font-body text-on-surface-variant leading-relaxed">Breathtaking bridal sets that capture the grandeur of Kerala’s rich heritage.</p>
                </div>
                
                <!-- Diamond Brilliance -->
                <div class="bg-surface-variant/30 border border-[#5E1C24]/60 p-10 hover:border-primary/50 transition-colors duration-500 group">
                    <span class="material-symbols-outlined text-[32px] text-tertiary mb-6 group-hover:scale-110 transition-transform duration-500">diamond</span>
                    <h3 class="font-noto-serif text-2xl text-[#F5F2EB] mb-4">Diamond Brilliance</h3>
                    <p class="font-body text-on-surface-variant leading-relaxed">Precision-cut diamonds that offer an unmatched sparkle for your special moments.</p>
                </div>

                <!-- Lightweight & Daily Wear -->
                <div class="bg-surface-variant/30 border border-[#5E1C24]/60 p-10 hover:border-primary/50 transition-colors duration-500 group">
                    <span class="material-symbols-outlined text-[32px] text-tertiary mb-6 group-hover:scale-110 transition-transform duration-500">wb_sunny</span>
                    <h3 class="font-noto-serif text-2xl text-[#F5F2EB] mb-4">Lightweight & Daily Wear</h3>
                    <p class="font-body text-on-surface-variant leading-relaxed">Elegant, modern designs perfect for the workplace and everyday sophistication.</p>
                </div>

                <!-- Kids Ornaments -->
                <div class="bg-surface-variant/30 border border-[#5E1C24]/60 p-10 hover:border-primary/50 transition-colors duration-500 group">
                    <span class="material-symbols-outlined text-[32px] text-tertiary mb-6 group-hover:scale-110 transition-transform duration-500">child_care</span>
                    <h3 class="font-noto-serif text-2xl text-[#F5F2EB] mb-4">Kids' Ornaments</h3>
                    <p class="font-body text-on-surface-variant leading-relaxed">Gentle and beautiful pieces crafted specifically for the little ones.</p>
                </div>

                <!-- Silver Artistry -->
                <div class="bg-surface-variant/30 border border-[#5E1C24]/60 p-10 hover:border-primary/50 transition-colors duration-500 group md:col-span-2 lg:col-span-1">
                    <span class="material-symbols-outlined text-[32px] text-[#9CA3AF] mb-6 group-hover:scale-110 transition-transform duration-500">auto_awesome</span>
                    <h3 class="font-noto-serif text-2xl text-[#F5F2EB] mb-4">Silver Artistry</h3>
                    <p class="font-body text-on-surface-variant leading-relaxed">A versatile range of silver ornaments and articles that blend utility with style.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Why Choose Vellathur & Our Promise -->
    <section class="max-w-7xl mx-auto px-6 md:px-12 py-24 grid grid-cols-1 md:grid-cols-2 gap-16 relative z-10">
        
        <div class="flex flex-col justify-center">
            <span class="font-label text-xs tracking-[0.2em] uppercase text-primary mb-3 block">— Customer First</span>
            <h2 class="font-noto-serif text-3xl lg:text-4xl text-on-surface mb-6">Why Choose Vellathur?</h2>
            <p class="font-body text-lg text-on-surface-variant leading-relaxed mb-6">
                We believe that buying jewellery is an emotional journey. That is why we prioritize a customer-first approach, offering a transparent pricing policy and personalized service.
            </p>
            <p class="font-body text-lg text-on-surface-variant leading-relaxed">
                Whether you are looking for a custom-designed masterpiece or exploring our latest arrivals, our expert staff is dedicated to helping you find jewellery that resonates with your unique personality.
            </p>
        </div>

        <div class="bg-surface-variant/20 border border-[#5E1C24]/50 p-12 lg:p-16 flex flex-col justify-center relative overflow-hidden group">
            <!-- Glow background purely for styling -->
            <div class="absolute -right-1/4 -bottom-1/4 w-full h-full bg-secondary/5 blur-[100px] pointer-events-none group-hover:bg-secondary/10 transition-colors duration-1000"></div>
            
            <h2 class="font-noto-serif text-3xl lg:text-4xl text-on-surface mb-6 relative z-10"><span class="italic text-tertiary">Our</span> Promise</h2>
            <p class="font-body text-lg text-on-surface-variant leading-relaxed mb-8 relative z-10">
                <strong class="text-[#F5F2EB] font-normal tracking-wide">Purity is our promise, and your trust is our greatest reward.</strong><br/><br/>
                Step into Vellathur Gold & Diamonds at Trikkandiyoor, Tirur, and experience a world where every jewel gleams with authenticity and every design tells a story of grace.
            </p>
            
            <a href="https://share.google/40om84GB7T6PG33Jd" target="_blank" class="inline-flex items-center gap-3 border border-outline-variant/30 text-on-surface hover:bg-surface-variant hover:border-surface-variant px-8 py-4 font-label text-xs tracking-[0.2em] uppercase transition-all duration-300 w-max relative z-10">
                Visit Us <span class="material-symbols-outlined text-[16px]">trending_flat</span>
            </a>
        </div>

    </section>

</main>"""

with open('about.html', 'w', encoding='utf-8') as f:
    f.write(head_nav + about_main + footer_scripts)

print("Created about.html")
