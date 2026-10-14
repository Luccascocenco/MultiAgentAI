from agents.architect import architect
from agents.frontend import frontend
from agents.backend import backend
from agents.database import database
from agents.reviewer import reviewer
from agents.designer import designer
from ollama import chat

import ast
import difflib
import glob
import builtins
import sqlite3
import time
import os
import re
import unicodedata
from datetime import datetime

from verificador import verificar_projeto, garantir_documento_html


PASTA_APP = os.path.dirname(os.path.abspath(__file__))

# Quantas versões do backend.py o agente pode gerar até passar na conferência.
MAX_TENTATIVAS_BACKEND = 3

# Se o agente não conseguir gerar um backend.py válido nas tentativas acima,
# o orquestrador monta um backend simples a partir do schema.sql, para o site
# nunca ficar sem servidor. Troque para False se preferir ver a falha.
USAR_BACKEND_RESERVA = True

# Estas regras são anexadas ao pedido do arquiteto e do agente de banco de
# dados. Sem elas o modelo costuma escolher tecnologias que o resto do
# pipeline não suporta (React, Node, MongoDB) e SQL de MySQL/PostgreSQL.
RESTRICOES_TECNICAS = """
RESTRIÇÕES TÉCNICAS OBRIGATÓRIAS (ignore qualquer outra tecnologia):
- Entregue SOMENTE a arquitetura em texto: visão geral, módulos, lista de
  arquivos, tabelas do banco e rotas da API. NÃO escreva código (nem HTML,
  CSS, JavaScript, Python ou SQL): outros agentes vão escrever o código.
- Front-end: apenas HTML, CSS e JavaScript puros (sem React, Vue, Angular,
  npm ou bundlers), em 3 arquivos: static/index.html, static/style.css e
  static/script.js.
- Back-end: apenas Python com Flask, em um único arquivo backend.py.
  NÃO use Node.js, Express nem MongoDB.
- Banco de dados: apenas SQLite (arquivo database.db).
- Não use serviços externos (S3, nuvem, login de terceiros).
- Mantenha o projeto simples: no máximo 3 tabelas.
- Nomes de tabelas e colunas em minúsculas, sem acentos e sem espaços.
- Os nomes das tabelas devem vir do PEDIDO DO USUÁRIO (o assunto do site):
  pergunte-se "o que este site mostra ou vende?" e use o plural desse
  substantivo como tabela principal. Se o site vende coisas, a tabela
  principal se chama produtos. Não use nomes de assuntos que o pedido
  não menciona.
"""

RESTRICOES_BANCO = """
REGRAS PARA O BANCO DE DADOS:
- Use somente SQLite. NÃO use CREATE DATABASE nem USE.
- Toda tabela começa com: id INTEGER PRIMARY KEY AUTOINCREMENT.
- Use apenas os tipos INTEGER, TEXT e REAL.
- Nomes de tabelas e colunas em minúsculas, sem acentos, sem espaços e sem
  hífen.
- Use os mesmos nomes de tabelas da ARQUITETURA e do assunto do pedido do
  usuário. Se o site vende coisas, a tabela principal se chama produtos.
  NUNCA invente nomes sem relação com o pedido.
- No máximo 3 tabelas, cada CREATE TABLE UMA ÚNICA VEZ.
- NÃO comente o SQL: nenhum comando pode começar com "--". Escreva os
  comandos soltos, prontos para executar.
- Se o PEDIDO ORIGINAL DO USUÁRIO citar dados (por exemplo produtos com
  nome, descrição e preço), use EXATAMENTE esses dados nos INSERTs, sem
  inventar registros extras. Se não citar, inclua 3 INSERTs de exemplo,
  com dados realistas, para cada tabela principal.
- Se o item tiver imagem, guarde na coluna "imagem" um caminho como
  img/nome.jpg.
- Entregue somente o SQL, sem explicações.
"""


def ler_backend_salvo(caminho_projeto):
    """Lê o backend.py que acabou de ser salvo no projeto ('' se não existir)."""

    caminho = os.path.join(caminho_projeto, "backend.py")

    if not os.path.exists(caminho):
        return ""

    with open(caminho, encoding="utf-8", errors="replace") as arquivo:
        return arquivo.read()


def nomes_indefinidos(codigo):
    """Acha nomes usados no código que nunca são importados nem definidos.

    É uma checagem simples (parecida com a do pyflakes): pega erros comuns do
    modelo, como usar os.environ sem import os ou chamar uma função que nunca
    foi escrita. Devolve a lista de nomes suspeitos.
    """

    try:
        arvore = ast.parse(codigo)
    except SyntaxError:
        return []

    definidos = set(dir(builtins)) | {"__file__"}

    for no in ast.walk(arvore):

        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            definidos.add(no.name)

        elif isinstance(no, ast.arg):
            definidos.add(no.arg)

        elif isinstance(no, ast.Import):
            for alias in no.names:
                definidos.add((alias.asname or alias.name).split(".")[0])

        elif isinstance(no, ast.ImportFrom):
            for alias in no.names:
                if alias.name == "*":
                    return []  # import * : não dá para saber o que entrou
                definidos.add(alias.asname or alias.name)

        elif isinstance(no, ast.Name) and isinstance(no.ctx, (ast.Store, ast.Del)):
            definidos.add(no.id)

        elif isinstance(no, ast.ExceptHandler) and no.name:
            definidos.add(no.name)

    usados = {
        no.id for no in ast.walk(arvore)
        if isinstance(no, ast.Name) and isinstance(no.ctx, ast.Load)
    }

    return sorted(usados - definidos)


def validar_backend(codigo, schema_sql=""):
    """Confere o backend.py gerado pelo modelo e devolve a lista de problemas."""

    if not codigo.strip():
        return ["o arquivo backend.py não foi gerado (formato FILE: ausente)"]

    try:
        ast.parse(codigo)
    except SyntaxError as erro:
        return [f"erro de sintaxe na linha {erro.lineno}: {erro.msg}"]

    problemas = []

    if "Flask" not in codigo:
        problemas.append("não usa Flask")

    if re.search(r"\brequest\.", codigo) and not re.search(
        r"from\s+flask\s+import[^\n]*\brequest\b", codigo
    ):
        problemas.append(
            "usa request mas não importa (use: from flask import Flask, jsonify, request)"
        )

    if "schema.sql" not in codigo or "executescript" not in codigo:
        problemas.append(
            "não cria o banco lendo o arquivo database/schema.sql e "
            "executando com conn.executescript(...)"
        )

    if re.search(r"CREATE\s+TABLE", codigo, re.IGNORECASE):
        problemas.append(
            "escreve CREATE TABLE no Python (inventou tabelas); as tabelas "
            "vêm só do schema.sql, remova qualquer CREATE TABLE do código"
        )

    if "static_url_path" not in codigo:
        problemas.append(
            'falta static_url_path="" em Flask(__name__, static_folder="static", '
            'static_url_path=""); sem isso o CSS e o JS do site não carregam'
        )

    tabelas = re.findall(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"`\[]?(\w+)",
        schema_sql,
        re.IGNORECASE
    )

    if tabelas and not any(
        f"/api/{t.lower()}" in codigo.lower() for t in tabelas
    ):
        problemas.append(
            "nenhuma rota /api/<tabela> usa as tabelas do esquema; as "
            "tabelas são: " + ", ".join(tabelas)
        )

    if schema_sql:

        inventadas = chaves_json_inventadas(codigo, info_do_schema(schema_sql))

        if inventadas:
            problemas.append(
                "devolve chaves JSON que não são colunas do esquema ("
                + ", ".join(inventadas)
                + "); devolva uma LISTA de linhas com "
                "jsonify([dict(linha) for linha in linhas]), usando "
                "exatamente os nomes das colunas, sem renomear campos e "
                "sem embrulhar a lista em outro objeto"
            )

    if "app.run" not in codigo:
        problemas.append("não inicia o servidor com app.run(...)")

    if "send_static_file" not in codigo:
        problemas.append(
            'a rota "/" não devolve o site: use '
            'return app.send_static_file("index.html")'
        )

    indefinidos = nomes_indefinidos(codigo)

    if indefinidos:
        problemas.append(
            "usa nomes que não existem no arquivo (faltou import ou "
            "definir a função): " + ", ".join(indefinidos)
        )

    if re.search(r"\bsubprocess\b|os\.system|os\.popen|\bnpm\b|pip\s+install", codigo):
        problemas.append(
            "executa comandos externos (subprocess, os.system, npm ou pip); "
            "remova isso, o backend.py só pode usar Flask e a biblioteca padrão"
        )

    return problemas


# Quantas versões do CSS o designer pode gerar até passar na conferência.
MAX_TENTATIVAS_DESIGN = 2


# Nomes em inglês que o modelo costuma usar no JavaScript, e a coluna em
# português que provavelmente significa a mesma coisa.
SINONIMOS_CAMPOS = {
    "name": "nome", "title": "titulo", "description": "descricao",
    "desc": "descricao", "price": "preco", "image": "imagem",
    "img": "imagem", "photo": "imagem", "foto": "imagem",
    "category": "categoria", "stock": "estoque", "quantity": "quantidade",
    "qty": "quantidade", "author": "autor", "email": "email",
    "preco_unitario": "preco", "valor": "preco",
}

# Chaves de JSON que o backend pode usar sem serem colunas (mensagens, etc.)
CHAVES_JSON_LIVRES = {
    "id", "erro", "error", "message", "mensagem", "msg", "status", "ok",
    "success", "sucesso",
}

SEGREDO_RE = re.compile(r"senha|password|passwd|hash|token", re.IGNORECASE)


def sem_acento(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


# Nomes de tabelas que já "vazaram" de exemplos antigos dos prompts (o modelo
# pequeno copia exemplos). Só valem como erro se o pedido do usuário NÃO
# fala desse assunto.
NOMES_DE_EXEMPLO_ANTIGOS = ("atracoes", "atracao", "ingressos", "ingresso", "circo")


# Usado só se o agente de banco não entregar nenhum SQL utilizável, para o
# site nunca nascer sem dados (sem tabelas não há API, imagens nem cards).
SCHEMA_RESERVA = """CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco REAL NOT NULL,
    imagem TEXT,
    categoria TEXT
);
"""


def nomes_vazados(texto, pedido):
    """Nomes de exemplo antigos que aparecem no texto mas não no pedido."""
    t = sem_acento(texto).lower()
    ped = sem_acento(pedido).lower()
    return sorted(
        n for n in NOMES_DE_EXEMPLO_ANTIGOS
        if re.search(rf"\b{n}\b", t) and not re.search(rf"\b{n}", ped)
    )


def problemas_do_schema(schema_sql, pedido):
    """Problemas que justificam pedir o banco de novo ao agente."""
    problemas = []

    if "CREATE TABLE" not in schema_sql.upper():
        problemas.append(
            "O SQL não tem nenhum CREATE TABLE executável. Não comente o SQL "
            "com '--': escreva os comandos soltos dentro do bloco de código."
        )

    vazados = nomes_vazados(schema_sql, pedido)
    if vazados:
        problemas.append(
            "As tabelas/dados usam nomes que não têm relação com o pedido do "
            f"usuário: {', '.join(vazados)}. Use somente o assunto do pedido."
        )

    tabelas = {
        t.lower() for t in re.findall(
            r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"`\[]?(\w+)",
            schema_sql, re.IGNORECASE
        )
    }
    if len(tabelas) > 3:
        problemas.append(
            f"Foram criadas {len(tabelas)} tabelas; o máximo é 3, e cada "
            "tabela deve ser criada uma única vez."
        )

    return problemas


def info_do_schema(schema_sql):
    """{tabela: [colunas]} lendo o schema.sql numa base SQLite em memória."""

    try:
        conn = sqlite3.connect(":memory:")
        conn.executescript(schema_sql)

        tabelas = [
            linha[0] for linha in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
                "ORDER BY rowid"
            )
        ]

        info = {
            t: [c[1] for c in conn.execute(f'PRAGMA table_info("{t}")')]
            for t in tabelas
        }

        conn.close()

        return info

    except sqlite3.Error:
        return {}


def rotas_api_do_backend(codigo):
    """Nomes que vêm depois de /api/ nas rotas do backend.py."""

    rotas = set()

    for rota in re.findall(r"route\(\s*[\"'](/api/[^\"']+)[\"']", codigo):

        base = rota[len("/api/"):].split("/")[0]

        if base and not base.startswith("<"):
            rotas.add(base.lower())

    return rotas


def tabela_principal(info, rotas=None):
    """A tabela que o site mostra nos cards: a entidade base com mais
    colunas, ignorando tabelas com senha (usuários) e tabelas sem rota."""

    candidatas = [t for t in info if not rotas or t.lower() in rotas]

    sem_segredo = [
        t for t in candidatas
        if not any(SEGREDO_RE.search(c) for c in info[t])
    ]

    pool = sem_segredo or candidatas or list(info)

    # prefere a entidade base (jogos, produtos...) às tabelas que apontam
    # para outras (carrinhos, compras), que têm colunas como usuario_id
    independentes = [
        t for t in pool
        if not any(c.lower().endswith("_id") for c in info[t])
    ]

    pool = independentes or pool

    return max(pool, key=lambda t: len(info[t])) if pool else ""


def chaves_json_inventadas(codigo, info):
    """Chaves de dicionário no backend.py que não são colunas do esquema.

    Se o backend devolve {"name": ...} mas a coluna é "nome", o JavaScript
    (que segue o esquema) não acha o campo e os cards não aparecem.
    """

    if not info:
        return []

    colunas = {c.lower() for cols in info.values() for c in cols}

    # O "__main__" do bloco `if __name__ == "__main__":` termina em ":" e
    # parecia uma chave de dicionário (falso positivo). Remove esse bloco
    # da análise antes de procurar as chaves.
    codigo_sem_main = re.sub(
        r"if\s+__name__\s*==\s*[\"']__main__[\"']\s*:", "", codigo
    )

    chaves = set(re.findall(r"[\"'](\w+)[\"']\s*:", codigo_sem_main))

    return sorted(
        k for k in chaves
        if k.lower() not in colunas and k.lower() not in CHAVES_JSON_LIVRES
    )


