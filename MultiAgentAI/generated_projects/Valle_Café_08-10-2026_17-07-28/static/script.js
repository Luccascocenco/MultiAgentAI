async function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    container.innerHTML = "";
    try {
        const resposta = await fetch("/api/produtos");
        const produtos = await resposta.json();
        produtos.forEach((produto) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `
                <h3>${produto.nome}</h3>
                <p>${produto.descricao}</p>
                <p>R$ ${produto.preco.toFixed(2)}</p>
                <button>Comprar</button>
            `;
            container.appendChild(card);
        });
    } catch (erro) {
        const mensagem = document.getElementById("mensagem-status");
        mensagem.innerHTML = "Não foi possível carregar os produtos.";
    }
}

async function carregarDiagramas() {
    const resposta = await fetch("/api/diagramas");
    const diagramas = await resposta.json();
    const container = document.getElementById("produtos-container");
    container.innerHTML = "";
    diagramas.forEach((diagrama) => {
        const card = document.createElement("div");
        card.className = "produto-card";
        card.innerHTML = `
            <h3>${diagrama.nome}</h3>
            <p>${diagrama.conteudo}</p>
            <p>Produtos:</p>
            <div class="produtos-grid">
                ${await fetch("/api/produtos/diagrama/" + diagrama.id).then((resposta) => resposta.json()).then((produtos) => {
                    produtos.forEach((produto) => {
                        const card = document.createElement("div");
                        card.className = "produto-card";
                        card.innerHTML = `
                            <h3>${produto.nome}</h3>
                            <p>${produto.descricao}</p>
                            <p>R$ ${produto.preco.toFixed(2)}</p>
                            <button>Comprar</button>
                        `;
                        container.appendChild(card);
                    });
                })}
            </div>
        `;
        container.appendChild(card);
    });
}

carregarDiagramas();

function pesquisar() {
    const entrada = document.getElementById("pesquisa");
    const palavra = entrada.value;
    const resposta = document.getElementById("produtos-container");
    resposta.innerHTML = "";
    fetch("/api/produtos/pesquisa/" + palavra)
        .then((resposta) => resposta.json())
        .then((produtos) => {
            produtos.forEach((produto) => {
                const card = document.createElement("div");
                card.className = "produto-card";
                card.innerHTML = `
                    <h3>${produto.nome}</h3>
                    <p>${produto.descricao}</p>
                    <p>R$ ${produto.preco.toFixed(2)}</p>
                    <button>Comprar</button>
                `;
                resposta.appendChild(card);
            });
        });
}