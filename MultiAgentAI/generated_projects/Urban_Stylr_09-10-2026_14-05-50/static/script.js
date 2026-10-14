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

async function carregarPromocoes() {
    const container = document.getElementById("promoçoes-container");
    try {
        const resposta = await fetch("/api/promocoes");
        const promocoes = await resposta.json();
        container.innerHTML = "";
        promocoes.forEach((promocao) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `
                <h3>${promocao.nome}</h3>
                <p>${promocao.descricao}</p>
                <p>R$ ${promocao.preco.toFixed(2)}</p>
                <button>Comprar</button>
            `;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar as promoções.</p>";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    carregarProdutos();
    carregarPromocoes();
});