def corrigir_contrato_front_back(caminho_projeto, schema_sql, codigo_backend):
    """Faz o script.js usar os mesmos nomes que o backend e o HTML têm.

    O esquema (schema.sql) é a fonte da verdade. No script.js, corrige:
    - a URL do fetch, se não existir uma rota /api/<nome> no backend;
    - os campos dos itens (produto.name -> produto.nome, etc.);
    - ids usados em getElementById que não existem no index.html.
    O que não der para corrigir com segurança só é avisado no terminal.
    """

    caminho_js = achar_na_static(caminho_projeto, ".js")
    caminho_html = achar_na_static(caminho_projeto, ".html")

    info = info_do_schema(schema_sql)

    if not caminho_js or not info:
        return

    js = ler_texto(caminho_js)
    original = js

    rotas = rotas_api_do_backend(codigo_backend) or {t.lower() for t in info}
    principal = tabela_principal(info, rotas)
    por_minuscula = {t.lower(): t for t in info}

    mudancas = []
    avisos = []
    tabelas_usadas = []

    # --- 1) URL do fetch ------------------------------------------------

    def corrigir_url(m):

        base = m.group(2)

        if base.lower() in rotas:
            tabelas_usadas.append(base.lower())
            return m.group(0)

        parecidas = difflib.get_close_matches(
            sem_acento(base).lower(), sorted(rotas), n=1, cutoff=0.6
        )

        destino = parecidas[0] if parecidas else principal.lower()

        tabelas_usadas.append(destino)
        mudancas.append(f'URL "/api/{base}" -> "/api/{destino}"')

        return f"{m.group(1)}{destino}"

    js = re.sub(r"""(["'`]/api/)([\w\-]+)""", corrigir_url, js)

    # --- 2) campos dos itens -------------------------------------------

    tabelas_dos_cards = [
        t for t in tabelas_usadas if t in por_minuscula
    ] or [principal.lower()]

    colunas = []

    for t in tabelas_dos_cards:
        for c in info[por_minuscula[t]]:
            if c not in colunas:
                colunas.append(c)

    por_chave = {sem_acento(c).lower(): c for c in colunas}

    # só os itens dos dados da API: listas vindas de "await resposta.json()".
    # (querySelectorAll(...).forEach(card => ...) percorre elementos do DOM,
    # que não têm nada a ver com as colunas do banco)
    listas = set(re.findall(
        r"(?:const|let|var)\s+(\w+)\s*=\s*await\s+\w+\.json\(\)", js
    ))

    variaveis = set()

    for lista in listas:

        variaveis.update(re.findall(
            rf"\b{re.escape(lista)}\.(?:forEach|map|filter|find|some)\(\s*"
            r"(?:async\s+)?(?:function\s*)?\(?\s*(\w+)",
            js
        ))

        variaveis.update(re.findall(
            rf"for\s*\(\s*(?:const|let|var)\s+(\w+)\s+of\s+"
            rf"{re.escape(lista)}\b",
            js
        ))

    comuns = {
        "length", "push", "map", "forEach", "filter", "slice", "find",
        "toString", "join", "includes", "reduce", "sort", "some",
    }

    for var in sorted(variaveis):

        def corrigir_campo(m, var=var):

            campo = m.group(1)

            if campo in comuns:
                return m.group(0)

            chave = sem_acento(campo).lower()

            if chave in por_chave:
                real = por_chave[chave]
            elif SINONIMOS_CAMPOS.get(chave) in por_chave:
                real = por_chave[SINONIMOS_CAMPOS[chave]]
            else:
                parecidas = difflib.get_close_matches(
                    chave, list(por_chave), n=1, cutoff=0.7
                )
                real = por_chave[parecidas[0]] if parecidas else None

            if real is None:
                avisos.append(
                    f'o JS usa "{var}.{campo}", mas nenhuma coluna se '
                    f"parece com isso (colunas: {', '.join(colunas)})"
                )
                return m.group(0)

            if real != campo:
                mudancas.append(f'campo "{var}.{campo}" -> "{var}.{real}"')

            return f"{var}.{real}"

        js = re.sub(
            rf"(?<![\w.]){re.escape(var)}\.(\w+)", corrigir_campo, js
        )

    # --- 3) ids que o JS procura no HTML ---------------------------------

    if caminho_html:

        ids_html = set(re.findall(
            r"""\bid\s*=\s*["']([^"']+)["']""", ler_texto(caminho_html)
        ))

        def corrigir_id(m):

            nome = m.group(2)

            if nome in ids_html or not ids_html:
                return m.group(0)

            parecidos = difflib.get_close_matches(
                nome, sorted(ids_html), n=1, cutoff=0.5
            )

            if not parecidos:
                avisos.append(
                    f'o JS procura o id "{nome}", que não existe no index.html'
                )
                return m.group(0)

            mudancas.append(f'id "{nome}" -> "{parecidos[0]}"')

            return f"{m.group(1)}{parecidos[0]}{m.group(3)}"

        js = re.sub(
            r"""(getElementById\(\s*["'])([^"']+)(["']\s*\))""",
            corrigir_id,
            js
        )

    # --- 4) fetch POST/PUT com corpo JSON ---------------------------------

    antes = js

    js = re.sub(
        r"""(method\s*:\s*["'](?:POST|PUT|PATCH)["']\s*,)(?![^}]*headers)""",
        r'\1 headers: {"Content-Type": "application/json"},',
        js
    )

    if js != antes:
        mudancas.append(
            "fetch POST/PUT sem cabeçalho -> adicionado Content-Type: "
            "application/json (sem ele o Flask não lê o JSON enviado)"
        )

    # --- 5) o JS usa métodos que o backend não tem ----------------------

    metodos = metodos_api_do_backend(codigo_backend)

    if metodos:

        for base, resto in re.findall(
            r"""fetch\(\s*["'`]/api/([\w\-]+)[^"'`]*["'`]\s*,\s*\{([^;]{0,300})""",
            js
        ):

            achado = re.search(r"""method\s*:\s*["'](\w+)""", resto)

            if achado and base.lower() in metodos:

                metodo = achado.group(1).upper()

                if metodo not in metodos[base.lower()]:
                    avisos.append(
                        f"o JS chama {metodo} /api/{base}, mas o backend só "
                        f"tem {', '.join(sorted(metodos[base.lower()]))} "
                        "nessa rota (a chamada vai dar erro 405)"
                    )

    # --- resultado ---------------------------------------------------------

    if js != original:

        with open(caminho_js, "w", encoding="utf-8") as arquivo:
            arquivo.write(js)

    if mudancas:
        print(">>> contrato front/back: o script.js foi ajustado:")
        for item in dict.fromkeys(mudancas):
            print(f"    - {item}")

    for aviso in dict.fromkeys(avisos):
        print(f">>> contrato front/back: ATENÇÃO — {aviso}")

    if not mudancas and not avisos:
        print(">>> contrato front/back: nomes do script.js conferem com a API")


# ---------------------------------------------------------------
# SANEAR O SCHEMA: o schema.sql tem que rodar do começo ao fim sem erro,
# senão o backend nem inicia (ex: INSERTs com o mesmo id repetido dão
# "UNIQUE constraint failed: produtos.id").
# ---------------------------------------------------------------

def dividir_comandos_sql(sql):
    """Separa o script em comandos completos (respeita aspas e ';')."""

    comandos = []
    atual = ""

    for linha in sql.splitlines(keepends=True):

        atual += linha

        if sqlite3.complete_statement(atual):
            comandos.append(atual.strip())
            atual = ""

    if atual.strip():
        comandos.append(atual.strip())

    return comandos


def dividir_fora_de_aspas(texto):
    """Divide por vírgulas que estão fora de aspas e de parênteses."""

    partes = []
    atual = ""
    aspas = False
    nivel = 0
    i = 0

    while i < len(texto):

        c = texto[i]

        if c == "'":

            if aspas and texto[i + 1:i + 2] == "'":
                atual += "''"
                i += 2
                continue

            aspas = not aspas

        elif not aspas:

            if c == "(":
                nivel += 1
            elif c == ")":
                nivel -= 1
            elif c == "," and nivel == 0:
                partes.append(atual.strip())
                atual = ""
                i += 1
                continue

        atual += c
        i += 1

    partes.append(atual.strip())

    return partes


def remover_id_do_insert(comando):
    """Tira a coluna id de um INSERT (o SQLite numera sozinho).

    INSERT INTO t (id, a, b) VALUES (1, 'x', 2), (1, 'y', 3);
    vira
    INSERT INTO t (a, b) VALUES ('x', 2), ('y', 3);
    Se o comando não tiver id na primeira coluna, devolve igual.
    """

    m = re.match(
        r"(?is)^(INSERT\s+(?:OR\s+\w+\s+)?INTO\s+\S+\s*)\(\s*([^)]*?)\s*\)"
        r"\s*VALUES\s*(.*?);?\s*$",
        comando
    )

    if not m:
        return comando

    colunas = [c.strip() for c in m.group(2).split(",")]

    if not colunas or colunas[0].strip('"`[]').lower() != "id":
        return comando

    novas = []

    for tupla in dividir_fora_de_aspas(m.group(3)):

        if not (tupla.startswith("(") and tupla.endswith(")")):
            return comando

        valores = dividir_fora_de_aspas(tupla[1:-1])

        if len(valores) != len(colunas):
            return comando

        novas.append("(" + ", ".join(valores[1:]) + ")")

    return f"{m.group(1)}({', '.join(colunas[1:])}) VALUES {', '.join(novas)};"


def sanear_schema(schema_sql):
    """Devolve um schema que executa sem erro.

    Cada comando é testado num banco em memória. Um INSERT que falha (id
    repetido, por exemplo) é refeito sem a coluna id; se ainda assim falhar,
    é descartado. O resultado é o que de fato roda no backend.
    """

    conn = sqlite3.connect(":memory:")

    mantidos = []
    descartados = []

    for comando in dividir_comandos_sql(schema_sql):

        erro_final = None

        for variante in dict.fromkeys([comando, remover_id_do_insert(comando)]):

            try:
                conn.executescript(variante)
            except sqlite3.Error as erro:
                erro_final = erro
                continue

            if variante != comando:
                print(
                    ">>> database: INSERT com id repetido refeito sem o id: "
                    + comando[:70].replace("\n", " ") + "..."
                )

            mantidos.append(variante)
            erro_final = None
            break

        if erro_final is not None and "no column named" in str(erro_final):

            if reparar_insert_com_coluna_nova(conn, comando, mantidos):
                erro_final = None

        if erro_final is not None:
            descartados.append((comando, erro_final))

    conn.close()

    for comando, erro in descartados:
        print(
            f">>> database: comando descartado ({erro}): "
            + comando[:70].replace("\n", " ") + "..."
        )

    return "\n\n".join(mantidos) + "\n"


# ---------------------------------------------------------------
# COLUNAS NOVAS: o agente de banco costuma escrever um INSERT com a coluna
# "imagem" sem ter criado essa coluna no CREATE TABLE. Descartar o INSERT
# faz as imagens sumirem (a API não devolve "imagem" e o card fica com a
# figura quebrada). Aqui a coluna é criada e os valores são aproveitados.
# ---------------------------------------------------------------

_INSERT_RE = re.compile(
    r"(?is)^INSERT\s+(?:OR\s+\w+\s+)?INTO\s+[\"`\[]?(\w+)[\"`\]]?\s*"
    r"\(\s*([^)]*?)\s*\)\s*VALUES\s*(.*?);?\s*$"
)

COLUNA_IMAGEM_RE = re.compile(r"imagem|image|foto|img|capa|thumb|banner", re.IGNORECASE)
COLUNA_PRECO_RE = re.compile(r"preco|valor|price", re.IGNORECASE)
PEDIDO_VISUAL_RE = re.compile(
    r"loja|produto|cat[aá]logo|galeria|vitrine|card[aá]pio|portf[oó]lio|vend",
    re.IGNORECASE
)


def tipo_da_coluna_nova(nome):

    if COLUNA_PRECO_RE.search(nome):
        return "REAL"

    if re.search(r"quantidade|estoque|qtd", nome, re.IGNORECASE):
        return "INTEGER"

    return "TEXT"


def adicionar_coluna_ao_create(create_sql, coluna, tipo):
    """Escreve a coluna dentro do CREATE TABLE (antes das chaves estrangeiras)."""

    ini = create_sql.index("(")
    fim = create_sql.rindex(")")

    definicoes = [
        d.strip() for d in dividir_fora_de_aspas(create_sql[ini + 1:fim]) if d.strip()
    ]

    posicao = next(
        (
            i for i, d in enumerate(definicoes)
            if re.match(r"(?i)(FOREIGN\s+KEY|CONSTRAINT|PRIMARY\s+KEY|UNIQUE\s*\(|CHECK\s*\()", d)
        ),
        len(definicoes)
    )

    definicoes.insert(posicao, f"{coluna} {tipo}")

    return (
        create_sql[:ini + 1] + "\n    " + ",\n    ".join(definicoes) + "\n" + create_sql[fim:]
    )


def reparar_insert_com_coluna_nova(conn, comando, mantidos):
    """INSERT com coluna que a tabela não tem: cria a coluna e aproveita os dados.

    As linhas que já existem (mesmo nome) só recebem a coluna nova com UPDATE,
    sem duplicar o produto; as que não existem são inseridas. Devolve True se
    conseguiu (e então "mantidos" e "conn" já estão atualizados).
    """

    m = _INSERT_RE.match(comando)

    if not m:
        return False

    tabela = m.group(1)
    colunas = [c.strip().strip('"`[]') for c in m.group(2).split(",")]

    existentes = [l[1] for l in conn.execute(f'PRAGMA table_info("{tabela}")')]

    if not existentes:
        return False

    minusculas = {e.lower() for e in existentes}
    novas = [c for c in colunas if c.lower() not in minusculas]

    if not novas:
        return False

    linhas = []

    for tupla in dividir_fora_de_aspas(m.group(3)):

        if not (tupla.startswith("(") and tupla.endswith(")")):
            return False

        valores = dividir_fora_de_aspas(tupla[1:-1])

        if len(valores) != len(colunas):
            return False

        linhas.append(dict(zip(colunas, valores)))

    chave = next(
        (c for c in colunas if c.lower() != "id" and c.lower() in minusculas), None
    )

    indice = next(
        (
            i for i, c in enumerate(mantidos)
            if re.match(
                rf'(?is)^\s*CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`\[]?'
                rf'{re.escape(tabela)}["`\]]?\s*\(', c
            )
        ),
        None
    )

    if indice is None:
        return False

    alteracoes = [
        f'ALTER TABLE "{tabela}" ADD COLUMN "{c}" {tipo_da_coluna_nova(c)}' for c in novas
    ]

    try:

        # ensaio numa cópia: só mexe no banco de verdade se tudo der certo
        copia = sqlite3.connect(":memory:")
        conn.backup(copia)

        for alteracao in alteracoes:
            copia.execute(alteracao)

        comandos = []

        for linha in linhas:

            existe = chave and copia.execute(
                f'SELECT 1 FROM "{tabela}" WHERE "{chave}" = {linha[chave]} LIMIT 1'
            ).fetchone()

            if existe:
                sets = ", ".join(f"{c} = {linha[c]}" for c in novas)
                comandos.append(
                    f"UPDATE {tabela} SET {sets} WHERE {chave} = {linha[chave]};"
                )
            else:
                comandos.append(
                    f"INSERT INTO {tabela} ({', '.join(colunas)}) "
                    f"VALUES ({', '.join(linha[c] for c in colunas)});"
                )

        for comando_novo in comandos:
            copia.execute(comando_novo)

        copia.close()

    except sqlite3.Error:
        return False

    novo_create = mantidos[indice]

    for c in novas:
        novo_create = adicionar_coluna_ao_create(novo_create, c, tipo_da_coluna_nova(c))

    for alteracao in alteracoes:
        conn.execute(alteracao)

    for comando_novo in comandos:
        conn.execute(comando_novo)

    mantidos[indice] = novo_create
    mantidos.extend(comandos)

    print(
        f">>> database: a tabela '{tabela}' não tinha a coluna "
        f"{', '.join(novas)}; criada, e os valores do INSERT foram aplicados"
    )

    return True


