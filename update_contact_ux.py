import re

with open('contact.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    <script>var submitted=false;</script>
    <iframe name="hidden_iframe" id="hidden_iframe" style="display:none;" onload="if(submitted){alert('Your inquiry has been seamlessly registered. The Vellathur atelier will contact you shortly.'); window.location='home.html';}"></iframe>

    <!-- Contact Form Container -->
    <div class="w-full max-w-2xl px-6 md:px-12">
        <form action="https://docs.google.com/forms/u/0/d/e/1FAIpQLSeDnjttOrIRpT8CEDlHIe9pKeXeHyVlhzhBbj4caF5d5bHO1Q/formResponse" method="POST" target="hidden_iframe" onsubmit="submitted=true;" class="flex flex-col gap-8 bg-surface-variant/40 p-8 md:p-12 border border-[#5E1C24]/50 shadow-2xl relative overflow-hidden group mb-12">"""

replacement = """    <script>
        var submitted = false;
        function handleSuccess() {
            if(submitted) {
                const formBlock = document.getElementById("contact-form-wrapper");
                const successBlock = document.getElementById("success-block");
                
                // Fade out transition
                formBlock.style.opacity = '0';
                formBlock.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    formBlock.style.display = 'none';
                    successBlock.classList.remove("hidden");
                    successBlock.classList.add("flex");
                    
                    // Fade in transition
                    void successBlock.offsetWidth; // reflow
                    successBlock.style.opacity = '1';
                    successBlock.style.transform = 'scale(1)';
                }, 400);
            }
        }
    </script>
    <iframe name="hidden_iframe" id="hidden_iframe" style="display:none;" onload="handleSuccess()"></iframe>

    <!-- Contact Form Container -->
    <div class="w-full max-w-2xl px-6 md:px-12 relative min-h-[400px]">
        <!-- Form Block -->
        <div id="contact-form-wrapper" class="transition-all duration-500 ease-in-out opacity-100 scale-100 origin-top">
            <form action="https://docs.google.com/forms/u/0/d/e/1FAIpQLSeDnjttOrIRpT8CEDlHIe9pKeXeHyVlhzhBbj4caF5d5bHO1Q/formResponse" method="POST" target="hidden_iframe" onsubmit="submitted=true;" class="flex flex-col gap-8 bg-surface-variant/40 p-8 md:p-12 border border-[#5E1C24]/50 shadow-2xl relative overflow-hidden group mb-12">"""

target_end_form = """            <button type="submit" class="relative z-10 mt-6 bg-on-surface text-surface hover:bg-primary-container hover:text-secondary px-8 py-5 font-label text-xs tracking-[0.2em] uppercase transition-all duration-500 w-full text-center">
                Submit Inquiry
            </button>
        </form>
    </div>"""

replacement_end_form = """            <button type="submit" class="relative z-10 mt-6 bg-on-surface text-surface hover:bg-primary-container hover:text-secondary px-8 py-5 font-label text-xs tracking-[0.2em] uppercase transition-all duration-500 w-full text-center">
                Submit Inquiry
            </button>
        </form>
        </div>
        
        <!-- Success Block -->
        <div id="success-block" class="hidden flex-col items-center justify-center p-12 bg-surface-variant/20 border border-[#5E1C24]/50 shadow-2xl transition-all duration-500 ease-in-out opacity-0 scale-95 origin-top absolute top-0 left-6 right-6 md:left-12 md:right-12">
            <span class="material-symbols-outlined text-[64px] text-primary mb-6">task_alt</span>
            <h2 class="font-noto-serif text-3xl text-on-surface mb-4">Inquiry Received</h2>
            <p class="font-body text-on-surface-variant text-base mb-8 text-center max-w-md">Your message has been seamlessly transmitted. A Vellathur atelier representative will be in touch shortly.</p>
            <a href="home.html" class="bg-on-surface text-surface hover:bg-primary hover:text-white px-8 py-4 font-label text-xs tracking-[0.2em] uppercase transition-all duration-500 flex items-center justify-center gap-3">
                <span class="material-symbols-outlined text-[16px]">arrow_back</span> Return to Home
            </a>
        </div>
    </div>"""

content = content.replace(target, replacement)
content = content.replace(target_end_form, replacement_end_form)

with open('contact.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated contact UX successfully')
