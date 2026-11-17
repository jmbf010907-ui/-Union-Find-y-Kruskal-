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

def mix(c1, c2, t):
    return tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))

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

WHITE = (255, 255, 255); VIOLET = (124, 58, 237)
NAMES = "ABCDEF"

def card(c, b, title, lines, col=BLUE, sz=25, gap=40):
    """Tarjeta de teoría: un título y unas pocas líneas cortas."""
    c.rect(b, 22, fill=mix(col, WHITE, 0.92), outline=mix(col, WHITE, 0.6), w=2)
    c.rect((b[0], b[1] + 18, b[0] + 8, b[1] + 64), 4, fill=col)
    c.text((b[0] + 30, b[1] + 42), title, "bold", 26, mix(col, (0, 0, 0), 0.25), "lm")
    y = b[1] + 96
    for ln in lines:
        if ln == "":
            y += gap * 0.5; continue
        k = "mono" if ln.startswith("  ") else "reg"
        c.text((b[0] + 30, y), ln.strip() if k == "reg" else ln[2:], "monor" if k == "mono" else "reg",
               sz - (2 if k == "mono" else 0), INK, "lm"); y += gap

def arrays(c, par, rk=None, changed=(), y=640, conj=None, x0=230, cw=104):
    ch = 58; gap = 8
    rows = [("padre", par, CARD, INK)] + ([("rango", rk, (238, 243, 251), MUTED)] if rk is not None else [])
    c.text((x0 - 24, y + ch * 0.5), "i", "semi", 24, MUTED, "rm")
    for i in range(len(par)):
        c.text((x0 + i * (cw + gap) + cw / 2, y + ch * 0.5), NAMES[i], "bold", 26, MUTED, "mm")
    for r, (lab, vals, bf, tc) in enumerate(rows):
        yy = y + (ch + 10) * (r + 1)
        c.text((x0 - 24, yy + ch / 2), lab, "semi", 24, INK if r == 0 else MUTED, "rm")
        for i, v in enumerate(vals):
            x = x0 + i * (cw + gap); hot = (r, i) in changed
            c.rect((x, yy, x + cw, yy + ch), 12, fill=AMBER_BG if hot else bf, outline=AMBER if hot else LINE, w=3 if hot else 1.5)
            s = NAMES[v] if r == 0 else str(v)
            c.text((x + cw / 2, yy + ch / 2), s, "mono" if hot or r == 0 else "monor", 30, (146, 64, 14) if hot else tc, "mm")
    if conj is not None:
        bx = x0 + 6 * (cw + gap) + 50
        c.rect((bx, y + ch + 10, bx + 220, y + ch * 3 + 20), 18, fill=(232, 240, 255), outline=(189, 208, 250), w=2)
        c.text((bx + 110, y + ch * 1.55 + 14), "conjuntos", "semi", 24, MUTED, "mm")
        c.text((bx + 110, y + ch * 2.45 + 18), str(conj), "black", 60, BLUE, "mm")

def pill(c, txt, fg, bg, right=1520, y=64):
    bw = c.tw(txt, "bold", 30) + 56
    c.rect((right - bw, y, right, y + 52), 26, fill=bg); c.text((right - bw / 2, y + 26), txt, "bold", 30, fg, "mm")

# ================= Sección 1 · Union-Find =================
def uf_step(name, paso, titulo, sub, par, rk, teoria, changed=(), conj=None, rings=None, ghost=None,
            hot_edge=None, badge=None, color=BLUE):
    c = Canvas(); header(c, paso, titulo, sub, color)
    pos = layout(par, 110, 1040, 290, 120); rings = rings or {}
    if ghost:
        a, b = ghost; c.arrow(pos[a], pos[b], 50, 52, 4, (176, 190, 214), dash=10)
    for i in range(6):
        if par[i] != i:
            hot = hot_edge == (i, par[i])
            c.arrow(pos[i], pos[par[i]], 50, 52, 6 if hot else 4.5, AMBER if hot else (70, 92, 128))
    for i in range(6):
        if par[i] == i: self_loop(c, pos[i], 46, (120, 140, 175))
        node(c, pos[i], NAMES[i], SET[root(par, i)], ring=rings.get(i))
    card(c, (1090, 220, 1530, 600), "Teoría", teoria, color)
    arrays(c, par, rk, changed, y=630, conj=conj)
    if badge: pill(c, *badge)
    c.save(name)