def garantir_coluna_imagem(schema_sql, pedido=""):
    """Dá uma coluna 'imagem' às tabelas de itens que ainda não têm.

    Vale para tabelas de "coisas que aparecem em cards" (sem colunas *_id e
    sem senha) quando elas têm preço, quando o pedido fala de loja/produto/
    catálogo, ou quando alguma tabela já usa imagens. Os valores são criados
    depois pelo ilustrador (SVGs em static/img/).
    """

    info = info_do_schema(schema_sql)

    if not info:
        return schema_sql

    ja_tem_imagem = any(
        COLUNA_IMAGEM_RE.search(c) for colunas in info.values() for c in colunas
    )

    pedido_visual = bool(PEDIDO_VISUAL_RE.search(sem_acento(pedido).lower()))

    alvo = []

    for tabela, colunas in info.items():

        if any(COLUNA_IMAGEM_RE.search(c) for c in colunas):
            continue

        if any(c.lower().endswith("_id") for c in colunas):
            continue

        if any(SEGREDO_RE.search(c) for c in colunas):
            continue

        if (
            any(COLUNA_PRECO_RE.search(c) for c in colunas)
            or ja_tem_imagem
            or pedido_visual
        ):
            alvo.append(tabela)

    if not alvo:
        return schema_sql

    comandos = dividir_comandos_sql(schema_sql)

    for tabela in alvo:

        for i, comando in enumerate(comandos):

            if re.match(
                rf'(?is)^\s*CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`\[]?'
                rf'{re.escape(tabela)}["`\]]?\s*\(', comando
            ):
                comandos[i] = adicionar_coluna_ao_create(comando, "imagem", "TEXT")
                break

    print(
        ">>> database: coluna 'imagem' criada em: " + ", ".join(alvo)
        + " (os cards ganham uma ilustração)"
    )

    return "\n\n".join(comandos) + "\n"


# ---------------------------------------------------------------
# DADOS DE EXEMPLO: sem linhas no banco, a API devolve [] e o site abre
# sem nenhum card (e sem nenhum erro).
# ---------------------------------------------------------------

def linhas_por_tabela(schema_sql):
    """Quantas linhas cada tabela tem depois de executar o schema."""

    try:
        conn = sqlite3.connect(":memory:")
        conn.executescript(schema_sql)

        tabelas = [
            linha[0] for linha in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            )
        ]

        contagem = {
            t: conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            for t in tabelas
        }

        conn.close()

        return contagem

    except sqlite3.Error:
        return {}


def sql_da_tabela(schema_sql, tabela):
    """O CREATE TABLE de uma tabela do esquema ('' se não achar)."""

    try:
        conn = sqlite3.connect(":memory:")
        conn.executescript(schema_sql)

        linha = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
            (tabela,)
        ).fetchone()

        conn.close()

        return linha[0] if linha else ""

    except sqlite3.Error:
        return ""


def inserts_genericos(schema_sql, tabela, quantidade=5):
    """INSERTs simples feitos só com código, para quando o modelo falha."""

    try:
        conn = sqlite3.connect(":memory:")
        conn.executescript(schema_sql)
        colunas = conn.execute(f'PRAGMA table_info("{tabela}")').fetchall()
        conn.close()
    except sqlite3.Error:
        return []

    # linhas do PRAGMA: (cid, nome, tipo, notnull, valor_padrao, pk)
    campos = [c for c in colunas if not c[5] and c[4] is None]

    if not campos:
        return []

    singular = tabela[:-1] if tabela.lower().endswith("s") and len(tabela) > 3 else tabela

    def texto(valor):
        return "'" + str(valor).replace("'", "''") + "'"

    inserts = []

    for i in range(1, quantidade + 1):

        valores = []

        for _, nome, tipo, *_resto in campos:

            n = nome.lower()
            t = (tipo or "").upper()

            if "date" in n or "data" in n or "DATE" in t or "TIME" in t:
                valores.append(texto(f"2026-01-{i:02d}"))
            elif n.endswith("_id"):
                valores.append("1")
            elif "INT" in t:
                valores.append(str(i))
            elif any(x in t for x in ("REAL", "FLOA", "DOUB", "NUM", "DEC")):
                valores.append(f"{19.9 + 10 * i:.2f}")
            elif "email" in n:
                valores.append(texto(f"exemplo{i}@email.com"))
            elif "senha" in n or "password" in n:
                valores.append(texto("senha123"))
            elif any(x in n for x in ("imagem", "foto", "img")):
                valores.append(texto(""))
            elif any(x in n for x in ("descricao", "conteudo", "texto", "sinopse")):
                valores.append(texto(f"Descricao do item {i}"))
            else:
                valores.append(texto(f"{singular.capitalize()} {i}"))

        nomes = ", ".join(c[1] for c in campos)

        inserts.append(
            f"INSERT INTO {tabela} ({nomes}) VALUES ({', '.join(valores)});"
        )

    return inserts


def inserts_do_modelo(tabela, create_sql, tema):
    """Pede ao modelo uns INSERTs de exemplo (tarefa pequena e focada)."""

    resposta = chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você escreve dados de exemplo para um banco SQLite. "
                    "Responda SOMENTE com comandos SQL INSERT INTO, um por "
                    "linha, cada um terminando com ponto e vírgula. Sem "
                    "explicações, sem markdown e sem CREATE TABLE."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"TEMA DO SITE:\n{tema}\n\nTABELA:\n{create_sql}\n\n"
                    f"Escreva 6 comandos INSERT INTO {tabela} com dados "
                    "realistas, em português, combinando com o tema. Não "
                    "informe a coluna id (ela é automática). Use exatamente "
                    "os nomes de colunas da tabela e textos entre aspas "
                    "simples."
                ),
            },
        ],
        options={"num_ctx": 4096},
    ).message.content

    padrao_tabela = rf"INSERT\s+INTO\s+[\"`\[]?{re.escape(tabela)}\b"

    return [
        comando
        for comando in re.findall(
            r"INSERT\s+INTO\b.*?;", resposta, re.IGNORECASE | re.DOTALL
        )
        if re.match(padrao_tabela, comando, re.IGNORECASE)
    ]


def garantir_dados_exemplo(schema_sql, tema=""):
    """Se a tabela principal estiver vazia, acrescenta INSERTs de exemplo."""

    info = info_do_schema(schema_sql)

    if not info:
        return schema_sql

    principal = tabela_principal(info)

    if not principal or linhas_por_tabela(schema_sql).get(principal, 0) >= 1:
        return schema_sql

    print(
        f">>> database: a tabela '{principal}' não tem dados de exemplo "
        "(o site abriria sem nenhum card). Gerando dados..."
    )

    inserts = ""

    try:

        candidatos = inserts_do_modelo(
            principal, sql_da_tabela(schema_sql, principal), tema
        )

        texto = remover_acentos_dos_nomes("\n".join(candidatos))

        if linhas_por_tabela(schema_sql + "\n" + texto).get(principal, 0) >= 3:
            inserts = texto
            print(">>> database: dados de exemplo gerados pelo modelo")

    except Exception as erro:

        print(f">>> database: o modelo não gerou os dados ({erro})")

    if not inserts:

        inserts = "\n".join(inserts_genericos(schema_sql, principal))

        if inserts:
            print(">>> database: usando dados de exemplo genéricos")

    if not inserts:
        return schema_sql

    return schema_sql.rstrip() + "\n\n" + inserts + "\n"


# ---------------------------------------------------------------
# PALETA: contraste mínimo entre texto e fundo
# ---------------------------------------------------------------

# Variáveis que o designer é obrigado a definir em :root
VARIAVEIS_PALETA = [
    "--fundo", "--superficie", "--texto", "--texto-suave",
    "--primaria", "--primaria-hover", "--sobre-primaria", "--borda",
]


def hex_para_rgb(valor):

    v = (valor or "").strip().lstrip("#")

    if len(v) == 3:
        v = "".join(c * 2 for c in v)

    if len(v) != 6:
        return None

    try:
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def luminancia(rgb):

    def canal(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (canal(x) for x in rgb)

    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    """Razão de contraste (WCAG) entre duas cores RGB: de 1 a 21."""

    la, lb = luminancia(a), luminancia(b)

    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def rgb_para_hex(rgb):
    return "#%02x%02x%02x" % tuple(int(max(0, min(255, c))) for c in rgb)


def ajustar_paleta(css):
    """Conserta no :root o que deixaria o texto ilegível.

    Se o texto não tem contraste suficiente com o fundo (ou o texto do botão
    com a cor do botão), troca o texto por branco ou quase preto, o que
    funcionar melhor. Se o hover do botão for igual à cor normal, escurece
    (ou clareia) um pouco. Devolve (css, lista_de_ajustes).
    """

    ajustes = []

    def variaveis():
        return dict(re.findall(
            r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})\s*;", css
        ))

    def definir(nome, valor):
        return re.sub(
            rf"({re.escape(nome)}\s*:\s*)#[0-9a-fA-F]{{3,6}}",
            rf"\g<1>{valor}",
            css,
            count=1
        )

    # Fundo claro com superfície escura (ou o contrário) não tem texto único
    # que sirva nos dois (ex.: menu #111 sobre cabeçalho #1B1F24). Aproxima a
    # superfície do tom do fundo.
    vf, vs = variaveis().get("--fundo"), variaveis().get("--superficie")
    rf, rs = hex_para_rgb(vf), hex_para_rgb(vs)

    if rf and rs:

        def serve_nos_dois(a, b):
            return any(
                contraste(t, a) >= 4.5 and contraste(t, b) >= 4.5
                for t in [(255, 255, 255), (17, 17, 17)]
            )

        if not serve_nos_dois(rf, rs):
            fundo_claro = luminancia(rf) > 0.4
            novo = (
                _misturar_hex(vf, "#ffffff", 0.6) if fundo_claro
                else _misturar_hex(vf, "#ffffff", 0.08)
            )
            if not serve_nos_dois(rf, hex_para_rgb(novo)):
                novo = vf
            ajustes.append(
                f"--superficie: {vs} -> {novo} (fundo e superfície em tons opostos "
                "deixavam o texto do menu/cabeçalho ilegível)"
            )
            css = definir("--superficie", novo)

    pares = [
        ("--texto", ["--fundo", "--superficie"]),
        ("--texto-suave", ["--fundo", "--superficie"]),
        ("--sobre-primaria", ["--primaria", "--primaria-hover"]),
    ]

    for nome, fundos in pares:

        vars_ = variaveis()

        texto_rgb = hex_para_rgb(vars_.get(nome))
        fundos_rgb = [
            hex_para_rgb(vars_.get(f)) for f in fundos if hex_para_rgb(vars_.get(f))
        ]

        if not texto_rgb or not fundos_rgb:
            continue

        if all(contraste(texto_rgb, f) >= 4.5 for f in fundos_rgb):
            continue

        melhor = max(
            [(255, 255, 255), (17, 17, 17)],
            key=lambda cor: min(contraste(cor, f) for f in fundos_rgb)
        )

        novo = rgb_para_hex(melhor)

        ajustes.append(f"{nome}: {vars_[nome]} -> {novo} (contraste baixo)")

        css = definir(nome, novo)

    vars_ = variaveis()

    primaria = hex_para_rgb(vars_.get("--primaria"))
    hover = hex_para_rgb(vars_.get("--primaria-hover"))

    if primaria and hover and primaria == hover:

        fator = 0.85 if luminancia(primaria) > 0.2 else 1.25

        novo = rgb_para_hex([c * fator for c in primaria])

        ajustes.append(f"--primaria-hover: igual à --primaria -> {novo}")

        css = definir("--primaria-hover", novo)

    # Borda com a mesma cor do fundo (ou dos cards) fica invisível na tela:
    # puxa um pouco para a cor do texto, para ela aparecer.
    vars_ = variaveis()

    borda = hex_para_rgb(vars_.get("--borda"))
    superficie = hex_para_rgb(vars_.get("--superficie"))
    fundo = hex_para_rgb(vars_.get("--fundo"))
    texto = hex_para_rgb(vars_.get("--texto"))

    if borda and texto and borda in (superficie, fundo):

        novo = rgb_para_hex([b * 0.8 + t * 0.2 for b, t in zip(borda, texto)])

        ajustes.append(
            f"--borda: igual ao fundo ({vars_['--borda']}) -> {novo} "
            "(a borda ficava invisível)"
        )

        css = definir("--borda", novo)

    return css, ajustes


def _misturar_hex(a, b, t):
    """Mistura duas cores (#rrggbb): t=0 devolve a, t=1 devolve b."""

    ra, rb = hex_para_rgb(a), hex_para_rgb(b)

    return rgb_para_hex([x * (1 - t) + y * t for x, y in zip(ra, rb)])


def _melhor_texto_sobre(cor):
    """#111111 ou #ffffff, o que tiver mais contraste com a cor."""

    rgb = hex_para_rgb(cor)

    return "#111111" if contraste(rgb, (17, 17, 17)) >= contraste(rgb, (255, 255, 255)) else "#ffffff"


def _saturacao(rgb):
    mx, mn = max(rgb), min(rgb)
    return 0 if mx == 0 else (mx - mn) / mx


def completar_variaveis_root(css):
    """Cria no :root as variáveis da paleta que o designer esqueceu.

    O validador exige --fundo, --texto, --primaria etc. em hexadecimal. Em vez
    de jogar fora um CSS bom por faltar uma variável, deriva as que faltam
    das que existem. Devolve (css, lista_de_ajustes).
    """

    ajustes = []

    m = re.search(r":root\s*\{([^{}]*)\}", css)

    existentes = dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})\s*;", m.group(1))) if m else {}

    faltam = [v for v in VARIAVEIS_PALETA if v not in existentes]

    if not faltam:
        return css, ajustes

    todas = [
        "#%02x%02x%02x" % hex_para_rgb(h)
        for h in re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", css) if hex_para_rgb(h)
    ]
    todas = list(dict.fromkeys(todas)) or ["#ffffff", "#222222", "#c8863a"]

    # apelidos: --cor-creme, --bg, --main-color... para os papéis da paleta
    apelidos = {
        "--fundo": r"fundo|bg|background|creme|claro",
        "--texto": r"texto|text|grafite|fg|escuro",
        "--primaria": r"primar|principal|main|brand|caramelo|accent|destaque",
        "--borda": r"borda|border",
        "--superficie": r"superficie|surface|card",
    }

    valores = {}

    for papel, padrao in apelidos.items():
        for nome, valor in existentes.items():
            if papel not in valores and re.search(padrao, nome, re.IGNORECASE):
                valores[papel] = valor

    for nome in VARIAVEIS_PALETA:
        if nome in existentes:
            valores[nome] = existentes[nome]

    claras = [c for c in todas if luminancia(hex_para_rgb(c)) > 0.6]
    escuras = [c for c in todas if luminancia(hex_para_rgb(c)) < 0.15]

    valores.setdefault("--fundo", max(claras, key=lambda c: luminancia(hex_para_rgb(c))) if claras else "#ffffff")
    fundo = valores["--fundo"]
    fundo_claro = luminancia(hex_para_rgb(fundo)) > 0.4

    valores.setdefault("--texto", (min(escuras, key=lambda c: luminancia(hex_para_rgb(c))) if escuras else "#1f1f1f") if fundo_claro else "#f5f5f5")

    # texto precisa ser legível sobre o fundo
    if contraste(hex_para_rgb(valores["--texto"]), hex_para_rgb(fundo)) < 4.5:
        valores["--texto"] = "#1f1f1f" if fundo_claro else "#f5f5f5"

    coloridas = sorted(
        [c for c in todas if _saturacao(hex_para_rgb(c)) > 0.3],
        key=lambda c: -_saturacao(hex_para_rgb(c))
    )

    valores.setdefault("--primaria", coloridas[0] if coloridas else "#c8863a")
    valores.setdefault("--superficie", _misturar_hex(fundo, "#ffffff" if fundo_claro else "#000000", 0.55 if fundo_claro else 0.15))
    valores.setdefault("--texto-suave", _misturar_hex(valores["--texto"], fundo, 0.3))
    valores.setdefault("--primaria-hover", _misturar_hex(valores["--primaria"], "#000000", 0.18))
    valores.setdefault("--sobre-primaria", _melhor_texto_sobre(valores["--primaria"]))
    valores.setdefault("--borda", _misturar_hex(fundo, valores["--texto"], 0.2))

    linhas = "".join(f"    {n}: {valores[n]};\n" for n in faltam)

    if m:
        css = css[:m.end() - 1].rstrip() + "\n" + linhas + css[m.end() - 1:]
    else:
        css = ":root {\n" + linhas + "}\n\n" + css

    ajustes.append("variáveis criadas no :root: " + ", ".join(faltam))

    return css, ajustes


