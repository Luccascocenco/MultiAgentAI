"""Teste automático do site gerado pelos agentes.

Roda o backend.py do projeto numa cópia temporária (o projeto original não é
alterado), chama todas as rotas GET da API como um navegador faria e confere
se o HTML e o JavaScript combinam com o backend e com o banco de dados.

Devolve uma lista de problemas em português (lista vazia = tudo certo).

Uso dentro do orchestrator.py:

    from verificador import verificar_projeto
    problemas = verificar_projeto(caminho_projeto, gerar_backend_reserva)

Uso na linha de comando (para testar um projeto que já foi gerado):

    python verificador.py MultiAgentAI\\generated_projects\\NomeDoProjeto
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:  # mesma regra do ilustrador para saber se uma coluna é de imagem
    from ilustrador import eh_coluna_de_imagem as _eh_coluna_de_imagem
except Exception:  # pragma: no cover
    def _eh_coluna_de_imagem(nome):
        return bool(re.search(r"imagem|image|foto|img|banner|thumb", str(nome), re.I))

TEMPO_LIMITE = 40  # segundos para o backend.py subir e responder
MARCADOR = "@@RESULTADO@@"

# Propriedades comuns do JavaScript/DOM, que não são campos do banco.
_PROPRIEDADES_COMUNS = {
    "length", "push", "map", "forEach", "filter", "find", "toString",
    "toFixed", "toLocaleString", "style", "classList", "dataset",
    "textContent", "innerHTML", "value", "addEventListener", "appendChild",
    "children",
}

# Este programa roda num Python separado: se o backend.py gerado travar ou
# quebrar, o app (a janela de chat) não é afetado.
_PROGRAMA_DE_TESTE = r'''
import importlib.util, io, json, logging, os, sys

pasta = sys.argv[1]
os.chdir(pasta)
saida = {"erro_carga": None, "regras": [], "rotas": []}
registro = io.StringIO()

try:
    spec = importlib.util.spec_from_file_location(
        "backend_gerado", os.path.join(pasta, "backend.py")
    )
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    app = modulo.app
    if hasattr(modulo, "inicializar_banco"):
        modulo.inicializar_banco()
except BaseException as erro:
    saida["erro_carga"] = type(erro).__name__ + ": " + str(erro)
else:
    app.logger.addHandler(logging.StreamHandler(registro))
    cliente = app.test_client()

    for regra in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        metodos = sorted(m for m in regra.methods if m not in ("HEAD", "OPTIONS"))
        saida["regras"].append({"rota": regra.rule, "metodos": metodos})

        if regra.endpoint == "static" or "GET" not in metodos or regra.arguments:
            continue

        resposta = cliente.get(regra.rule)
        item = {
            "rota": regra.rule,
            "status": resposta.status_code,
            "tipo": resposta.mimetype,
        }

        if resposta.status_code >= 500:
            linhas = [l for l in registro.getvalue().splitlines() if l.strip()]
            item["detalhe"] = linhas[-1] if linhas else ""
            registro.seek(0)
            registro.truncate(0)
        elif resposta.mimetype == "application/json":
            dados = resposta.get_json(silent=True)
            if isinstance(dados, list):
                item["linhas"] = len(dados)
                item["campos"] = (
                    sorted(dados[0].keys())
                    if dados and isinstance(dados[0], dict) else []
                )

        saida["rotas"].append(item)

print("@@RESULTADO@@" + json.dumps(saida))
'''


def _ler(caminho):
    """Lê um arquivo de texto; devolve None se ele não existir."""

    try:
        with open(caminho, encoding="utf-8", errors="replace") as arquivo:
            return arquivo.read()
    except OSError:
        return None


def _resultado_vazio(erro):
    return {"erro_carga": erro, "regras": [], "rotas": []}


def _executar_teste(pasta_projeto):
    """Copia o projeto para uma pasta temporária e roda o teste lá."""

    temporaria = tempfile.mkdtemp(prefix="verificador_")

    try:
        copia = os.path.join(temporaria, "projeto")

        # O database.db fica de fora: o banco é recriado do zero a partir do
        # schema.sql, exatamente como na primeira vez que o site abre.
        shutil.copytree(
            pasta_projeto,
            copia,
            ignore=shutil.ignore_patterns(
                "database.db", "*.db-journal", "__pycache__", "*.log", "docs"
            ),
        )

        if not os.path.exists(os.path.join(copia, "backend.py")):
            return _resultado_vazio("o arquivo backend.py não existe no projeto")

        try:
            execucao = subprocess.run(
                [sys.executable, "-I", "-c", _PROGRAMA_DE_TESTE, copia],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=TEMPO_LIMITE,
                stdin=subprocess.DEVNULL,
                cwd=temporaria,
                env=dict(os.environ, PYTHONIOENCODING="utf-8"),
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except subprocess.TimeoutExpired:
            return _resultado_vazio(
                f"o backend.py não respondeu em {TEMPO_LIMITE} segundos "
                "(travou ao iniciar?)"
            )

        for linha in execucao.stdout.splitlines():
            if linha.startswith(MARCADOR):
                return json.loads(linha[len(MARCADOR):])

        detalhe = (execucao.stderr or execucao.stdout).strip().splitlines()

        return _resultado_vazio(
            "o teste não terminou: " + (detalhe[-1] if detalhe else "sem detalhes")
        )

    finally:
        shutil.rmtree(temporaria, ignore_errors=True)


def _regex_da_rota(rota):
    """Transforma '/api/produtos/<int:item_id>' num regex que aceita '/api/produtos/1'."""

    partes = re.split(r"(<[^>]+>)", rota)

    padrao = "".join(
        "[^/]+" if parte.startswith("<") else re.escape(parte)
        for parte in partes
    )

    return re.compile("^" + padrao + "/?$")


def _colunas_do_schema(sql):
    """{'tabela': {'coluna', ...}} lido dos CREATE TABLE do schema.sql."""

    tabelas = {}

    for nome, corpo in re.findall(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`\[]?(\w+)["`\]]?\s*\((.*?)\)\s*;',
        sql, re.IGNORECASE | re.DOTALL
    ):
        colunas, nivel, atual = [], 0, ""

        for letra in corpo + ",":
            if letra == "(":
                nivel += 1
            elif letra == ")":
                nivel -= 1
            if letra == "," and nivel == 0:
                colunas.append(atual.strip())
                atual = ""
            else:
                atual += letra

        tabelas[nome.lower()] = {
            c.split()[0].strip('"`[]').lower()
            for c in colunas
            if c and c.split()[0].upper() not in
            ("FOREIGN", "PRIMARY", "UNIQUE", "CHECK", "CONSTRAINT")
        }

    return tabelas


def _posts_do_js(js):
    """[(caminho, [chaves enviadas])] dos fetch(..., {method: "POST", body: JSON.stringify({...})})."""

    achados = []

    for m in re.finditer(r'fetch\(\s*["\'`](/api/[\w\-/]+)["\'`]\s*,', js):

        trecho = js[m.end(): m.end() + 500]

        if not re.search(r'method\s*:\s*["\']POST["\']', trecho, re.IGNORECASE):
            continue

        corpo = re.search(r'JSON\.stringify\(\s*\{([^}]*)\}', trecho)

        if corpo:
            achados.append((m.group(1), re.findall(r'\b(\w+)\s*:', corpo.group(1))))

    return achados


_NOMES_GLOBAIS = {
    "document", "window", "console", "Math", "Number", "String", "JSON",
    "Date", "Object", "Array", "this", "event", "undefined", "null",
    "true", "false", "navigator", "location", "localStorage",
}


def _fim_do_bloco_js(texto, inicio):
    nivel = 0
    for i in range(inicio, len(texto)):
        if texto[i] == "{":
            nivel += 1
        elif texto[i] == "}":
            nivel -= 1
            if nivel == 0:
                return i
    return len(texto)


def _usos_fora_de_escopo(js):
    """Nomes usados em ${...} que não existem naquele ponto do código.

    Ex.: um template com ${produto.nome} escrito ANTES do forEach que cria
    o "produto" dá ReferenceError e o site não mostra nada.
    """

    escopos = []  # (nome, inicio, fim)

    padrao_funcao = re.compile(
        r"(?:function\s*\w*\s*\(([^()]*)\)\s*\{)"        # function f(a, b) {
        r"|(?:\(([^()]*)\)\s*=>\s*(\{)?)"                # (a, b) => {  /  (a) => expr
        r"|(?:\b([A-Za-z_$][\w$]*)\s*=>\s*(\{)?)"        # a => {  /  a => expr
        r"|(?:\b\w+\s*\(([^()]*)\)\s*\{)"                # método(a) {  /  if (x) {
        r"|(?:catch\s*\(\s*(\w+)\s*\)\s*\{)"             # catch (e) {
    )

    for m in padrao_funcao.finditer(js):

        parametros = m.group(1) or m.group(2) or m.group(4) or m.group(6) or m.group(7) or ""
        nomes = re.findall(r"[A-Za-z_$][\w$]*", parametros.split("=")[0] if "{" not in parametros else parametros)

        abre_bloco = m.group(0).rstrip().endswith("{")

        if abre_bloco:
            fim = _fim_do_bloco_js(js, m.end() - 1)
        else:  # arrow com corpo de expressão: vai até o ")" ou ";" que fecha
            nivel, fim = 0, len(js)
            for i in range(m.end(), len(js)):
                c = js[i]
                if c in "([{":
                    nivel += 1
                elif c in ")]}":
                    nivel -= 1
                    if nivel < 0:
                        fim = i
                        break
                elif c == ";" and nivel == 0:
                    fim = i
                    break

        for nome in nomes:
            escopos.append((nome, m.start(), fim))

    declaradas = []  # (nome, posição)

    for m in re.finditer(r"\b(?:const|let|var)\s+(\{[^}]*\}|\[[^\]]*\]|[A-Za-z_$][\w$]*)", js):
        for nome in re.findall(r"[A-Za-z_$][\w$]*", m.group(1)):
            declaradas.append((nome, m.start()))

    for m in re.finditer(r"\bfor\s*\(\s*(?:const|let|var)\s+(\w+)", js):
        escopos.append((m.group(1), m.start(), _fim_do_bloco_js(js, js.find("{", m.end()) if js.find("{", m.end()) != -1 else m.end())))

    for m in re.finditer(r"\bfunction\s+([A-Za-z_$][\w$]*)", js):
        declaradas.append((m.group(1), 0))

    fora = set()

    for m in re.finditer(r"\$\{\s*([A-Za-z_$][\w$]*)", js):

        nome, pos = m.group(1), m.start()

        if nome in _NOMES_GLOBAIS:
            continue

        if any(n == nome and ini <= pos <= fim for n, ini, fim in escopos):
            continue

        if any(n == nome and p < pos for n, p in declaradas):
            continue

        fora.add(nome)

    return sorted(fora)


def _problemas_graves_do_js(js):
    """Erros que deixam o site sem dados, mesmo com o backend funcionando."""

    problemas = []

    for url in sorted(set(re.findall(r"""["'`](https?://[^"'`\s]+)""", js))):
        host = re.sub(r"^https?://", "", url).split("/")[0].split(":")[0]
        if host not in ("localhost", "127.0.0.1", "0.0.0.0") and (
            "/api" in url or "example." in host
        ):
            problemas.append(
                f'o script.js busca dados em um endereço externo ({url}) '
                "e não no próprio backend (/api/...)"
            )

    if re.search(r"n[ãa]o implementad|not implemented|\bTODO\b|implementar", js, re.IGNORECASE):
        problemas.append(
            "o script.js tem funções sem implementação (só comentários): "
            "os botões ligados a elas não fazem nada"
        )

    for nome in _usos_fora_de_escopo(js):
        problemas.append(
            f'o script.js usa "{nome}" dentro de um texto ${{...}} num lugar '
            "onde essa variável não foi declarada (dá erro e a lista não aparece)"
        )

    return problemas



def _verificar(pasta_projeto):
    """Devolve (problemas, backend_quebrado, resultado_do_teste)."""

    resultado = _executar_teste(pasta_projeto)
    problemas = []

    if resultado["erro_carga"]:
        return (
            ["o backend.py não inicia: " + resultado["erro_carga"]],
            True,
            resultado,
        )

    rotas = {r["rota"]: r for r in resultado["rotas"]}
    quebrado = False

    for rota in resultado["rotas"]:
        if rota["status"] >= 500:
            quebrado = True
            problemas.append(
                f'a rota GET {rota["rota"]} deu erro {rota["status"]}: '
                f'{rota.get("detalhe") or "sem detalhes"}'
            )

    # ---------------- HTML, CSS e JavaScript ----------------
    pasta_static = os.path.join(pasta_projeto, "static")
    html = _ler(os.path.join(pasta_static, "index.html"))

    if html is None:
        problemas.append("falta o arquivo static/index.html (o site não tem página inicial)")
        return problemas, quebrado, resultado

    pagina = rotas.get("/")

    if pagina is None:
        problemas.append('o backend.py não tem a rota "/" (página inicial)')
    elif pagina["status"] == 200 and pagina["tipo"] != "text/html":
        problemas.append(f'a rota "/" não devolve o index.html (tipo: {pagina["tipo"]})')
    elif pagina["status"] not in (200, 500):
        problemas.append(f'a página inicial (/) respondeu {pagina["status"]} em vez de 200')

    if not re.search(r'<link[^>]+stylesheet', html, re.IGNORECASE):
        problemas.append("o index.html não chama nenhum arquivo CSS (a página fica sem estilo)")

    if not re.search(r'<script[^>]+src=', html, re.IGNORECASE):
        problemas.append("o index.html não chama nenhum arquivo JavaScript (nada funciona)")

    ids_do_html = set(re.findall(r'\bid\s*=\s*["\']([^"\']+)["\']', html))

    for ancora in sorted(set(re.findall(r'href\s*=\s*["\']#([\w-]+)["\']', html))):
        if ancora not in ids_do_html:
            problemas.append(
                f'o menu aponta para "#{ancora}", mas não existe nenhum '
                f'elemento com id="{ancora}" no index.html'
            )

    referencias = (
        re.findall(r'<link[^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
        + re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
    )

    arquivos_js = []

    for ref in referencias:

        if re.match(r"^(https?:)?//|^data:", ref):
            continue  # arquivo externo (CDN): não dá para conferir aqui

        limpo = ref.split("?")[0].lstrip("/")
        caminho = os.path.join(pasta_static, limpo)

        if not os.path.exists(caminho):
            problemas.append(f'o index.html chama "{ref}", mas o arquivo static/{limpo} não existe')
        elif limpo.lower().endswith(".js"):
            arquivos_js.append(caminho)

    js = "\n".join(_ler(c) or "" for c in arquivos_js)

    if not js.strip():
        return problemas, quebrado, resultado

    # O JavaScript procura elementos pelo id: eles precisam existir no HTML.
    ids_html = set(re.findall(r'\bid\s*=\s*["\']([^"\']+)["\']', html))
    ids_criados_no_js = set(re.findall(r'\bid\s*=\s*["\\\']?([\w-]+)', js))

    ids_usados = set(
        re.findall(r'getElementById\(\s*["\']([^"\']+)["\']\s*\)', js)
        + re.findall(r'querySelector\(\s*["\']#([\w-]+)["\']\s*\)', js)
    )

    for id_usado in sorted(ids_usados):
        if id_usado not in ids_html and id_usado not in ids_criados_no_js:
            problemas.append(
                f'o script.js procura o elemento id="{id_usado}", mas ele não '
                f'existe no index.html (ids do HTML: {", ".join(sorted(ids_html)[:8]) or "nenhum"})'
            )

    problemas.extend(_problemas_graves_do_js(js))

    if resultado["rotas"] and not re.search(r"""["'`]/api/""", js) and any(
        r["rota"].startswith("/api/") and r.get("linhas", 0) > 0 for r in resultado["rotas"]
    ):
        problemas.append(
            "o script.js não busca nenhum dado de /api/...: a página não mostra "
            "o que está no banco de dados"
        )

    # Botões do HTML precisam fazer alguma coisa (ter ação no JavaScript).
    for id_botao, texto in re.findall(
        r'<button\b[^>]*\bid\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</button>',
        html, re.IGNORECASE | re.DOTALL
    ):
        if "onclick" in html.lower() and re.search(
            rf'id\s*=\s*["\']{re.escape(id_botao)}["\'][^>]*onclick', html
        ):
            continue
        if id_botao not in js:
            problemas.append(
                f'o botão "{texto.strip()}" (id="{id_botao}") não tem nenhuma '
                "ação no script.js (clicar nele não faz nada)"
            )

    # O que o JavaScript envia (POST) precisa ser coluna da tabela.
    colunas = _colunas_do_schema(
        _ler(os.path.join(pasta_projeto, "database", "schema.sql")) or ""
    )

    for caminho, chaves in _posts_do_js(js):
        tabela = caminho.rstrip("/").split("/")[-1].lower()
        if tabela in colunas:
            erradas = [c for c in chaves if c.lower() not in colunas[tabela]]
            if erradas:
                problemas.append(
                    f'o script.js envia {", ".join(erradas)} em POST {caminho}, '
                    f'mas a tabela {tabela} só tem as colunas: '
                    f'{", ".join(sorted(colunas[tabela]))}'
                )

    # Imagens citadas no banco precisam existir em static/.
    schema_texto = _ler(os.path.join(pasta_projeto, "database", "schema.sql")) or ""
    faltam = sorted({
        img for img in re.findall(
            r"'([^'\n]+\.(?:jpe?g|png|gif|webp|svg))'", schema_texto, re.I
        )
        if not os.path.exists(os.path.join(pasta_static, img))
    })
    if faltam:
        problemas.append(
            f"o banco cita {len(faltam)} imagem(ns) que não existem em static/ "
            f"(ex.: {faltam[0]}): os cards ficam com a figura quebrada"
        )

    # <img> fixas do HTML (logo, destaque...) precisam existir em static/.
    try:
        from ilustrador import _imagens_do_html_que_faltam
        html_faltam = _imagens_do_html_que_faltam(html, pasta_static)
    except Exception:
        html_faltam = []
    if html_faltam:
        problemas.append(
            f"o index.html usa {len(html_faltam)} imagem(ns) que não existem em static/ "
            f"(ex.: {html_faltam[0][0]}): logo ou imagem de destaque quebrados"
        )

    # Ícones de biblioteca (Font Awesome) sem a biblioteca: botões ficam vazios.
    if re.search(r'<i\s[^>]*class\s*=\s*["\'][^"\']*\bfa[srbl]?\b', html, re.I) and not re.search(
        r"font-?awesome|fontawesome", html, re.I
    ):
        problemas.append(
            "o index.html usa ícones <i class=\"fa...\"> mas a biblioteca de ícones "
            "não é carregada: os botões ficam vazios (ícone não mostra a imagem)"
        )

    # As rotas chamadas pelo JavaScript precisam existir no backend.
    regras = resultado["regras"]
    caminhos_js = set(re.findall(r'["\'`](/api/[^"\'`?\s]*)', js))

    for caminho in sorted(caminhos_js):
        exemplo = re.sub(r"\$\{[^}]*\}", "1", caminho)
        if not any(_regex_da_rota(r["rota"]).match(exemplo) for r in regras):
            problemas.append(f'o script.js chama "{caminho}", mas o backend.py não tem essa rota')

    # Rotas que o JavaScript lê (GET): precisam devolver registros, e os
    # campos usados no JavaScript precisam existir no que a API devolve.
    leituras = set(
        re.findall(r'fetch\(\s*["\'`](/api/[^"\'`?]+)["\'`]\s*\)', js)
        + re.findall(r'(?:const|let|var)\s+\w+\s*=\s*["\'`](/api/[^"\'`?]+)["\'`]', js)
    )

    campos_api = set()

    for caminho in sorted(leituras):

        rota = rotas.get(caminho.rstrip("/"))

        if rota is None or "linhas" not in rota:
            continue

        if rota["linhas"] == 0:
            problemas.append(
                f"a rota {caminho} devolve 0 registros: a página vai aparecer "
                "vazia (o schema.sql tem INSERTs de exemplo?)"
            )

        campos_api |= set(rota.get("campos", []))

    if campos_api:

        fontes = set(re.findall(
            r'(?:const|let|var)\s+(\w+)\s*=\s*await\s+[\w.]+\.json\(\)', js
        ))
        fontes |= set(re.findall(r'\.then\(\s*\(?\s*(\w+)\s*\)?\s*=>', js))

        usados = {}

        for fonte in fontes:

            nome = re.escape(fonte)

            variaveis = set(re.findall(rf'\b{nome}\.(?:forEach|map)\(\s*\(?\s*(\w+)', js))
            variaveis |= set(re.findall(
                rf'for\s*\(\s*(?:const|let|var)\s+(\w+)\s+of\s+{nome}\b', js
            ))

            for variavel in variaveis:
                for campo in re.findall(rf'\b{re.escape(variavel)}\.(\w+)', js):
                    if campo not in _PROPRIEDADES_COMUNS and campo not in campos_api:
                        usados.setdefault(campo, variavel)

        # a API devolve uma imagem, mas o card não a mostra
        for campo in sorted(campos_api):
            if _eh_coluna_de_imagem(campo) and not re.search(
                rf"\.{re.escape(campo)}\b", js
            ):
                problemas.append(
                    f'a API devolve o campo "{campo}", mas o script.js não mostra '
                    "a imagem nos cards"
                )

        for campo, variavel in sorted(usados.items()):
            problemas.append(
                f'o script.js usa {variavel}.{campo}, mas a API não devolve o '
                f'campo "{campo}" (campos da API: {", ".join(sorted(campos_api))})'
            )

    problemas.extend(_campos_por_rota(js, rotas))

    return problemas, quebrado, resultado


def _campos_por_rota(js, rotas):
    """Confere, rota por rota, os campos que cada trecho do JS usa nos itens
    devolvidos por ela (ex.: a lista de pedidos não tem "nome" nem "preco",
    mesmo que a de produtos tenha)."""

    achados = []
    inicios = [m.start() for m in re.finditer(r"(?:async\s+)?function\s+\w+|\bconst\s+\w+\s*=\s*(?:async\s*)?\(", js)]
    inicios.append(len(js))

    for a, b in zip(inicios, inicios[1:]):

        trecho = js[a:b]
        m = re.search(r'fetch\(\s*["\'`](/api/[^"\'`?/]+)/?["\'`]\s*\)', trecho)

        if not m:
            continue

        rota = rotas.get(m.group(1))

        if not rota or "campos" not in rota or not rota.get("linhas"):
            continue

        campos = set(rota["campos"])
        fontes = set(re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*await\s+[\w.]+\.json\(\)', trecho))
        fontes |= set(re.findall(r'\.then\(\s*\(?\s*(\w+)\s*\)?\s*=>', trecho))

        for fonte in fontes:
            nome = re.escape(fonte)
            variaveis = set(re.findall(rf'\b{nome}\.(?:forEach|map)\(\s*\(?\s*(\w+)', trecho))
            variaveis |= set(re.findall(rf'for\s*\(\s*(?:const|let|var)\s+(\w+)\s+of\s+{nome}\b', trecho))

            for variavel in variaveis:
                for campo in dict.fromkeys(re.findall(rf'\b{re.escape(variavel)}\.(\w+)', trecho)):
                    if campo not in _PROPRIEDADES_COMUNS and campo not in campos:
                        achados.append(
                            f'o script.js usa {variavel}.{campo} nos itens de {m.group(1)}, mas essa '
                            f'rota não devolve o campo "{campo}" (campos: {", ".join(sorted(campos))})'
                        )

    return achados



# ----------------------------------------------------------------------
# Reparo automático do front-end
# ----------------------------------------------------------------------

_MARCA_LIGACOES = "Ligações automáticas"


def _sem_acento(texto):
    import unicodedata
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    ).lower()


def _fim_do_bloco(texto, inicio):
    """Índice da '}' que fecha a '{' que está em texto[inicio]."""

    nivel = 0

    for i in range(inicio, len(texto)):
        if texto[i] == "{":
            nivel += 1
        elif texto[i] == "}":
            nivel -= 1
            if nivel == 0:
                return i

    return -1


_JS_RECONSTRUIDO = r"""// ===== script.js refeito automaticamente pelo verificador =====
// O script original tinha erros que deixavam a página sem dados. Este monta
// as listas direto da API (/api/...) e liga os botões às seções da página.
const CONFIG = __CONFIG__;

function criar(tag, classe, texto) {
    const elemento = document.createElement(tag);
    if (classe) { elemento.className = classe; }
    if (texto !== undefined && texto !== null) { elemento.textContent = texto; }
    return elemento;
}

function rotulo(chave) {
    const texto = chave.replace(/_/g, " ");
    return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function formatar(chave, valor) {
    if (/preco|valor|total/i.test(chave) && valor !== null && valor !== "" && !isNaN(Number(valor))) {
        return "R$ " + Number(valor).toFixed(2).replace(".", ",");
    }
    return valor;
}

let temporizador = null;

function mostrarMensagem(texto) {
    const area = document.getElementById(CONFIG.status);
    if (!area) { return; }
    area.textContent = texto;
    clearTimeout(temporizador);
    temporizador = setTimeout(() => { area.textContent = ""; }, 4000);
}

async function buscar(rota) {
    const resposta = await fetch(rota);
    if (!resposta.ok) { throw new Error(rota + " respondeu " + resposta.status); }
    return resposta.json();
}

async function carregarColecao(colecao) {
    const container = document.getElementById(colecao.container);
    if (!container) { return; }

    try {
        const itens = await buscar(colecao.rota);
        const nomes = {};

        for (const campo of Object.keys(colecao.relacoes)) {
            const relacao = colecao.relacoes[campo];
            const lista = await buscar(relacao.rota);
            nomes[campo] = {};
            lista.forEach((registro) => { nomes[campo][registro.id] = registro[relacao.nome]; });
        }

        container.innerHTML = "";

        if (!itens.length) {
            container.textContent = "Nada cadastrado por enquanto.";
            return;
        }

        itens.forEach((item) => {
            const card = criar("div", CONFIG.classeCard);
            const relacionados = Object.keys(colecao.relacoes);
            let titulo = colecao.nome ? item[colecao.nome] : null;

            if (!titulo && relacionados.length) {
                titulo = nomes[relacionados[0]][item[relacionados[0]]];
            }
            if (!titulo) { titulo = rotulo(colecao.tabela) + " " + (item[colecao.chave || "id"] ?? ""); }

            if (colecao.imagem && item[colecao.imagem]) {
                const imagem = criar("img", "card-img");
                imagem.src = item[colecao.imagem];
                imagem.alt = String(titulo);
                imagem.loading = "lazy";
                imagem.onerror = () => { imagem.style.display = "none"; };
                card.appendChild(imagem);
            }

            card.appendChild(criar("h3", "", titulo));

            if (colecao.categoria && item[colecao.categoria]) {
                card.appendChild(criar("span", "etiqueta", item[colecao.categoria]));
            }

            if (colecao.descricao && item[colecao.descricao]) {
                card.appendChild(criar("p", "", item[colecao.descricao]));
            }

            const jaMostrados = [
                "id", colecao.chave, colecao.nome, colecao.imagem, colecao.categoria, colecao.descricao,
            ];

            Object.keys(item).forEach((chave) => {
                if (jaMostrados.includes(chave) || chave in colecao.relacoes) { return; }
                if (item[chave] === null || item[chave] === "") { return; }
                const valor = item[chave];
                if (/^(preco|valor)/i.test(chave) && !isNaN(Number(valor))) {
                    card.appendChild(criar("p", "preco", formatar(chave, valor)));
                } else if (/^(avaliacao|nota|rating)/i.test(chave) && !isNaN(Number(valor))) {
                    card.appendChild(criar("p", "avaliacao", "★ " + Number(valor).toFixed(1).replace(".", ",")));
                } else {
                    const nomeCurto = chave.replace(new RegExp("_" + colecao.tabela + "$", "i"), "");
                    card.appendChild(criar("p", "", rotulo(nomeCurto) + ": " + formatar(chave, valor)));
                }
            });

            Object.keys(colecao.relacoes).forEach((campo) => {
                const relacionado = nomes[campo][item[campo]];
                if (relacionado && relacionado !== titulo) {
                    card.appendChild(criar("p", "", rotulo(campo.replace(/_id$/, "")) + ": " + relacionado));
                }
            });

            if (colecao.principal) {
                const botao = criar("button", "", CONFIG.textoBotao);
                botao.addEventListener("click", () => {
                    mostrarMensagem("Você escolheu: " + titulo + ".");
                });
                card.appendChild(botao);
            }

            container.appendChild(card);
        });
    } catch (erro) {
        console.error(erro);
        container.textContent = "Não foi possível carregar os dados. O servidor está rodando?";
    }
}

CONFIG.colecoes.forEach(carregarColecao);

CONFIG.ligacoes.forEach(([idBotao, idAlvo]) => {
    const botao = document.getElementById(idBotao);
    if (!botao) { return; }
    botao.addEventListener("click", () => {
        if (idAlvo === "topo") {
            window.scrollTo({ top: 0, behavior: "smooth" });
            return;
        }
        const alvo = document.getElementById(idAlvo);
        if (alvo) { alvo.scrollIntoView({ behavior: "smooth" }); }
    });
});
"""


def _radical(palavra):
    p = _sem_acento(palavra)
    return p[:-1] if p.endswith("s") and len(p) > 4 else p


def _nomes_do_banco(pasta_projeto):
    """Nomes (sem acento, minúsculos) dos itens que estão no schema.sql."""
    import sqlite3
    schema = _ler(os.path.join(pasta_projeto, "database", "schema.sql")) or ""
    nomes = set()
    banco = sqlite3.connect(":memory:")
    try:
        banco.executescript(schema)
        for (tabela,) in banco.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall():
            colunas = [c[1] for c in banco.execute(f'PRAGMA table_info("{tabela}")')]
            for c in colunas:
                if re.match(r"(nome|titulo|name|title)", c, re.I):
                    for (v,) in banco.execute(f'SELECT "{c}" FROM "{tabela}"'):
                        if v:
                            nomes.add(re.sub(r"\s+", " ", _sem_acento(str(v)).lower()).strip())
    except sqlite3.Error:
        pass
    finally:
        banco.close()
    return nomes


def _remover_cards_fixos(html, nomes):
    """Tira do HTML os cards escritos à mão que só repetem itens do banco
    (a lista de verdade vem da API) e as seções que ficam vazias por isso."""
    if not nomes:
        return html, 0

    removidos = 0

    def tira(m):
        nonlocal removidos
        titulo = re.search(r"<h[2-4]\b[^>]*>(.*?)</h[2-4]>", m.group(1), re.S | re.I)
        if not titulo:
            return m.group(0)
        texto = re.sub(r"<[^>]+>", "", titulo.group(1))
        texto = re.sub(r"\s+", " ", _sem_acento(texto).lower()).strip()
        if texto in nomes:
            removidos += 1
            return ""
        return m.group(0)

    novo = re.sub(
        r'<div\b[^>]*class\s*=\s*"[^"]*\b(?:card|produto-card|item-card)\b[^"]*"[^>]*>'
        r'((?:(?!<div\b|</div>).)*)</div>[ \t]*\n?',
        tira, html, flags=re.S | re.I
    )

    if removidos:
        # seção que sobrou só com título e uma grade vazia
        novo = re.sub(
            r'<section\b[^>]*>\s*<h2\b[^>]*>[^<]*</h2>\s*<div\b[^>]*>\s*</div>\s*</section>[ \t]*\n?',
            "", novo, flags=re.S | re.I
        )
    return novo, removidos


def _garantir_classe(html, container, classe):
    """Se o container da lista não tem uma classe de grade, ganha a 'classe'
    (senão os cards ficam empilhados, um por linha)."""
    m = re.search(
        r'<(div|section|ul)\b([^>]*\bid\s*=\s*["\']' + re.escape(container) + r'["\'][^>]*)>', html, re.I
    )
    if not m or re.search(r'class\s*=\s*"[^"]*grid[^"]*"', m.group(2), re.I):
        return html
    attrs = m.group(2)
    if re.search(r'class\s*=\s*"[^"]*"', attrs):
        attrs = re.sub(r'class\s*=\s*"([^"]*)"', lambda c: f'class="{c.group(1)} {classe}"', attrs, count=1)
    else:
        attrs += f' class="{classe}"'
    return html[:m.start()] + f"<{m.group(1)}{attrs}>" + html[m.end():]


def _reconstruir_front(pasta_projeto, resultado, problemas):
    """Refaz o script.js (e as seções que faltam no HTML) a partir da API.

    Usado quando o JavaScript gerado pelo agente está quebrado de um jeito
    que não dá para remendar (endereço externo, variável inexistente,
    funções vazias). A API e o banco são a fonte da verdade.
    """

    pasta_static = os.path.join(pasta_projeto, "static")
    caminho_html = os.path.join(pasta_static, "index.html")
    caminho_js = os.path.join(pasta_static, "script.js")
    caminho_css = os.path.join(pasta_static, "style.css")

    html = _ler(caminho_html)
    js_antigo = _ler(caminho_js) or ""
    css = _ler(caminho_css) or ""

    if not html:
        return []

    rotas = {
        r["rota"]: r for r in resultado["rotas"]
        if r["rota"].startswith("/api/") and "linhas" in r and "<" not in r["rota"]
    }

    if not rotas:
        return []

    def tabela_de(rota):
        return rota.rstrip("/").split("/")[-1]

    # tabelas só de apoio (id + nome) não ganham seção própria
    def tem_nome(info):
        return any(
            re.match(r"(nome|titulo|name|title|autor|author|cliente|assunto)", c, re.I)
            for c in info.get("campos", [])
        )

    # tabelas sem nome/título (ex: pedido, favorito: só chaves, quantidade e
    # datas) não são vitrine e não ganham seção; só voltam se não houver outra
    colecoes_rotas = [
        r for r, info in rotas.items()
        if set(info.get("campos", [])) - {"id", "nome"} and tem_nome(info)
    ] or [
        r for r, info in rotas.items()
        if set(info.get("campos", [])) - {"id", "nome"}
    ] or list(rotas)

    def eh_principal(rota):
        campos = rotas[rota].get("campos", [])
        return (
            any(re.match(r"(preco|valor)", c, re.I) for c in campos)
            and any(re.match(r"(nome|titulo|name|title)", c, re.I) for c in campos)
        )

    colecoes_rotas.sort(key=lambda r: (not eh_principal(r), list(rotas).index(r)))
    principal_rota = colecoes_rotas[0]

    ids_html = set(re.findall(r'\bid\s*=\s*["\']([^"\']+)["\']', html))
    classes_html = set(re.findall(r'class\s*=\s*"([^"]+)"', html))

    classes_css = set(re.findall(r"\.([A-Za-z_][\w-]*)", css))
    grade_existente = next(
        (c for grupo in classes_html for c in grupo.split() if "grid" in c.lower()), None
    ) or next((c for c in sorted(classes_css) if "grid" in c.lower()), None)
    classe_grade = grade_existente or "grade-itens"

    m_card = re.search(r'className\s*=\s*["\']([^"\']+)["\']', js_antigo)
    classe_card = (
        m_card.group(1).split()[0] if m_card
        else next((c for c in sorted(classes_css) if "card" in c.lower()), "item-card")
    )

    mudancas = []
    secoes = []        # (id_alvo, palavras-chave)
    colecoes = []
    novas_secoes = ""

    usados = set()

    for rota in colecoes_rotas:

        tabela = tabela_de(rota)
        campos = rotas[rota].get("campos", [])
        principal = rota == principal_rota

        existentes = [
            i for i in ids_html
            if tabela.lower() in i.lower() and re.search(r"container|lista|grid|itens", i, re.I) and i not in usados
        ]
        if not existentes and principal:
            existentes = [
                i for i in sorted(ids_html)
                if re.search(r"container|grid|lista", i, re.I)
                and not any(tabela_de(o).lower() in i.lower() for o in colecoes_rotas if o != rota)
                and i not in usados
            ]

        if existentes:
            container = existentes[0]
        else:
            container = f"{tabela}-container"
            titulo_secao = tabela.replace("_", " ").capitalize()
            novas_secoes += (
                f'        <section id="{tabela}">\n'
                f"            <h2>{titulo_secao}</h2>\n"
                f'            <div id="{container}" class="{classe_grade}"></div>\n'
                "        </section>\n"
            )
            mudancas.append(f'criada no HTML a seção "{titulo_secao}" (vem de {rota})')

        usados.add(container)

        if existentes:
            html = _garantir_classe(html, container, classe_grade)

        # lista principal solta no <main>: ganha seção própria e um título
        if principal and not re.search(
            r'<section\b[^>]*>(?:(?!</section>).)*?\bid\s*=\s*["\']' + re.escape(container) + r'["\']',
            html, re.DOTALL
        ):
            botoes = re.findall(r"<button\b[^>]*>(.*?)</button>", html, re.IGNORECASE | re.DOTALL)
            titulo_p = next(
                (t.strip() for t in botoes if _radical(t.strip()) in ("cardapio", "catalogo", "loja", "vitrine")),
                tabela.replace("_", " ").capitalize()
            )
            html, trocou = re.subn(
                r'(<div\b[^>]*\bid\s*=\s*["\']' + re.escape(container) + r'["\'][^>]*>\s*</div>)',
                f'<section id="{tabela}">\n            <h2>{titulo_p}</h2>\n            \\1\n        </section>',
                html, count=1
            )
            if trocou:
                mudancas.append(f'a lista principal ganhou a seção "{titulo_p}"')

        # alvo de rolagem: a seção que contém o container (ou o próprio container)
        m_sec = re.search(
            r'<section\b[^>]*\bid\s*=\s*["\']([^"\']+)["\'][^>]*>(?:(?!</section>).)*?\bid\s*=\s*["\']'
            + re.escape(container) + r'["\']', html, re.DOTALL
        )
        alvo = m_sec.group(1) if m_sec else (tabela if container == f"{tabela}-container" else container)

        palavras = {_radical(w) for w in re.findall(r"[A-Za-zÀ-ÿ]+", alvo + " " + tabela + " " + container)}
        if principal:
            palavras |= {"cardapio", "catalogo", "produto", "item", "loja", "vitrine", "espetaculo", "atracao", "servico"}
        secoes.append((alvo, palavras))

        nome = next((c for c in ("nome", "titulo", "name", "title") if c in campos), None) or next(
            (c for c in campos if re.match(r"(nome|titulo|name|title)", c, re.I)), None
        )
        imagem = next((c for c in campos if _eh_coluna_de_imagem(c)), None)
        categoria = next((c for c in campos if c in ("categoria", "tipo", "category")), None) or next(
            (c for c in campos if re.match(r"(categoria|tipo|category)", c, re.I)), None
        )
        descricao = next((c for c in campos if c in ("descricao", "detalhes", "resumo", "description")), None) or next(
            (c for c in campos if re.match(r"(descri|resumo|detalhe)", c, re.I)), None
        )
        chave = next((c for c in campos if c == "id" or c in (f"id_{tabela}", f"{tabela}_id")), None)

        relacoes = {}
        for campo in campos:
            if campo.endswith("_id") and campo != "id":
                base = campo[:-3]
                destino = next(
                    (o for o in rotas if tabela_de(o).lower() in (base, base + "s", base + "es")), None
                )
                if destino:
                    nome_destino = next(
                        (c for c in ("nome", "titulo", "name", "title") if c in rotas[destino].get("campos", [])), "id"
                    )
                    relacoes[campo] = {"rota": destino, "nome": nome_destino}

        colecoes.append({
            "tabela": tabela, "rota": rota, "container": container, "principal": principal,
            "nome": nome, "imagem": imagem, "categoria": categoria, "descricao": descricao,
            "chave": chave, "relacoes": relacoes,
        })

    if novas_secoes:
        pos = html.find("</main>")
        pos = pos if pos != -1 else html.find("<script")
        html = html[:pos] + novas_secoes + html[pos:]

    if "mensagem-status" not in ids_html:
        pos = html.find("</main>")
        pos = pos if pos != -1 else html.find("<script")
        html = html[:pos] + '        <div id="mensagem-status" role="status"></div>\n' + html[pos:]
        mudancas.append('criado no HTML o elemento id="mensagem-status"')

    html, n_fixos = _remover_cards_fixos(html, _nomes_do_banco(pasta_projeto))
    if n_fixos:
        mudancas.append(f"{n_fixos} cards escritos à mão no HTML removidos (repetiam o banco; a lista vem da API)")

    # ---- botões sem id (ex: os do hero) ganham um, para poderem ser ligados ----
    contador_botoes = 0

    def dar_id_ao_botao(m):
        nonlocal contador_botoes
        if re.search(r"\bid\s*=", m.group(1)):
            return m.group(0)
        contador_botoes += 1
        return f'<button id="botao-auto-{contador_botoes}"{m.group(1)}>'

    html = re.sub(r"<button\b([^>]*)>", dar_id_ao_botao, html, flags=re.I)

    # ---- botões do menu -> seções ----------------------------------------
    parados = {"fazer", "comprar", "adicionar", "abrir", "ver", "conhecer", "nosso", "nossa", "para"}
    ligacoes = []

    for id_botao, texto in re.findall(
        r'<button\b[^>]*\bid\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</button>', html, re.IGNORECASE | re.DOTALL
    ):
        palavras_botao = {
            _radical(w) for w in re.findall(r"[A-Za-zÀ-ÿ]+", texto)
            if len(w) > 3 and _sem_acento(w) not in parados
        }

        melhor = max(secoes, key=lambda s: len(palavras_botao & s[1]), default=None)

        if melhor and palavras_botao & melhor[1]:
            alvo = melhor[0]
        elif palavras_botao & {"menu", "inicio", "home", "topo"} or not palavras_botao:
            alvo = "topo"
        else:
            alvo = secoes[0][0]

        ligacoes.append([id_botao, alvo])
        mudancas.append(f'botão "{re.sub(chr(60) + "[^>]*>", "", texto).strip()}" agora leva até #{alvo}')

    texto_botao = (re.search(r"<button[^>]*>([^<$]+)</button>", js_antigo) or [None, "Adicionar ao pedido"])[1].strip()

    config = {
        "status": "mensagem-status",
        "classeCard": classe_card,
        "textoBotao": texto_botao or "Adicionar ao pedido",
        "colecoes": colecoes,
        "ligacoes": ligacoes,
    }

    novo_js = _JS_RECONSTRUIDO.replace("__CONFIG__", json.dumps(config, ensure_ascii=False, indent=4))

    mudancas.insert(0, "script.js refeito a partir da API: " + ", ".join(c["rota"] for c in colecoes))


    # ---- CSS das classes novas (só se o CSS ainda não as tem) -------------
    extra = ""
    if classe_grade not in classes_css:
        extra += (
            f".{classe_grade} {{\n    display: grid;\n    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));\n"
            "    gap: 20px;\n    width: 100%;\n}\n\n"
        )
    if classe_card not in classes_css:
        extra += (
            f".{classe_card} {{\n    background-color: var(--superficie, #fff);\n    border: 1px solid var(--borda, #ddd);\n"
            "    border-radius: 12px;\n    padding: 16px;\n    display: flex;\n    flex-direction: column;\n    gap: 8px;\n}\n\n"
        )
    if "card-img" not in classes_css:
        extra += (
            ".card-img {\n    display: block;\n    width: 100%;\n    aspect-ratio: 16 / 10;\n"
            "    object-fit: cover;\n    border-radius: 8px;\n}\n\n"
        )
    if "etiqueta" not in classes_css:
        extra += (
            ".etiqueta {\n    align-self: flex-start;\n    background-color: var(--secundaria, var(--primaria, #888));\n"
            "    color: var(--sobre-secundaria, var(--sobre-primaria, #fff));\n    font-size: 0.75rem;\n"
            "    padding: 2px 10px;\n    border-radius: 999px;\n}\n\n"
        )
    if classe_grade in classes_css and "grade centralizada" not in css:
        extra += (
            f"/* grade centralizada */\n.{classe_grade} {{\n    margin-left: auto;\n    margin-right: auto;\n}}\n\n"
        )
    if not re.search(r"\.preco\b", css):
        extra += ".preco {\n    font-weight: 700;\n    color: var(--texto, inherit);\n}\n\n"
    if not re.search(r"\.avaliacao\b", css):
        extra += ".avaliacao {\n    color: var(--texto-suave, inherit);\n}\n\n"
    if "#mensagem-status:empty" not in css:
        extra += (
            "#mensagem-status:empty {\n    display: none;\n}\n\n"
            "#mensagem-status {\n    position: fixed;\n    bottom: 20px;\n    left: 50%;\n    transform: translateX(-50%);\n"
            "    background-color: var(--primaria, #333);\n    color: var(--sobre-primaria, #fff);\n    padding: 12px 20px;\n"
            "    border-radius: 10px;\n    z-index: 1000;\n}\n"
        )

    if extra:
        with open(caminho_css, "a", encoding="utf-8") as arq:
            arq.write("\n/* Ajuste automático: classes do front refeito */\n" + extra)

    with open(caminho_html, "w", encoding="utf-8") as arq:
        arq.write(html)
    with open(caminho_js, "w", encoding="utf-8") as arq:
        arq.write(novo_js)

    return mudancas


def _criar_imagens_que_faltam(pasta_projeto, problemas):
    """Chama o ilustrador quando o banco cita imagens que não existem."""

    mudancas = []

    if any("imagem(ns) que não existem" in p for p in problemas) or any(
        "não mostra a imagem" in p for p in problemas
    ):
        try:
            from ilustrador import gerar_imagens
            feitas = gerar_imagens(pasta_projeto)
            if feitas:
                mudancas.append(
                    f"criadas {sum(1 for f in feitas if f.startswith('imagem criada'))} "
                    "ilustrações em static/img/ (SVG) e o schema.sql foi acertado"
                )
                if any("hero.svg" in f for f in feitas):
                    mudancas.append("criada a imagem de capa do #hero")
        except Exception as erro:  # nunca derruba a geração do site
            print(f">>> teste: não consegui criar as imagens: {erro}")

    return mudancas


def _reparar_front(pasta_projeto, problemas, resultado):
    """Conserta o que dá para consertar com segurança no HTML/JS gerado.

    - remove do card os campos que a API não devolve (ex.: preço numa
      tabela sem preço), que faziam o JavaScript quebrar e a lista sumir;
    - troca um "POST" com campos que a tabela não tem por uma ação simples
      (mostrar qual item foi escolhido);
    - dá ação aos botões que não faziam nada (rolar até a seção certa);
    - cria a área de mensagens e a seção de ingressos, se faltarem.

    Devolve a lista do que foi alterado.
    """

    pasta_static = os.path.join(pasta_projeto, "static")
    caminho_html = os.path.join(pasta_static, "index.html")
    caminho_js = os.path.join(pasta_static, "script.js")
    caminho_css = os.path.join(pasta_static, "style.css")

    html = _ler(caminho_html)
    js = _ler(caminho_js)

    imagens_novas = _criar_imagens_que_faltam(pasta_projeto, problemas)

    graves = ("endereço externo", "sem implementação", "não foi declarada", "não busca nenhum dado", "não tem essa rota", "essa rota não devolve o campo")

    if html and js is not None and any(g in p for p in problemas for g in graves):
        feitas = _reconstruir_front(pasta_projeto, resultado, problemas)
        if feitas:
            return imagens_novas + feitas

    if not html or js is None or _MARCA_LIGACOES in js:
        return []

    mudancas = []
    rotas_get = {
        r["rota"]: r for r in resultado["rotas"]
        if r["rota"].startswith("/api/") and "linhas" in r and "<" not in r["rota"]
    }

    # rota principal = a que o JS lê para montar os cards
    lidas = re.findall(r'fetch\(\s*["\'`](/api/[\w\-]+)["\'`]\s*\)', js)
    principal = next((r for r in lidas if r in rotas_get), None) or next(iter(rotas_get), None)

    if not principal:
        return []

    campos = rotas_get[principal].get("campos", [])
    campo_nome = next(
        (c for c in ("nome", "titulo", "name", "title") if c in campos),
        next((c for c in campos if c != "id"), "id")
    )

    for problema in problemas:

        m = re.match(r'a API devolve o campo "(\w+)", mas o script\.js não mostra', problema)

        if not m:
            continue

        campo_img = m.group(1)
        achou = None

        for t in re.finditer(r"\.innerHTML\s*=\s*`", js):
            resto = js[t.end(): t.end() + 600]
            v_ = re.search(r"\$\{\s*(\w+)\.\w+", resto)
            if v_:
                achou = (t.end(), v_.group(1))
                break

        if achou:
            pos, var = achou
            js = (
                js[:pos]
                + f'<img class="card-img" src="${{{var}.{campo_img}}}" '
                + f'alt="${{{var}.{campo_nome}}}" loading="lazy">'
                + js[pos:]
            )
            mudancas.append(f"o card agora mostra a imagem ({var}.{campo_img})")

            css_atual = _ler(caminho_css) or ""
            if "card-img" not in css_atual:
                with open(caminho_css, "a", encoding="utf-8") as arq:
                    arq.write(
                        "\n/* Ajuste automático: imagem dos cards */\n"
                        ".card-img {\n    display: block;\n    width: 100%;\n"
                        "    aspect-ratio: 16 / 10;\n    object-fit: cover;\n"
                        "    border-radius: 8px;\n    margin-bottom: 12px;\n}\n"
                    )

    # ---- 1) campos que a API não devolve --------------------------------
    for problema in problemas:

        m = re.match(r"o script\.js usa (\w+)\.(\w+), mas a API não devolve", problema)

        if not m:
            continue

        var, campo = m.groups()

        # <img src="${var.campo}">: se a API não devolve o campo, a figura
        # fica quebrada (ícone de imagem partida + texto alternativo)
        sem_img = re.sub(
            r"<img\b[^>]*\$\{[^}]*\b\w+\." + re.escape(campo)
            + r"\b[^}]*\}[^>]*>\s*",
            "", js
        )

        if sem_img != js:
            js = sem_img
            mudancas.append(f'removidas as figuras quebradas que usam .{campo} (a API não devolve "{campo}")')

        novo = re.sub(
            r"<(p|span|div|small|strong|li|h4|h5)\b[^>]*>"
            r"(?:(?!</\1>).)*?\$\{[^}]*\b" + re.escape(var) + r"\." + re.escape(campo) +
            r"\b[^}]*\}(?:(?!</\1>).)*?</\1>",
            "", js, flags=re.DOTALL
        )

        if novo != js:
            js = novo
            mudancas.append(f'removido do card o campo {var}.{campo} (a API não devolve "{campo}")')

    # ---- 2) id da área de mensagens ------------------------------------
    status = None
    m = re.search(r'getElementById\(\s*["\']([^"\']*(?:status|mensagem|erro|aviso)[^"\']*)["\']', js, re.IGNORECASE)
    if m:
        status = m.group(1)
    for problema in problemas:
        m = re.search(r'id="([^"]*(?:status|mensagem|erro|aviso)[^"]*)"', problema, re.IGNORECASE)
        if m and status is None:
            status = m.group(1)
    status = status or "mensagem-status"

    # ---- 3) POST com campos que a tabela não tem ------------------------
    precisa_ingressos = False

    for problema in problemas:

        if " em POST " not in problema:
            continue

        caminho = re.search(r"em POST (/api/[\w\-/]+),", problema).group(1)
        corpo_fetch = re.search(
            r'fetch\(\s*["\'`]' + re.escape(caminho) + r'["\'`]\s*,', js
        )

        if not corpo_fetch:
            continue

        achadas = list(re.finditer(r"function\s+(\w+)\s*\(", js[:corpo_fetch.start()]))
        if not achadas:
            continue

        funcao = achadas[-1]
        abre = js.find("{", js.find(")", funcao.end()))
        fecha = _fim_do_bloco(js, abre)

        if abre < 0 or fecha < 0:
            continue

        nome_funcao = funcao.group(1)
        inicio = js.rfind("async", 0, funcao.start())
        inicio = inicio if inicio != -1 and js[inicio:funcao.start()].strip() == "async" else funcao.start()

        novo = (
            f"async function {nome_funcao}(id) {{\n"
            f'    const status = document.getElementById("{status}");\n'
            f"    try {{\n"
            f'        const resposta = await fetch("{principal}");\n'
            f"        const itens = await resposta.json();\n"
            f"        const item = itens.find((i) => i.id === id);\n"
            f"        if (status && item) {{\n"
            f'            status.textContent = "Você escolheu: " + item.{campo_nome} + ".";\n'
            f"        }}\n"
            f'        const alvo = document.getElementById("ingressos");\n'
            f'        if (alvo) {{ alvo.scrollIntoView({{ behavior: "smooth" }}); }}\n'
            f"    }} catch (erro) {{\n"
            f'        if (status) {{ status.textContent = "Servidor indisponível."; }}\n'
            f"    }}\n"
            f"}}"
        )

        js = js[:inicio] + novo + js[fecha + 1:]
        mudancas.append(
            f"{nome_funcao}(): enviava campos que a tabela não tem (POST {caminho}); "
            "agora mostra qual item foi escolhido"
        )
        precisa_ingressos = True

    # ---- 4) seção de ingressos (se há API de ingressos e não há seção) --
    rota_ingressos = next((r for r in rotas_get if "ingress" in r.lower()), None)
    ids_html = set(re.findall(r'\bid\s*=\s*["\']([^"\']+)["\']', html))

    if rota_ingressos and "ingressos" not in ids_html and "ingressos-container" not in ids_html:

        id_container = next(
            (i for i in re.findall(r'getElementById\(\s*["\']([^"\']+)["\']', js)
             if re.search(r'container|lista|grid|catalogo', i, re.IGNORECASE)), None
        )
        m_classe = re.search(r'className\s*=\s*["\']([^"\']+)["\']', js)
        classe_card = m_classe.group(1) if m_classe else ""
        m_grid = re.search(
            r'id\s*=\s*["\']' + re.escape(id_container or "?") + r'["\'][^>]*class\s*=\s*["\']([^"\']+)["\']'
            r'|class\s*=\s*["\']([^"\']+)["\'][^>]*id\s*=\s*["\']' + re.escape(id_container or "?") + r'["\']',
            html
        )
        classe_grid = (m_grid.group(1) or m_grid.group(2)) if m_grid else ""

        secao = (
            '        <section id="ingressos">\n'
            "            <h2>Ingressos</h2>\n"
            f'            <div id="ingressos-container" class="{classe_grid}"></div>\n'
            "        </section>\n"
        )

        # entra logo depois da seção que contém a lista principal
        pos = None
        if id_container:
            m_cont = re.search(r'id\s*=\s*["\']' + re.escape(id_container) + r'["\']', html)
            if m_cont:
                fim = html.find("</section>", m_cont.end())
                if fim != -1:
                    pos = fim + len("</section>\n")
        if pos is None:
            pos = html.find("</main>")
        if pos != -1:
            html = html[:pos] + secao + html[pos:]
            mudancas.append('criada a seção "Ingressos" (a API tem ' + rota_ingressos + ")")

            # relações *_id -> nome (ex.: diagrama_id -> /api/diagramas)
            relacoes = {}
            for campo in rotas_get[rota_ingressos].get("campos", []):
                if campo.endswith("_id") and campo != "id":
                    base = campo[:-3]
                    destino = next(
                        (r for r in rotas_get if r.split("/")[-1].lower() in (base, base + "s", base + "es")), None
                    )
                    if destino:
                        relacoes[campo] = destino

            js = js.rstrip() + "\n\n" + _JS_INGRESSOS.format(
                marca=_MARCA_LIGACOES, rota=rota_ingressos,
                relacoes=json.dumps(relacoes), status=status,
                classe=classe_card, nome=campo_nome
            )

            if re.search(r"<nav\b", html) and 'href="#ingressos"' not in html:
                html = re.sub(r"</nav>", '\n            <a href="#ingressos">Ingressos</a>\n        </nav>', html, count=1)
                css_nav = _ler(caminho_css)
                if css_nav is not None:
                    with open(caminho_css, "a", encoding="utf-8") as arq:
                        arq.write("\n/* Ajuste automático: espaço entre os links do menu */\nheader nav a + a { margin-left: 20px; }\n")

    # ---- 5) botões sem ação --------------------------------------------
    id_secao = None
    m_cont = re.search(
        r'<section\b[^>]*\bid\s*=\s*["\']([^"\']+)["\'][^>]*>(?:(?!</section>).)*?'
        r'id\s*=\s*["\']' + re.escape(next(iter(re.findall(r'getElementById\(\s*["\']([^"\']*(?:container|lista|grid)[^"\']*)["\']', js)), "?")) + r'["\']',
        html, re.DOTALL
    )
    if m_cont:
        id_secao = m_cont.group(1)
    id_secao = id_secao or ("catalogo" if "catalogo" in ids_html else None)

    ligacoes = []
    ids_html = set(re.findall(r'\bid\s*=\s*["\']([^"\']+)["\']', html))

    for id_botao, texto in re.findall(
        r'<button\b[^>]*\bid\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</button>',
        html, re.IGNORECASE | re.DOTALL
    ):
        if id_botao in js:
            continue

        t = _sem_acento(texto)

        if ("ingress" in t or "comprar" in t) and "ingressos" in ids_html:
            alvo = "ingressos"
        elif id_secao and any(p in t for p in ("espet", "atra", "catalog", "ver ", "conhec")):
            alvo = id_secao
        elif id_secao and ("ingress" in t or "comprar" in t):
            alvo = id_secao
        else:
            continue

        ligacoes.append((id_botao, alvo))
        mudancas.append(f'botão "{texto.strip()}" agora leva até a seção #{alvo}')

    if ligacoes or precisa_ingressos or "mensagem" in status:
        if ligacoes:
            linhas = "\n".join(
                f'    ligar("{b}", "{a}");' for b, a in ligacoes
            )
            js = js.rstrip() + (
                f"\n\n// ===== {_MARCA_LIGACOES}: botões que levam até uma seção =====\n"
                "(function () {\n"
                "    function ligar(idBotao, idSecao) {\n"
                "        const botao = document.getElementById(idBotao);\n"
                "        const secao = document.getElementById(idSecao);\n"
                "        if (botao && secao) {\n"
                '            botao.addEventListener("click", () => secao.scrollIntoView({ behavior: "smooth" }));\n'
                "        }\n"
                "    }\n"
                f"{linhas}\n"
                "})();\n"
            )

    # ---- 6) área de mensagens: tem que existir no HTML ------------------
    ids_usados = set(re.findall(r'getElementById\(\s*["\']([^"\']+)["\']', js))
    ids_html = set(re.findall(r'\bid\s*=\s*["\']([^"\']+)["\']', html))
    ids_criados = set(re.findall(r'\bid\s*=\s*["\\\']?([\w-]+)', js))

    for faltando in sorted(ids_usados - ids_html - ids_criados):

        tag = (
            f'<p id="{faltando}" role="status"></p>\n'
            if re.search(r"status|mensagem|erro|aviso", faltando, re.IGNORECASE)
            else f'<div id="{faltando}"></div>\n'
        )

        pos = html.find("</main>")
        pos = pos if pos != -1 else html.find("<script")

        if pos != -1:
            html = html[:pos] + "        " + tag + html[pos:]
            mudancas.append(f'criado no HTML o elemento id="{faltando}" que o script.js procura')

            css = _ler(caminho_css)
            if css is not None and re.search(r"status|mensagem|erro|aviso", faltando, re.IGNORECASE):
                with open(caminho_css, "a", encoding="utf-8") as arq:
                    arq.write(
                        "\n/* Ajuste automático: aviso que aparece na parte de baixo da tela */\n"
                        f"#{faltando}:empty {{ display: none; }}\n"
                        f"#{faltando}:not(:empty) {{\n"
                        "    position: fixed;\n    bottom: 20px;\n    left: 50%;\n"
                        "    transform: translateX(-50%);\n"
                        "    background: var(--fundo, #222);\n    color: var(--texto, #fff);\n"
                        "    border: 1px solid var(--borda, #fff);\n"
                        "    border-radius: 10px;\n    padding: 12px 20px;\n    z-index: 1000;\n}\n"
                    )

    # erro de digitação que o modelo copia da arquitetura
    if "Espanacos" in html:
        html = html.replace("Espanacos", "Espetáculos")
        mudancas.append('corrigido "Espanacos" -> "Espetáculos" no HTML')

    if mudancas:
        with open(caminho_html, "w", encoding="utf-8") as arq:
            arq.write(html)
        with open(caminho_js, "w", encoding="utf-8") as arq:
            arq.write(js if js.endswith("\n") else js + "\n")

    return mudancas


_JS_INGRESSOS = r"""// ===== {marca}: lista de ingressos =====
async function carregarIngressos() {{
    const container = document.getElementById("ingressos-container");
    if (!container) {{ return; }}
    const relacoes = {relacoes};
    try {{
        const resposta = await fetch("{rota}");
        const ingressos = await resposta.json();
        const nomes = {{}};
        for (const campo of Object.keys(relacoes)) {{
            const lista = await (await fetch(relacoes[campo])).json();
            nomes[campo] = {{}};
            lista.forEach((item) => {{ nomes[campo][item.id] = item.{nome}; }});
        }}
        container.innerHTML = "";
        ingressos.forEach((ingresso) => {{
            const card = document.createElement("div");
            card.className = "{classe}";
            const campoRelacao = Object.keys(relacoes)[0];
            const titulo = document.createElement("h3");
            titulo.textContent = campoRelacao
                ? (nomes[campoRelacao][ingresso[campoRelacao]] || "Ingresso " + ingresso.id)
                : "Ingresso " + ingresso.id;
            card.appendChild(titulo);
            Object.keys(ingresso).forEach((chave) => {{
                if (chave === "id" || chave in relacoes) {{ return; }}
                const linha = document.createElement("p");
                let valor = ingresso[chave];
                if (/preco|valor/i.test(chave) && !isNaN(Number(valor))) {{
                    valor = "R$ " + Number(valor).toFixed(2).replace(".", ",");
                }}
                linha.textContent = chave.charAt(0).toUpperCase() + chave.slice(1) + ": " + valor;
                card.appendChild(linha);
            }});
            const botao = document.createElement("button");
            botao.textContent = "Selecionar ingresso";
            botao.addEventListener("click", () => {{
                const status = document.getElementById("{status}");
                if (status) {{ status.textContent = "Ingresso selecionado: " + titulo.textContent + "."; }}
            }});
            card.appendChild(botao);
            container.appendChild(card);
        }});
    }} catch (erro) {{
        container.textContent = "Não foi possível carregar os ingressos.";
    }}
}}

carregarIngressos();
"""


def garantir_documento_html(pasta_projeto):
    """Garante que static/index.html seja uma página completa e chame o CSS e o JS.

    O modelo às vezes devolve só um pedaço do HTML (ex.: só o <header>) ou
    esquece o <link> do CSS e o <script> do JS. Sem essas tags a página abre
    sem estilo e sem nenhum comportamento. Devolve a lista do que foi mudado.
    """

    pasta_static = os.path.join(pasta_projeto, "static")
    caminho = os.path.join(pasta_static, "index.html")
    html = _ler(caminho)

    if html is None:
        return []

    def achar(nome_padrao, extensao):
        if os.path.exists(os.path.join(pasta_static, nome_padrao)):
            return nome_padrao
        outros = sorted(glob.glob(os.path.join(pasta_static, f"*{extensao}")))
        return os.path.basename(outros[0]) if outros else None

    css, js = achar("style.css", ".css"), achar("script.js", ".js")
    original, mudancas = html, []

    if not re.search(r"<html\b", html, re.I):
        titulo = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
        texto = re.sub(r"<[^>]+>", "", titulo.group(1)).strip() if titulo else "Site"
        corpo = re.sub(r"<!DOCTYPE[^>]*>", "", html, flags=re.I).strip()
        html = (
            '<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n'
            '    <meta charset="UTF-8">\n'
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f"    <title>{texto}</title>\n</head>\n<body>\n{corpo}\n</body>\n</html>\n"
        )
        mudancas.append("index.html era só um trecho: montada a página completa")

    elif not re.search(r"<head\b", html, re.I):
        html = re.sub(
            r"(<html\b[^>]*>)",
            lambda m: m.group(1) + '\n<head>\n    <meta charset="UTF-8">\n</head>',
            html, count=1, flags=re.I,
        )
        mudancas.append("index.html sem <head>: criado")

    if css and not re.search(r'<link\b[^>]*rel\s*=\s*["\']stylesheet["\']', html, re.I):
        html = re.sub(
            r"</head>",
            lambda m: f'    <link rel="stylesheet" href="{css}">\n</head>',
            html, count=1, flags=re.I,
        )
        mudancas.append(f'adicionado <link rel="stylesheet" href="{css}">')

    if js and not re.search(r"<script\b[^>]*\bsrc\s*=", html, re.I):
        if re.search(r"</body>", html, re.I):
            html = re.sub(
                r"</body>",
                lambda m: f'    <script src="{js}"></script>\n</body>',
                html, count=1, flags=re.I,
            )
        else:
            html = html.rstrip() + f'\n<script src="{js}"></script>\n'
        mudancas.append(f'adicionado <script src="{js}">')

    if html != original:
        with open(caminho, "w", encoding="utf-8") as arq:
            arq.write(html)

    return mudancas


def verificar_projeto(pasta_projeto, gerar_backend_reserva=None):
    """Testa o site gerado e, se o backend.py estiver quebrado, tenta refazê-lo.

    gerar_backend_reserva: função opcional (a do orchestrator) que recebe o
    texto do schema.sql e devolve o código de um backend.py funcional. Ela é
    usada só quando o backend.py gerado pelo agente tem erro.

    Devolve a lista de problemas que continuam depois do teste (e do reparo).
    """

    # As imagens são criadas SEMPRE, antes de qualquer teste. Antes, o
    # ilustrador só rodava se o teste achasse um problema de imagem, e esse
    # teste só enxerga caminhos entre aspas simples com extensão (ex:
    # 'img/x.jpg'). Imagem NULL, sem extensão ou entre aspas duplas passava
    # batido e o card ficava com a figura quebrada.
    try:
        from ilustrador import gerar_imagens
        for linha in gerar_imagens(pasta_projeto):
            print(f">>> ilustrador: {linha}")
    except Exception as erro:  # nunca derruba a geração do site
        print(f">>> ilustrador: não consegui criar as imagens: {erro}")

    for mudanca in garantir_documento_html(pasta_projeto):
        print(f">>> teste: index.html consertado: {mudanca}")

    print("\n>>> teste: rodando o site numa cópia temporária e chamando as rotas...")

    problemas, quebrado, resultado = _verificar(pasta_projeto)

    if quebrado and gerar_backend_reserva:

        print(">>> teste: o backend.py gerado tem erro:")

        for problema in problemas:
            print(f"    - {problema}")

        # O schema.sql que está no disco é a verdade: é ele que cria o banco.
        schema = _ler(os.path.join(pasta_projeto, "database", "schema.sql"))
        codigo = gerar_backend_reserva(schema) if schema else ""

        if codigo:

            caminho_backend = os.path.join(pasta_projeto, "backend.py")
            guardado = os.path.join(pasta_projeto, "docs", "backend_com_erro.py")

            if os.path.exists(caminho_backend):
                os.makedirs(os.path.dirname(guardado), exist_ok=True)
                shutil.copyfile(caminho_backend, guardado)

            with open(caminho_backend, "w", encoding="utf-8") as arquivo:
                arquivo.write(codigo)

            print(
                ">>> teste: backend.py refeito a partir do schema.sql "
                "(o original ficou em docs/backend_com_erro.py). Testando de novo..."
            )

            problemas, quebrado, resultado = _verificar(pasta_projeto)

    if problemas and not quebrado:

        mudancas = _reparar_front(pasta_projeto, problemas, resultado)

        if mudancas:

            print(">>> teste: consertando o front-end automaticamente:")

            for mudanca in mudancas:
                print(f"    - {mudanca}")

            print(">>> teste: testando de novo...")

            problemas, quebrado, resultado = _verificar(pasta_projeto)

    for rota in resultado["rotas"]:
        if rota["status"] < 500 and rota["rota"].startswith("/api/"):
            registros = f' ({rota["linhas"]} registros)' if "linhas" in rota else ""
            print(f'>>> teste: GET {rota["rota"]} -> {rota["status"]}{registros}')

    if problemas:

        print(">>> teste: problemas encontrados:")

        for problema in problemas:
            print(f"    - {problema}")

    else:

        print(">>> teste: site OK (backend, banco, HTML e JavaScript combinam).")

    return problemas


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Uso: python verificador.py <pasta_do_projeto_gerado>")
        sys.exit(2)

    sys.exit(1 if verificar_projeto(sys.argv[1]) else 0)
