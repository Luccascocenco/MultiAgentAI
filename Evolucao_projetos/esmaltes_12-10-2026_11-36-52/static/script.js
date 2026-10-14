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
                <h3>${produto[itens.id].nome}</h3>
                <p>${produto[itens.id].descricao}</p>
                <p>R$ ${produto[itens.id].preco.toFixed(2)}</p>
                <button>Comprar</button>
            `;
            container.appendChild(card);
        });
    } catch (erro) {
        const mensagem = document.getElementById("mensagem-status");
        mensagem.innerHTML = "Não foi possível carregar os produtos.";
    }
}

carregarProdutos();