def restaurar_regras_faltantes(css_novo, css_original, classes_exigidas):
    """Copia do CSS original as regras das classes que o designer perdeu."""

    perdidas = sorted(classes_exigidas - classes_do_css(css_novo))

    if not perdidas:
        return css_novo, []

    original = re.sub(r"/\*.*?\*/", "", css_original, flags=re.DOTALL)

    copiadas = []
    extra = ""

    for seletor, corpo in re.findall(r"([^{}]+)\{([^{}]*)\}", original):

        if any(re.search(rf"\.{re.escape(c)}(?![\w-])", seletor) for c in perdidas):
            extra += f"\n{seletor.strip()} {{{corpo}}}\n"

    if not extra:
        return css_novo, []

    for c in perdidas:
        if re.search(rf"\.{re.escape(c)}(?![\w-])", extra):
            copiadas.append(c)

    return css_novo.rstrip() + "\n\n/* regras restauradas do CSS original */" + extra, copiadas


def papeis_da_paleta(hexes):
    """Distribui as cores do pedido entre os papéis do site (fundo, cabeçalho...)."""

    cores = list(dict.fromkeys(
        "#%02x%02x%02x" % hex_para_rgb(h) for h in hexes if hex_para_rgb(h)
    ))

    if len(cores) < 3:
        cores = ["#fff6e8", "#ffffff", "#2b2b2b", "#4b2e1e", "#c8863a", "#5c6b3a"]

    def lum(c):
        return luminancia(hex_para_rgb(c))

    def sat(c):
        return _saturacao(hex_para_rgb(c))

    claras = [c for c in cores if lum(c) > 0.7]

    if claras:  # tema claro
        fundo = max(claras, key=lambda c: (round(sat(c), 2), lum(c)))
        superficie = "#ffffff" if "#ffffff" in cores else _misturar_hex(fundo, "#ffffff", 0.6)
        escuras = [c for c in cores if lum(c) < 0.12]
        texto = min(escuras, key=sat) if escuras else "#1f1f1f"
    else:       # tema escuro
        fundo = min(cores, key=lum)
        superficie = _misturar_hex(fundo, "#ffffff", 0.08)
        texto = max(cores, key=lum) if lum(max(cores, key=lum)) > 0.5 else "#f5f5f5"

    usadas = {fundo, superficie, texto}

    escuras_cor = sorted(
        [c for c in cores if c not in usadas and lum(c) < 0.2 and sat(c) > 0.25], key=lum
    )
    cabecalho = escuras_cor[0] if escuras_cor else (texto if claras else _misturar_hex(fundo, "#000000", 0.3))

    restantes = sorted(
        [c for c in cores if c not in usadas | {cabecalho} and sat(c) > 0.3], key=lambda c: -sat(c)
    )
    primaria = restantes[0] if restantes else cabecalho
    secundaria = restantes[1] if len(restantes) > 1 else primaria

    if contraste(hex_para_rgb(texto), hex_para_rgb(fundo)) < 4.5:
        texto = "#1f1f1f" if lum(fundo) > 0.4 else "#f5f5f5"

    return {
        "fundo": fundo,
        "superficie": superficie,
        "texto": texto,
        "texto-suave": _misturar_hex(texto, fundo, 0.3),
        "cabecalho": cabecalho,
        "sobre-cabecalho": _melhor_texto_sobre(cabecalho),
        "primaria": primaria,
        "primaria-hover": _misturar_hex(primaria, "#000000", 0.18),
        "sobre-primaria": _melhor_texto_sobre(primaria),
        "secundaria": secundaria,
        "sobre-secundaria": _melhor_texto_sobre(secundaria),
        "borda": _misturar_hex(fundo, texto, 0.18),
    }


def gerar_css_reserva(html, classes, pedido, css_original):
    """CSS completo e seguro, usado quando o designer não entrega um CSS válido.

    Usa as cores citadas no pedido do usuário (ou, na falta delas, as do CSS
    original) e as classes que o HTML/JS realmente usam.
    """

    hexes = re.findall(r"#[0-9a-fA-F]{6}\b", pedido or "") or re.findall(
        r"#[0-9a-fA-F]{6}\b", css_original or ""
    )

    p = papeis_da_paleta(hexes)

    raiz = ":root {\n" + "".join(f"    --{n}: {v};\n" for n, v in p.items()) + (
        "    --raio: 12px;\n"
        "    --sombra: 0 4px 14px rgba(0, 0, 0, 0.12);\n"
        "}\n\n"
    )

    todas = set(classes) | classes_do_css(css_original or "")

    grades = sorted(c for c in todas if any(t in c.lower() for t in ("grid", "grade", "lista"))) or ["produtos-grid"]
    cards = sorted(c for c in todas if "card" in c.lower()) or ["produto-card"]

    G = ", ".join(f".{c}" for c in grades)
    C = ", ".join(f".{c}" for c in cards)
    CH = ", ".join(f".{c}:hover" for c in cards)
    CI = ", ".join(f".{c} img" for c in cards)
    CH3 = ", ".join(f".{c} h3" for c in cards)
    CP = ", ".join(f".{c} p" for c in cards)
    CB = ", ".join(f".{c} button" for c in cards)

    corpo = f"""* {{ box-sizing: border-box; }}

body {{
    margin: 0;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    background-color: var(--fundo);
    color: var(--texto);
    line-height: 1.5;
}}

header {{
    background-color: var(--cabecalho);
    color: var(--sobre-cabecalho);
    padding: 16px 28px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--sombra);
}}

header h1 {{
    margin: 0;
    font-size: 1.5rem;
    letter-spacing: 0.04em;
    color: inherit;
}}

nav, nav ul, footer ul {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 8px;
    list-style: none;
    margin: 0;
    padding: 0;
}}

nav li, footer li {{
    list-style: none;
}}

nav a, nav button {{
    position: static;
    background: transparent;
    color: var(--sobre-cabecalho);
    border: 1px solid transparent;
    border-radius: var(--raio);
    padding: 8px 14px;
    font: inherit;
    text-decoration: none;
    cursor: pointer;
    box-shadow: none;
    transition: background-color 0.2s ease;
}}

nav a:hover, nav button:hover {{
    background-color: rgba(127, 127, 127, 0.28);
}}

nav [id*="fazer"], nav [id*="comprar"], nav .destaque {{
    background-color: var(--primaria);
    color: var(--sobre-primaria);
    font-weight: 600;
}}

nav [id*="fazer"]:hover, nav [id*="comprar"]:hover, nav .destaque:hover {{
    background-color: var(--primaria-hover);
}}

main {{
    max-width: 1600px;
    margin: 0 auto;
    padding: 32px 24px 56px;
}}

section {{
    margin-bottom: 48px;
    scroll-margin-top: 90px;
}}

h2 {{
    margin: 0 0 20px;
    font-size: 1.6rem;
    color: var(--cabecalho);
    display: inline-block;
    padding-bottom: 4px;
    border-bottom: 3px solid var(--primaria);
}}

#hero, .hero {{
    background-color: var(--cabecalho);
    color: var(--sobre-cabecalho);
    text-align: center;
    padding: 56px 24px;
    border-radius: var(--raio);
}}

#hero h1, #hero h2, .hero h1 {{
    color: inherit;
    border: none;
}}

{G} {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 20px;
    width: 100%;
}}

{C} {{
    background-color: var(--superficie);
    border: 1px solid var(--borda);
    border-radius: var(--raio);
    padding: 16px;
    box-shadow: var(--sombra);
    display: flex;
    flex-direction: column;
    gap: 8px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}

{CH} {{
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
}}

{CI}, .card-img {{
    display: block;
    width: 100%;
    aspect-ratio: 16 / 10;
    object-fit: cover;
    border-radius: 8px;
}}

{CH3} {{
    margin: 0;
    font-size: 1.1rem;
    color: var(--texto);
}}

{CP} {{
    margin: 0;
    color: var(--texto-suave);
}}

.etiqueta {{
    align-self: flex-start;
    background-color: var(--secundaria);
    color: var(--sobre-secundaria);
    font-size: 0.75rem;
    padding: 2px 10px;
    border-radius: 999px;
}}

button {{
    font: inherit;
    cursor: pointer;
    border: none;
    border-radius: var(--raio);
    padding: 10px 18px;
    background-color: var(--primaria);
    color: var(--sobre-primaria);
    transition: background-color 0.2s ease;
}}

button:hover {{
    background-color: var(--primaria-hover);
}}

{CB} {{
    margin-top: auto;
}}

footer {{
    background-color: var(--cabecalho);
    color: var(--sobre-cabecalho);
    text-align: center;
    padding: 24px;
}}

footer a {{
    color: var(--sobre-cabecalho);
    text-decoration: none;
}}

#mensagem-status:empty {{
    display: none;
}}

#mensagem-status {{
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background-color: var(--cabecalho);
    color: var(--sobre-cabecalho);
    border-radius: var(--raio);
    padding: 12px 20px;
    z-index: 1000;
    box-shadow: var(--sombra);
}}

@media (max-width: 640px) {{
    header {{ flex-direction: column; align-items: flex-start; }}
    main {{ padding: 20px 14px 40px; }}
}}
"""

    return "/* CSS de reserva: gerado pelo orchestrator com as cores do pedido */\n" + raiz + corpo


def restaurar_variaveis_perdidas(css_novo, css_original):
    """Recoloca no :root as variáveis do CSS original que o novo ainda usa.

    Ex.: o designer escreve var(--azul-marinho) nas regras mas apaga a
    definição --azul-marinho: #023047; sem ela a cor some e o site fica sem
    a paleta pedida. Devolve (css, lista_de_variaveis_restauradas).
    """

    usadas = set(re.findall(r"var\(\s*(--[\w-]+)", css_novo))
    definidas = set(re.findall(r"(--[\w-]+)\s*:", css_novo))

    originais = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;{}]+);", css_original or ""))

    # as que o CSS novo usa e não define + as cores nomeadas do original
    # (--azul-*, --cor-*) que o designer deixou de lado
    faltam = sorted(n for n in usadas - definidas if n in originais)

    if not faltam:
        return css_novo, []

    linhas = "".join(f"    {n}: {originais[n].strip()};\n" for n in faltam)

    m = re.search(r":root\s*\{", css_novo)

    if m:
        css_novo = css_novo[:m.end()] + "\n" + linhas.rstrip("\n") + css_novo[m.end():]
    else:
        css_novo = ":root {\n" + linhas + "}\n\n" + css_novo

    return css_novo, faltam


def resolver_alias_root(css):
    """Troca '--fundo: var(--azul-claro)' pelo hexadecimal de --azul-claro."""

    m = re.search(r":root\s*\{([^{}]*)\}", css)

    if not m:
        return css

    corpo = m.group(1)
    valores = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", corpo))

    def resolver(nome, nivel=0):
        valor = valores.get(nome, "").strip()
        ref = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", valor)
        if ref and nivel < 5:
            return resolver(ref.group(1), nivel + 1)
        return valor

    def trocar(mm):
        nome, valor = mm.group(1), mm.group(2).strip()
        if re.fullmatch(r"var\(\s*--[\w-]+\s*\)", valor):
            final = resolver(nome)
            if final and not final.startswith("var("):
                return f"{nome}: {final};"
        return mm.group(0)

    novo_corpo = re.sub(r"(--[\w-]+)\s*:\s*([^;]+);", trocar, corpo)

    # variável declarada duas vezes: vale a última, então mantém só ela
    vistos = {}
    for mm in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", novo_corpo):
        vistos[mm.group(1)] = mm.group(0)
    linhas = [vistos[n] for n in dict.fromkeys(re.findall(r"(--[\w-]+)\s*:", novo_corpo))]
    novo_corpo = "\n    " + "\n    ".join(linhas) + "\n"

    return css[:m.start(1)] + novo_corpo + css[m.end(1):]


