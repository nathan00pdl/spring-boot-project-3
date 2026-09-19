"""Post-process a Mermaid SVG so it renders the same in any viewer.

1. Edge labels get an opaque background written on the rect itself, and the
   stylesheet rule that draws them at 50% opacity is removed: the arrow never
   shows through its label, whatever the viewer does with CSS.
2. The viewBox grows by PAD on every side, so the white background does not end
   right at the outermost boxes.
Idempotent: a second run changes nothing.
"""
import re, sys, pathlib
PAD = 24
LABEL_FILL = '#ECECFF'
for f in sys.argv[1:]:
    p = pathlib.Path(f); s = p.read_text()
    if 'data-finished="1"' in s:
        print(f'{f}: already finished'); continue
    # 1. opaque edge-label backgrounds
    s = re.sub(r'opacity:0\.5;(background-color:rgba\(232,232,232, 0\.8\);fill:rgba\(232,232,232, 0\.8\);)', r'\1', s)
    def fix(m):
        g = m.group(0)
        return re.sub(r'<rect class="background" style="[^"]*"', f'<rect class="background" style="fill:{LABEL_FILL};opacity:1" fill="{LABEL_FILL}"', g)
    s = re.sub(r'<g class="edgeLabel".*?</g></g></g>', fix, s, flags=re.S)
    # 2. padding
    m = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', s)
    x, y, w, h = map(float, m.groups())
    nx, ny, nw, nh = x - PAD, y - PAD, w + 2 * PAD, h + 2 * PAD
    s = s.replace(m.group(0), f'viewBox="{nx} {ny} {nw} {nh}"', 1)
    s = re.sub(r'max-width: [\d.]+px', f'max-width: {nw}px', s, count=1)
    s = s.replace('<svg id="my-svg"', '<svg data-finished="1" id="my-svg"', 1)
    p.write_text(s)
    labels = len(re.findall(rf'<rect class="background" style="fill:{LABEL_FILL};opacity:1"', s))
    print(f'{f}: {w:.0f}x{h:.0f} -> {nw:.0f}x{nh:.0f}, {labels} edge label(s) made opaque')
