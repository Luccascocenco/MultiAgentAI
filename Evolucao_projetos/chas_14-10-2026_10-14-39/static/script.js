async function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    try {
        const resposta = await fetch("/api/produtos");
        const produtos = await resposta.json();
        container.innerHTML = "";
        produtos.forEach((produto) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `<img class="card-img" src="${produto.imagem}" alt="${produto.nome}" loading="lazy">
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

async function carregarCategoria() {
    const resposta = await fetch("/api/produtos");
    const categorias = await resposta.json();
    return categorias;
}

async function carregarPedidos() {
    const resposta = await fetch("/api/produtos");
    const pedidos = await resposta.json();
    return pedidos;
}

async function carregarProduto(produtoId) {
    const resposta = await fetch(`/api/produtos/${produtoId}`);
    const produto = await resposta.json();
    return produto;
}

async function carregarCategorias() {
    const resposta = await fetch("/api/produtos");
    const categorias = await resposta.json();
    return categorias;
}

async function carregarPedidosId(produtoId) {
    const resposta = await fetch(`/api/produtos/${produtoId}`);
    const pedidos = await resposta.json();
    return pedidos;
}

carregarProdutos();
