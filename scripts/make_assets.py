"""Generates every SVG on the GitHub profile, in a dark and a light variant.

Fonts are the Geist family Avenoric already uses, subset per file and embedded,
so the graphics look identical on every device. Usage:
    python make_assets.py <geist fonts dir> <out dir>
"""
import base64, html, io, math, os, re, sys
from fontTools import subset
from fontTools.ttLib import TTFont

FONTS, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

FONT_FILES = {
    'G': os.path.join(FONTS, 'geist-sans', 'Geist-Regular.ttf'),
    'GS': os.path.join(FONTS, 'geist-sans', 'Geist-SemiBold.ttf'),
    'GM': os.path.join(FONTS, 'geist-mono', 'GeistMono-Regular.ttf'),
}
PIXEL = os.path.join(FONTS, 'geist-pixel', 'GeistPixel-Grid.woff2')

THEMES = {
    'dark': dict(bg='#0B0B0B', panel='#111111', ink='#F0EDE6', muted='#8F8A80', faint='#F0EDE6',
                 border='#262421', accent='#E8650F', live='#3FB950'),
    'light': dict(bg='#F6F3EC', panel='#FBF9F4', ink='#141312', muted='#6B665E', faint='#141312',
                  border='#DDD7CC', accent='#C9540A', live='#1A7F37'),
}

SANS, SEMI, MONO, PIX = "font-family:G,sans-serif", "font-family:GS,sans-serif", "font-family:GM,monospace", "font-family:GP,GM,monospace"

BASE_CSS = """
.f{opacity:0;animation:up .9s cubic-bezier(.2,.7,.2,1) forwards}
@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes pulse{0%{transform:scale(1);opacity:.9}100%{transform:scale(3.2);opacity:0}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes rip{0%{transform:scale(.04);opacity:0}12%{opacity:.55}100%{transform:scale(1);opacity:0}}
@keyframes dash{to{stroke-dashoffset:0}}
@keyframes flow{to{stroke-dashoffset:-24}}
@keyframes glow{0%,100%{fill:var(--m)}40%,60%{fill:var(--a)}}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.4s ease-out infinite}
.blink{animation:blink 1.1s step-end infinite}
.flow{stroke-dasharray:4 8;animation:flow 1.2s linear infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.f{opacity:1}.bill,.bar{transform:none!important}.prog,.draw{stroke-dashoffset:0!important}}
"""


def font_face(name, data, fmt):
    return f"@font-face{{font-family:{name};src:url(data:font/{fmt};base64,{data}) format('{fmt}')}}"


def subset_font(path, text):
    f = TTFont(path)
    opts = subset.Options()
    opts.layout_features = ['kern', 'liga', 'calt']
    s = subset.Subsetter(opts)
    s.populate(text=text)
    s.subset(f)
    f.flavor = 'woff'
    buf = io.BytesIO()
    f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def svg(name, w, h, body, t, label, css=''):
    text = ''.join(html.unescape(m) for m in re.findall(r'>([^<]+)<', body)) + '0123456789 '
    faces = []
    for fam, path in FONT_FILES.items():
        if f'font-family:{fam},' in body:
            faces.append(font_face(fam, subset_font(path, text), 'woff'))
    if 'font-family:GP' in body:
        with open(PIXEL, 'rb') as fh:
            faces.append(font_face('GP', base64.b64encode(fh.read()).decode(), 'woff2'))
    style = '\n'.join(faces) + BASE_CSS + f":root{{--a:{t['accent']};--m:{t['muted']}}}" + css
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
           f'role="img" aria-label="{html.escape(label)}">\n<style>{style}</style>\n'
           f'<defs><clipPath id="clip"><rect width="{w}" height="{h}" rx="20"/></clipPath>'
           f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
           f'<circle cx="1" cy="1" r="1" fill="{t["faint"]}" fill-opacity=".07"/></pattern></defs>\n'
           f'<g clip-path="url(#clip)">\n{body}\n</g>\n'
           f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="20" fill="none" stroke="{t["border"]}"/>\n</svg>\n')
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as fh:
        fh.write(doc)
    return len(doc)