def cores_do_pedido_ausentes(css, pedido):
    """Cores (#rrggbb) citadas no pedido que não aparecem no CSS."""

    pedidas = list(dict.fromkeys(h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", pedido or "")))

    if len(pedidas) < 3:
        return []

    no_css = {h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", css)}

    return [c for c in pedidas if c not in no_css]


def completar_estilos_base(css):
    """Acrescenta estilos básicos para o que o designer deixou sem regra.

    Só entra o que faltar (regras de baixa especificidade, que não mexem no
    que o designer já estilizou): botões, títulos, <main>, imagens, rolagem.
    """

    sem = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    seletores = [s.strip() for s, _ in re.findall(r"([^{}]+)\{([^{}]*)\}", sem)]

    def tem(padrao):
        return any(re.fullmatch(padrao, s) for s in seletores)

    extra = ""
    ajustes = []

    if not tem(r"button"):
        extra += (
            "button {\n    font: inherit;\n    cursor: pointer;\n    border: none;\n"
            "    border-radius: var(--raio, 10px);\n    padding: 10px 18px;\n"
            "    background-color: var(--primaria);\n    color: var(--sobre-primaria);\n}\n\n"
            "button:hover {\n    background-color: var(--primaria-hover);\n}\n\n"
        )
        ajustes.append("estilo básico para os botões que ficaram sem regra")

    if not tem(r"main"):
        extra += "main {\n    max-width: 1400px;\n    margin: 0 auto;\n    padding: 24px;\n}\n\n"
        ajustes.append("<main> centralizado e com largura máxima")

    if not tem(r"h2|section h2|main h2"):
        extra += "h2 {\n    margin: 0 0 16px;\n    color: var(--texto);\n}\n\n"
        ajustes.append("estilo para os títulos <h2>")

    if not tem(r"section"):
        extra += "section {\n    margin-bottom: 40px;\n}\n\n"

    if not any("scroll-behavior" in c for _, c in re.findall(r"([^{}]+)\{([^{}]*)\}", sem)):
        extra += "html {\n    scroll-behavior: smooth;\n}\n\nsection {\n    scroll-margin-top: 90px;\n}\n\n"

    if extra:
        css = css.rstrip() + "\n\n/* Ajuste automático: estilos básicos que faltavam */\n" + extra.rstrip() + "\n"

    return css, ajustes


def consertar_css_visual(css):
    """Botões com largura/altura fixas cortavam o texto; campos de formulário
    usavam a cor do texto como fundo. Devolve (css, lista_de_ajustes)."""

    ajustes = []

    def regra(m):
        seletor, corpo = m.group(1), m.group(2)
        sel = seletor.strip().lower()
        original = corpo

        if re.search(r"(^|[\s,>+~])(button|\.btn[\w-]*|\.botao[\w-]*)\s*(:[\w-]+)?\s*(,|$)", sel) or sel.endswith("button"):
            sem_tamanho = re.sub(r"(?<![\w-])width\s*:\s*\d+px\s*;", "", corpo)
            sem_tamanho = re.sub(
                r"(?<![\w-])height\s*:\s*\d+px\s*;", "min-height: 36px;", sem_tamanho
            )
            if sem_tamanho != corpo:  # só mexe se havia tamanho fixo
                corpo = sem_tamanho.rstrip() + "\n    width: auto;\n"
                if "padding" not in corpo:
                    corpo += "    padding: 8px 18px;\n"

        if re.search(r"input|textarea|select", sel):
            novo = re.sub(
                r"(background(?:-color)?\s*:\s*)var\(--texto(?:-suave)?\)",
                r"\1var(--superficie)", corpo
            )
            if novo != corpo and "color:" not in re.sub(r"background-color:[^;]*;", "", novo):
                novo = novo.rstrip() + "\n    color: var(--texto);\n"
            corpo = novo

        if corpo != original:
            ajustes.append(f"{seletor.strip()}: tamanho fixo/fundo do campo corrigido")
        return seletor + "{" + corpo + "}"

    css = re.sub(r"([^{}@]+)\{([^{}]*)\}", regra, css)

    return css, ajustes


def consertar_css_do_designer(css):
    """Desfaz os usos errados de variáveis que o modelo pequeno costuma fazer.

    Exemplos reais: --sombra: 10px (sem cor) usada como "0 0 var(--sombra)
    var(--espaco)", que vira um brilho enorme; minmax(var(--espaco), 1fr),
    que cria dezenas de colunas de 20px e empilha os cards; texto escuro
    (--sobre-primaria) em títulos sobre fundo escuro; cards com largura e
    altura fixas; hover que deixa o card cinza-claro com texto claro.
    Devolve (css, lista_de_ajustes).
    """

    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)  # comentários

    ajustes = []

    def registrar(texto):
        if texto not in ajustes:
            ajustes.append(texto)

    def eh_comprimento(valor):
        return bool(re.fullmatch(r"\s*-?\d+(\.\d+)?(px|rem|em|%)\s*", valor))

    # ---- 1) valores das variáveis que não são cores ----------------------
    def corrigir_root(m):

        corpo = m.group(2)

        def corrigir_var(v):

            nome, valor = v.group(1), v.group(2).strip()

            if nome == "--sombra" and not re.search(r"rgba?\(|#[0-9a-fA-F]{3,8}|hsla?\(", valor):
                registrar(f"--sombra: {valor} (sem cor) -> sombra suave")
                valor = "0 4px 14px rgba(0, 0, 0, 0.35)"

            if nome in ("--espaco", "--raio") and not eh_comprimento(valor):
                registrar(f"{nome}: {valor} não é um tamanho")
                valor = "20px" if nome == "--espaco" else "10px"

            return f"{nome}: {valor};"

        corpo = re.sub(r"(--[\w-]+)\s*:\s*([^;]+);", corrigir_var, corpo)

        return m.group(1) + "{" + corpo + "}"

    css = re.sub(r"(:root\s*)\{([^{}]*)\}", corrigir_root, css)

    vars_ = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", css))
    fonte_eh_tamanho = eh_comprimento(vars_.get("--fonte", ""))

    # ---- 2) regra por regra ----------------------------------------------
    def corrigir_regra(m):

        seletor, corpo = m.group(1), m.group(2)

        sel = seletor.strip()

        if sel.startswith(":root") or sel.startswith("@"):
            return m.group(0)

        eh_botao = bool(re.search(r"button|btn|botao", sel, re.IGNORECASE))
        eh_card = bool(re.search(r"card", sel, re.IGNORECASE)) and not eh_botao
        so_o_card = bool(re.fullmatch(r"(?:[.#][\w-]*card[\w-]*|[\w.#\s-]*\s[.#][\w-]*card[\w-]*)(?::hover)?", sel))
        com_estado = bool(re.search(r":(hover|active|disabled|focus)", sel))

        # regras sem sentido para um card (card :disabled, :active:hover...)
        if eh_card and re.search(r":disabled|:active", sel):
            registrar(f"removida a regra sem sentido {sel}")
            return ""

        def trocar(padrao, novo, texto, aviso=None):
            resultado = re.sub(padrao, novo, texto, flags=re.IGNORECASE)
            if aviso and resultado != texto:
                registrar(aviso)
            return resultado

        # sombra com variáveis erradas -> usa só a --sombra
        corpo = trocar(
            r"box-shadow\s*:[^;]*var\(--(?:sombra|espaco|raio)\)[^;]*;",
            "box-shadow: var(--sombra);",
            corpo,
            "box-shadow montado com várias variáveis -> box-shadow: var(--sombra)"
        )

        # grade com colunas de 20px
        corpo = re.sub(
            r"(grid-template-columns\s*:[^;]*?minmax\()\s*([^,]+?)\s*,",
            lambda g: (
                g.group(1) + "220px,"
                if g.group(2).startswith("var(") or (
                    re.fullmatch(r"\d+px", g.group(2).strip())
                    and int(g.group(2).strip()[:-2]) < 140
                ) else g.group(0)
            ),
            corpo,
            flags=re.IGNORECASE
        )

        # grade dentro de um <main> flex centralizado encolhe até caber 1 card:
        # garante que ela ocupe a largura toda
        if re.search(r"grid-template-columns\s*:\s*repeat\(\s*auto-", corpo) and not re.search(
            r"(?<![\w-])width\s*:", corpo
        ):
            corpo = corpo.rstrip() + (
                "\n    width: 100%;\n    max-width: 1200px;\n    box-sizing: border-box;\n"
            )
            registrar(f"{sel}: a grade ocupa a largura toda (várias colunas)")

        # <main> com 100px de respiro de cada lado deixa o conteúdo espremido
        if sel == "main" and re.search(r"padding\s*:\s*(?:[89]\d|\d{3,})px\s*;", corpo):
            corpo = re.sub(r"padding\s*:\s*[^;]+;", "padding: 40px 20px;", corpo)
            registrar("main: espaçamento lateral reduzido")

        # texto escuro (cor "sobre a primária") fora de botões
        if not eh_botao and not re.search(
            r"background(?:-color)?\s*:\s*var\(--primaria\)", corpo
        ):
            corpo = trocar(
                r"(?<![\w-])color\s*:\s*var\(--sobre-primaria\)",
                "color: var(--texto)",
                corpo,
                f"{sel}: texto escuro em fundo escuro -> var(--texto)"
            )

        # texto na cor da borda (ex: links com color: var(--borda) num
        # cabeçalho que também usa --borda de fundo ficam invisíveis) ou com
        # pouco contraste sobre o fundo/superfície -> cor do texto
        if not eh_botao and not re.search(r"hero|banner|footer|rodape|capa", sel, re.IGNORECASE):

            def texto_legivel(mm):
                nome_var = mm.group(1)
                if nome_var in ("--texto", "--texto-suave", "--sobre-primaria"):
                    return mm.group(0)
                if nome_var != "--borda":
                    cor = hex_para_rgb(vars_.get(nome_var, ""))
                    bases = [hex_para_rgb(vars_.get(v, "")) for v in ("--fundo", "--superficie")]
                    bases = [b for b in bases if b]
                    if not cor or not bases or min(contraste(cor, b) for b in bases) >= 3:
                        return mm.group(0)
                registrar(f"{sel}: texto com {nome_var} ilegível -> var(--texto)")
                return "color: var(--texto)"

            corpo = re.sub(
                r"(?<![\w-])color\s*:\s*var\((--(?:borda|primaria|primaria-hover))\)",
                texto_legivel, corpo, flags=re.IGNORECASE
            )

        # tamanhos fixos nos cards: a grade é quem manda
        if so_o_card and not com_estado:
            corpo = trocar(r"(?<![\w-])width\s*:\s*\d+px\s*;", "", corpo,
                           f"{sel}: removida a largura fixa")
            corpo = trocar(r"(?<![\w-])height\s*:\s*\d+px\s*;", "", corpo,
                           f"{sel}: removida a altura fixa")
            corpo = trocar(r"(?<![\w-])transform\s*:\s*translateY\([^)]*\)\s*;", "", corpo,
                           f"{sel}: removido o deslocamento fixo do card")

        # hover do card: fundo claro com texto claro fica ilegível
        if eh_card and ":hover" in sel:
            novo = re.sub(
                r"background(?:-color)?\s*:\s*var\(--primaria-hover\)\s*;",
                "", corpo, flags=re.IGNORECASE
            )
            if novo != corpo:
                registrar(f"{sel}: o hover não troca mais o fundo (texto ficava ilegível)")
                corpo = novo
            corpo = re.sub(
                r"transform\s*:\s*translateY\(\s*[0-9.]+(?:px|rem)\s*\)\s*;",
                "transform: translateY(-4px);", corpo
            )
            if not re.search(r"transform", corpo):
                corpo = corpo.rstrip() + "\n    transform: translateY(-4px);\n"

        # botão com padding gigante (20px em cima e embaixo)
        if eh_botao:
            corpo = trocar(
                r"padding\s*:\s*var\(--espaco\)\s+var\(--espaco\)\s*;",
                "padding: 10px 20px;", corpo,
                f"{sel}: padding do botão reduzido"
            )

        # títulos com o tamanho da variável --fonte (16px)
        ultimo = re.split(r"[\s>+~]", re.sub(r":[\w-]+", "", sel).strip())[-1].lower()
        if ultimo in ("h1", "h2", "h3") and re.search(r"font-size\s*:\s*var\(--fonte\)", corpo):
            tamanho = {"h1": "2rem", "h2": "1.5rem", "h3": "1.15rem"}[ultimo]
            corpo = re.sub(r"font-size\s*:\s*var\(--fonte\)", f"font-size: {tamanho}", corpo)
            registrar(f"{sel}: título com tamanho próprio ({tamanho})")

        # --fonte guardava um tamanho mas foi usada como família (ou o inverso)
        if not fonte_eh_tamanho:
            corpo = re.sub(r"font-size\s*:\s*var\(--fonte\)", "font-size: 1rem", corpo)

        if not corpo.strip():
            return ""

        return f"{seletor}{{{corpo}}}"

    css = re.sub(r"([^{}]+)\{([^{}]*)\}", corrigir_regra, css)

    css = re.sub(r"\n{3,}", "\n\n", css).strip() + "\n"

    return css, ajustes


def completar_estilo_dos_cards(css, classes):
    """Garante borda, transição e efeito de hover nos cards.

    O designer é instruído a fazer isso, mas o modelo pequeno às vezes
    esquece. Em vez de descartar o CSS inteiro por isso, acrescenta ao final
    só o que estiver faltando. Devolve (css, lista_de_ajustes).
    """

    sem_comentarios = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)

    regras = re.findall(r"([^{}]+)\{([^{}]*)\}", sem_comentarios)

    ajustes = []
    extra = ""

    for classe in sorted(c for c in classes if "card" in c.lower()):

        da_classe = [
            (seletor, corpo) for seletor, corpo in regras
            if re.search(rf"\.{re.escape(classe)}(?![\w-])", seletor)
        ]

        if not da_classe:
            continue  # a classe nem tem regra: outra conferência cuida disso

        corpos = " ".join(c for s, c in da_classe if ":hover" not in s)

        tem_borda = re.search(
            r"\bborder\s*:|\bborder-(?:top|right|bottom|left|width|color|style)\b",
            corpos
        )
        tem_transicao = "transition" in corpos
        tem_hover = any(":hover" in s for s, _ in da_classe)

        base = []

        if not tem_borda:
            base.append("    border: 1px solid var(--borda);")
            ajustes.append(f".{classe}: borda de 1px com var(--borda)")

        if not tem_transicao:
            base.append("    transition: transform 0.2s ease, box-shadow 0.2s ease;")
            ajustes.append(f".{classe}: transição suave")

        if base:
            extra += f"\n.{classe} {{\n" + "\n".join(base) + "\n}\n"

        if not tem_hover:
            extra += (
                f"\n.{classe}:hover {{\n"
                "    transform: translateY(-4px);\n"
                "    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);\n"
                "}\n"
            )
            ajustes.append(f".{classe}:hover (o card sobe um pouco)")

    if extra:
        css = (
            css.rstrip()
            + "\n\n/* Ajuste automático: borda, transição e hover dos cards */"
            + extra
        )

    return css, ajustes


def metodos_api_do_backend(codigo):
    """{nome_da_rota: {métodos}} das rotas /api/ do backend.py."""

    metodos = {}

    for rota, lista in re.findall(
        r"route\(\s*[\"'](/api/[^\"']+)[\"']\s*(?:,\s*methods\s*=\s*\[([^\]]*)\])?",
        codigo
    ):

        base = rota[len("/api/"):].split("/")[0].lower()

        if not base or base.startswith("<"):
            continue

        achados = {m.upper() for m in re.findall(r"[\"'](\w+)[\"']", lista)}

        metodos.setdefault(base, set()).update(achados or {"GET"})

    return metodos


def ler_texto(caminho):
    """Lê um arquivo de texto ('' se não existir)."""

    if not caminho or not os.path.exists(caminho):
        return ""

    with open(caminho, encoding="utf-8", errors="replace") as arquivo:
        return arquivo.read()


def achar_na_static(caminho_projeto, extensao):
    """Caminho do arquivo static/*<extensao> ('' se não houver).

    Prefere os nomes padrão (index.html, style.css, script.js). Se não
    existirem, usa o primeiro da pasta em ordem alfabética, porque o agente
    de front-end nem sempre chama o arquivo de style.css.
    """

    preferido = {
        ".html": "index.html",
        ".css": "style.css",
        ".js": "script.js",
    }.get(extensao)

    if preferido:
        caminho = os.path.join(caminho_projeto, "static", preferido)
        if os.path.exists(caminho):
            return caminho

    achados = sorted(
        glob.glob(os.path.join(caminho_projeto, "static", f"*{extensao}"))
    )

    return achados[0] if achados else ""


def classes_usadas(*textos):
    """Classes citadas no HTML (class="...") e no JS (className, classList)."""

    classes = set()

    for texto in textos:

        for valor in re.findall(
            r'class(?:Name)?\s*=\s*["\']([^"\']+)["\']', texto
        ):
            classes.update(valor.split())

        for valor in re.findall(
            r'classList\.(?:add|toggle|remove)\(\s*["\']([^"\']+)["\']', texto
        ):
            classes.add(valor)

    return sorted(classes)


def classes_do_css(css):
    """Nomes de classe que aparecem como seletor no CSS (.card, .btn...)."""

    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)  # comentários
    css = re.sub(r"url\([^)]*\)", "", css)                # .jpg, .png...

    return set(re.findall(r"\.([A-Za-z_][\w-]*)", css))


