async function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    const url = "/api/produtos";
    try {
        const resposta = await fetch(url);
        const produtos = await resposta.json();
        container.innerHTML = "";
        produtos.forEach((produto) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `
                <img src="${produto.imagem}" alt="${produto.nome}">
                <h3>${produto.nome}</h3>
                <p>${produto.descricao}</p>
                <p>R$ ${produto.preco.toFixed(2)}</p>
                <button>Comprar</button>
            `;
            container.appendChild(card);
        });
    } catch (erro) {
        console.error(erro);
        container.innerHTML = "<p>Não foi possível carregar os produtos.</p>";
    }
}

async function carregarCarrinho() {
    const container = document.getElementById("carrinho-container");
    const url = "/api/carrinho";
    try {
        const resposta = await fetch(url);
        const carrinho = await resposta.json();
        container.innerHTML = "";
        carrinho.forEach((item) => {
            const li = document.createElement("li");
            li.innerHTML = `
                <input type="number" value="${item.quantidade}">
                <button>Remover</button>
            `;
            container.appendChild(li);
        });
    } catch (erro) {
        console.error(erro);
        container.innerHTML = "<p>Não foi possível carregar o carrinho.</p>";
    }
}

async function carregarNovidades() {
    const container = document.getElementById("novidades-container");
    const url = "/api/produtos";
    try {
        const resposta = await fetch(url);
        const novidades = await resposta.json();
        container.innerHTML = "";
        novidades.forEach((item) => {
            const li = document.createElement("li");
            li.innerHTML = `
                <input type="number" value="${item.quantidade}">
                <button>Remover</button>
            `;
            container.appendChild(li);
        });
    } catch (erro) {
        console.error(erro);
        container.innerHTML = "<p>Não foi possível carregar as novidades.</p>";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    carregarProdutos();
    carregarCarrinho();
    carregarNovidades();
});