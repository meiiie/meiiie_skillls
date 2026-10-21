"""Post-process a built pptx: drop the theme style reference (<p:style>) from every drawn shape.
python-pptx autoshapes carry effectRef idx=2; LibreOffice (and some PowerPoint themes) then paint the
theme's soft shadow under every hairline of a map, which turns a graticule into grey bands. Our shapes
set fill, line and effects explicitly, so the style reference is never wanted.
  python3 postfix.py deck.pptx"""
import re, sys, zipfile, shutil, os, tempfile
src = sys.argv[1]
tmp = tempfile.mktemp(suffix='.pptx')
n = 0
with zipfile.ZipFile(src) as zi, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
    for it in zi.infolist():
        data = zi.read(it.filename)
        if re.match(r'ppt/slides/slide\d+\.xml$', it.filename):
            s = data.decode('utf8')
            s, k = re.subn(r'<p:style>.*?</p:style>', '', s, flags=re.S)
            n += k
            data = s.encode('utf8')
        zo.writestr(it, data)
shutil.move(tmp, src)
print('removed style refs:', n)
