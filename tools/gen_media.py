"""Genera los diagramas del README y de las diapositivas."""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "media"
os.makedirs(OUT, exist_ok=True)
W, H, S = 1600, 900, 2

F_DIR = "/usr/share/fonts/opentype/inter/"
F = {"black": F_DIR + "InterDisplay-Black.otf", "bold": F_DIR + "Inter-Bold.otf",
     "semi": F_DIR + "Inter-SemiBold.otf", "reg": F_DIR + "Inter-Regular.otf",
     "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
     "monor": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"}
_fc = {}
def font(k, sz):
    if (k, sz) not in _fc: _fc[(k, sz)] = ImageFont.truetype(F[k], int(sz * S))
    return _fc[(k, sz)]

BG = (246, 249, 255); INK = (11, 37, 69); MUTED = (84, 104, 133); LINE = (196, 208, 228)
BLUE = (30, 94, 255); CARD = (255, 255, 255)
AMBER = (245, 158, 11); AMBER_BG = (254, 243, 199); GREEN = (16, 163, 107); GREEN_BG = (220, 252, 231)
RED = (225, 45, 57); RED_BG = (254, 226, 226)
SET = [(37, 99, 235), (13, 148, 136), (234, 88, 12), (124, 58, 237), (202, 138, 4), (219, 39, 119)]

class Canvas:
    def __init__(self):
        self.im = Image.new("RGB", (W * S, H * S), BG); self.d = ImageDraw.Draw(self.im)
    def text(self, xy, s, k, sz, fill=INK, anchor="la"):
        self.d.text((xy[0] * S, xy[1] * S), s, font=font(k, sz), fill=fill, anchor=anchor)
    def tw(self, s, k, sz): return font(k, sz).getlength(s) / S
    def rect(self, b, r=0, fill=None, outline=None, w=1):
        self.d.rounded_rectangle([b[0] * S, b[1] * S, b[2] * S, b[3] * S], radius=r * S, fill=fill, outline=outline, width=int(w * S))
    def circle(self, c, r, fill=None, outline=None, w=1):
        self.d.ellipse([(c[0] - r) * S, (c[1] - r) * S, (c[0] + r) * S, (c[1] + r) * S], fill=fill, outline=outline, width=int(w * S))
    def line(self, a, b, w, fill, dash=None):
        if not dash:
            self.d.line([a[0] * S, a[1] * S, b[0] * S, b[1] * S], fill=fill, width=int(w * S)); return
        L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; t = 0
        while t < L:
            e = min(t + dash, L)
            self.d.line([(a[0] + ux * t) * S, (a[1] + uy * t) * S, (a[0] + ux * e) * S, (a[1] + uy * e) * S], fill=fill, width=int(w * S)); t += dash * 2
    def arrow(self, a, b, r1, r2, w=4, fill=MUTED, dash=None, head=16):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        s = (a[0] + ux * r1, a[1] + uy * r1); e = (b[0] - ux * r2, b[1] - uy * r2)
        base = (e[0] - ux * head, e[1] - uy * head); self.line(s, base, w, fill, dash)
        px, py = -uy, ux
        self.d.polygon([e[0] * S, e[1] * S, (base[0] + px * head * .55) * S, (base[1] + py * head * .55) * S,
                        (base[0] - px * head * .55) * S, (base[1] - py * head * .55) * S], fill=fill)
    def save(self, name):
        self.im.resize((W, H), Image.LANCZOS).save(os.path.join(OUT, name), optimize=True); print("ok", name)

def header(c, paso, titulo, sub, color=BLUE):
    pw = c.tw(paso, "bold", 22) + 40
    c.rect((80, 64, 80 + pw, 108), 22, fill=color); c.text((80 + pw / 2, 86), paso, "bold", 22, (255, 255, 255), "mm")
    c.text((80 + pw + 24, 86), titulo, "mono", 40, INK, "lm")
    c.text((80, 150), sub, "reg", 28, MUTED, "lm")

def node(c, p, label, col, r=46, ring=None):
    if ring: c.circle(p, r + 13, outline=ring, w=7)
    c.circle((p[0] + 4, p[1] + 6), r, fill=(214, 224, 242))
    c.circle(p, r, fill=col, outline=(255, 255, 255), w=4)
    c.text(p, label, "black", 40, (255, 255, 255), "mm")

def self_loop(c, p, r, col):
    cx, cy, rr = p[0] + r * 0.62, p[1] - r * 0.92, r * 0.42
    c.d.arc([(cx - rr) * S, (cy - rr) * S, (cx + rr) * S, (cy + rr) * S], start=150, end=430, fill=col, width=int(3.5 * S))
    a = math.radians(70); ex, ey = cx + rr * math.cos(a), cy + rr * math.sin(a)
    c.d.polygon([ex * S, (ey + 7) * S, (ex - 9) * S, (ey - 6) * S, (ex + 8) * S, (ey - 8) * S], fill=col)

def root(par, i):
    while par[i] != i: i = par[i]
    return i

def layout(par, x0, x1, y0, dy):
    n = len(par); ch = {i: [] for i in range(n)}
    for i in range(n):
        if par[i] != i: ch[par[i]].append(i)
    roots = [i for i in range(n) if par[i] == i]
    def wd(i): return max(1, sum(wd(k) for k in ch[i]))
    tot = sum(wd(r) for r in roots); unit = min(210, (x1 - x0) / tot); off = x0 + ((x1 - x0) - tot * unit) / 2; pos = {}
    def place(i, l, dep):
        pos[i] = (off + (l + wd(i) / 2) * unit, y0 + dep * dy); k0 = l
        for k in ch[i]: place(k, k0, dep + 1); k0 += wd(k)
    k0 = 0
    for r in roots: place(r, k0, 0); k0 += wd(r)
    return pos

def arrays(c, par, rk, changed=(), y=640, conj=None):
    cw, ch = 104, 62; x0 = 230
    c.text((x0 - 24, y + ch * 0.5), "i", "semi", 26, MUTED, "rm")
    c.text((x0 - 24, y + ch * 1.5 + 10), "padre", "semi", 26, INK, "rm")
    c.text((x0 - 24, y + ch * 2.5 + 20), "rango", "semi", 26, MUTED, "rm")
    for i in range(len(par)):
        x = x0 + i * (cw + 8)
        c.text((x + cw / 2, y + ch * 0.5), str(i), "monor", 26, MUTED, "mm")
        for row, val, yy, base_fill, txtc in ((0, par[i], y + ch + 10, CARD, INK), (1, rk[i], y + ch * 2 + 20, (238, 243, 251), MUTED)):
            hot = (row, i) in changed
            c.rect((x, yy, x + cw, yy + ch), 12, fill=AMBER_BG if hot else base_fill, outline=AMBER if hot else LINE, w=3 if hot else 1.5)
            c.text((x + cw / 2, yy + ch / 2), str(val), "mono" if hot or row == 0 else "monor", 32, (146, 64, 14) if hot else txtc, "mm")
    if conj is not None:
        bx = x0 + 6 * (cw + 8) + 60
        c.rect((bx, y + ch + 10, bx + 330, y + ch * 3 + 20), 18, fill=(232, 240, 255), outline=(189, 208, 250), w=2)
        c.text((bx + 165, y + ch * 1.55 + 18), "conjuntos", "semi", 26, MUTED, "mm")
        c.text((bx + 165, y + ch * 2.45 + 18), str(conj), "black", 64, BLUE, "mm")

def uf_step(name, paso, titulo, sub, par, rk, changed=(), conj=None, rings=None, ghost=None, hot_edge=None, badge=None, color=BLUE):
    c = Canvas(); header(c, paso, titulo, sub, color)
    pos = layout(par, 120, 1480, 280, 120); rings = rings or {}
    if ghost:
        a, b = ghost; c.arrow(pos[a], pos[b], 50, 52, 4, (176, 190, 214), dash=10)
    for i in range(len(par)):
        if par[i] != i:
            hot = hot_edge == (i, par[i])
            c.arrow(pos[i], pos[par[i]], 50, 52, 6 if hot else 4.5, AMBER if hot else (70, 92, 128))
    for i in range(len(par)):
        if par[i] == i: self_loop(c, pos[i], 46, (120, 140, 175))
        node(c, pos[i], str(i), SET[root(par, i)], ring=rings.get(i))
    arrays(c, par, rk, changed, conj=conj)
    if badge:
        txt, fg, bg = badge; bw = c.tw(txt, "bold", 30) + 56
        c.rect((1520 - bw, 64, 1520, 116), 26, fill=bg); c.text((1520 - bw / 2, 90), txt, "bold", 30, fg, "mm")
    c.save(name)

# ---------- Union-Find: la demo del equipo ----------
uf_step("uf_paso0.png", "Paso 0", "UnionFind(6)", "Cada elemento es su propio padre: seis conjuntos de un elemento.",
        [0, 1, 2, 3, 4, 5], [0] * 6, conj=6)
uf_step("uf_paso1.png", "Paso 1", "union(0, 1)", "Raíces distintas y rangos iguales: 1 cuelga de 0 y rango[0] sube a 1.",
        [0, 0, 2, 3, 4, 5], [1, 0, 0, 0, 0, 0], {(0, 1), (1, 0)}, 5, {0: AMBER, 1: AMBER}, hot_edge=(1, 0))
uf_step("uf_paso2.png", "Paso 2", "union(2, 3)", "El mismo caso del otro lado: 3 cuelga de 2 y rango[2] sube a 1.",
        [0, 0, 2, 2, 4, 5], [1, 0, 1, 0, 0, 0], {(0, 3), (1, 2)}, 4, {2: AMBER, 3: AMBER}, hot_edge=(3, 2))
uf_step("uf_paso3.png", "Paso 3", "union(1, 3)", "find(1) = 0 y find(3) = 2. Rangos iguales: el árbol de 2 cuelga de 0.",
        [0, 0, 0, 2, 4, 5], [2, 0, 1, 0, 0, 0], {(0, 2), (1, 0)}, 3, {0: AMBER, 2: AMBER}, hot_edge=(2, 0))
uf_step("uf_paso4.png", "Paso 4", "conectados(0, 2)", "find(0) = 0 y find(2) = 0: misma raíz, mismo conjunto.",
        [0, 0, 0, 2, 4, 5], [2, 0, 1, 0, 0, 0], set(), 3, {0: GREEN, 2: GREEN, 5: RED}, badge=("True", GREEN, GREEN_BG), color=GREEN)
uf_step("uf_paso5.png", "Paso 5", "find(3)", "3 estaba a dos saltos (3 → 2 → 0). La compresión lo deja apuntando directo a 0.",
        [0, 0, 0, 0, 4, 5], [2, 0, 1, 0, 0, 0], {(0, 3)}, 3, {3: AMBER, 0: AMBER}, ghost=(3, 2), hot_edge=(3, 0))
uf_step("uf_paso6.png", "Paso 6", "union(0, 2)", "Misma raíz: union() no cambia nada y devuelve False. Esa arista cerraría un ciclo.",
        [0, 0, 0, 0, 4, 5], [2, 0, 1, 0, 0, 0], set(), 3, {0: RED, 2: RED}, badge=("False · ciclo", RED, RED_BG), color=RED)

# ---------- Kruskal ----------
NAMES = "ABCDEF"; P = [(0, 0), (0, 150), (140, 75), (260, 150), (260, 0), (400, 75)]
EDGES = [(0, 2, 2), (2, 4, 3), (0, 1, 4), (3, 4, 4), (1, 2, 5), (4, 5, 6), (1, 3, 10), (3, 5, 11)]
def kstate(k):
    par = list(range(6)); rk = [0] * 6; st = ["p"] * 8; total = 0
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    info = None
    for i in range(k + 1):
        a, b, w = EDGES[i]; ra, rb = find(a), find(b); info = (ra, rb)
        if ra != rb:
            if rk[ra] < rk[rb]: ra, rb = rb, ra
            par[rb] = ra; rk[ra] += rk[ra] == rk[rb]; st[i] = "a"; total += w
        else: st[i] = "r"
    return par, st, total, info

def kgraph(name, k, paso, titulo, sub, color=BLUE):
    c = Canvas(); header(c, paso, titulo, sub, color)
    par, st, total, info = kstate(k); gp = lambda i: (150 + P[i][0] * 2.3, 300 + P[i][1] * 2.75)
    for i, (a, b, w) in enumerate(EDGES):
        A, B = gp(a), gp(b)
        if i == k: c.line(A, B, 24, (253, 230, 170))
        if st[i] == "a": c.line(A, B, 10, GREEN)
        elif st[i] == "r": c.line(A, B, 5, RED, dash=14)
        else: c.line(A, B, 4, (180, 192, 214))
        mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
        c.rect((mx - 26, my - 22, mx + 26, my + 22), 11, fill=CARD, outline=LINE, w=2); c.text((mx, my), str(w), "bold", 26, INK, "mm")
    for i in range(6):
        ring = AMBER if k >= 0 and i in EDGES[k][:2] else None
        node(c, gp(i), NAMES[i], SET[root(par, i)] if k >= 0 else (120, 136, 168), ring=ring)
    x0, y0 = 1180, 250
    c.rect((x0 - 30, y0 - 30, 1530, y0 + 8 * 62 + 10), 24, fill=CARD, outline=LINE, w=2)
    c.text((x0, y0 - 2), "aristas por peso", "semi", 24, MUTED, "lm")
    for i, (a, b, w) in enumerate(EDGES):
        y = y0 + 40 + i * 58; s = st[i]
        if i == k: c.rect((x0 - 14, y - 24, 1514, y + 24), 12, fill=AMBER_BG)
        col = GREEN if s == "a" else RED if s == "r" else INK
        c.text((x0, y), f"{NAMES[a]}–{NAMES[b]}", "mono", 30, col, "lm"); c.text((x0 + 150, y), f"{w:>2}", "monor", 30, MUTED, "lm")
        c.text((1490, y), "✓" if s == "a" else "✗" if s == "r" else "", "bold", 30, col, "rm")
    acc = st.count("a")
    c.text((150, 850), f"árbol: {acc} de 5 aristas  ·  peso {total}", "bold", 30, GREEN if acc == 5 else INK, "lm")
    c.save(name)

kgraph("kruskal_grafo.png", -1, "Kruskal", "6 vértices, 8 aristas", "Meta: conectar todos los vértices con el menor peso total y sin ciclos.")
for k in range(8):
    a, b, w = EDGES[k]; par0 = kstate(k - 1)[0] if k else list(range(6)); ra, rb = root(par0, a), root(par0, b)
    ok = ra != rb
    sub = (f"find({NAMES[a]}) = {NAMES[ra]}, find({NAMES[b]}) = {NAMES[rb]}. " +
           ("Raíces distintas: se acepta y se hace union." if ok else "Misma raíz: cerraría un ciclo, se descarta."))
    kgraph(f"kruskal_paso{k + 1}.png", k, f"Paso {k + 1}", f"arista {NAMES[a]}–{NAMES[b]} ({w})", sub, GREEN if ok else RED)

# ---------- Código con colores ----------
CODE = '''class UnionFind:
    def __init__(self, n):
        self.padre = list(range(n))   # cada uno es su propio conjunto
        self.rango = [0] * n
        self.conjuntos = n

    def find(self, x):
        if self.padre[x] != x:
            self.padre[x] = self.find(self.padre[x])   # compresión
        return self.padre[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                  # ya estaban unidos: ciclo
        if self.rango[ra] < self.rango[rb]:
            ra, rb = rb, ra               # ra es el árbol más alto
        self.padre[rb] = ra
        if self.rango[ra] == self.rango[rb]:
            self.rango[ra] += 1
        self.conjuntos -= 1
        return True'''
KW = {"class", "def", "if", "return", "self", "True", "False"}
def code_img(name):
    c = Canvas(); c.im.paste((15, 23, 42), [0, 0, W * S, H * S])
    c.rect((40, 34, 1560, 866), 26, fill=(22, 32, 56))
    for i, col in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]): c.circle((84 + i * 32, 74), 9, fill=col)
    c.text((800, 74), "union_find.py", "semi", 22, (148, 163, 184), "mm")
    y = 130; lh = 33.5
    for ln in CODE.split("\n"):
        x = 90; code, _, com = ln.partition("#")
        for tok in __import__("re").findall(r"\s+|\w+|[^\w\s]", code):
            col = (226, 232, 240)
            if tok in KW: col = (196, 148, 255)
            elif tok in ("find", "union", "__init__", "UnionFind"): col = (125, 211, 252)
            elif tok.isdigit(): col = (251, 191, 36)
            elif tok in ("padre", "rango", "conjuntos"): col = (134, 239, 172)
            c.text((x, y), tok, "mono", 25, col, "lm"); x += c.tw(tok, "mono", 25)
        if com: c.text((x, y), "#" + com, "monor", 25, (100, 116, 139), "lm")
        y += lh
    c.save(name)