def tx(x, y, s, style, size, fill, extra='', delay=None, anchor='start', ls=None):
    cls = ' class="f"' if delay is not None else ''
    if delay is not None:
        style = f'{style};animation-delay:{delay}s'
    lsp = f' letter-spacing="{ls}"' if ls is not None else ''
    return (f'<text x="{x}" y="{y}" style="{style}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}"{lsp}{cls}{extra}>{html.escape(s)}</text>')


def live_dot(x, y, t):
    return (f'<circle cx="{x}" cy="{y}" r="5" fill="{t["live"]}" class="pulse"/>'
            f'<circle cx="{x}" cy="{y}" r="5" fill="{t["live"]}"/>')


# ───────────────────────── hero ─────────────────────────
def hero(t, k):
    W, H, cx, cy = 1280, 440, 1070, 250
    b = [f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>']
    for i in range(24):
        r = 20 + i * 18
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["faint"]}" '
                 f'stroke-opacity="{max(.05, .42 - i * .016):.3f}"/>')
    for d in (0, -3, -6):
        b.append(f'<circle class="rp" style="animation-delay:{d}s" cx="{cx}" cy="{cy}" r="440" fill="none" '
                 f'stroke="{t["accent"]}" stroke-width="1.4" vector-effect="non-scaling-stroke"/>')
    r = 20 + 10 * 18
    a0, a1 = math.radians(-160), math.radians(-70)
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    b.append(f'<g class="orbit"><path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}" fill="none" '
             f'stroke="{t["accent"]}" stroke-width="3" stroke-linecap="round"/>'
             f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="6" fill="{t["accent"]}"/></g>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{t["accent"]}"/>'
             f'<circle cx="{cx}" cy="{cy}" r="7" fill="{t["accent"]}" class="pulse"/>')
    b.append(f'<rect x="0" y="0" width="700" height="{H}" fill="{t["bg"]}" fill-opacity=".55"/>')
    b.append(tx(74, 98, 'FOUNDER · AVENORIC', PIX, 22, t['accent'], delay=.05, ls=3))
    b.append(tx(68, 214, 'Kanak Raj', SEMI, 118, t['ink'], delay=.15, ls=-5))
    b.append(f'<rect x="74" y="246" width="84" height="3" fill="{t["accent"]}" class="f" style="animation-delay:.3s"/>')
    b.append(tx(74, 300, 'I build AI products people actually use.', SANS, 32, t['ink'], delay=.4, ls=-.5))
    term = '~/avenoric $ shipping explainmate + plintrix'
    b.append(f'<g class="f" style="animation-delay:.6s">{tx(74, 362, term, MONO, 19, t["muted"])}'
             f'<rect x="{74 + len(term) * 11.4 + 6:.0f}" y="346" width="11" height="21" fill="{t["accent"]}" class="blink"/></g>')
    b.append(tx(W - 44, H - 36, 'EST. 2025', PIX, 16, t['muted'], anchor='end', ls=2, delay=.8))
    css = (".rp{transform-box:fill-box;transform-origin:center;opacity:0;animation:rip 9s linear infinite}"
           f".orbit{{transform-origin:{cx}px {cy}px;animation:spin 48s linear infinite}}")
    return svg(f'hero-{k}.svg', W, H, '\n'.join(b), t,
               'Kanak Raj. Founder, Avenoric. I build AI products people actually use.', css)


# ───────────────────────── product cards ─────────────────────────
def card_shell(t, label, name, lines, footer_left, domain):
    W, H = 620, 320
    b = [f'<rect width="{W}" height="{H}" fill="{t["panel"]}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>']
    b.append(tx(34, 56, label, PIX, 16, t['accent'], ls=2, delay=0))
    b.append(tx(32, 126, name, SEMI, 50, t['ink'], ls=-2, delay=.1))
    for i, ln in enumerate(lines):
        b.append(tx(34, 172 + i * 28, ln, SANS, 19, t['muted'], delay=.2 + i * .05))
    b.append(f'<line x1="34" y1="262" x2="{W - 34}" y2="262" stroke="{t["border"]}"/>')
    b.append(live_dot(42, 290, t))
    b.append(tx(58, 296, footer_left, MONO, 16, t['ink']))
    b.append(tx(W - 34, 296, domain + ' ↗', MONO, 16, t['accent'], anchor='end'))
    return W, H, b


