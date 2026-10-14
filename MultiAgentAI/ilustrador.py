"""Cria imagens genéricas (SVG) para os itens do site, só para visualizar o layout.

Os agentes escrevem no banco caminhos como 'img/nome.jpg', mas nenhum deles
cria esses arquivos, e os cards ficam sem figura. Este módulo:

- lê o database/schema.sql e acha as linhas que têm uma coluna de imagem;
- cria para cada uma um SVG genérico (fundo na paleta do style.css do
  projeto, anéis e as iniciais do item) em static/img/;
- acerta o caminho no schema.sql;
- cria também static/img/hero.svg e o CSS que o usa no #hero, se houver.

Uso na linha de comando:  python ilustrador.py <pasta_do_projeto_gerado>
"""
import hashlib
import html as html_lib
import math
import os
import random
import re
import sqlite3
import sys
import unicodedata

_COLUNAS_DE_IMAGEM = re.compile(r"imagem|image|foto|img|capa|banner|thumb", re.I)
_COLUNAS_DE_NOME = ("nome", "titulo", "name", "title")
_MARCA_CSS = "Ajuste automático: imagem do hero"
_MARCA_MENU = "Ajuste automático: menu de navegação"


# ----------------------------------------------------------------- cores

def _sem_acento(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    ).lower()


def _slug(texto):
    return re.sub(r"[^a-z0-9]+", "-", _sem_acento(texto)).strip("-") or "item"


def _rgb(hexa):
    h = hexa.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in rgb)


def _misturar(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return _hex([x * (1 - t) + y * t for x, y in zip(ra, rb)])


def _luz(hexa):
    r, g, b = _rgb(hexa)
    return 0.299 * r + 0.587 * g + 0.114 * b


def _texto_sobre(cor):
    return "#1a1a1a" if _luz(cor) > 140 else "#ffffff"


def _sat(hexa):
    r, g, b = _rgb(hexa)
    return 0 if max(r, g, b) == 0 else (max(r, g, b) - min(r, g, b)) / max(r, g, b)


def _paleta(css):
    """(base, destaque, claro, acento) lidos do :root do style.css.

    base: fundo escuro do desenho; destaque: cor do círculo central;
    claro: cor do texto/estrelas; acento: cor dos anéis.
    """

    v = dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})\s*;", css or ""))

    def pegar(*nomes):
        return [v[n] for n in nomes if n in v]

    # base: a primeira cor escura da paleta (senão escurece o fundo)
    base = next(
        (c for c in pegar("--cabecalho", "--fundo", "--texto", "--superficie", "--primaria") if _luz(c) < 90),
        None
    )
    if not base:
        origem = (pegar("--cabecalho", "--primaria", "--fundo") or ["#14213d"])[0]
        base = _misturar(origem, "#000000", 0.6)

    # destaque: a cor mais viva que não seja a base
    candidatas = [c for c in pegar("--primaria", "--secundaria", "--superficie", "--cabecalho", "--borda")
                  if c.lower() != base.lower()]
    destaque = max(candidatas, key=_sat) if candidatas else _misturar(base, "#ffffff", 0.4)

    if _sat(destaque) < 0.2:
        destaque = "#c8863a"

    # claro: a cor mais clara disponível
    claros = [c for c in pegar("--fundo", "--texto", "--superficie", "--primaria") if _luz(c) > 190]
    claro = max(claros, key=_luz) if claros else "#fff4de"

    # acento dos anéis: borda viva, senão o destaque clareado
    borda = (pegar("--borda") or [None])[0]
    acento = borda if borda and _sat(borda) > 0.3 and _luz(borda) > 90 else _misturar(destaque, "#ffffff", 0.35)

    return base, destaque, claro, acento


# --------------------------------------------------------------- desenhos

def _estrela(cx, cy, r, cor, opacidade=1.0):
    pontos = []
    for i in range(10):
        raio = r if i % 2 == 0 else r * 0.45
        ang = math.radians(-90 + 36 * i)
        pontos.append(f"{cx + raio * math.cos(ang):.1f},{cy + raio * math.sin(ang):.1f}")
    return f'<polygon points="{" ".join(pontos)}" fill="{cor}" opacity="{opacidade}"/>'


def _estrelinhas(rnd, n, cor, area=(0, 0, 640, 400)):
    x0, y0, x1, y1 = area
    return "".join(
        _estrela(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(3, 9), cor, rnd.uniform(0.35, 0.9))
        for _ in range(n)
    )


