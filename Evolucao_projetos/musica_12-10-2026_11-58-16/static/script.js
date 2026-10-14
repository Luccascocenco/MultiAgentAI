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

async function carregarPedidos() {
    const mensagemStatus = document.getElementById("mensagem-status");
    try {
        const resposta = await fetch("/api/pedidos");
        const pedidos = await resposta.json();
        // Não implementado aqui, mas seria necessário criar um botão para carregar pedidos
    } catch (erro) {
        mensagemStatus.innerHTML = "<p>Não foi possível carregar os pedidos.</p>";
    }
}

async function carregarClientes() {
    const mensagemStatus = document.getElementById("mensagem-status");
    try {
        const resposta = await fetch("/api/clientes");
        const clientes = await resposta.json();
        // Não implementado aqui, mas seria necessário criar um botão para carregar clientes
    } catch (erro) {
        mensagemStatus.innerHTML = "<p>Não foi possível carregar os clientes.</p>";
    }
}

carregarProdutos();