def explainmate(t, k):
    W, H, b = card_shell(t, '01 · FLAGSHIP', 'ExplainMate', [
        "An AI study partner. It links a student's",
        'explanations, quizzes, notes, mistakes and',
        'exam prep into one tutor that adapts to them.'],
        'LIVE  ·  20,000 USERS', 'explainmate.tech')
    cx, cy, R = 528, 92, 50
    names = 5
    pts = [(cx + R * math.cos(math.radians(-90 + i * 72)), cy + R * math.sin(math.radians(-90 + i * 72))) for i in range(names)]
    for i, (x, y) in enumerate(pts):
        nx, ny = pts[(i + 1) % names]
        b.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{t["border"]}"/>')
        b.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{t["muted"]}" stroke-opacity=".5" class="flow"/>')
    for i, (x, y) in enumerate(pts):
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" class="sat" style="animation-delay:{i * .6}s"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{t["accent"]}"/>')
    css = ".sat{fill:var(--m);animation:glow 3s ease-in-out infinite}"
    return svg(f'card-explainmate-{k}.svg', W, H, '\n'.join(b), t,
               'ExplainMate: an AI study partner. Live, 20,000 users. explainmate.tech', css)


def plintrix(t, k):
    W, H, b = card_shell(t, '02 · LEARN AI', 'Plintrix', [
        'The fun way to learn AI: five-minute, game-like',
        'lessons with a tutor that cites its sources. A',
        'second model checks every question first.'],
        'LIVE', 'plintrix.tech')
    path = [(452, 128), (488, 96), (524, 118), (560, 82), (588, 50)]
    d = 'M' + ' L'.join(f'{x} {y}' for x, y in path)
    b.append(f'<path d="{d}" fill="none" stroke="{t["border"]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(f'<path d="{d}" fill="none" stroke="{t["accent"]}" stroke-width="3" stroke-linecap="round" '
             f'stroke-linejoin="round" pathLength="100" class="prog"/>')
    for i, (x, y) in enumerate(path):
        last = i == len(path) - 1
        b.append(f'<circle cx="{x}" cy="{y}" r="{8 if last else 6}" fill="{t["accent"] if last else t["ink"]}"/>')
    lx, ly = path[-1]
    b.append(f'<circle cx="{lx}" cy="{ly}" r="8" fill="{t["accent"]}" class="pulse"/>')
    css = ".prog{stroke-dasharray:100;stroke-dashoffset:100;animation:dash 2.4s .4s cubic-bezier(.4,0,.2,1) forwards}"
    return svg(f'card-plintrix-{k}.svg', W, H, '\n'.join(b), t,
               'Plintrix: the fun way to learn AI. Live. plintrix.tech', css)


# ───────────────────────── open-source builds ─────────────────────────
def box(x, y, w, h, label, t, accent=False, sub=None):
    stroke = t['accent'] if accent else t['border']
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{t["bg"]}" stroke="{stroke}" stroke-width="{1.6 if accent else 1}"/>',
           tx(x + w / 2, y + h / 2 + (0 if sub else 6), label, MONO, 16, t['accent'] if accent else t['ink'], anchor='middle')]
    if sub:
        out.append(tx(x + w / 2, y + h / 2 + 22, sub, MONO, 12, t['muted'], anchor='middle'))
    return '\n'.join(out)


def arrow(x1, y1, x2, y2, t):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["muted"]}" stroke-width="1.5" class="flow"/>'
            f'<circle cx="{x2}" cy="{y2}" r="3" fill="{t["muted"]}"/>')