def _iniciais(nome):
    palavras = [p for p in re.findall(r"[^\W\d_]+", nome) if len(p) > 2] or [nome or "?"]
    return "".join(p[0] for p in palavras[:2]).upper()


def _motivo(fundo, destaque, claro, ouro, nome, w=640, h=400):
    """Anéis concêntricos com as iniciais do item no centro."""

    cx, cy = w / 2, h / 2
    formas = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c}" stroke-width="{sw}" opacity="{o}"/>'
        for r, c, sw, o in [(165, ouro, 2, 0.35), (135, claro, 2, 0.30), (105, ouro, 3, 0.55)]
    )
    pontos = "".join(
        f'<circle cx="{cx + 165 * math.cos(math.radians(a)):.0f}" cy="{cy + 165 * math.sin(math.radians(a)):.0f}" '
        f'r="6" fill="{ouro}" opacity="0.8"/>'
        for a in range(0, 360, 45)
    )
    return (
        formas + pontos
        + f'<circle cx="{cx}" cy="{cy}" r="88" fill="{destaque}"/>'
        + f'<text x="{cx}" y="{cy + 30}" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="84" font-weight="bold" fill="{_texto_sobre(destaque)}">{_escapar(_iniciais(nome))}</text>'
    )


def _inteiro(texto):
    return int(hashlib.md5(str(texto).encode("utf-8")).hexdigest(), 16)


def _cores_do_item(paleta, k):
    """Uma de 6 combinações de cores, todas tiradas da paleta do projeto."""

    fundo, destaque, claro, ouro = paleta
    escuro = _misturar(fundo, "#000000", 0.25)
    suave = _misturar(claro, destaque, 0.12)

    variantes = [
        dict(bg=_misturar(fundo, destaque, 0.30), bg2=escuro, a=ouro, b=claro, c=destaque, badge=destaque),
        dict(bg=destaque, bg2=_misturar(destaque, "#000000", 0.35), a=claro, b=ouro, c=escuro, badge=claro),
        dict(bg=suave, bg2=_misturar(suave, destaque, 0.25), a=destaque, b=ouro, c=escuro, badge=escuro),
        dict(bg=_misturar(ouro, "#000000", 0.50), bg2=_misturar(ouro, "#000000", 0.75), a=ouro, b=claro, c=destaque, badge=claro),
        dict(bg=_misturar(claro, ouro, 0.45), bg2=_misturar(claro, ouro, 0.70), a=escuro, b=destaque, c=claro, badge=destaque),
        dict(bg=_misturar(destaque, claro, 0.50), bg2=_misturar(destaque, claro, 0.25), a=escuro, b=destaque, c=ouro, badge=escuro),
    ]
    return variantes[k % len(variantes)]


def _caminho_suave(pontos):
    """Curva fechada e arredondada que passa perto dos pontos (para as manchas)."""
    n = len(pontos)
    meio = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    ini = meio(pontos[-1], pontos[0])
    d = f"M{ini[0]:.0f},{ini[1]:.0f} "
    for i in range(n):
        p, q = pontos[i], meio(pontos[i], pontos[(i + 1) % n])
        d += f"Q{p[0]:.0f},{p[1]:.0f} {q[0]:.0f},{q[1]:.0f} "
    return d + "Z"


def _forma_aneis(c, rnd, w, h):
    cx, cy = w / 2, h / 2
    saida = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{cor}" stroke-width="{sw}" opacity="{o}"/>'
        for r, cor, sw, o in [(165, c["a"], 2, 0.45), (135, c["b"], 2, 0.35), (105, c["a"], 3, 0.6)]
    )
    saida += "".join(
        f'<circle cx="{cx + 165 * math.cos(math.radians(a)):.0f}" cy="{cy + 165 * math.sin(math.radians(a)):.0f}" '
        f'r="6" fill="{c["a"]}" opacity="0.8"/>'
        for a in range(0, 360, 45)
    )
    return saida