T = "s1_"
uf_step(T + "paso0.png", "Paso 0", "UnionFind(6)", "Seis computadoras sin cables: cada una es su propio conjunto.",
        [0, 1, 2, 3, 4, 5], [0] * 6,
        ["Cada elemento empieza", "siendo su propio padre.", "", "padre[x] == x", "  → x es raíz", "", "La raíz representa", "a todo su conjunto."], conj=6)
uf_step(T + "paso1.png", "Paso 1", "union(A, B)", "find(A) = A y find(B) = B: raíces distintas, se unen.",
        [0, 0, 2, 3, 4, 5], [1, 0, 0, 0, 0, 0],
        ["union(a, b) une raíces.", "", "Unión por rango:", "la raíz de menor rango", "cuelga de la mayor.", "Empate → la elegida", "sube su rango en 1."],
        {(0, 1), (1, 0)}, 5, {0: AMBER, 1: AMBER}, hot_edge=(1, 0))
uf_step(T + "paso2.png", "Paso 2", "union(D, F)", "El mismo caso en otro grupo: F cuelga de D y rango[D] sube a 1.",
        [0, 0, 2, 3, 4, 3], [1, 0, 0, 1, 0, 0],
        ["Cada union exitosa", "reduce los conjuntos", "en 1.", "", "Ahora hay dos árboles", "de altura 1: {A, B}", "y {D, F}."],
        {(0, 5), (1, 3)}, 4, {3: AMBER, 5: AMBER}, hot_edge=(5, 3))
uf_step(T + "paso3.png", "Paso 3", "union(B, D)", "find(B) = A y find(D) = D. Rangos iguales (1 y 1): D cuelga de A.",
        [0, 0, 2, 0, 4, 3], [2, 0, 0, 1, 0, 0],
        ["Se unen las raíces,", "no los elementos.", "", "  B → A    D → D", "", "rango[A] sube a 2.", "F queda a 2 saltos", "de la raíz."],
        {(0, 3), (1, 0)}, 3, {0: AMBER, 3: AMBER}, hot_edge=(3, 0))
uf_step(T + "paso4.png", "Paso 4", "find(F)", "F → D → A. Al regresar, F queda apuntando directo a la raíz A.",
        [0, 0, 2, 0, 4, 0], [2, 0, 0, 1, 0, 0],
        ["Compresión de caminos:", "find sube a la raíz y", "al volver de la", "recursión deja a cada", "nodo apuntando a ella.", "", "El árbol se aplana:", "el próximo find es O(1)."],
        {(0, 5)}, 3, {5: AMBER, 0: AMBER}, ghost=(5, 3), hot_edge=(5, 0), color=AMBER)
uf_step(T + "paso5.png", "Paso 5", "conectados(B, F)", "find(B) = A y find(F) = A: misma raíz, misma red. conectados(A, E) → False.",
        [0, 0, 2, 0, 4, 0], [2, 0, 0, 1, 0, 0],
        ["Mismo conjunto ⇔", "misma raíz.", "", "  B → A = A ← F  ✓", "  A → A ≠ E ← E  ✗", "", "No se recorre la red:", "solo dos find()."],
        set(), 3, {1: GREEN, 5: GREEN, 4: RED}, badge=("True", GREEN, GREEN_BG), color=GREEN)
uf_step(T + "paso6.png", "Paso 6", "union(B, F)", "Ya tienen la misma raíz: no cambia nada y devuelve False.",
        [0, 0, 2, 0, 4, 0], [2, 0, 0, 1, 0, 0],
        ["find(a) == find(b)", "  → return False", "", "Ya había camino entre", "B y F: este cable", "cerraría un ciclo.", "", "Esto usa Kruskal →"],
        set(), 3, {1: RED, 5: RED}, badge=("False · ciclo", RED, RED_BG), color=RED)

