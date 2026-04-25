import re

# Read collections.html to use as boilerplate
with open('collections.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract everything before <main
head_nav = re.split(r'<main', content)[0]

# Extract everything after </main>
footer_scripts = re.split(r'</main>', content)[1]

# Overwrite active state in Nav bar for Contact Us
# From: href="collections.html" class="... border-b-2 border-[#CCA365] ..."
head_nav = head_nav.replace('border-b-2 border-[#CCA365]', 'border-b border-transparent hover:border-[#CCA365]')

# Add active state to Contact Us
# Find: href="#" for Contact Us and make it active and link to contact.html
new_nav_str = '<a class="text-[#F5F2EB] hover:text-[#CCA365] border-b-2 border-[#CCA365] transition-colors py-1" href="contact.html">Contact Us</a>'
head_nav = re.sub(r'<a class="text-\[#F5F2EB\].*?href=".*?".*?>Contact Us</a>', new_nav_str, head_nav)

contact_main = """<main class="w-full relative z-10 flex flex-col pt-32 pb-24 bg-surface text-on-surface items-center min-h-screen">
    <!-- Hero Section for Contact -->
    <div class="text-center mb-16 px-4 max-w-3xl">
        <span class="font-label text-xs tracking-[0.3em] uppercase text-secondary mb-4 block">Reaching Out</span>
        <h1 class="font-noto-serif text-5xl md:text-7xl mb-6 leading-tight tracking-tight text-white drop-shadow-md">
            Get In <span class="italic text-primary">Touch</span>
        </h1>
        <p class="font-body text-on-surface-variant text-base md:text-lg max-w-xl mx-auto">
            Whether you have an inquiry about a bespoke piece, need to coordinate an atelier visit, or simply wish to say hello, we are at your service.
        </p>
    </div>

    <!-- Contact Form Container -->
    <div class="w-full max-w-2xl px-6 md:px-12">
        <form class="flex flex-col gap-8 bg-surface-variant/40 p-8 md:p-12 border border-[#5E1C24]/50 shadow-2xl relative overflow-hidden group mb-12">
            
            <!-- Glow aesthetic -->
            <div class="absolute -top-1/2 -left-1/2 w-full h-full bg-primary/5 blur-[100px] pointer-events-none group-focus-within:bg-primary/20 transition-colors duration-1000"></div>

            <div class="flex flex-col gap-1 relative z-10">
                <label for="fullName" class="font-label text-[10px] tracking-[0.2em] uppercase text-[#888888]">Full Name</label>
                <input type="text" id="fullName" name="fullName" required class="bg-transparent border-b border-[#5E1C24] focus:border-primary text-[#F5F2EB] font-body text-base py-3 outline-none transition-colors duration-300 placeholder-[#5E1C24]" placeholder="Enter your name">
            </div>

            <div class="flex flex-col gap-1 relative z-10">
                <label for="email" class="font-label text-[10px] tracking-[0.2em] uppercase text-[#888888]">Email Address</label>
                <input type="email" id="email" name="email" required class="bg-transparent border-b border-[#5E1C24] focus:border-primary text-[#F5F2EB] font-body text-base py-3 outline-none transition-colors duration-300 placeholder-[#5E1C24]" placeholder="your.email@domain.com">
            </div>

            <div class="flex flex-col gap-1 relative z-10">
                <label for="phone" class="font-label text-[10px] tracking-[0.2em] uppercase text-[#888888]">Phone Number</label>
                <input type="tel" id="phone" name="phone" required class="bg-transparent border-b border-[#5E1C24] focus:border-primary text-[#F5F2EB] font-body text-base py-3 outline-none transition-colors duration-300 placeholder-[#5E1C24]" placeholder="+91 00000 00000">
            </div>

            <div class="flex flex-col gap-1 relative z-10">
                <label for="message" class="font-label text-[10px] tracking-[0.2em] uppercase text-[#888888]">Message (Optional)</label>
                <textarea id="message" name="message" rows="4" class="bg-transparent border-b border-[#5E1C24] focus:border-primary text-[#F5F2EB] font-body text-base py-3 outline-none transition-colors duration-300 placeholder-[#5E1C24] resize-none" placeholder="How may we assist you today?"></textarea>
            </div>

            <button type="submit" onclick="event.preventDefault(); alert('Your inquiry has been submitted beautifully.');" class="relative z-10 mt-6 bg-on-surface text-surface hover:bg-primary-container hover:text-secondary px-8 py-5 font-label text-xs tracking-[0.2em] uppercase transition-all duration-500 w-full text-center">
                Submit Inquiry
            </button>
        </form>
    </div>
</main>"""

with open('contact.html', 'w', encoding='utf-8') as f:
    f.write(head_nav + contact_main + footer_scripts)

print("Created contact.html")
