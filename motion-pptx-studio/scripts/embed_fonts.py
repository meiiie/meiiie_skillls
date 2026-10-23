#!/usr/bin/env python3
"""Embed static TTF fonts in a .pptx the way PowerPoint does (ppt/fonts/fontN.fntdata = EOT wrapper).

  python3 embed_fonts.py DECK.pptx --font 'Family=Regular.ttf[,Bold.ttf[,Italic.ttf[,BoldItalic.ttf]]]' ... [--out OUT.pptx]
Use STATIC faces (not variable fonts) whose OS/2 fsType allows embedding (OFL fonts: 0 = installable).
Family must equal the typeface your text runs use. Verify once in real PowerPoint (File > Options > Save
shows the font as embedded); LibreOffice ignores embedded fonts, so its renders prove nothing either way.
"""
import argparse, re, struct, zipfile, shutil, tempfile, os
from fontTools.ttLib import TTFont

def eot(path):
    data = open(path, 'rb').read(); f = TTFont(path)
    os2, head, name = f['OS/2'], f['head'], f['name']
    if os2.fsType & 0x0002 and not os2.fsType & 0x000C:
        raise SystemExit(f'{path}: fsType {os2.fsType} forbids embedding')
    s = lambda i: (name.getDebugName(i) or '').encode('utf-16-le')
    pan = os2.panose
    panose = bytes([pan.bFamilyType, pan.bSerifStyle, pan.bWeight, pan.bProportion, pan.bContrast,
                    pan.bStrokeVariation, pan.bArmStyle, pan.bLetterForm, pan.bMidline, pan.bXHeight])
    italic = 1 if os2.fsSelection & 1 else 0
    body = struct.pack('<10sBBIHH', panose, 1, italic, os2.usWeightClass, os2.fsType, 0x504C)
    body += struct.pack('<4I', os2.ulUnicodeRange1, os2.ulUnicodeRange2, os2.ulUnicodeRange3, os2.ulUnicodeRange4)
    body += struct.pack('<2I', getattr(os2, 'ulCodePageRange1', 0), getattr(os2, 'ulCodePageRange2', 0))
    body += struct.pack('<I4I', head.checkSumAdjustment, 0, 0, 0, 0)
    for i in (1, 2, 5, 4):
        body += struct.pack('<HH', 0, len(s(i))) + s(i)
    body += struct.pack('<HH', 0, 0)                      # Padding5, RootStringSize (v2.1)
    hdr_len = 16 + len(body)
    return struct.pack('<IIII', hdr_len + len(data), len(data), 0x00020001, 0) + body + data

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('deck'); ap.add_argument('--font', action='append', required=True)
    ap.add_argument('--out'); a = ap.parse_args(); out = a.out or a.deck
    z = zipfile.ZipFile(a.deck); files = {n: z.read(n) for n in z.namelist()}; z.close()
    pres = files['ppt/presentation.xml'].decode(); rels = files['ppt/_rels/presentation.xml.rels'].decode()
    ct = files['[Content_Types].xml'].decode()
    if 'Extension="fntdata"' not in ct:
        ct = ct.replace('<Default ', '<Default Extension="fntdata" ContentType="application/x-fontdata"/><Default ', 1)
    nrid = max(int(x) for x in re.findall(r'Id="rId(\d+)"', rels)) + 1
    n = len([k for k in files if k.startswith('ppt/fonts/')]) + 1
    entries = ''
    for spec in a.font:
        fam, paths = spec.split('=', 1)
        e = f'<p:embeddedFont><p:font typeface="{fam}"/>'
        for slot, p in zip(('regular', 'bold', 'italic', 'boldItalic'), paths.split(',')):
            if not p: continue
            files[f'ppt/fonts/font{n}.fntdata'] = eot(p)
            rels = rels.replace('</Relationships>', f'<Relationship Id="rId{nrid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/font" Target="fonts/font{n}.fntdata"/></Relationships>')
            e += f'<p:{slot} r:id="rId{nrid}"/>'; nrid += 1; n += 1
        entries += e + '</p:embeddedFont>'
    if '<p:embeddedFontLst>' in pres:
        pres = pres.replace('</p:embeddedFontLst>', entries + '</p:embeddedFontLst>')
    else:
        pres = re.sub(r'(<p:notesSz[^>]*/>)', r'\1<p:embeddedFontLst>' + entries.replace('\\', '\\\\') + '</p:embeddedFontLst>', pres, count=1)
    pres = re.sub(r'\s(embedTrueTypeFonts|saveSubsetFonts)="[^"]*"', '', pres)
    pres = re.sub(r'<p:presentation\b', '<p:presentation embedTrueTypeFonts="1"', pres, count=1)
    files['ppt/presentation.xml'] = pres.encode(); files['ppt/_rels/presentation.xml.rels'] = rels.encode()
    files['[Content_Types].xml'] = ct.encode()
    tmp = tempfile.mktemp(suffix='.pptx')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as w:
        for k in (['[Content_Types].xml'] + [k for k in files if k != '[Content_Types].xml']): w.writestr(k, files[k])
    shutil.move(tmp, out); print(f'embedded {n-1} faces -> {out}')

if __name__ == '__main__':
    main()