# ================= Sección 2 · Kruskal =================
CAB = [(0, 1, 1), (3, 5, 2), (1, 3, 3), (4, 5, 4), (3, 4, 5), (0, 2, 6), (2, 4, 7), (1, 2, 8)]
GRID = {0: (0, 0), 2: (1, 0), 4: (2, 0), 1: (0, 1), 3: (1, 1), 5: (2, 1)}   # A C E arriba, B D F abajo

def kstate(k):
    """Estado tras procesar los cables 0..k con el mismo UnionFind (find recursivo)."""
    par = list(range(6)); rk = [0] * 6; st = ["p"] * 8; total = 0; info = None
    def find(x):
        if par[x] != x: par[x] = find(par[x])
        return par[x]
    for i in range(k + 1):
        a, b, w = CAB[i]
        if st.count("a") == 5: st[i] = "s"; continue
        ra, rb = find(a), find(b); info = (ra, rb)
        if ra != rb:
            if rk[ra] < rk[rb]: ra, rb = rb, ra
            par[rb] = ra; rk[ra] += rk[ra] == rk[rb]; st[i] = "a"; total += w
        else: st[i] = "r"
    return par, rk, st, total, info

def draw_net(c, st, k=-1, gx=150, gy=300, dx=260, dy=230, colors=None, labels=True, accepted_only=False):
    gp = lambda i: (gx + GRID[i][0] * dx, gy + GRID[i][1] * dy)
    for i, (a, b, w) in enumerate(CAB):
        A, B = gp(a), gp(b); s = st[i] if st else "p"
        if accepted_only and s != "a": continue
        if i == k: c.line(A, B, 26, (253, 230, 170))
        if s == "a": c.line(A, B, 10, GREEN)
        elif s == "r": c.line(A, B, 5, RED, dash=14)
        else: c.line(A, B, 4, (180, 192, 214))
        if labels:
            t = 0.5 if a != 1 or b != 2 else 0.32
            mx, my = A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t
            c.rect((mx - 24, my - 21, mx + 24, my + 21), 11, fill=CARD, outline=GREEN if s == "a" else LINE, w=2)
            c.text((mx, my), str(w), "bold", 25, INK, "mm")
    for i in range(6):
        ring = AMBER if k >= 0 and i in CAB[k][:2] else None
        node(c, gp(i), NAMES[i], colors[i] if colors else (120, 136, 168), ring=ring)
    return gp

def edge_list(c, st, k, x0=800, y0=240, x1=1120):
    c.rect((x0 - 26, y0 - 22, x1, y0 + 8 * 56 + 46), 22, fill=CARD, outline=LINE, w=2)
    c.text((x0, y0 + 8), "cables ordenados", "semi", 22, MUTED, "lm")
    for i, (a, b, w) in enumerate(CAB):
        y = y0 + 60 + i * 56; s = st[i]
        if i == k: c.rect((x0 - 12, y - 24, x1 - 14, y + 24), 12, fill=AMBER_BG)
        col = GREEN if s == "a" else RED if s == "r" else INK if s == "p" else (160, 172, 194)
        c.text((x0, y), f"{NAMES[a]}–{NAMES[b]}", "mono", 28, col, "lm"); c.text((x0 + 120, y), f"{w}", "monor", 28, MUTED, "lm")
        c.text((x1 - 34, y), "✓" if s == "a" else "✗" if s == "r" else "", "bold", 28, col, "rm")

def k_step(name, k, paso, titulo, sub, teoria, color, changed=()):
    c = Canvas(); header(c, paso, titulo, sub, color)
    par, rk, st, total, _ = kstate(k)
    draw_net(c, st, k, colors=[SET[root(par, i)] for i in range(6)] if k >= 0 else None)
    edge_list(c, st, k)
    card(c, (1160, 220, 1530, 640), "Teoría", teoria, color, sz=24, gap=38)
    arrays(c, par, None, changed, y=650, x0=200, cw=74)
    acc = st.count("a")
    c.rect((1160, 680, 1530, 800), 20, fill=GREEN_BG if acc == 5 else (240, 245, 252))
    c.text((1345, 718), f"árbol: {acc} de 5 cables", "semi", 26, INK, "mm")
    c.text((1345, 768), f"costo = {total}", "black", 40, GREEN if acc == 5 else INK, "mm")
    c.save(name)