def build_shell(t, label, name, tags, lines):
    W, H = 1280, 300
    b = [f'<rect width="{W}" height="{H}" fill="{t["panel"]}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>']
    b.append(tx(40, 58, label, PIX, 16, t['accent'], ls=2, delay=0))
    b.append(tx(38, 116, name, SEMI, 44, t['ink'], ls=-1.5, delay=.1))
    x = 40
    for tag in tags:
        w = len(tag) * 9.6 + 22
        b.append(f'<g class="f" style="animation-delay:.2s"><rect x="{x}" y="140" width="{w:.0f}" height="28" rx="14" '
                 f'fill="none" stroke="{t["border"]}"/>{tx(x + w / 2, 159, tag, MONO, 14, t["muted"], anchor="middle")}</g>')
        x += w + 8
    for i, ln in enumerate(lines):
        b.append(tx(40, 212 + i * 28, ln, SANS, 19, t['muted'], delay=.3 + i * .05))
    b.append(f'<line x1="640" y1="40" x2="640" y2="{H - 40}" stroke="{t["border"]}"/>')
    return W, H, b


def fixit(t, k):
    W, H, b = build_shell(t, 'OPEN SOURCE · FINE-TUNING', 'FixIT SLM', ['PyTorch', 'LoRA', 'Ollama', 'Next.js'], [
        "Microsoft's phi-3, fine-tuned with LoRA into a hardware",
        'and software troubleshooter. Runs fully offline.'])
    b.append(box(680, 70, 120, 56, 'phi-3', t, sub='base model'))
    b.append(arrow(800, 98, 846, 98, t))
    b.append(box(850, 70, 150, 56, '+ LoRA', t, sub='own dataset'))
    b.append(arrow(1000, 98, 1046, 98, t))
    b.append(box(1050, 70, 190, 56, 'FixIT · local', t, accent=True, sub='via Ollama, no cloud'))
    steps = ["what's wrong", 'why', 'analogy', 'fix', 'verify']
    b.append(tx(680, 172, 'EVERY ANSWER FOLLOWS:', PIX, 13, t['muted'], ls=1.5))
    x = 680
    for i, s in enumerate(steps):
        w = len(s) * 9 + 26
        b.append(f'<rect x="{x}" y="190" width="{w:.0f}" height="34" rx="17" class="step" style="animation-delay:{i * .5}s" '
                 f'stroke="{t["border"]}"/>{tx(x + w / 2, 212, s, MONO, 14, t["ink"], anchor="middle")}')
        if i < len(steps) - 1:
            b.append(tx(x + w + 7, 212, '→', MONO, 14, t['muted']))
        x += w + 24
    css = f".step{{fill:{t['bg']};animation:stp 2.5s ease-in-out infinite}}@keyframes stp{{0%,100%{{stroke:{t['border']}}}20%,40%{{stroke:{t['accent']}}}}}"
    return svg(f'build-fixit-{k}.svg', W, H, '\n'.join(b), t,
               'FixIT SLM: phi-3 fine-tuned with LoRA into an offline troubleshooter.', css)


def flux(t, k):
    W, H, b = build_shell(t, 'GITLAB AI HACKATHON · MULTI-AGENT', 'FluxSentinel AI', ['Node.js', 'Claude', 'Gemini', 'OSV'], [
        'Reviews GitLab merge requests. Claude and Gemini audit each',
        'diff on their own; a judge ranks findings by agreement.'])
    b.append(box(676, 122, 120, 56, 'MR diff', t, sub='webhook'))
    b.append(arrow(796, 140, 846, 92, t))
    b.append(arrow(796, 160, 846, 208, t))
    b.append(box(850, 64, 130, 56, 'Claude', t))
    b.append(box(850, 180, 130, 56, 'Gemini', t))
    b.append(arrow(980, 92, 1026, 140, t))
    b.append(arrow(980, 208, 1026, 160, t))
    b.append(f'<g transform="translate(1066 150)"><rect x="-36" y="-36" width="72" height="72" rx="8" transform="rotate(45)" '
             f'fill="{t["bg"]}" stroke="{t["accent"]}" stroke-width="1.6"/>{tx(0, 6, "judge", MONO, 14, t["accent"], anchor="middle")}</g>')
    b.append(arrow(1118, 150, 1146, 150, t))
    b.append(box(1150, 122, 92, 56, 'risk', t, sub='0–100'))
    b.append(tx(1066, 262, '+ regex scan · OSV dependency check', MONO, 12, t['muted'], anchor='middle'))
    return svg(f'build-flux-{k}.svg', W, H, '\n'.join(b), t,
               'FluxSentinel AI: Claude and Gemini audit merge requests independently; a judge pass ranks findings by agreement and scores risk.')