def extrair_css(resposta):
    """Pega o CSS da resposta do designer (com ou sem cerca ```css)."""

    blocos = re.findall(
        r"```(?:css)?[ \t]*\n(.*?)```", resposta, re.DOTALL | re.IGNORECASE
    )

    if blocos:
        return max(blocos, key=len).strip()

    # sem cerca de código: só aceita se a resposta parece ser CSS puro
    if "{" in resposta and "<html" not in resposta.lower():
        return resposta.strip()

    return ""


def validar_css(css_novo, classes_exigidas):
    """Confere o CSS do designer e devolve a lista de problemas."""

    if not css_novo.strip():
        return ["a resposta não trouxe um bloco de CSS"]

    problemas = []

    if css_novo.count("{") != css_novo.count("}"):
        problemas.append("chaves { } desbalanceadas (CSS cortado ou quebrado)")

    if css_novo.count("{") < 5:
        problemas.append("CSS curto demais; reescreva o arquivo completo")

    if "@import" in css_novo:
        problemas.append("usa @import; remova (nada de recursos externos)")

    ausentes = [
        v for v in VARIAVEIS_PALETA
        if not re.search(rf"{re.escape(v)}\s*:\s*#[0-9a-fA-F]{{3,6}}", css_novo)
    ]

    if ausentes:
        problemas.append(
            "o :root precisa definir estas variáveis com cor hexadecimal "
            "(#rrggbb): " + ", ".join(ausentes)
        )

    if css_novo.count("var(--") < 10:
        problemas.append(
            "quase não usa as variáveis do :root; use var(--fundo), "
            "var(--texto), var(--primaria)... nas regras"
        )

    perdidas = sorted(classes_exigidas - classes_do_css(css_novo))

    if perdidas:
        problemas.append(
            "faltam regras para classes que já existiam no CSS "
            "(o site pode quebrar): " + ", ".join(perdidas)
        )

    return problemas


def variaveis_do_root(css):
    """{--nome: valor} do bloco :root de um CSS."""

    m = re.search(r":root\s*\{([^{}]*)\}", css or "")

    return dict(re.findall(r"(--[^\s:;]+)\s*:\s*([^;]+);", m.group(1))) if m else {}


def resolver_variaveis_da_paleta(css_novo, css_original):
    """Troca var(--x) do :root por hexadecimal e recupera variáveis da paleta
    original que o designer usou mas deixou de definir.

    O modelo costuma escrever --fundo: var(--azul-claro) sem definir
    --azul-claro (o :root dele substitui o original). Sem esta correção a cor
    some e completar_variaveis_root inventa cores padrão (branco/laranja).
    """

    ajustes = []
    original = variaveis_do_root(css_original)
    novo = variaveis_do_root(css_novo)
    todas = {**original, **novo}

    def resolver(valor, nivel=0):
        m = re.fullmatch(r"\s*var\(\s*(--[^\s,)]+)\s*\)\s*", valor)
        if m and nivel < 5 and m.group(1) in todas:
            return resolver(todas[m.group(1)], nivel + 1)
        return valor.strip()

    m_root = re.search(r":root\s*\{([^{}]*)\}", css_novo)

    if not m_root:
        return css_novo, ajustes

    def trocar(mm):
        nome, valor = mm.group(1), mm.group(2)
        resolvido = resolver(valor)
        if resolvido != valor.strip():
            ajustes.append(f"{nome}: {valor.strip()} -> {resolvido}")
        return f"{nome}: {resolvido};"

    corpo = re.sub(r"(--[^\s:;]+)\s*:\s*([^;]+);", trocar, m_root.group(1))

    usadas = set(re.findall(r"var\(\s*(--[^\s,)]+)", css_novo))

    for nome in sorted(usadas):
        if nome not in novo and nome in original:
            corpo = corpo.rstrip() + f"\n    {nome}: {resolver(original[nome])};\n"
            ajustes.append(f"{nome} restaurada da paleta original")

    css = css_novo[:m_root.start(1)] + corpo + css_novo[m_root.end(1):]

    return css, ajustes


def limpar_php_do_html(html):
    """Troca o PHP que o modelo escreveu por containers vazios (o JS preenche)."""

    if not re.search(r"<\?", html):
        return html, []

    avisos = []

    def trocar_secao(m):
        abertura, id_secao, corpo = m.group(1), m.group(2), m.group(3)

        if "<?" not in corpo:
            return m.group(0)

        h2 = re.search(r"<h2\b.*?</h2>", corpo, re.DOTALL | re.IGNORECASE)
        classe = re.search(r'class\s*=\s*"([^"]*grid[^"]*)"', corpo)

        avisos.append(f'seção "{id_secao}": PHP removido, criado {id_secao}-container')

        return (
            f"{abertura}\n            {h2.group(0) if h2 else ''}\n"
            f'            <div id="{id_secao}-container" '
            f'class="{classe.group(1) if classe else "produtos-grid"}"></div>\n'
            "        </section>"
        )

    html = re.sub(
        r'(<section\b[^>]*\bid\s*=\s*["\']([^"\']+)["\'][^>]*>)(.*?)</section>',
        trocar_secao, html, flags=re.DOTALL | re.IGNORECASE
    )

    # qualquer PHP que sobrou fora das seções
    html = re.sub(r"<\?(?:php|=).*?\?>", "", html, flags=re.DOTALL)

    return html, avisos


def remover_secoes_repetidas(html):
    """Apaga <section id="x"> repetida (o modelo as copia depois do rodapé):
    fica a primeira que tem conteúdo."""

    avisos = []
    vistos = set()

    def tratar(m):
        id_ = m.group(2)
        if id_ in vistos:
            avisos.append(f'seção repetida "{id_}" removida')
            return ""
        vistos.add(id_)
        return m.group(0)

    html = re.sub(
        r'(<section\b[^>]*\bid\s*=\s*["\']([^"\']+)["\'][^>]*>)(.*?)</section>',
        tratar, html, flags=re.DOTALL | re.IGNORECASE
    )
    return html, avisos


def aprimorar_css(caminho_projeto, tema=""):
    """Roda o designer sobre o front-end salvo e troca o CSS se ele passar
    na conferência. Se não passar, o CSS original do front-end é mantido."""

    caminho_html = achar_na_static(caminho_projeto, ".html")
    caminho_css = achar_na_static(caminho_projeto, ".css")
    caminho_js = achar_na_static(caminho_projeto, ".js")

    if not caminho_html or not caminho_css:
        print(">>> designer: não achei o HTML e o CSS em static/, nada a fazer")
        return

    html = ler_texto(caminho_html)
    css_original = ler_texto(caminho_css)
    js = ler_texto(caminho_js)

    classes = classes_usadas(html, js)
    exigidas = classes_do_css(css_original)

    # guarda o CSS do front-end para você comparar antes/depois
    salvar_arquivo(caminho_projeto, "docs/style_original.css", css_original)

    problemas = []

    for tentativa in range(1, MAX_TENTATIVAS_DESIGN + 1):

        paleta = "\n".join(f"{n}: {v}" for n, v in variaveis_do_root(css_original).items())

        resposta = designer(html, css_original, classes, problemas, tema, paleta)

        css_novo = extrair_css(resposta)

        # traz de volta regras de classes que o designer perdeu e cria as
        # variáveis da paleta que ele esqueceu (em vez de descartar o CSS)
        css_novo, copiadas = restaurar_regras_faltantes(css_novo, css_original, exigidas)

        for classe in copiadas:
            print(f">>> designer: regra de .{classe} restaurada do CSS original")

        # resolve var(--x) do :root e recupera as variáveis da paleta original
        css_novo, perdidas = restaurar_variaveis_perdidas(css_novo, css_original)

        if perdidas:
            print(f">>> designer: variáveis restauradas do CSS original: {', '.join(perdidas)}")

        css_novo = resolver_alias_root(css_novo)

        css_novo, restauradas = resolver_variaveis_da_paleta(css_novo, css_original)

        for restaurada in restauradas:
            print(f">>> designer: paleta: {restaurada}")

        css_novo, criadas = completar_variaveis_root(css_novo)

        for criada in criadas:
            print(f">>> designer: {criada}")

        # corrige contraste ruim (texto escuro no fundo escuro, etc.)
        css_novo, ajustes = ajustar_paleta(css_novo)

        for ajuste in ajustes:
            print(f">>> designer: paleta ajustada: {ajuste}")

        # desfaz usos errados de variáveis (sombra gigante, colunas de 20px,
        # texto escuro em fundo escuro, cards com tamanho fixo...)
        css_novo, consertos = consertar_css_do_designer(css_novo)

        for conserto in consertos:
            print(f">>> designer: CSS consertado: {conserto}")

        css_novo, visuais = consertar_css_visual(css_novo)

        for visual in visuais:
            print(f">>> designer: CSS consertado: {visual}")

        problemas = validar_css(css_novo, exigidas)

        ausentes = cores_do_pedido_ausentes(css_novo, tema)
        if ausentes:
            problemas.append(
                "o CSS não usa estas cores do pedido: " + ", ".join(ausentes)
            )

        if not problemas:

            # acrescenta o que o designer esqueceu nos cards (borda, hover)
            css_novo, extras = completar_estilo_dos_cards(css_novo, classes)

            for extra in extras:
                print(f">>> designer: acrescentado ao CSS: {extra}")

            css_novo, basicos = completar_estilos_base(css_novo)

            for basico in basicos:
                print(f">>> designer: acrescentado ao CSS: {basico}")

            with open(caminho_css, "w", encoding="utf-8") as arquivo:
                arquivo.write(css_novo + "\n")

            print(
                f">>> designer: CSS aprimorado na tentativa {tentativa} "
                f"({os.path.basename(caminho_css)})"
            )

            return

        print(f">>> designer: problemas na versão {tentativa} do CSS:")

        for problema in problemas:
            print(f"    - {problema}")

    print(
        ">>> designer: nenhuma versão passou na conferência; usando o CSS de "
        "reserva (cores do pedido + classes do site). O CSS do front-end "
        "continua em docs/style_original.css"
    )

    css_reserva = gerar_css_reserva(html, classes, tema, css_original)

    with open(caminho_css, "w", encoding="utf-8") as arquivo:
        arquivo.write(css_reserva)


def extrair_sql(resposta):
    """Pega só os comandos SQL da resposta do modelo.

    Funciona com ou sem bloco de código (```), e descarta texto explicativo
    que o modelo escreva antes ou depois. Só ficam CREATE TABLE, CREATE INDEX
    e INSERT INTO, que são o que o SQLite precisa para montar o banco.
    """

    blocos = re.findall(r"```[\w]*[ \t]*\n(.*?)```", resposta, re.DOTALL)

    texto = "\n".join(blocos) if blocos else resposta

    # Modelos pequenos às vezes entregam o SQL inteiro comentado
    # ("-- CREATE TABLE ..."). Sem nenhum comando ativo, tira o "--" do
    # começo das linhas; senão cada comando ficava incompleto, era
    # descartado e o schema.sql nascia vazio.
    ha_ativo = re.search(r"(?mi)^[ \t]*(CREATE|INSERT)\b", texto)
    ha_comentado = re.search(r"(?mi)^[ \t]*--[ \t]*(CREATE|INSERT)\b", texto)
    if ha_comentado and not ha_ativo:
        texto = re.sub(r"(?m)^[ \t]*--[ \t]?", "", texto)

    comandos = re.findall(
        r"(?:CREATE\s+(?:UNIQUE\s+)?(?:TABLE|INDEX)|INSERT\s+INTO)\b.*?;",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    return "\n\n".join(c.strip() for c in comandos)


def limpar_sql(sql):
    """Remove o que o SQLite não entende (CREATE DATABASE, USE, AUTO_INCREMENT...)."""

    linhas = [
        linha for linha in sql.splitlines()
        if not re.match(r"\s*(CREATE\s+DATABASE|DROP\s+DATABASE|USE)\b", linha, re.IGNORECASE)
    ]

    sql = "\n".join(linhas)

    sql = re.sub(r"\bAUTO_INCREMENT\b", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\)\s*ENGINE\s*=[^;]*;", ");", sql, flags=re.IGNORECASE)

    sql = remover_acentos_dos_nomes(sql)

    return sql.strip() + "\n"


def remover_acentos_dos_nomes(sql):
    """Tira os acentos dos nomes de tabelas e colunas (descrição -> descricao).

    Os textos entre aspas simples (os dados dos INSERTs) são preservados.
    Sem isso, o banco fica com colunas como "preço" e o JavaScript, que
    costuma escrever "preco", não encontra os campos.
    """

    resultado = []
    dentro_de_texto = False
    i = 0

    while i < len(sql):

        c = sql[i]

        if c == "'":

            if dentro_de_texto and i + 1 < len(sql) and sql[i + 1] == "'":
                resultado.append("''")  # aspas escapadas dentro de um texto
                i += 2
                continue

            dentro_de_texto = not dentro_de_texto
            resultado.append(c)

        elif dentro_de_texto:

            resultado.append(c)

        else:

            sem_acento = "".join(
                x for x in unicodedata.normalize("NFD", c)
                if unicodedata.category(x) != "Mn"
            )

            resultado.append(sem_acento)

        i += 1

    return "".join(resultado)


def remover_codigo(texto):
    """Tira de um texto os blocos de código (```css, ```python ...).

    O arquiteto às vezes escreve o projeto inteiro em vez de só planejar, e
    isso confunde os outros agentes. Blocos sem linguagem (como a árvore de
    pastas) são mantidos.
    """

    def decidir(m):
        linguagem = m.group(1).lower()
        return m.group(0) if linguagem in ("", "text", "txt", "plaintext") else ""

    texto = re.sub(r"```([\w+-]*)[ \t]*\n.*?```", decidir, texto, flags=re.DOTALL)

    # bloco de código aberto e nunca fechado
    texto = re.sub(r"```[\w+-]+[ \t]*\n.*", "", texto, flags=re.DOTALL)

    return re.sub(r"\n{3,}", "\n\n", texto).strip()