T = "s2_"
k_step(T + "paso0.png", -1, "Paso 0", "ordenar los cables", "Se ordenan los 8 cables de menor a mayor costo. Nadie está conectado todavía.",
       ["Kruskal es voraz:", "", "1. ordenar por peso", "2. tomar el cable si", "   no forma ciclo", "3. parar con V − 1", "   cables (aquí 5)", "", "Para 2 usa Union-Find."], BLUE)
k_step(T + "paso1.png", 0, "Paso 1", "A–B (1)", "find(A) = A, find(B) = B. Raíces distintas: se acepta y union(A, B).",
       ["Raíces distintas", "  → no hay camino", "  entre A y B.", "", "Se acepta el cable", "y union los junta.", "", "Es el paso 1 de la", "sección 1."], GREEN, {(0, 1)})
k_step(T + "paso2.png", 1, "Paso 2", "D–F (2)", "find(D) = D, find(F) = F. Raíces distintas: se acepta y union(D, F).",
       ["No toca a {A, B}:", "aparece otro grupo.", "", "Kruskal crece como", "un bosque, no como", "un solo árbol.", "", "Igual al paso 2."], GREEN, {(0, 5)})
k_step(T + "paso3.png", 2, "Paso 3", "B–D (3)", "find(B) = A, find(D) = D. Raíces distintas: se unen los dos grupos.",
       ["Une {A, B} con {D, F}.", "", "Rangos 1 y 1:", "D cuelga de A y", "rango[A] = 2.", "", "Mismo resultado que", "el paso 3 de la", "sección 1."], GREEN, {(0, 3)})
k_step(T + "paso4.png", 3, "Paso 4", "E–F (4)", "find(E) = E, find(F) = A (y F se comprime). Raíces distintas: se acepta.",
       ["find(F): F → D → A", "y comprime: F → A.", "", "rango[E] = 0 < 2:", "E cuelga de A.", "", "Ya hay 4 cables."], GREEN, {(0, 4), (0, 5)})
k_step(T + "paso5.png", 4, "Paso 5", "D–E (5)", "find(D) = A y find(E) = A. Misma raíz: el cable cerraría un ciclo, se descarta.",
       ["Ya hay camino:", "  D – F – E", "", "union devuelve False", "  → se rechaza.", "", "Sin Union-Find habría", "que recorrer la red."], RED)
k_step(T + "paso6.png", 5, "Paso 6", "A–C (6)", "find(A) = A, find(C) = C. Se acepta: ya son 5 cables = V − 1. Termina.",
       ["5 cables = V − 1", "  → árbol completo.", "", "C–E (7) y B–C (8)", "ni se revisan.", "", "Todas las raíces", "son A: un conjunto."], GREEN, {(0, 2)})

def resultado(name):
    c = Canvas(); header(c, "Resultado", "Árbol de expansión mínima", "Las 6 computadoras conectadas, sin ciclos y con el menor costo.", GREEN)
    par, rk, st, total, _ = kstate(7)
    draw_net(c, st, colors=[GREEN] * 6, accepted_only=True, gx=200, gy=330, dx=300, dy=250)
    x0 = 1020
    c.rect((x0 - 30, 240, 1530, 620), 24, fill=GREEN_BG)
    c.text((x0, 284), "cables comprados", "semi", 24, (6, 95, 70), "lm")
    for i, (a, b, w) in enumerate([CAB[j] for j in range(8) if st[j] == "a"]):
        y = 334 + i * 44; c.text((x0, y), f"{NAMES[a]}–{NAMES[b]}", "mono", 28, (6, 95, 70), "lm"); c.text((x0 + 120, y), str(w), "monor", 28, (6, 95, 70), "lm")
    c.text((1300, 360), "costo", "semi", 26, MUTED, "mm"); c.text((1300, 440), str(total), "black", 96, GREEN, "mm")
    c.text((1300, 520), "de 36 posibles", "reg", 22, MUTED, "mm")
    c.rect((90, 760, 1510, 860), 20, fill=(240, 245, 252))
    c.text((800, 792), "D–E se rechazó por ciclo (union devolvió False).", "bold", 28, INK, "mm")
    c.text((800, 834), "C–E y B–C nunca se revisaron: Kruskal paró al llegar a V − 1 = 5 cables.", "reg", 26, MUTED, "mm")
    c.save(name)
