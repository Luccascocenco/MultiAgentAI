// Funcão para carregar os produtos
async function carregarProdutos() {
    const container = document.getElementById("produtos-grid");
    try {
        const resposta = await fetch("/api/produtos");
        const produtos = await resposta.json();
        container.innerHTML = "";
        produtos.forEach((produto) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `
                <img src="${produto.imagem}" alt="${produto.nome}">
                <h2>${produto.nome}</h2>
                <p>${produto.descricao}</p>
                <p>R$ ${produto.preco.toFixed(2)}</p>
                <button>Adicionar ao carrinho</button>
            `;
            container.appendChild(card);
        });
    } catch (erro) {
        console.error(erro);
        container.innerHTML = `<p>Não foi possível carregar os produtos.</p>`;
    }
}

// Funcão para carregar os produtos
carregarProdutos();