def _forma_ondas(c, rnd, w, h):
    saida = f'<circle cx="{rnd.uniform(w * .2, w * .8):.0f}" cy="{h * .3:.0f}" r="70" fill="{c["b"]}" opacity="0.4"/>'
    for i, cor in enumerate((c["a"], c["b"], c["c"])):
        base = h * (0.55 + i * 0.14)
        amp, fase = rnd.uniform(14, 30), rnd.uniform(0, 6.28)
        pts = " ".join(
            f"{x},{base + amp * math.sin(x / w * 6.28 * 1.5 + fase):.1f}" for x in range(0, w + 1, 20)
        )
        saida += f'<polygon points="0,{h} {pts} {w},{h}" fill="{cor}" opacity="{0.45 + i * 0.15:.2f}"/>'
    return saida


def _forma_geometrica(c, rnd, w, h):
    saida = ""
    cores = [c["a"], c["b"], c["c"]]
    for i in range(8):
        cor, o = cores[i % 3], rnd.uniform(0.25, 0.6)
        x, y, t = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(50, 130)
        if i % 3 == 0:
            saida += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{t / 1.6:.0f}" fill="{cor}" opacity="{o:.2f}"/>'
        elif i % 3 == 1:
            saida += (f'<rect x="{x:.0f}" y="{y:.0f}" width="{t:.0f}" height="{t:.0f}" fill="{cor}" '
                      f'opacity="{o:.2f}" transform="rotate({rnd.uniform(0, 80):.0f} {x:.0f} {y:.0f})"/>')
        else:
            saida += (f'<polygon points="{x:.0f},{y - t / 2:.0f} {x + t / 2:.0f},{y + t / 2:.0f} '
                      f'{x - t / 2:.0f},{y + t / 2:.0f}" fill="{cor}" opacity="{o:.2f}"/>')
    return saida


def _forma_listras(c, rnd, w, h):
    larg = rnd.choice((34, 46, 58))
    return "".join(
        f'<polygon points="{x},0 {x + larg},0 {x + larg - h},{h} {x - h},{h}" fill="{c["a"]}" opacity="0.25"/>'
        for x in range(0, w + h, larg * 2)
    )


