#!/usr/bin/env python3
"""svgbanner - lightweight animated SVG banners for your README. Zero dependencies."""
import argparse
import random
import sys
from xml.sax.saxutils import escape

# name: (background1, background2, accent1, accent2)
THEMES = {
    "neon": ("#0f0c29", "#302b63", "#00f5d4", "#f15bb5"),
    "sunset": ("#1a0b2e", "#4a1942", "#ff9a3c", "#ff3cac"),
    "ocean": ("#03111f", "#0b3954", "#4cc9f0", "#7ae582"),
    "forest": ("#071a12", "#0f3d2a", "#b8f35c", "#2ee59d"),
    "mono": ("#0d1117", "#1c2128", "#e6edf3", "#8b949e"),
}
FONT = "'JetBrains Mono','Fira Code',Consolas,Menlo,monospace"


def f(n):
    return f"{n:.1f}".rstrip("0").rstrip(".")


def build(text, sub, theme, w, h, seed):
    bg1, bg2, c1, c2 = THEMES[theme]
    rnd = random.Random(seed)
    n = max(len(text), 1)
    size = int(max(16, min(h * 0.28, (w * 0.86) / (n * 0.6))))
    tw = n * size * 0.6
    x0 = (w - tw) / 2
    base = h * 0.5 + size * 0.3
    start = 0.4
    dur = max(1.2, n * 0.09)
    widths = ";".join(f(tw * i / n) for i in range(n + 1))
    xs = ";".join(f(x0 + tw * i / n) for i in range(n + 1))

    dots = []
    for _ in range(16):
        cx, cy = rnd.uniform(10, w - 10), rnd.uniform(14, h * 0.72)
        r, d = rnd.uniform(1, 2.6), rnd.uniform(3, 6)
        col = rnd.choice((c1, c2))
        dots.append(
            f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{col}">'
            f'<animate attributeName="cy" values="{f(cy)};{f(cy - 18)};{f(cy)}" dur="{f(d)}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".1;.7;.1" dur="{f(d)}s" repeatCount="indefinite"/></circle>'
        )

    def wave(y, amp, color, op, d):
        p = (f"M0,{f(y)} Q{f(w / 4)},{f(y - amp)} {f(w / 2)},{f(y)} T{f(w)},{f(y)} "
             f"T{f(w * 1.5)},{f(y)} T{f(w * 2)},{f(y)} V{h} H0Z")
        return (f'<path d="{p}" fill="{color}" opacity="{op}"><animateTransform attributeName="transform" '
                f'type="translate" from="0 0" to="-{w} 0" dur="{d}s" repeatCount="indefinite"/></path>')

    subtitle = ""
    if sub:
        subtitle = (
            f'<text x="{f(w / 2)}" y="{f(base + size * 0.85)}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{f(max(12, size * 0.36))}" fill="{c2}" opacity="0">{escape(sub)}'
            f'<animate attributeName="opacity" from="0" to=".9" begin="{f(start + dur + 0.2)}s" dur=".8s" fill="freeze"/></text>'
        )
    title = escape(text)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">
<title>{title}</title>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient>
<linearGradient id="tx" gradientUnits="userSpaceOnUse" x1="{f(x0)}" y1="0" x2="{f(x0 + tw)}" y2="0"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>
<clipPath id="rc"><rect width="{w}" height="{h}" rx="16"/></clipPath>
<clipPath id="ty"><rect x="{f(x0)}" y="0" width="0" height="{h}"><animate attributeName="width" values="{widths}" begin="{start}s" dur="{f(dur)}s" calcMode="discrete" fill="freeze"/></rect></clipPath>
</defs>
<g clip-path="url(#rc)">
<rect width="{w}" height="{h}" fill="url(#bg)"/>
{chr(10).join(dots)}
{wave(h * 0.9, h * 0.07, c1, ".18", 9)}
{wave(h * 0.94, h * 0.05, c2, ".22", 6)}
<text x="{f(x0)}" y="{f(base)}" font-family="{FONT}" font-size="{size}" font-weight="700" fill="url(#tx)" clip-path="url(#ty)">{title}</text>
<rect x="{f(x0)}" y="{f(base - size * 0.82)}" width="3" height="{f(size * 0.95)}" rx="1.5" fill="{c1}"><animate attributeName="x" values="{xs}" begin="{start}s" dur="{f(dur)}s" calcMode="discrete" fill="freeze"/><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>
{subtitle}
</g>
</svg>
'''


def main():
    ap = argparse.ArgumentParser(prog="svgbanner", description="Make an animated SVG banner for your README.")
    ap.add_argument("text", nargs="?", help="main headline (typed out by the animation)")
    ap.add_argument("-s", "--sub", default="", help="subtitle that fades in")
    ap.add_argument("-t", "--theme", default="neon", choices=sorted(THEMES))
    ap.add_argument("-o", "--out", default="banner.svg")
    ap.add_argument("--width", type=int, default=900)
    ap.add_argument("--height", type=int, default=240)
    ap.add_argument("--seed", type=int, default=7, help="changes the floating particles")
    ap.add_argument("--list-themes", action="store_true")
    a = ap.parse_args()
    if a.list_themes:
        print("\n".join(sorted(THEMES)))
        return 0
    if not a.text:
        ap.error("text is required, e.g. svgbanner.py 'Hello World' -s 'my project'")
    if a.width < 300 or a.height < 120:
        ap.error("--width must be >= 300 and --height >= 120")
    svg = build(a.text, a.sub, a.theme, a.width, a.height, a.seed)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote {a.out} ({len(svg.encode()) / 1024:.1f} KB, theme={a.theme})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
