async function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    try {
        const resposta = await fetch("/api/produtos");
        const produtos = await resposta.json();
        container.innerHTML = "";
        produtos.forEach((produto) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `
                <img src="img/${produto.nome}.jpg" alt="${produto.nome}">
                <h3>${produto.nome}</h3>
                <p>${produto.descricao}</p>
                <p>R$ ${produto.preco.toFixed(2)}</p>
                <button>Comprar</button>
            `;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar os produtos.</p>";
    }
}

carregarProdutos();

// ===== Ligações automáticas: botões que levam até uma seção =====
(function () {
    function ligar(idBotao, idSecao) {
        const botao = document.getElementById(idBotao);
        const secao = document.getElementById(idSecao);
        if (botao && secao) {
            botao.addEventListener("click", () => secao.scrollIntoView({ behavior: "smooth" }));
        }
    }
    ligar("ver-buquês", "produtos");
})();