def _forma_pontos(c, rnd, w, h):
    passo = 32
    cx, cy = rnd.uniform(w * .3, w * .7), rnd.uniform(h * .3, h * .7)
    maxd = math.hypot(w, h) / 1.6
    saida = ""
    for gy in range(passo // 2, h, passo):
        for gx in range(passo // 2, w, passo):
            r = max(1.5, 12 * (1 - math.hypot(gx - cx, gy - cy) / maxd))
            saida += f'<circle cx="{gx}" cy="{gy}" r="{r:.1f}" fill="{c["a"]}" opacity="0.55"/>'
    return saida


def _forma_montanhas(c, rnd, w, h):
    saida = f'<circle cx="{rnd.uniform(w * .25, w * .75):.0f}" cy="{h * .28:.0f}" r="48" fill="{c["b"]}" opacity="0.55"/>'
    for i, cor in enumerate((c["a"], c["b"], c["c"])):
        base = h * (0.62 + i * 0.12)
        pts, x = [], 0
        while x < w:
            pts.append(f"{x},{base - rnd.uniform(20, 95 - i * 20):.0f}")
            x += rnd.randint(70, 120)
        pts.append(f"{w},{base - rnd.uniform(20, 60):.0f}")
        saida += f'<polygon points="0,{h} {" ".join(pts)} {w},{h}" fill="{cor}" opacity="{0.5 + i * 0.15:.2f}"/>'
    return saida


def _forma_losangos(c, rnd, w, h):
    cx, cy = w / 2, h / 2
    saida = ""
    for i, s in enumerate((165, 130, 95)):
        cor = c["a"] if i % 2 == 0 else c["b"]
        saida += (f'<polygon points="{cx},{cy - s} {cx + s * 1.3:.0f},{cy} {cx},{cy + s} {cx - s * 1.3:.0f},{cy}" '
                  f'fill="none" stroke="{cor}" stroke-width="3" opacity="{0.6 - i * 0.1:.2f}"/>')
    for x, y in ((50, 50), (w - 50, 50), (50, h - 50), (w - 50, h - 50)):
        saida += (f'<polygon points="{x},{y - 18} {x + 24},{y} {x},{y + 18} {x - 24},{y}" '
                  f'fill="{c["c"]}" opacity="0.7"/>')
    return saida


def _forma_manchas(c, rnd, w, h):
    saida = ""
    for cor in (c["a"], c["b"], c["c"], c["a"]):
        cx, cy, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(70, 130)
        pts = [
            (cx + r * rnd.uniform(.7, 1.15) * math.cos(2 * math.pi * j / 7),
             cy + r * rnd.uniform(.7, 1.15) * math.sin(2 * math.pi * j / 7))
            for j in range(7)
        ]
        saida += f'<path d="{_caminho_suave(pts)}" fill="{cor}" opacity="{rnd.uniform(0.3, 0.55):.2f}"/>'
    return saida


def _forma_mosaico(c, rnd, w, h):
    t = 40
    cores = [c["a"], c["b"], c["c"]]
    return "".join(
        f'<rect x="{gx + 2}" y="{gy + 2}" width="{t - 4}" height="{t - 4}" rx="6" '
        f'fill="{rnd.choice(cores)}" opacity="{rnd.uniform(0.2, 0.6):.2f}"/>'
        for gy in range(0, h, t) for gx in range(0, w, t) if rnd.random() < 0.45
    )


def _forma_raios(c, rnd, w, h):
    cx, cy = w / 2, h / 2
    n = rnd.choice((12, 16, 20))
    saida = ""
    for i in range(0, n, 2):
        a1, a2 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        saida += (f'<polygon points="{cx},{cy} {cx + 600 * math.cos(a1):.0f},{cy + 600 * math.sin(a1):.0f} '
                  f'{cx + 600 * math.cos(a2):.0f},{cy + 600 * math.sin(a2):.0f}" fill="{c["a"]}" opacity="0.22"/>')
    return saida


_ESTILOS = (
    _forma_aneis, _forma_ondas, _forma_geometrica, _forma_listras, _forma_pontos,
    _forma_montanhas, _forma_losangos, _forma_manchas, _forma_mosaico, _forma_raios,
)


def _svg_card(nome, paleta, w=640, h=400, indice=None):
    """Ilustração genérica do item. Com 'indice', itens vizinhos nunca repetem
    nem o estilo nem as cores; sem ele, o estilo sai do nome do item."""

    semente = _inteiro(nome)
    rnd = random.Random(semente)
    k = semente if indice is None else indice

    c = _cores_do_item(paleta, (k * 5) % 6)
    forma = _ESTILOS[k % len(_ESTILOS)]

    cx, cy = w / 2, h / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
        f'aria-label="{_escapar(nome)}">'
        f'<defs><radialGradient id="g" cx="50%" cy="38%" r="75%">'
        f'<stop offset="0" stop-color="{c["bg"]}"/><stop offset="1" stop-color="{c["bg2"]}"/></radialGradient></defs>'
        f'<rect width="{w}" height="{h}" fill="url(#g)"/>'
        + forma(c, rnd, w, h)
        + f'<circle cx="{cx}" cy="{cy}" r="96" fill="{c["bg2"]}" opacity="0.35"/>'
        + f'<circle cx="{cx}" cy="{cy}" r="88" fill="{c["badge"]}"/>'
        + f'<text x="{cx}" y="{cy + 30}" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="84" font-weight="bold" fill="{_texto_sobre(c["badge"])}">{_escapar(_iniciais(nome))}</text>'
        + f'<rect x="3" y="3" width="{w - 6}" height="{h - 6}" fill="none" stroke="{c["a"]}" stroke-width="3" '
        f'opacity="0.5" rx="10"/>'
        "</svg>\n"
    )


def _bokeh(rnd, n, cores, w, h):
    """Círculos translúcidos de fundo (no lugar das estrelas do hero)."""
    return "".join(
        f'<circle cx="{rnd.uniform(0, w):.0f}" cy="{rnd.uniform(0, h):.0f}" r="{rnd.uniform(20, 90):.0f}" '
        f'fill="{rnd.choice(cores)}" opacity="{rnd.uniform(0.06, 0.18):.2f}"/>'
        for _ in range(n)
    )


def _svg_hero(titulo, paleta, w=1600, h=700):
    fundo, destaque, claro, ouro = paleta
    rnd = random.Random("hero" + titulo)

    escuro = _misturar(fundo, "#000000", 0.45)
    meio = _misturar(fundo, destaque, 0.35)

    raios = "".join(
        f'<polygon points="{w / 2},{h * 0.75} {w / 2 + 1700 * math.cos(math.radians(a)):.0f},'
        f'{h * 0.75 + 1700 * math.sin(math.radians(a)):.0f} '
        f'{w / 2 + 1700 * math.cos(math.radians(a + 4)):.0f},{h * 0.75 + 1700 * math.sin(math.radians(a + 4)):.0f}" '
        f'fill="{ouro}" opacity="0.07"/>'
        for a in range(200, 340, 9)
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" '
        f'width="{w}" height="{h}" role="img" aria-label="{_escapar(titulo)}">'
        f'<defs><linearGradient id="c" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{escuro}"/><stop offset="1" stop-color="{meio}"/></linearGradient></defs>'
        f'<rect width="{w}" height="{h}" fill="url(#c)"/>'
        + raios
        + _bokeh(rnd, 14, (ouro, claro, destaque), w, h)
        + "</svg>\n"
    )


def _escapar(texto):
    return (
        str(texto).replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;")
    )



def _svg_logo(nome, paleta, w=200, h=200):
    """Logotipo genérico: quadrado arredondado com as iniciais da marca."""
    fundo, destaque, claro, ouro = paleta
    limpo = re.sub(
        r"\b(logotipo|logomarca|logo|marca|imagem|da|de|do)\b", "", nome, flags=re.I
    ).strip() or nome
    base = _misturar(fundo, "#000000", 0.25)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{_escapar(nome)}">'
        f'<rect width="{w}" height="{h}" rx="36" fill="{base}"/>'
        f'<rect x="4" y="4" width="{w - 8}" height="{h - 8}" rx="32" fill="none" stroke="{ouro}" '
        f'stroke-width="4" opacity="0.7"/>'
        f'<circle cx="{w / 2}" cy="{h / 2}" r="70" fill="{destaque}"/>'
        f'<text x="{w / 2}" y="{h / 2 + 22}" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="64" font-weight="bold" fill="{_texto_sobre(destaque)}">'
        f'{_escapar(_iniciais(limpo))}</text></svg>\n'
    )


