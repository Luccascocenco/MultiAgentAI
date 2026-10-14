async function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    try {
        const resposta = await fetch("/api/produtos");
        const produtos = await resposta.json();
        container.innerHTML = "";
        produtos.forEach((produto) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `<h3>${produto.nome}</h3><p>${produto.descricao}</p><p>R$ ${produto.preco.toFixed(2)}</p><button>Comprar</button>`;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar os produtos.</p>";
    }
}

async function carregarCarrinho() {
    const container = document.getElementById("carrinho-container");
    try {
        const resposta = await fetch("/api/produtos");
        const carrinho = await resposta.json();
        container.innerHTML = "";
        carrinho.forEach((item) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `<h3>${item.produtoId.nome}</h3><p>${item.quantidade} unidades</p><button>Remover</button>`;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar o carrinho.</p>";
    }
}

async function carregarPedidos() {
    const container = document.getElementById("pedidos-container");
    try {
        const resposta = await fetch("/api/pedidos");
        const pedidos = await resposta.json();
        container.innerHTML = "";
        pedidos.forEach((pedido) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `<h3>${pedido.produtoId.nome}</h3><p>${pedido.quantidade} unidades</p><button>Remover</button>`;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar os pedidos.</p>";
    }
}

document.getElementById("produtos-container").addEventListener("click", () => {
    document.getElementById("produtos-container").scrollIntoView({ behavior: "smooth" });
});

document.getElementById("carrinho-container").addEventListener("click", () => {
    document.getElementById("carrinho-container").scrollIntoView({ behavior: "smooth" });
});

document.getElementById("pedidos-container").addEventListener("click", () => {
    document.getElementById("pedidos-container").scrollIntoView({ behavior: "smooth" });
});

carregarProdutos();
carregarCarrinho();
carregarPedidos();