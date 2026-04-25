const fs = require('fs');

const files = ['d:/vellathur/profile.html', 'd:/vellathur/diamonds.html', 'd:/vellathur/22k_gold.html'];

for (const f of files) {
    try {
        let content = fs.readFileSync(f, 'utf8');
        
        // Clean up old isolated anchor
        content = content.replace(/\s*<a href="home\.html" class="flex items-center flex-shrink-0 h-full">\s*<img src="Asset 3@3x \(1\)\.png"[^>]+>\s*<\/a>/g, '');
        
        // Replace target header span container with flex-row + logo
        const target_header_old = '<a href="home.html" class="flex flex-col items-center justify-center group whitespace-nowrap mt-1 text-center">';
        const target_header_new = `<a href="home.html" class="flex flex-row items-center justify-center group whitespace-nowrap gap-3">
                <img src="Asset 3@3x (1).png" alt="Vellathur Logo" class="h-8 md:h-10 w-auto object-contain filter invert opacity-90 group-hover:opacity-100 transition-opacity" style="filter: invert(1) drop-shadow(0 0 5px rgba(204, 163, 101, 0.2));">
                <div class="flex flex-col items-center justify-center mt-1 text-center">`;
        if (content.indexOf(target_header_new) === -1) {
            content = content.replace(target_header_old, target_header_new);
            content = content.replace(/Gold & Diamonds<\/span>\s*<\/a>/g, 'Gold & Diamonds</span>\n                </div>\n            </a>');
        }
        
        // Clean up old footer logo
        content = content.replace(/\s*<img src="Asset 3@3x \(1\)\.png" alt="Vellathur Logo" class="h-16 md:h-24 w-auto object-contain brightness-0 invert opacity-90">/g, '');
        
        // Only insert if it's not already having the new styling
        const logo_new_style = 'style="filter: invert(1) drop-shadow(0 0 5px rgba(204, 163, 101, 0.1));"';
        if (content.indexOf(logo_new_style) === -1 || (content.indexOf(logo_new_style) === content.lastIndexOf(logo_new_style))) {
            // Footer match
            content = content.replace(/<div class="flex flex-col items-center">\s*<div class="font-noto-serif text-2xl/g, `<div class="flex flex-col items-center">\n        <img src="Asset 3@3x (1).png" alt="Vellathur Logo" class="h-16 md:h-20 w-auto object-contain filter invert opacity-70 mb-4" style="filter: invert(1) drop-shadow(0 0 5px rgba(204, 163, 101, 0.1));">\n        <div class="font-noto-serif text-2xl`);
        }
        
        fs.writeFileSync(f, content, 'utf8');
        console.log(`Updated ${f}`);
    } catch (e) {
        console.error(`Failed on ${f}:`, e);
    }
}