resultado("s2_resultado.png")

# ================= Problema, portadas y teoría =================
def problema(name):
    c = Canvas(); header(c, "El problema", "6 computadoras, 8 cables", "Hay que conectarlas todas gastando lo menos posible en cable.", INK)
    draw_net(c, ["p"] * 8, gx=170, gy=330, dx=310, dy=300)
    qs = [(250, "¿A y F ya están conectadas?", "Sección 1 · Union-Find", "find(A) == find(F)", BLUE),
          (470, "¿Qué cables compro?", "Sección 2 · Kruskal", "menor costo, sin ciclos", GREEN)]
    for y, q, s, d, col in qs:
        c.rect((900, y, 1530, y + 190), 24, fill=mix(col, WHITE, 0.9), outline=mix(col, WHITE, 0.55), w=2)
        c.text((935, y + 48), q, "bold", 30, INK, "lm")
        c.text((935, y + 104), s, "semi", 26, col, "lm")
        c.text((935, y + 150), d, "monor", 24, MUTED, "lm")
    c.text((170, 760), "Los números son el costo de cada cable.", "reg", 24, MUTED, "lm")
    c.save(name)
problema("problema.png")

def portada(name, num, titulo, sub, items, col):
    c = Canvas(); c.im.paste(mix(col, (8, 16, 40), 0.55), [0, 0, W * S, H * S])
    c.text((110, 200), f"Sección {num}", "semi", 34, mix(col, WHITE, 0.6), "lm")
    c.text((106, 300), titulo, "black", 120, WHITE, "lm")
    c.text((110, 400), sub, "reg", 32, mix(col, WHITE, 0.75), "lm")
    for i, it in enumerate(items):
        y = 520 + i * 70
        c.circle((130, y), 20, fill=mix(col, WHITE, 0.25)); c.text((130, y), str(i + 1), "bold", 22, WHITE, "mm")
        c.text((175, y), it, "semi", 30, WHITE, "lm")
    c.save(name)
portada("s1_portada.png", 1, "Union-Find", "¿Estas dos computadoras ya están conectadas?",
        ["Teoría: conjuntos como árboles", "Paso a paso con A … F (7 pasos)", "Código y lo que imprime"], BLUE)
portada("s2_portada.png", 2, "Kruskal", "¿Qué cables compro para conectarlas todas al menor costo?",
        ["Teoría: algoritmo voraz + Union-Find", "Paso a paso sobre la misma red (6 pasos)", "Resultado, código y lo que imprime"], GREEN)

def teoria_uf(name):
    c = Canvas(); header(c, "Teoría", "Union-Find", "Estructura para conjuntos disjuntos: cada conjunto es un árbol y su raíz lo representa.")
    card(c, (80, 220, 780, 560), "Idea", ["Un arreglo padre[] guarda el árbol.", "padre[x] == x  → x es la raíz.", "", "Dos elementos están en el mismo", "conjunto si llegan a la misma raíz."], BLUE, sz=27, gap=44)
    card(c, (820, 220, 1520, 560), "Operaciones", ["  find(x)        → raíz de x", "  union(a, b)    → junta conjuntos", "  conectados(a,b) → find(a)==find(b)", "", "union devuelve False si ya estaban."], VIOLET, sz=27, gap=44)
    card(c, (80, 590, 780, 860), "Unión por rango", ["El árbol bajo cuelga del alto.", "La altura queda en O(log n)."], AMBER, sz=27, gap=44)
    card(c, (820, 590, 1520, 860), "Compresión de caminos", ["find deja todo el camino", "apuntando a la raíz → O(α(n))."], GREEN, sz=27, gap=44)
    c.save(name)
teoria_uf("s1_teoria.png")