code_img("codigo_union_find.png")

# ---------- Benchmark ----------
def bench(name):
    c = Canvas(); header(c, "Análisis", "n = 20 000", "Peor caso: unir en cadena y luego hacer find() de todos. Escala logarítmica.", (124, 58, 237))
    rows = [("sin optimizaciones", 199_990_000, "7.72 s", RED), ("solo compresión", 39_997, "0.008 s", BLUE),
            ("solo unión por rango", 39_997, "0.007 s", (13, 148, 136)), ("compresión + rango", 39_997, "0.008 s", GREEN)]
    x0, x1 = 470, 1260; lo, hi = 3.0, 9.0
    for t in range(3, 10):
        x = x0 + (t - lo) / (hi - lo) * (x1 - x0)
        c.line((x, 250), (x, 760), 1.5, (222, 230, 242)); c.text((x, 790), f"10^{t}", "monor", 20, MUTED, "mm")
    c.text((x0 + (x1 - x0) / 2, 835), "saltos de padre (escala log)", "semi", 22, MUTED, "mm")
    for i, (lab, v, t, col) in enumerate(rows):
        y = 300 + i * 118; xv = x0 + (math.log10(v) - lo) / (hi - lo) * (x1 - x0)
        c.text((x0 - 26, y), lab, "semi", 28, INK, "rm")
        c.rect((x0, y - 34, xv, y + 34), 14, fill=col)
        if xv - x0 > 420:
            c.text((xv - 22, y - 12), f"{v:,}".replace(",", " "), "bold", 28, (255, 255, 255), "rm"); c.text((xv - 22, y + 20), t, "semi", 22, (255, 228, 230), "rm")
        else:
            c.text((xv + 18, y - 12), f"{v:,}".replace(",", " "), "bold", 28, INK, "lm"); c.text((xv + 18, y + 20), t, "reg", 22, MUTED, "lm")
    c.rect((1300, 560, 1540, 740), 22, fill=RED_BG); c.text((1420, 620), "5 000×", "black", 54, RED, "mm"); c.text((1420, 685), "más saltos sin optimizar", "semi", 18, RED, "mm")
    c.save(name)