# Ícones do Font Awesome / similares viram emoji (a biblioteca não é carregada,
# então os botões só com ícone ficavam vazios).
_ICONES = {
    "search": "🔍", "cart": "🛒", "shopping": "🛒", "bag": "🛍", "user": "👤",
    "heart": "♥", "star": "★", "phone": "📞", "envelope": "✉", "mail": "✉",
    "home": "🏠", "bars": "☰", "menu": "☰", "times": "✕", "close": "✕",
    "instagram": "📷", "whatsapp": "💬", "truck": "🚚", "tag": "🏷",
    "gift": "🎁", "map": "📍", "clock": "🕒", "check": "✔", "arrow": "→",
}


def _trocar_icones(html):
    """Troca <i class="fas fa-xxx"></i> por emoji, se não há biblioteca de ícones."""

    if re.search(r"font-?awesome|bootstrap-icons|material-icons|fontawesome", html, re.I):
        return html

    def troca(m):
        classes = m.group(1)
        if not re.search(r"(^|\s)fa[srbl]?(\s|$)|(^|\s)fa-", classes):
            return m.group(0)
        nomes = " ".join(re.findall(r"fa-([\w-]+)", classes)).lower()
        emoji = next((e for chave, e in _ICONES.items() if chave in nomes), "•")
        return f'<span class="icone" aria-hidden="true">{emoji}</span>'

    return re.sub(
        r"<i\b[^>]*\bclass\s*=\s*[\"']([^\"']*)[\"'][^>]*>\s*</i>", troca, html, flags=re.I
    )


def _imagens_do_html_que_faltam(html, pasta_static):
    """[(src, alt)] das <img> fixas do HTML cujo arquivo não existe em static/."""

    achados = []
    for m in re.finditer(r"<img\b[^>]*>", html, re.I):
        tag = m.group(0)
        src = re.search(r"\bsrc\s*=\s*[\"']([^\"']+)[\"']", tag, re.I)
        if not src:
            continue
        valor = src.group(1)
        if re.match(r"(https?:|data:|//)", valor) or "${" in valor or ".." in valor:
            continue
        if os.path.exists(os.path.join(pasta_static, valor.split("?")[0].lstrip("/"))):
            continue
        alt = re.search(r"\balt\s*=\s*[\"']([^\"']*)[\"']", tag, re.I)
        achados.append((valor, alt.group(1) if alt else ""))
    return achados



# ------------------------------------------------------------------- menu