def teoria_k(name):
    c = Canvas(); header(c, "Teoría", "Kruskal", "Árbol de expansión mínima: conectar los V vértices con V − 1 aristas de peso total mínimo.", GREEN)
    card(c, (80, 220, 780, 600), "Algoritmo (voraz)", ["  ordenar aristas por peso", "  para cada (u, v, w):", "      si union(u, v):", "          agregar al árbol", "      si |árbol| == V − 1: parar"], GREEN, sz=27, gap=50)
    card(c, (820, 220, 1520, 600), "¿Por qué Union-Find?", ["Antes de aceptar una arista hay", "que saber si u y v ya están", "conectados (si no, ciclo).", "", "union() lo responde en O(α(V))", "sin recorrer el grafo."], BLUE, sz=27, gap=46)
    card(c, (80, 630, 1520, 860), "Complejidad", ["Ordenar: O(E log E)   +   E operaciones de Union-Find: O(E · α(V))", "Total: O(E log E). El ordenamiento domina."], VIOLET, sz=28, gap=48)
    c.save(name)
teoria_k("s2_teoria.png")

# ================= Código y salida =================
import re
KW = {"class", "def", "if", "return", "self", "True", "False", "for", "in", "from", "import"}
FN = {"find", "union", "__init__", "UnionFind", "kruskal", "sorted", "enumerate", "len", "append", "range", "list"}
VAR = {"padre", "rango", "conjuntos", "arbol", "costo", "uf"}
def code_img(name, fname, code, sz=25, lh=33.5):
    c = Canvas(); c.im.paste((15, 23, 42), [0, 0, W * S, H * S])
    c.rect((40, 34, 1560, 866), 26, fill=(22, 32, 56))
    for i, col in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]): c.circle((84 + i * 32, 74), 9, fill=col)
    c.text((800, 74), fname, "semi", 22, (148, 163, 184), "mm")
    y = 130
    for ln in code.split("\n"):
        x = 90; cd, _, com = ln.partition("#")
        for tok in re.findall(r"\s+|\w+|[^\w\s]", cd):
            col = (226, 232, 240)
            if tok in KW: col = (196, 148, 255)
            elif tok in FN: col = (125, 211, 252)
            elif tok.isdigit(): col = (251, 191, 36)
            elif tok in VAR: col = (134, 239, 172)
            c.text((x, y), tok, "mono", sz, col, "lm"); x += c.tw(tok, "mono", sz)
        if com: c.text((x, y), "#" + com, "monor", sz, (100, 116, 139), "lm")
        y += lh
    c.save(name)

UF_CODE = '''class UnionFind:
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
            return False                  # misma raíz: ciclo
        if self.rango[ra] < self.rango[rb]:
            ra, rb = rb, ra               # ra es el árbol más alto
        self.padre[rb] = ra
        if self.rango[ra] == self.rango[rb]:
            self.rango[ra] += 1
        self.conjuntos -= 1
        return True'''
K_CODE = '''from union_find import UnionFind, ID

CABLES = [(1, "A", "B"), (2, "D", "F"), (3, "B", "D"), (4, "E", "F"),
          (5, "D", "E"), (6, "A", "C"), (7, "C", "E"), (8, "B", "C")]

def kruskal(n, aristas):
    uf = UnionFind(n)
    arbol, costo = [], 0
    for w, u, v in sorted(aristas):         # 1) de menor a mayor costo
        if uf.union(ID[u], ID[v]):          # 2) raíces distintas: sin ciclo
            arbol.append((u, v, w))
            costo += w
        if len(arbol) == n - 1:             # 3) ya hay V - 1 cables
            break
    return arbol, costo

arbol, costo = kruskal(6, CABLES)          # costo = 16'''
code_img("s1_codigo.png", "src/union_find.py", UF_CODE)
code_img("s2_codigo.png", "src/kruskal.py", K_CODE, sz=26, lh=38)

def terminal(name, cmd, lines, hl):
    c = Canvas(); c.im.paste((15, 23, 42), [0, 0, W * S, H * S])
    c.rect((40, 34, 1560, 866), 26, fill=(10, 14, 28))
    for i, col in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]): c.circle((84 + i * 32, 74), 9, fill=col)
    c.text((800, 74), "terminal", "semi", 22, (148, 163, 184), "mm")
    c.text((90, 128), "$ " + cmd, "mono", 24, (134, 239, 172), "lm")
    n = len(lines); lh = min(36, 680 / max(n, 1)); sz = min(23, lh * 0.66); y = 128 + lh * 1.4
    for ln in lines:
        col = (226, 232, 240)
        if ln.startswith("Paso") or ln.startswith("Cables") or ln.startswith("Árbol") or ln.startswith("Costo"): col = (125, 211, 252)
        if ln.startswith("   "): col = (160, 174, 196)
        for key, kc in hl:
            if key in ln: col = kc
        c.text((90, y), ln, "mono" if col != (160, 174, 196) else "monor", sz, col, "lm"); y += lh
    c.save(name)