bench("benchmark.png")

# ---------- Complejidades ----------
def complejidad(name):
    c = Canvas(); header(c, "Complejidad", "find · union · Kruskal", "Lo que cuesta cada operación según las optimizaciones que se usen.", (124, 58, 237))
    cols = ["", "find", "union", "altura máx."]; xs = [110, 760, 1050, 1340]
    rows = [("sin optimizaciones", "O(n)", "O(n)", "n − 1", RED), ("solo unión por rango", "O(log n)", "O(log n)", "log n", INK),
            ("solo compresión", "O(log n)*", "O(log n)*", "—", INK), ("rango + compresión", "O(α(n))*", "O(α(n))*", "—", GREEN)]
    c.rect((80, 230, 1520, 300), 16, fill=(232, 240, 255))
    for x, h in zip(xs, cols): c.text((x, 265), h, "bold", 28, BLUE, "lm")
    for i, (a, f, u, hh, col) in enumerate(rows):
        y = 350 + i * 82
        if i % 2: c.rect((80, y - 38, 1520, y + 38), 14, fill=(240, 245, 252))
        c.text((xs[0], y), a, "semi", 30, INK, "lm")
        for x, v in zip(xs[1:], (f, u, hh)): c.text((x, y), v, "mono", 30, col, "lm")
    c.rect((80, 700, 1520, 850), 20, fill=GREEN_BG)
    c.text((110, 742), "Kruskal = ordenar O(E log E) + E veces union() a costo O(α(V))", "bold", 30, (6, 95, 70), "lm")
    c.text((110, 800), "* amortizado.  α(n) ≤ 4 para cualquier n práctico, así que manda el ordenamiento: O(E log E).", "reg", 26, (6, 95, 70), "lm")
    c.save(name)
complejidad("complejidad.png")
