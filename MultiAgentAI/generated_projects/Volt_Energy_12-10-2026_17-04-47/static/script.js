async function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    try {
        const resposta = await fetch("/api/produtos");
        const produtos = await resposta.json();
        container.innerHTML = "";
        produtos.forEach((produto) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `<h3>${produto.nome}</h3><p>${produto.descricao}</p><p>R$ ${produto.preco.toFixed(2)}</p><button data-id="${produto.id}">Comprar</button>`;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar os produtos.</p>";
    }
}

async function adicionarAoCarrinho(produtoId) {
    const status = document.getElementById("mensagem-status");
    try {
        const resposta = await fetch("/api/carrinho", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ produto_id: produtoId, quantidade: 1 })
        });
        status.textContent = resposta.ok ? "Adicionado ao carrinho!" : "Erro ao adicionar.";
    } catch (erro) {
        status.textContent = "Servidor indisponível.";
    }
}

document.getElementById("produtos-container").addEventListener("click", (e) => {
    const botao = e.target.closest("button[data-id]");
    if (botao) adicionarAoCarrinho(Number(botao.dataset.id));
});

carregarProdutos();