# Peças do backend de reserva (usado só se o agente não acertar o backend.py).
# O texto "CREATE TABLE" não aparece aqui de propósito: as tabelas vêm só do
# database/schema.sql.
_RESERVA_CABECALHO = '''"""Backend Flask do site, montado a partir do database/schema.sql.

O banco (database.db) é criado na primeira execução, lendo o arquivo
database/schema.sql. Cada tabela do esquema ganha rotas em /api/<tabela>.
"""
from flask import Flask, jsonify, request
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

# static_url_path="" faz o Flask servir style.css e script.js na raiz do site
app = Flask(__name__, static_folder="static", static_url_path="")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_banco():
    # Cria o banco só na primeira vez, executando o schema.sql
    if os.path.exists(DB_PATH) and os.path.getsize(DB_PATH) > 0:
        return

    conn = get_db_connection()
    try:
        with open(SCHEMA_PATH, encoding="utf-8") as arquivo:
            conn.executescript(arquivo.read())
        conn.commit()
    except sqlite3.Error:
        # não deixa um database.db pela metade (senão a próxima execução
        # acharia que o banco já existe e pularia a criação)
        conn.close()
        os.remove(DB_PATH)
        raise
    conn.close()


@app.route("/")
def home():
    return app.send_static_file("index.html")
'''

_RESERVA_LISTAR = '''

@app.route("/api/@@URL@@", methods=["GET"])
def listar_@@TABELA@@():
    conn = get_db_connection()
    linhas = conn.execute("SELECT @@COLUNAS@@ FROM @@TABELA@@").fetchall()
    conn.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/@@URL@@/<int:item_id>", methods=["GET"])
def obter_@@TABELA@@(item_id):
    conn = get_db_connection()
    linha = conn.execute(
        "SELECT @@COLUNAS@@ FROM @@TABELA@@ WHERE @@CHAVE@@ = ?", (item_id,)
    ).fetchone()
    conn.close()
    if linha is None:
        return jsonify({"erro": "Registro não encontrado"}), 404
    return jsonify(dict(linha))
'''

_RESERVA_CRIAR = '''

@app.route("/api/@@URL@@", methods=["POST"])
def criar_@@TABELA@@():
    dados = request.get_json(silent=True) or {}
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO @@TABELA@@ (@@CAMPOS@@) VALUES (@@INTERROGACOES@@)",
            (@@VALORES@@,)
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        conn.close()
        return jsonify({"erro": str(erro)}), 400
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": novo_id}), 201
'''

_RESERVA_RODAPE = '''

if __name__ == "__main__":
    inicializar_banco()
    porta = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=porta)
'''


def gerar_backend_reserva(schema_sql):
    """Monta um backend.py simples (uma rota GET, GET/<id> e POST por tabela).

    Lê as tabelas e colunas do próprio schema.sql, então sempre combina com o
    banco. Devolve "" se o esquema não puder ser lido.
    """

    try:
        conn = sqlite3.connect(":memory:")
        conn.executescript(schema_sql)

        tabelas = [
            linha[0] for linha in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid"
            )
        ]

        info = {
            t: conn.execute(f'PRAGMA table_info("{t}")').fetchall()
            for t in tabelas
        }

        conn.close()

    except sqlite3.Error as erro:

        print(f">>> backend de reserva: o schema.sql não pôde ser lido ({erro})")

        return ""

    segredo = re.compile(r"senha|password|passwd|hash|token", re.IGNORECASE)

    codigo = _RESERVA_CABECALHO

    for tabela in tabelas:

        if not re.fullmatch(r"\w+", tabela):
            continue

        colunas = [c for c in info[tabela] if re.fullmatch(r"\w+", c[1])]

        publicas = [c[1] for c in colunas if not segredo.search(c[1])]

        if not publicas:
            continue

        chaves = [c[1] for c in colunas if c[5]]
        chave = chaves[0] if len(chaves) == 1 else "rowid"

        codigo += (
            _RESERVA_LISTAR
            .replace("@@URL@@", tabela.lower())
            .replace("@@TABELA@@", tabela)
            .replace("@@COLUNAS@@", ", ".join(publicas))
            .replace("@@CHAVE@@", chave)
        )

        # colunas que o usuário precisa informar: sem chave e sem valor padrão
        campos = [c[1] for c in colunas if not c[5] and c[4] is None]

        if campos:

            codigo += (
                _RESERVA_CRIAR
                .replace("@@URL@@", tabela.lower())
                .replace("@@TABELA@@", tabela)
                .replace("@@CAMPOS@@", ", ".join(campos))
                .replace("@@INTERROGACOES@@", ", ".join("?" for _ in campos))
                .replace(
                    "@@VALORES@@",
                    ", ".join(f'dados.get("{c}")' for c in campos)
                )
            )

    return codigo + _RESERVA_RODAPE


def progresso(porcentagem, mensagem):
    print(f"\n[{porcentagem}%] {mensagem}")


def titulo():
    print("\n" + "=" * 50)
    print("              MULTI AGENT AI")
    print("=" * 50)


def criar_pastas_projeto(nome_projeto):

    data_hora = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    nome_pasta = f"{nome_projeto}_{data_hora}"

    caminho = os.path.join(
        "generated_projects",
        nome_pasta
    )

    os.makedirs(
        os.path.join(caminho, "static"),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(caminho, "database"),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(caminho, "docs"),
        exist_ok=True
    )

    return caminho


