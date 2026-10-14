async function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    try {
        const resposta = await fetch("/api/produtos");
        const produtos = await resposta.json();
        container.innerHTML = "";
        produtos.forEach((produto) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `<img class="card-img" src="${produto.imagem}" alt="${produto.nome}" loading="lazy"><h3>${produto.nome}</h3><p>R$ ${produto.preco.toFixed(2)}</p><button>Comprar</button>`;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar os produtos.</p>";
    }
}

carregarProdutos();