def stump(t, k):
    W, H, b = build_shell(t, 'GDG BUILD WITH AI · PROBABILITY', 'Stump.ai', ['TypeScript', 'Gemini', 'Bayes', 'entropy'], [
        'Akinator for IPL cricketers. Each question is the one with',
        'the most expected information, so belief sharpens fast.'])
    rnd = [0.62, 0.35, 0.8, 0.5, 0.28, 0.7, 0.44, 0.9, 0.33, 0.58]
    n, bw, gap = 10, 4, 1.6
    for q in range(8):
        ox = 680 + q * 70
        sharp = q / 7
        heights = []
        for j in range(n):
            base = rnd[j] * (1 - sharp) * 70 + 6
            if j == 6:
                base = 20 + sharp * 120
            heights.append(base)
        for j, hgt in enumerate(heights):
            x = ox + j * (bw + gap)
            fill = t['accent'] if (j == 6 and q >= 5) else t['muted']
            b.append(f'<rect x="{x}" y="{226 - hgt:.1f}" width="{bw}" height="{hgt:.1f}" rx="1.5" fill="{fill}" '
                     f'fill-opacity="{1 if fill == t["accent"] else .55}" class="bar" style="animation-delay:{q * .12 + j * .01:.2f}s"/>')
        b.append(tx(ox + 27, 252, f'Q{q + 1}', MONO, 13, t['muted'], anchor='middle'))
    b.append(tx(680, 70, 'BELIEF OVER PLAYERS, QUESTION BY QUESTION', PIX, 13, t['muted'], ls=1.5))
    css = ".bar{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .7s cubic-bezier(.2,.7,.2,1) forwards}@keyframes grow{to{transform:scaleY(1)}}"
    return svg(f'build-stump-{k}.svg', W, H, '\n'.join(b), t,
               'Stump.ai: guesses an IPL cricketer by asking the most informative question each turn.', css)