def salvar_arquivo(caminho, nome_arquivo, conteudo):

    caminho_completo = os.path.join(
        caminho,
        nome_arquivo
    )

    os.makedirs(
        os.path.dirname(caminho_completo),
        exist_ok=True
    )

    with open(
        caminho_completo,
        "w",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(conteudo)


def sanitizar_nome_arquivo(nome):
    """
    Modelos como o llama3.2 às vezes formatam o nome do arquivo com
    markdown (**negrito**, `código`, aspas, etc) ou deixam espaços/
    caracteres que o Windows não aceita em nomes de arquivo.

    Esta função limpa isso, mantendo apenas o caminho relativo real.
    """

    nome = nome.strip()

    # Remove markdown: **negrito**, `código`, *itálico*, aspas
    nome = nome.strip("*`'\"")

    # Remove caracteres inválidos em nomes de arquivo no Windows,
    # mas preserva "/" e "\" (caso o modelo mande subpastas) e "."
    nome = re.sub(r'[<>:"|?*]', "", nome)

    # Normaliza barras invertidas vindas do modelo para "/"
    nome = nome.replace("\\", "/")

    # Remove barras/espacos residuais nas pontas
    nome = nome.strip("/ ")

    return nome


def corrigir_referencias_html(html, nome_css, nome_js):
    """
    Garante que o <link> de CSS e o <script> de JS dentro do HTML
    apontem exatamente para os nomes de arquivo que foram salvos,
    independente do nome que o modelo tenha escrito no código
    (ex: "styles.css" no HTML vs "style.css" salvo em disco).
    """

    if nome_css:
        html = re.sub(
            r'<link\s+[^>]*rel=["\']stylesheet["\'][^>]*>',
            f'<link rel="stylesheet" href="{nome_css}">',
            html,
            count=1,
            flags=re.IGNORECASE
        )

    if nome_js:
        html = re.sub(
            r'<script\s+src=["\'][^"\']+\.js["\'][^>]*>\s*</script>',
            f'<script src="{nome_js}"></script>',
            html,
            count=1,
            flags=re.IGNORECASE
        )

    return html


def normalizar_front(resposta):
    """Deixa a resposta do agente de front-end só com arquivos do site.

    O modelo às vezes ignora o formato "FILE: nome" e escreve títulos como
    **HTML** / **CSS**, e ainda inclui backend.py e SQL no meio. Aqui:
    - blocos com "FILE: nome" são mantidos se forem .html, .css ou .js;
    - o que faltar (html, css ou js) é preenchido pelos blocos sem nome,
      reconhecidos pela linguagem (```html, ```css, ```javascript);
    - blocos de python, sql etc. são descartados.
    Devolve a resposta reescrita no formato FILE:. Se não achar nada
    aproveitável, devolve a resposta original (cai no fallback antigo).
    """

    arquivos = {}

    for nome, codigo in re.findall(
        r"FILE:\s*(\S+)\s*```[\w]*\s*\n(.*?)```",
        resposta,
        re.DOTALL | re.IGNORECASE
    ):

        nome = sanitizar_nome_arquivo(nome).split("/")[-1]

        if (
            nome.lower().endswith((".html", ".css", ".js"))
            and codigo.strip()
            and nome not in arquivos
        ):
            arquivos[nome] = codigo.strip()

    blocos = re.findall(r"```([\w+-]*)[ \t]*\n(.*?)```", resposta, re.DOTALL)

    padrao = [
        (".html", "index.html", ("html",)),
        (".css", "style.css", ("css",)),
        (".js", "script.js", ("javascript", "js")),
    ]

    for extensao, nome_padrao, linguagens in padrao:

        if any(n.lower().endswith(extensao) for n in arquivos):
            continue

        for linguagem, codigo in blocos:

            if linguagem.lower() in linguagens and codigo.strip():
                arquivos[nome_padrao] = codigo.strip()
                print(
                    f">>> front-end: {nome_padrao} reconhecido pelo bloco "
                    f"```{linguagem} (sem marcador FILE:)"
                )
                break

    if not arquivos:
        return resposta

    linguagem_de = {".html": "html", ".css": "css", ".js": "javascript"}

    return "\n\n".join(
        f"FILE: {nome}\n```{linguagem_de[os.path.splitext(nome)[1].lower()]}"
        f"\n{codigo}\n```"
        for nome, codigo in arquivos.items()
    )


def corrigir_links_quebrados(caminho_projeto):
    """Rede de segurança para links href="pagina.html" sem a página.

    A pasta static só deveria ter uma página (index.html), mas se o modelo
    linkar para outras, cria cada página que falta copiando o cabeçalho, o
    rodapé e o CSS do index.html, com um aviso de "em construção" no lugar
    do conteúdo. Também normaliza links como "static/sobre.html" para
    "sobre.html" (o Flask serve a pasta static na raiz do site).
    """

    pasta = os.path.join(caminho_projeto, "static")
    modelo = ler_texto(os.path.join(pasta, "index.html"))

    if not modelo:
        return

    criadas = []

    def normalizar(m):

        nome = re.sub(r"^(\./|/)+", "", m.group(2))
        nome = re.sub(r"^static/", "", nome)

        if not nome or "/" in nome:
            return m.group(0)

        destino = os.path.join(pasta, nome)

        if not os.path.exists(destino):

            titulo = os.path.splitext(nome)[0].replace("-", " ").replace("_", " ").title()

            pagina = re.sub(
                r"<title>.*?</title>", f"<title>{titulo}</title>",
                modelo, flags=re.IGNORECASE | re.DOTALL
            )
            pagina = re.sub(
                r"<main\b.*?</main>",
                f"<main>\n<h2>{titulo}</h2>\n"
                "<p>Esta página ainda está em construção.</p>\n</main>",
                pagina, flags=re.IGNORECASE | re.DOTALL
            )
            pagina = re.sub(
                r"<script\b.*?</script>", "",
                pagina, flags=re.IGNORECASE | re.DOTALL
            )

            salvar_arquivo(caminho_projeto, f"static/{nome}", pagina)
            criadas.append(nome)

        return f'{m.group(1)}"{nome}"'

    # duas passadas: a segunda também normaliza os links das páginas que a
    # primeira acabou de criar
    for _passada in range(2):

        for caminho in glob.glob(os.path.join(pasta, "*.html")):

            html = ler_texto(caminho)

            novo = re.sub(
                r'(href\s*=\s*)["\']([^"\'#?:]+\.html)["\']',
                normalizar,
                html,
                flags=re.IGNORECASE
            )

            if novo != html:
                salvar_arquivo(
                    caminho_projeto,
                    f"static/{os.path.basename(caminho)}",
                    novo
                )

    if criadas:
        print(
            ">>> front-end: links para páginas que não existiam; criadas "
            "páginas básicas: " + ", ".join(criadas)
        )


def salvar_arquivos_por_marcador(
    caminho_projeto, subpasta, resposta, nome_fallback, permitidos=None
):
    """
    Espera respostas no formato:

    FILE: nome_do_arquivo.ext
    ```linguagem
    conteudo
    ```

    Se o modelo não seguir o formato (comum em modelos pequenos como o
    llama3.2), cai num fallback que salva tudo como .txt, para não perder
    o conteúdo gerado.

    permitidos: conjunto opcional com os únicos nomes de arquivo que este
    agente pode gravar (ex: {"backend.py"}). Qualquer outro arquivo que o
    modelo escreva junto é ignorado; sem isso, o agente de back-end podia
    sobrescrever o database/schema.sql com uma versão sua.
    """

    padrao_file = r"FILE:\s*(\S+)\s*```[\w]*\s*\n(.*?)```"

    arquivos = re.findall(
        padrao_file,
        resposta,
        re.DOTALL | re.IGNORECASE
    )

    if not arquivos:

        # Fallback: modelos pequenos às vezes ignoram "FILE:" e escrevem
        # o nome do arquivo em negrito markdown antes do bloco de código,
        # ex: "**database.sql**\n```sql\n...\n```"
        padrao_negrito = r"\*\*([\w\-./]+\.\w+)\*\*\s*```[\w]*\s*\n(.*?)```"

        arquivos = re.findall(
            padrao_negrito,
            resposta,
            re.DOTALL | re.IGNORECASE
        )

        if arquivos:
            print(
                f">>> {subpasta}: marcador FILE: não encontrado, "
                f"usando padrão alternativo (**nome**) que foi detectado."
            )

    if not arquivos:

        # Fallback: nenhum marcador de nome de arquivo foi usado.
        # Se a resposta tiver exatamente UM bloco de código, assumimos
        # que é o arquivo principal esperado para essa subpasta, e
        # deduzimos a extensão pela linguagem declarada no bloco
        # (ex: ```python, ```sql) ou, na falta dela, pelo padrão da
        # própria subpasta (backend -> .py, database -> .sql).

        padrao_bloco_unico = r"```([\w]*)\s*\n(.*?)```"

        blocos = re.findall(
            padrao_bloco_unico,
            resposta,
            re.DOTALL
        )

        extensao_por_linguagem = {
            "python": "py",
            "py": "py",
            "sql": "sql",
            "javascript": "js",
            "js": "js",
            "html": "html",
            "css": "css",
        }

        extensao_por_subpasta = {
            "backend": "py",
            "database": "sql",
        }

        if len(blocos) == 1:

            linguagem, codigo = blocos[0]

            extensao = (
                extensao_por_linguagem.get(linguagem.lower())
                or extensao_por_subpasta.get(subpasta)
            )

            # A pasta static é servida publicamente pelo Flask: nela só
            # podem entrar arquivos do site (html, css, js).
            if subpasta == "static" and extensao not in ("html", "css", "js"):
                extensao = None

            if extensao and codigo.strip():

                nome_base = nome_fallback.rsplit(".", 1)[0]
                nome_gerado = f"{nome_base}.{extensao}"

                print(
                    f">>> {subpasta}: nenhum marcador de nome encontrado, "
                    f"mas um único bloco de código foi detectado. "
                    f"Salvando como {nome_gerado} (linguagem: {linguagem or 'não informada'})."
                )

                salvar_arquivo(
                    caminho_projeto,
                    f"{subpasta}/{nome_gerado}",
                    codigo.strip()
                )

                return

    if not arquivos:

        print(
            f">>> {subpasta}: resposta sem marcador FILE:, guardada como "
            f"texto em {subpasta}/{nome_fallback} (isso é só uma cópia "
            f"bruta; os arquivos do projeto são gerados separadamente)."
        )

        salvar_arquivo(
            caminho_projeto,
            f"{subpasta}/{nome_fallback}",
            resposta
        )

        return

    vistos = set()
    arquivos_para_salvar = {}

    for nome, conteudo in arquivos:

        nome = sanitizar_nome_arquivo(nome)

        if not nome:

            print(
                f">>> {subpasta}: nome de arquivo inválido, ignorado "
                f"(bruto: {nome!r})"
            )

            continue

        if permitidos is not None:

            # "backend/backend.py" vale como "backend.py"
            base = nome.split("/")[-1]

            if base not in permitidos:

                print(
                    f">>> {subpasta}: {nome} ignorado (este agente só pode "
                    f"gerar: {', '.join(sorted(permitidos))})"
                )

                continue

            nome = base

        if nome in vistos:

            print(
                f">>> {subpasta}: {nome} ignorado "
                f"(arquivo já foi gerado antes nesta resposta)"
            )

            continue

        vistos.add(nome)

        codigo = conteudo.strip()

        if not codigo:
            continue

        arquivos_para_salvar[nome] = codigo

    # Se estamos salvando o front-end, corrige as referências de CSS/JS
    # dentro do HTML para baterem com os nomes de arquivo reais salvos.
    if subpasta == "static":

        nome_html = next(
            (n for n in arquivos_para_salvar if n.lower().endswith(".html")),
            None
        )

        nome_css = next(
            (n for n in arquivos_para_salvar if n.lower().endswith(".css")),
            None
        )

        nome_js = next(
            (n for n in arquivos_para_salvar if n.lower().endswith(".js")),
            None
        )

        if nome_html:

            arquivos_para_salvar[nome_html] = corrigir_referencias_html(
                arquivos_para_salvar[nome_html],
                nome_css,
                nome_js
            )

            print(
                f">>> static: referências de CSS/JS corrigidas em "
                f"{nome_html} (css={nome_css}, js={nome_js})"
            )

    # A pasta static é servida publicamente pelo Flask (static_url_path=""),
    # então um backend.py ou um .db colocado lá ficaria baixável pelo
    # navegador. Só entram arquivos do site.
    if subpasta == "static":

        extensoes_site = (
            ".html", ".css", ".js", ".json", ".svg", ".png",
            ".jpg", ".jpeg", ".gif", ".ico", ".webp"
        )

        for nome in list(arquivos_para_salvar):

            if not nome.lower().endswith(extensoes_site):

                print(
                    f">>> static: {nome} ignorado (a pasta static só aceita "
                    f"arquivos do site: html, css, js e imagens)"
                )

                del arquivos_para_salvar[nome]

    for nome, codigo in arquivos_para_salvar.items():

        salvar_arquivo(
            caminho_projeto,
            f"{subpasta}/{nome}",
            codigo
        )

        print(f">>> {subpasta}: {nome} criado")


def criar_projeto(prompt, nome_projeto="ProjetoTeste"):

    titulo()

    # -----------------------------------------
    # CRIAR PROJETO
    # -----------------------------------------

    caminho_projeto = criar_pastas_projeto(
        nome_projeto
    )

    print(
        f"\nProjeto criado em:\n{caminho_projeto}"
    )

    # -----------------------------------------
    # ARQUITETO
    # -----------------------------------------

    progresso(
        10,
        "Analisando o pedido..."
    )

    time.sleep(1)

    progresso(
        20,
        "Arquiteto trabalhando..."
    )

    arquitetura = architect(f"{prompt}\n{RESTRICOES_TECNICAS}")

    # Se o arquiteto copiou nomes de um tema antigo, pede de novo uma vez.
    vazados = nomes_vazados(arquitetura, prompt)
    if vazados:
        print(f">>> arquiteto: nomes sem relação com o pedido ({', '.join(vazados)}); refazendo...")
        arquitetura = architect(
            f"{prompt}\n{RESTRICOES_TECNICAS}\n\n"
            f"ATENÇÃO: a versão anterior usou nomes que NÃO têm relação com o "
            f"pedido ({', '.join(vazados)}). Refaça usando somente o assunto do pedido."
        )

    # A resposta completa fica guardada em docs/.
    salvar_arquivo(
        caminho_projeto,
        "docs/arquitetura.txt",
        arquitetura
    )

    # Os outros agentes recebem só o planejamento, sem blocos de código:
    # quando o arquiteto escreve o projeto inteiro, o modelo do front-end
    # se confunde e devolve "correções" em vez dos arquivos.
    arquitetura = remover_codigo(arquitetura)

    # -----------------------------------------
    # DATABASE
    # -----------------------------------------

    progresso(
        30,
        "Banco de Dados trabalhando..."
    )

    banco = database(
        f"{arquitetura}\n\n"
        f"PEDIDO ORIGINAL DO USUÁRIO:\n{prompt}\n"
        f"{RESTRICOES_BANCO}"
    )

    progresso(
        40,
        "Salvando Banco de Dados..."
    )

    # O backend.py lê sempre database/schema.sql para criar o database.db,
    # então geramos esse arquivo de forma fixa, com o SQL já limpo. A
    # resposta bruta do modelo fica só em docs/ (a pasta database/ guarda
    # apenas o schema.sql, não um .txt solto).
    def montar_schema(resposta_banco):
        sql = limpar_sql(extrair_sql(resposta_banco))
        if "CREATE TABLE" in sql.upper():
            sql = sanear_schema(sql)
        return sql

    schema_sql = montar_schema(banco)

    # Se o banco saiu com nomes de outro tema ou tabelas demais, pede de novo
    # (uma vez), dizendo exatamente o que estava errado.
    problemas = problemas_do_schema(schema_sql, prompt)
    if problemas:
        print(">>> database: problemas no banco gerado, refazendo:")
        for problema in problemas:
            print(f">>>   - {problema}")
        banco = database(
            f"{arquitetura}\n\n"
            f"PEDIDO ORIGINAL DO USUÁRIO:\n{prompt}\n"
            f"{RESTRICOES_BANCO}\n"
            "A VERSÃO ANTERIOR TINHA ESTES PROBLEMAS. CORRIJA:\n- "
            + "\n- ".join(problemas)
        )
        novo_schema = montar_schema(banco)
        if "CREATE TABLE" in novo_schema.upper():
            schema_sql = novo_schema
        if problemas_do_schema(schema_sql, prompt):
            print(">>> database: ATENÇÃO — o banco ainda tem problemas; confira o schema.sql.")

    salvar_arquivo(caminho_projeto, "docs/banco_bruto.txt", banco)

    if "CREATE TABLE" not in schema_sql.upper():
        print(
            ">>> database: o modelo não entregou SQL utilizável; usando a "
            "tabela padrão 'produtos' (dados de exemplo serão gerados)."
        )
        schema_sql = SCHEMA_RESERVA

    # Sem nenhuma linha no banco o site abre vazio; garante dados de exemplo
    if "CREATE TABLE" in schema_sql.upper():
        schema_sql = garantir_dados_exemplo(schema_sql, prompt)
        schema_sql = garantir_coluna_imagem(schema_sql, prompt)

    salvar_arquivo(
        caminho_projeto,
        "database/schema.sql",
        schema_sql
    )

    if "CREATE TABLE" not in schema_sql.upper():

        print(
            ">>> database: ATENÇÃO — nenhum CREATE TABLE foi encontrado "
            "na resposta do modelo; o banco vai nascer vazio."
        )

    else:

        print(">>> database: schema.sql criado")
        
    # -----------------------------------------
    # FRONT-END
    # -----------------------------------------

    progresso(
        45,
        "Front-End trabalhando..."
    )

    # Envia a arquitetura e o pedido original ao agente frontend.
    # O esquema SQL é enviado separadamente.
    conteudo_frontend = (
        f"{arquitetura}\n\n"
        f"PEDIDO ORIGINAL DO USUÁRIO:\n{prompt}"
    )

    front = frontend(conteudo_frontend, schema_sql)

    # Descarta backend/SQL que o modelo tenha escrito junto e reconhece
    # os arquivos mesmo sem o marcador FILE:
    front = normalizar_front(front)

    progresso(
        55,
        "Salvando Front-End..."
    )

    salvar_arquivos_por_marcador(
        caminho_projeto,
        "static",
        front,
        "frontend.txt"
    )

    # Garante que nenhum link do site aponte para uma página inexistente
    # Se o modelo escreveu PHP no HTML, troca por containers vazios (o JS
    # preenche); sem isso o PHP aparece como texto e o verificador duplica seções
    caminho_html_front = achar_na_static(caminho_projeto, ".html")
    html_front, avisos_php = limpar_php_do_html(ler_texto(caminho_html_front))
    html_front, avisos_dup = remover_secoes_repetidas(html_front)
    avisos_php = avisos_php + avisos_dup

    if avisos_php:
        salvar_arquivo(
            caminho_projeto,
            "static/" + os.path.basename(caminho_html_front),
            html_front
        )
        for aviso in avisos_php:
            print(f">>> front-end: {aviso}")

    # Se o modelo devolveu só um trecho do HTML ou esqueceu o <link> do CSS
    # e o <script> do JS, completa a página antes do designer e dos links
    for mudanca in garantir_documento_html(caminho_projeto):
        print(f">>> front-end: {mudanca}")

    corrigir_links_quebrados(caminho_projeto)

    # -----------------------------------------
    # DESIGNER
    # -----------------------------------------

    progresso(
        58,
        "Designer aprimorando o CSS..."
    )

    aprimorar_css(caminho_projeto, prompt)

    # -----------------------------------------
    # BACK-END
    # -----------------------------------------

    progresso(
        60,
        "Back-End trabalhando..."
    )

    # O agente recebe o esquema do banco: o backend.py gerado lê o
    # database/schema.sql para criar o database.db e expõe as tabelas
    # em /api/<tabela>.
    back = backend(arquitetura, schema_sql)

    progresso(
        70,
        "Salvando Back-End..."
    )

    salvar_arquivos_por_marcador(
        caminho_projeto,
        ".",
        back,
        "backend.txt",
        permitidos={"backend.py"}
    )

    # Confere o código gerado. Se tiver problema, o agente ganha uma
    # segunda chance, já sabendo o que precisa corrigir.
    codigo_backend = ler_backend_salvo(caminho_projeto)
    problemas_backend = validar_backend(codigo_backend, schema_sql)

    tentativa_backend = 1

    while problemas_backend and tentativa_backend < MAX_TENTATIVAS_BACKEND:

        print(
            f">>> backend: problemas encontrados no código gerado "
            f"(versão {tentativa_backend}):"
        )

        for problema in problemas_backend:
            print(f"    - {problema}")

        tentativa_backend += 1

        print(
            f">>> backend: pedindo a versão {tentativa_backend} ao agente..."
        )

        back = backend(
            arquitetura,
            schema_sql
            + "\n\nA VERSÃO ANTERIOR DO backend.py TINHA ESTES PROBLEMAS. "
            "CORRIJA TODOS:\n- "
            + "\n- ".join(problemas_backend)
        )

        salvar_arquivos_por_marcador(
            caminho_projeto,
            ".",
            back,
            "backend.txt",
            permitidos={"backend.py"}
        )

        codigo_backend = ler_backend_salvo(caminho_projeto)
        problemas_backend = validar_backend(codigo_backend, schema_sql)

    if problemas_backend and USAR_BACKEND_RESERVA:

        print(
            f">>> backend: o agente não acertou o backend.py em "
            f"{tentativa_backend} tentativas (últimos problemas: "
            + "; ".join(problemas_backend)
            + "). Usando o backend de reserva, montado a partir do schema.sql."
        )

        reserva = gerar_backend_reserva(schema_sql)

        if reserva:

            salvar_arquivo(
                caminho_projeto,
                "backend.py",
                reserva
            )

            codigo_backend = reserva
            problemas_backend = validar_backend(codigo_backend, schema_sql)

    if problemas_backend:

        print(
            ">>> backend: ATENÇÃO — o backend.py ainda tem problemas: "
            + "; ".join(problemas_backend)
        )

    else:

        print(">>> backend: backend.py conferido (sintaxe, imports e schema.sql OK)")

    # Faz o script.js usar os mesmos nomes de rota, campos e ids que o
    # backend, o schema.sql e o index.html têm
    corrigir_contrato_front_back(caminho_projeto, schema_sql, codigo_backend)

    # -----------------------------------------
    # REVISOR
    # -----------------------------------------

    progresso(
        80,
        "Revisor analisando o projeto..."
    )

    projeto = f"""

ARQUITETURA:

{arquitetura}


FRONT-END:

{front}


BACK-END:

{back}


BANCO DE DADOS:

{schema_sql}

"""

    revisao = reviewer(projeto)

    # A revisão é sempre texto/análise, então continua como .txt
    salvar_arquivo(
        caminho_projeto,
        "docs/revisao.txt",
        revisao
    )

    # -----------------------------------------
    # TESTE AUTOMÁTICO DO SITE
    # -----------------------------------------

    progresso(
        97,
        "Testando o site gerado..."
    )

    # O schema.sql que está no disco precisa ser exatamente o que foi usado
    # para gerar o backend.py (se uma coluna sumir dele, a API dá erro 500
    # e o site abre sem os cards).
    salvar_arquivo(
        caminho_projeto,
        "database/schema.sql",
        schema_sql
    )

    # Roda o site numa cópia, chama as rotas da API e confere se o HTML e o
    # JavaScript combinam com o backend e com o banco. Se o backend.py
    # estiver quebrado, ele é refeito a partir do schema.sql.
    # Cria as ilustrações (SVG) que o banco e o HTML citam, em static/img/, e
    # acerta os caminhos no schema.sql. Sem isto os cards ficam com a figura
    # quebrada, e a pasta static/img nem chega a existir.
    try:
        from ilustrador import gerar_imagens
        for linha in gerar_imagens(caminho_projeto):
            print(f">>> ilustrador: {linha}")
    except Exception as erro:  # nunca derruba a geração do site
        print(f">>> ilustrador: não consegui criar as imagens ({erro})")

    verificar_projeto(
        caminho_projeto,
        gerar_backend_reserva if USAR_BACKEND_RESERVA else None
    )

    # -----------------------------------------
    # FINAL
    # -----------------------------------------

    progresso(
        100,
        "Projeto finalizado!"
    )

    print("\n" + "=" * 50)

    print("PROJETO SALVO EM:")

    print(caminho_projeto)

    print("=" * 50)

    print("\nEstrutura gerada:")

    print("- backend.py (Flask + SQLite, na raiz do projeto)")
    print("- static/    (index.html, style.css, script.js)")
    print("- database/  (schema.sql, usado para criar o database.db)")
    print("- docs/arquitetura.txt")
    print("- docs/revisao.txt")
    print("- docs/style_original.css (CSS antes do Designer)")
    print("\nPara rodar: entre na pasta do projeto e execute")
    print("  python backend.py")
    print("depois abra http://localhost:5000 no navegador.")

    print("=" * 50)