def _consertar_ancoras(html):
    """Links do menu como href="#roupas" sem nenhum id="roupas" na página não
    fazem nada. Aponta cada um para o id mais parecido; se não houver, para a
    lista principal (o primeiro "...-container"). "Início" vai para o topo."""

    ids = set(re.findall(r'\bid\s*=\s*["\']([^"\']+)["\']', html))
    containers = re.findall(r'\bid\s*=\s*["\']([\w-]+-container)["\']', html)
    principal = containers[0] if containers else None
    topo = {"inicio", "home", "topo", "top"}
    usou_topo = False

    def alvo(m):
        nonlocal usou_topo
        nome = m.group(2)
        if nome in ids or not nome.strip("-_"):
            return m.group(0)
        chave = unicodedata.normalize("NFD", nome.lower())
        chave = "".join(c for c in chave if unicodedata.category(c) != "Mn")
        if chave in topo:
            usou_topo = True
            return f'{m.group(1)}#topo{m.group(3)}'
        candidatos = [f"{nome}-container"] + [
            i for i in sorted(ids) if len(chave) >= 4 and (i.lower().startswith(chave) or chave in i.lower())
        ]
        novo = next((c for c in candidatos if c in ids), principal)
        return f'{m.group(1)}#{novo}{m.group(3)}' if novo else m.group(0)

    novo_html = re.sub(r'(href\s*=\s*["\'])#([^"\'\s]+)(["\'])', alvo, html, flags=re.I)

    if usou_topo and "topo" not in ids:
        corpo = re.search(r"<body\b([^>]*)>", novo_html, re.I)
        if corpo and not re.search(r"\bid\s*=", corpo.group(1), re.I):
            novo_html = novo_html.replace(corpo.group(0), f'<body id="topo"{corpo.group(1)}>', 1)

    return novo_html


_SECOES_IGNORADAS = {"hero", "topo", "mensagem-status", "mensagem", "status", "rodape", "footer", "header", "cabecalho"}


def _texto_limpo(trecho):
    texto = re.sub(r"<[^>]+>", " ", trecho)
    return re.sub(r"\s+", " ", html_lib.unescape(texto)).strip()


def _garantir_menu(html):
    """Se a página não tem <nav>, cria um menu no cabeçalho com links para as
    seções que existem nela. Não depende do tema: usa só o que está no HTML."""

    if re.search(r"<nav\b", html, re.I):
        return html

    itens, vistos = [], set()

    for m in re.finditer(r"<section\b([^>]*)>(.*?)</section>", html, re.I | re.S):
        id_ = re.search(r"\bid\s*=\s*[\"']([^\"']+)[\"']", m.group(1), re.I)
        if not id_ or id_.group(1).lower() in _SECOES_IGNORADAS or id_.group(1) in vistos:
            continue
        titulo = re.search(r"<h[1-6]\b[^>]*>(.*?)</h[1-6]>", m.group(2), re.I | re.S)
        rotulo = _texto_limpo(titulo.group(1)) if titulo else ""
        rotulo = rotulo or id_.group(1).replace("-", " ").replace("_", " ").capitalize()
        itens.append((id_.group(1), rotulo))
        vistos.add(id_.group(1))

    if not itens:  # sem <section>: usa os containers de dados (ex: produtos-container)
        for m in re.finditer(r"\bid\s*=\s*[\"']([\w-]+)-container[\"']", html, re.I):
            if m.group(1) not in vistos:
                itens.append((m.group(1) + "-container", m.group(1).replace("-", " ").replace("_", " ").capitalize()))
                vistos.add(m.group(1))

    if not itens:
        return html

    links = "".join(
        f'<a href="#{id_}">{_escapar(rotulo if len(rotulo) <= 22 else rotulo[:21] + "…")}</a>'
        for id_, rotulo in itens[:6]
    )
    nav = f'<nav class="menu-auto" aria-label="Menu principal">{links}</nav>'

    if re.search(r"</header>", html, re.I):
        return re.sub(r"</header>", nav + "</header>", html, count=1, flags=re.I)

    corpo = re.search(r"<body\b[^>]*>", html, re.I)
    return html[:corpo.end()] + nav + html[corpo.end():] if corpo else html


