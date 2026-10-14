from ollama import chat
import time


def frontend(architecture, schema_sql=""):

    print("\n>>> FRONTEND: iniciando...")

    inicio = time.time()

    # Se o agente de banco de dados já rodou, mandamos o esquema dele para
    # o front-end usar os mesmos nomes de colunas que a API vai devolver.
    conteudo_usuario = architecture

    if schema_sql.strip():
        conteudo_usuario = (
            f"{architecture}\n\n"
            "ESQUEMA DO BANCO DE DADOS (a API devolve cada linha das "
            "tabelas como JSON, com os nomes das colunas como chaves). "
            "Use EXATAMENTE estes nomes de colunas nos campos dos cards "
            "e use fetch(\"/api/<nome_da_tabela_principal>\"):\n\n"
            f"{schema_sql}"
        )

    try:
        response = chat(

            model="llama3.2",

            messages=[

                {
                    "role": "system",

                    "content": """
Você é um Engenheiro Front-End.

REGRAS OBRIGATÓRIAS:

- Gere EXATAMENTE 3 arquivos: index.html, style.css e script.js.
- Nunca gere Back-End nem Banco de Dados.
- O index.html deve ter um elemento container vazio (ex:
  <div id="produtos-container"></div>) onde os itens serão inseridos
  dinamicamente pelo JavaScript. NÃO coloque produtos/itens fixos
  escritos diretamente no HTML.
- O script.js deve usar fetch("/api/produtos") (ou o nome de entidade
  equivalente definido na arquitetura) para buscar os dados do backend,
  e então criar os cards dinamicamente com JavaScript
  (document.createElement ou innerHTML dentro de um loop).
- Cada card deve exibir os campos que existem no ESQUEMA DO BANCO (nome,
  descrição, categoria, imagem...) e um botão de ação. Mostre o preço
  (formatado como "R$ X,XX") SOMENTE se a tabela tiver uma coluna de preço:
  nunca use um campo que não esteja no esquema.
- Todo botão do HTML precisa ter ação no script.js (um botão de rolar até
  uma seção usa scrollIntoView). Todo id usado no JavaScript precisa existir
  no HTML.
- Trate o caso de erro na busca (ex: servidor Flask não estar rodando)
  mostrando uma mensagem amigável na tela via JavaScript.
- O style.css deve estilizar os cards em um grid responsivo.
- Use exatamente os nomes de arquivo "style.css" e "script.js" nas tags
  <link> e <script> do HTML (nunca "styles.css" ou "scripts.js").
- Gere cada arquivo UMA ÚNICA VEZ. Não repita o mesmo arquivo duas vezes.
- Baseie-se exclusivamente na arquitetura recebida para nomear a
  entidade principal (ex: produtos, livros, itens).
- Se a mensagem trouxer um "ESQUEMA DO BANCO DE DADOS", ele é a fonte da
  verdade: os campos de cada item (ex: item.titulo, item.autor) devem
  usar exatamente os nomes das colunas do esquema, e o endpoint deve ser
  "/api/<nome_da_tabela_principal>". Não invente campos que não existem
  no esquema, e só formate como preço (R$) colunas que sejam valores
  monetários.
- NUNCA use PHP, Jinja, Blade, EJS ou qualquer template de servidor (nada
  de <?php, <?=, {{ }}, {% %}). O HTML é estático: toda lista de itens
  começa como um <div id="<tabela>-container" class="produtos-grid"> VAZIO,
  e só o JavaScript (fetch) preenche. Cada seção de dados deve ter esse
  container, por exemplo:
  <section id="turmas"><h2>Turmas</h2><div id="turmas-container" class="produtos-grid"></div></section>
- Não escreva onclick="..." no HTML; ligue os botões no script.js.
- NUNCA use Font Awesome nem outra biblioteca de ícones (nada de
  <i class="fas ..."></i>): ela não é carregada e o botão fica vazio. Todo
  botão deve ter TEXTO escrito (ex: "Buscar", "Carrinho") ou um emoji.
- Os links do menu devem apontar para o id de uma seção da própria página
  (ex: href="#produtos"), nunca href="#" vazio; cada id usado precisa existir
  em uma <section id="...">.
- Cada seção citada no menu precisa existir no HTML.
- Não escreva nada fora dos blocos de código.
- SEMPRE feche cada bloco de código com crase tripla (```) ao final.

FORMATO OBRIGATÓRIO (siga exatamente este exemplo, incluindo o
fechamento com crase tripla, um bloco por arquivo):

FILE: index.html
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Loja</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header><h1>Loja</h1></header>
    <main>
        <div id="mensagem-status"></div>
        <div id="produtos-container" class="produtos-grid"></div>
    </main>
    <script src="script.js"></script>
</body>
</html>
```

FILE: style.css
```css
.produtos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 20px;
}
```

FILE: script.js
```javascript
async function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    try {
        const resposta = await fetch("/api/produtos");
        const produtos = await resposta.json();
        container.innerHTML = "";
        produtos.forEach((produto) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `<h3>${produto.nome}</h3><p>${produto.descricao}</p><p>R$ ${produto.preco.toFixed(2)}</p><button>Comprar</button>`;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar os produtos.</p>";
    }
}

carregarProdutos();
```
"""
                },

                {
                    "role": "user",
                    "content": conteudo_usuario
                }

            ],

            options={
                "num_ctx": 8192
            }

        )
        resultado = response.message.content

        fim = time.time()

        print(
            f">>> FRONTEND: tempo de execução: "
            f"{fim - inicio:.2f} segundos"
        )

        return resultado

    except Exception as erro:

        print("\n!!! ERRO NO FRONTEND !!!")
        print(erro)

        return ""