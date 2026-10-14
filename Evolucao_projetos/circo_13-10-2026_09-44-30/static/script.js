async function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    try {
        const resposta = await fetch("/api/diagramas");
        const produtos = await resposta.json();
        container.innerHTML = "";
        produtos.forEach((produto) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `<h3>${produto.nome}</h3><p>${produto.descricao}</p><p>R$ ${produto.preco.toFixed(2)}</p><button data-id="${produto.id}">Conhecer atração</button>`;
            container.appendChild(card);
        });
    } catch (erro) {
        document.getElementById("mensagem-status").textContent = "Não foi possível carregar os produtos.";
    }
}

async function adicionarAoCarrinho(produtoId) {
    const status = document.getElementById("mensagem-status");
    try {
        const resposta = await fetch("/api/ingressos", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ usuario_id: 1, produto_id: produtoId, quantidade: 1 })
        });
        status.textContent = resposta.ok ? "Adicionado ao carrinho!" : "Erro ao adicionar.";
    } catch (erro) {
        status.textContent = "Servidor indisponível.";
    }
}

document.getElementById("produtos-container").addEventListener("click", (e) => {
    const card = e.target.closest(".produto-card");
    if (card) {
        const botao = card.querySelector("button");
        if (botao) {
            adicionarAoCarrinho(Number(botao.dataset.id));
        }
    }
});

carregarProdutos();