# ───────────────────────── journey ─────────────────────────
def journey(t, k):
    W, H, y = 1280, 380, 190
    stops = [('BEFORE', ['Arduino robots,', 'Roblox games']),
             ('OCT 2025', ['Starts building', 'as K&D Labs']),
             ('NOV 2025', ['ExplainMate', 'goes live']),
             ('JAN 2026', ['K&D Labs becomes', 'Avenoric']),
             ('JUN 2026', ['Dainik Jagran,', 'Startup India']),
             ('SEP 2026', ['1M+ reach, 18k', 'signups in 3 weeks']),
             ('NOW', ['20,000 users,', '2 products live'])]
    b = [f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>']
    x0, x1 = 90, W - 90
    b.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{t["border"]}" stroke-width="2"/>')
    b.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{t["accent"]}" stroke-width="2" pathLength="100" class="draw"/>')
    step = (x1 - x0) / (len(stops) - 1)
    for i, (date, lines) in enumerate(stops):
        x = x0 + i * step
        d = .25 + i * .32
        last = i == len(stops) - 1
        up = i % 2 == 0
        stem_end = y - 34 if up else y + 34
        g = [f'<line x1="{x}" y1="{y}" x2="{x}" y2="{stem_end}" stroke="{t["border"]}"/>',
             f'<circle cx="{x}" cy="{y}" r="{9 if last else 6}" fill="{t["accent"] if last else t["bg"]}" stroke="{t["accent"]}" stroke-width="2"/>']
        if up:
            g.append(tx(x, y - 108, date, PIX, 15, t['accent'] if last else t['muted'], anchor='middle', ls=1.5))
            g += [tx(x, y - 80 + j * 24, ln, SANS, 18, t['ink'], anchor='middle') for j, ln in enumerate(lines)]
        else:
            g.append(tx(x, y + 64, date, PIX, 15, t['accent'] if last else t['muted'], anchor='middle', ls=1.5))
            g += [tx(x, y + 92 + j * 24, ln, SANS, 18, t['ink'], anchor='middle') for j, ln in enumerate(lines)]
        b.append(f'<g class="f" style="animation-delay:{d:.2f}s">' + ''.join(g) + '</g>')
        if last:
            b.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{t["accent"]}" class="pulse"/>')
    css = ".draw{stroke-dasharray:100;stroke-dashoffset:100;animation:dash 2.6s cubic-bezier(.4,0,.2,1) forwards}"
    return svg(f'journey-{k}.svg', W, H, '\n'.join(b), t,
               'Journey: Arduino robots and Roblox games, K&D Labs in Oct 2025, ExplainMate live Nov 2025, '
               'renamed Avenoric Jan 2026, press Jun 2026, 18k signups Sep 2026, 20,000 users now.', css)


# ───────────────────────── production ─────────────────────────
def production(t, k):
    W, H = 1280, 340
    b = [f'<rect width="{W}" height="{H}" fill="{t["panel"]}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>']
    b.append(tx(40, 58, 'NOTE 01 · GROWTH IS A LOAD TEST', PIX, 15, t['accent'], ls=2, delay=0))
    b.append(tx(36, 168, '18,000', SEMI, 104, t['ink'], ls=-4, delay=.1))
    b.append(tx(40, 214, 'signups in about three weeks, after one reel', SANS, 20, t['muted'], delay=.2))
    b.append(tx(40, 242, 'reached more than a million people.', SANS, 20, t['muted'], delay=.25))
    b.append(f'<line x1="640" y1="40" x2="640" y2="{H - 40}" stroke="{t["border"]}"/>')
    b.append(tx(680, 58, 'NOTE 02 · COST IS PART OF THE PRODUCT', PIX, 15, t['accent'], ls=2, delay=.1))
    b.append(tx(680, 110, 'MONTHLY CLOUD BILL', MONO, 14, t['muted'], ls=1))
    full = 400
    small = max(4, full * 350 / 21800)
    b.append(tx(680, 146, 'usual', MONO, 14, t['muted']))
    b.append(f'<rect x="760" y="132" width="{small:.1f}" height="18" rx="3" fill="{t["muted"]}"/>')
    b.append(tx(760 + small + 10, 147, '~₹350', MONO, 15, t['ink']))
    b.append(tx(680, 196, 'spike', MONO, 14, t['muted']))
    b.append(f'<rect x="760" y="180" width="{full}" height="18" rx="3" fill="{t["accent"]}" class="bill"/>')
    b.append(tx(760 + full + 12, 196, '₹21,800', MONO, 15, t['accent'], delay=1.8))
    b.append(tx(680, 266, '~62× in one month. Since then I watch cost per', SANS, 20, t['muted'], delay=.4))
    b.append(tx(680, 294, 'user the way I watch retention.', SANS, 20, t['muted'], delay=.45))
    css = ".bill{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grw 1.6s .5s cubic-bezier(.2,.7,.2,1) forwards}@keyframes grw{to{transform:scaleX(1)}}"
    return svg(f'production-{k}.svg', W, H, '\n'.join(b), t,
               '18,000 signups in about three weeks after a reel reached more than a million people. '
               'The monthly cloud bill went from about ₹350 to ₹21,800.', css)


# ───────────────────────── footer ─────────────────────────
def footer(t, k):
    W, H = 1280, 150
    b = [f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>']
    b.append(tx(W / 2, 82, 'BUILD EARLY. FAIL FAST. LEARN FASTER.', PIX, 26, t['ink'], anchor='middle', ls=4, delay=0))
    b.append(f'<rect x="{W / 2 - 30}" y="104" width="60" height="3" fill="{t["accent"]}" class="f" style="animation-delay:.3s"/>')
    return svg(f'footer-{k}.svg', W, H, '\n'.join(b), t, 'Build early. Fail fast. Learn faster.')


for k, t in THEMES.items():
    for fn in (hero, explainmate, plintrix, fixit, flux, stump, journey, production, footer):
        size = fn(t, k)
        print(f'{fn.__name__:12} {k:5} {size / 1024:6.1f} KB')
