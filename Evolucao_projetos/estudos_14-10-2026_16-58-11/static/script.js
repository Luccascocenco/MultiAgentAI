async function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    try {
        const resposta = await fetch("/api/produtos");
        const produtos = await resposta.json();
        container.innerHTML = "";
        produtos.forEach((produto) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `<img class="card-img" src="${produto.imagem}" alt="${produto.nome}" loading="lazy"><h3>${produto.nome}</h3><p>${produto.descricao}</p><p>R$ ${produto.preco.toFixed(2)}</p><button>Comprar</button>`;
            container.appendChild(card);
        });
    } catch (erro) {
        const mensagem = document.getElementById("mensagem-status");
        mensagem.textContent = "Não foi possível carregar os produtos.";
        mensagem.style.color = "red";
    }
}

async function carregarDetalhes() {
    const container = document.getElementById("detalhes-container");
    try {
        const resposta = await fetch("/api/produtos");
        const detalhes = await resposta.json();
        container.innerHTML = "";
        detalhes.forEach((detalhe) => {
            const card = document.createElement("div");
            card.className = "detalhes-card";
            card.innerHTML = `<h2>${detalhe.nome}</h2><p>${detalhe.descricao}</p><p>R$ ${detalhe.preco.toFixed(2)}</p><button>Comprar</button>`;
            container.appendChild(card);
        });
    } catch (erro) {
        const mensagem = document.getElementById("mensagem-status");
        mensagem.textContent = "Não foi possível carregar os detalhes.";
        mensagem.style.color = "red";
    }
}

async function carregarCarrinho() {
    const container = document.getElementById("carrinho-container");
    try {
        const resposta = await fetch("/api/carrinho");
        const carrinho = await resposta.json();
        container.innerHTML = "";
        carrinho.forEach((itens) => {
            const card = document.createElement("div");
            card.className = "itens-card";
            card.innerHTML = `<h3>${itens.nome}</h3><button>Remover</button>`;
            container.appendChild(card);
        });
    } catch (erro) {
        const mensagem = document.getElementById("mensagem-status");
        mensagem.textContent = "Não foi possível carregar o carrinho.";
        mensagem.style.color = "red";
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
            card.className = "pedidos-card";
            card.innerHTML = `<h2>${pedido.nome}</h2><p>${pedido.descricao}</p><p>R$ ${pedido.preco.toFixed(2)}</p><button>Comprar</button>`;
            container.appendChild(card);
        });
    } catch (erro) {
        const mensagem = document.getElementById("mensagem-status");
        mensagem.textContent = "Não foi possível carregar os pedidos.";
        mensagem.style.color = "red";
    }
}

carregarProdutos();
carregarDetalhes();
carregarCarrinho();
carregarPedidos();