terminal("s1_salida.png", "python src/union_find.py", open("/tmp/out_uf.txt").read().rstrip().split("\n"),
         [("False", (252, 165, 165)), ("find(F)", (251, 191, 36))])
terminal("s2_salida.png", "python src/kruskal.py", open("/tmp/out_k.txt").read().rstrip().split("\n"),
         [("rechaza", (252, 165, 165)), ("Costo total", (134, 239, 172))])

def interactivo(name, url):
    c = Canvas(); c.im.paste((12, 24, 56), [0, 0, W * S, H * S])
    c.text((110, 210), "Demo interactiva", "semi", 34, (147, 197, 253), "lm")
    c.text((106, 310), "Pruébalo tú", "black", 110, WHITE, "lm")
    c.text((110, 410), "Union-Find y Kruskal paso a paso sobre la misma red de 6 computadoras.", "reg", 30, (191, 219, 254), "lm")
    c.rect((110, 480, 1000, 560), 18, fill=(30, 58, 138)); c.text((140, 520), url, "mono", 25, WHITE, "lm")
    for i, t in enumerate(["Avanza y retrocede los pasos", "Ve el grafo, el bosque y padre[] a la vez", "Modo libre: haz tus propios union() y find()"]):
        c.circle((130, 640 + i * 62), 8, fill=(147, 197, 253)); c.text((160, 640 + i * 62), t, "semi", 28, WHITE, "lm")
    c.rect((1150, 480, 1490, 820), 24, outline=(147, 197, 253), w=3)
    c.text((1320, 650), "QR", "black", 60, (71, 85, 140), "mm")
    c.save(name)
interactivo("interactivo.png", "jmbf010907-ui.github.io/-Union-Find-y-Kruskal-")
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

def comparacion(name):
    c = Canvas(); header(c, "Comparación", "¿Por qué Union-Find?", "La pregunta '¿ya están conectados?' se puede responder de dos formas.", (124, 58, 237))
    cajas = [(90, "Recorrer el grafo", "Por cada arista, un DFS o BFS\npara ver si ya hay camino\nentre los dos vértices.",
              "O(V + E)", "por arista", "O(E · (V+E))", "en todo Kruskal", RED, RED_BG),
             (820, "Union-Find", "Por cada arista, dos find()\ny comparar las raíces.",
              "O(α(V))", "por arista", "O(E · α(V))", "en todo Kruskal", GREEN, GREEN_BG)]
    for x, titulo, desc, c1, c1s, c2, c2s, col, bg in cajas:
        c.rect((x, 230, x + 690, 740), 26, fill=CARD, outline=col, w=3)
        c.rect((x, 230, x + 690, 310), 26, fill=bg)
        c.text((x + 345, 270), titulo, "bold", 36, col, "mm")
        for i, ln in enumerate(desc.split("\n")): c.text((x + 40, 360 + i * 42), ln, "reg", 27, INK, "lm")
        c.rect((x + 40, 510, x + 650, 610), 16, fill=(244, 247, 252))
        c.text((x + 345, 548), c1, "mono", 38, col, "mm"); c.text((x + 345, 588), c1s, "reg", 22, MUTED, "mm")
        c.rect((x + 40, 625, x + 650, 715), 16, fill=bg)
        c.text((x + 345, 658), c2, "mono", 34, col, "mm"); c.text((x + 345, 695), c2s, "reg", 22, MUTED, "mm")
    c.rect((90, 780, 1510, 866), 20, fill=(237, 233, 254))
    c.text((800, 823), "Con 10 000 aristas y 5 000 vértices: ~50 millones de pasos contra ~40 mil.", "bold", 30, (76, 29, 149), "mm")
    c.save(name)

comparacion("comparacion.png")