_CSS_MENU = (
    f"\n/* {_MARCA_MENU} */\n"
    "html { scroll-behavior: smooth; }\n"
    "header { flex-wrap: wrap; }\n"
    "nav.menu-auto {\n    display: flex;\n    flex-wrap: wrap;\n    justify-content: center;\n"
    "    gap: 8px 22px;\n    flex-basis: 100%;\n    width: 100%;\n    margin-top: 10px;\n}\n"
    "nav.menu-auto a {\n    color: var(--texto, inherit);\n    text-decoration: none;\n    font-weight: 600;\n"
    "    padding: 6px 4px;\n    border-bottom: 2px solid transparent;\n}\n"
    "nav.menu-auto a:hover, nav.menu-auto a:focus {\n    color: var(--primaria, currentColor);\n"
    "    border-bottom-color: var(--primaria, currentColor);\n    outline: none;\n}\n"
)


# ------------------------------------------------------------- o projeto

def _ler(caminho):
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            return arquivo.read()
    except OSError:
        return None


def _linhas_com_imagem(schema):
    """[(tabela, coluna_imagem, id, nome, valor_atual)] lido de um banco em memória."""

    achados = []
    banco = sqlite3.connect(":memory:")

    try:
        banco.executescript(schema)

        for (tabela,) in banco.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall():

            info = banco.execute(f'PRAGMA table_info("{tabela}")').fetchall()
            colunas = [c[1] for c in info]
            coluna_img = next((c for c in colunas if _COLUNAS_DE_IMAGEM.search(c)), None)

            if not coluna_img:
                continue

            # a chave primária pode ter qualquer nome (id, id_produto...): usa o rowid
            chaves = {c[1] for c in info if c[5]} | {c for c in colunas if c.lower().startswith("id")}

            coluna_nome = next(
                (c for c in _COLUNAS_DE_NOME if c in colunas),
                next((c for c in colunas if c not in chaves and c != coluna_img), colunas[0])
            )

            for id_, nome, valor in banco.execute(
                f'SELECT rowid, "{coluna_nome}", "{coluna_img}" FROM "{tabela}"'
            ):
                achados.append((tabela, coluna_img, id_, str(nome), valor))

    except sqlite3.Error:
        return []
    finally:
        banco.close()

    return achados


