async function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    try {
        const resposta = await fetch("/api/jogos");
        const produtos = await resposta.json();
        container.innerHTML = "";
        produtos.forEach((produto) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `<h3>${produto.nome}</h3><p>${produto.conteudo}</p><p>R$ ${produto.preco.toFixed(2)}</p><button>Comprar</button>`;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar os produtos.</p>";
    }
}

async function adicionarAoCarrinho(jogoId) {
    try {
        const resposta = await fetch("/api/carrinhos", { method: "POST", body: JSON.stringify({ jogo_id: jogoId }) });
        const carro = await resposta.json();
        carregarProdutos();
    } catch (erro) {
        const mensagem = document.getElementById("mensagem-status");
        mensagem.innerHTML = "<p>Erro ao adicionar ao carrinho.</p>";
    }
}

async function removerDoCarrinho(jogoId) {
    try {
        const resposta = await fetch("/api/carrinhos", { method: "PUT", body: JSON.stringify({ jogo_id: jogoId }) });
        const carro = await resposta.json();
        carregarProdutos();
    } catch (erro) {
        const mensagem = document.getElementById("mensagem-status");
        mensagem.innerHTML = "<p>Erro ao remover do carrinho.</p>";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    carregarProdutos();
});

document.querySelectorAll(".produto-card button").forEach((botao) => {
    botao.addEventListener("click", () => {
        const jogoId = botao.parentNode.dataset.jogoId;
        adicionarAoCarrinho(jogoId);
    });
});

document.querySelectorAll(".produto-card").forEach((card) => {
    card.addEventListener("click", () => {
        const jogoId = card.dataset.jogoId;
        removerDoCarrinho(jogoId);
    });
});