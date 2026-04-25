import glob
for f in glob.glob('*.html'):
    data = open(f, encoding='utf-8').read()
    data = data.replace('<script src="i18n.js"></script>\n', '')
    open(f, 'w', encoding='utf-8').write(data)