def gerar_imagens(pasta_projeto):
    """Cria as imagens que faltam. Devolve a lista do que foi feito."""

    pasta_static = os.path.join(pasta_projeto, "static")
    caminho_schema = os.path.join(pasta_projeto, "database", "schema.sql")
    caminho_css = os.path.join(pasta_static, "style.css")
    caminho_html = os.path.join(pasta_static, "index.html")

    schema = _ler(caminho_schema)
    css = _ler(caminho_css) or ""
    html = _ler(caminho_html) or ""

    if not schema:
        return []

    paleta = _paleta(css)
    mudancas = []
    usados = set()
    novo_schema = schema
    atualizacoes = []

    base_indice = _inteiro(os.path.basename(os.path.abspath(pasta_projeto)))
    criadas = 0

    for tabela, coluna, id_, nome, valor in _linhas_com_imagem(schema):

        if valor and os.path.exists(os.path.join(pasta_static, str(valor))):
            continue  # a imagem já existe

        arquivo = f"{_slug(nome)}.svg"
        while arquivo in usados:
            arquivo = f"{_slug(nome)}-{id_}.svg"
        usados.add(arquivo)

        relativo = f"img/{arquivo}"
        os.makedirs(os.path.join(pasta_static, "img"), exist_ok=True)

        with open(os.path.join(pasta_static, relativo), "w", encoding="utf-8") as saida:
            saida.write(_svg_card(nome, paleta, indice=base_indice + criadas))
        criadas += 1

        if valor and f"'{valor}'" in novo_schema:
            novo_schema = novo_schema.replace(f"'{valor}'", f"'{relativo}'")
        else:
            atualizacoes.append(f"UPDATE {tabela} SET {coluna} = '{relativo}' WHERE id = {id_};")

        mudancas.append(f"imagem criada: static/{relativo} ({nome})")

    if atualizacoes:
        novo_schema = novo_schema.rstrip() + "\n\n" + "\n".join(atualizacoes) + "\n"

    if novo_schema != schema:

        with open(caminho_schema, "w", encoding="utf-8") as saida:
            saida.write(novo_schema)

        # o banco antigo foi criado com os caminhos antigos: o backend recria
        banco_antigo = os.path.join(pasta_projeto, "database.db")
        if os.path.exists(banco_antigo):
            try:
                os.remove(banco_antigo)
                mudancas.append("database.db antigo removido (será recriado com as imagens novas)")
            except OSError:
                pass

    # ---- <img> fixas do HTML (logo, destaque...) que apontam para arquivos
    # que não existem, e ícones de uma biblioteca que não é carregada --------
    html_novo = html
    feitos = set()

    for src, alt in _imagens_do_html_que_faltam(html, pasta_static):

        if src in feitos:
            continue
        feitos.add(src)

        stem = _slug(os.path.splitext(os.path.basename(src))[0])
        pasta_rel = os.path.dirname(src.lstrip("/")) or "img"
        relativo = f"{pasta_rel}/{stem}.svg"
        pista = f"{stem} {alt}".lower()
        titulo = (re.search(r"<title>(.*?)</title>", html, re.S | re.I) or [None, "Site"])[1].strip()

        if re.search(r"logo|marca|brand", pista):
            svg = _svg_logo(alt or titulo, paleta)
        elif re.search(r"hero|banner|destaque|capa|cover|fundo", pista):
            svg = _svg_hero(alt or titulo, paleta)
        else:
            svg = _svg_card(alt or stem, paleta)

        os.makedirs(os.path.dirname(os.path.join(pasta_static, relativo)), exist_ok=True)
        with open(os.path.join(pasta_static, relativo), "w", encoding="utf-8") as saida:
            saida.write(svg)

        html_novo = html_novo.replace(f'src="{src}"', f'src="{relativo}"')
        html_novo = html_novo.replace(f"src='{src}'", f"src='{relativo}'")
        mudancas.append(f"imagem criada: static/{relativo} (no lugar de {src})")

    sem_icones = _trocar_icones(html_novo)
    if sem_icones != html_novo:
        html_novo = sem_icones
        mudancas.append("ícones sem biblioteca trocados por emoji no index.html")

    com_ancoras = _consertar_ancoras(html_novo)
    if com_ancoras != html_novo:
        html_novo = com_ancoras
        mudancas.append("links do menu que apontavam para ids inexistentes foram corrigidos")

    com_menu = _garantir_menu(html_novo)
    menu_criado = com_menu != html_novo
    if menu_criado:
        html_novo = com_menu
        mudancas.append("menu de navegação criado no cabeçalho do index.html")

    if html_novo != html:
        with open(caminho_html, "w", encoding="utf-8") as saida:
            saida.write(html_novo)
        html = html_novo

    if menu_criado and _MARCA_MENU not in css:
        with open(caminho_css, "a", encoding="utf-8") as saida:
            saida.write(_CSS_MENU)

    # ---- imagem de capa do #hero -----------------------------------------
    if re.search(r'id\s*=\s*["\']hero["\']', html) and _MARCA_CSS not in css:

        titulo = (re.search(r"<title>(.*?)</title>", html, re.S | re.I) or [None, "Site"])[1].strip()

        os.makedirs(os.path.join(pasta_static, "img"), exist_ok=True)

        with open(os.path.join(pasta_static, "img", "hero.svg"), "w", encoding="utf-8") as saida:
            saida.write(_svg_hero(titulo, paleta))

        with open(caminho_css, "a", encoding="utf-8") as saida:
            saida.write(
                f"\n/* {_MARCA_CSS} */\n"
                "#hero {\n"
                "    background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.7)), url(img/hero.svg);\n"
                "    background-size: cover;\n"
                "    background-position: center bottom;\n"
                "    min-height: 360px;\n"
                "    display: flex;\n    flex-wrap: wrap;\n    align-items: center;\n    justify-content: center;\n    gap: 12px;\n"
                "}\n"
                "#hero h1, #hero h2, #hero h3, #hero p {\n    flex-basis: 100%;\n    margin: 0;\n"
                "}\n"
                "#hero, #hero h1, #hero h2, #hero h3, #hero p {\n    color: #ffffff;\n}\n"
            )

        mudancas.append("criada a imagem de capa static/img/hero.svg (aplicada no #hero)")

    return mudancas


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Uso: python ilustrador.py <pasta_do_projeto_gerado>")
        sys.exit(2)

    for linha in gerar_imagens(sys.argv[1]) or ["nada a fazer"]:
        print(">>> ilustrador:", linha)
