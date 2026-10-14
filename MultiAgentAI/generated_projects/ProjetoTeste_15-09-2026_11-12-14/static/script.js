// Funcionalidade de gerenciamento de estoque
async function carregarEstoque() {
    const resposta = await fetch("/api/estoque");
    const estoque = await resposta.json();
    const container = document.getElementById("produtos-container");
    container.innerHTML = "";
    estoque.forEach((produto) => {
        const card = document.createElement("div");
        card.className = "produto-card";
        card.innerHTML = `<h3>${produto.nome}</h3><p>${produto.descricao}</p><p>R$ ${produto.preco.toFixed(2)}</p><button>Comprar</button>`;
        container.appendChild(card);
    });
}

// Funcionalidade de gerenciamento de pedidos
async function carregarOrdens() {
    const resposta = await fetch("/api/ordens");
    const ordens = await resposta.json();
    const container = document.getElementById("ordens-container");
    container.innerHTML = "";
    ordens.forEach((ordem) => {
        const card = document.createElement("div");
        card.className = "ordem-card";
        card.innerHTML = `<h3>${ordem.cliente}</h3><p>${ordem.produto}</p><p>R$ ${ordem.preco.toFixed(2)}</p><button>Entregar</button>`;
        container.appendChild(card);
    });
}

// Funcionalidade de gerenciamento de clientes
async function carregarClientes() {
    const resposta = await fetch("/api/clientes");
    const clientes = await resposta.json();
    const container = document.getElementById("clientes-container");
    container.innerHTML = "";
    clientes.forEach((cliente) => {
        const card = document.createElement("div");
        card.className = "cliente-card";
        card.innerHTML = `<h3>${cliente.nome}</h3><p>${cliente.email}</p><p>${cliente.telefone}</p>`;
        container.appendChild(card);
    });
}

// Funcionalidade de gerenciamento de relatórios
async function carregarRelatorios() {
    const resposta = await fetch("/api/relatorios");
    const relatorio = await resposta.json();
    const container = document.getElementById("relatorios-container");
    container.innerHTML = "";
    relatorio.forEach((relatorio) => {
        const card = document.createElement("div");
        card.className = "relatorio-card";
        card.innerHTML = `<h3>${relatorio.titulo}</h3><p>${relatorio.conteudo}</p>`;
        container.appendChild(card);
    });
}

// Carregar os dados iniciais
carregarEstoque();
carregarOrdens();
carregarClientes();
carregarRelatorios();

// Evento para atualizar os dados
document.querySelector(".produto-card button").addEventListener("click", async () => {
    const resposta = await fetch("/api/estoque");
    const estoque = await resposta.json();
    carregarEstoque();
});

document.querySelector(".ordem-card button").addEventListener("click", async () => {
    const resposta = await fetch("/api/ordens");
    const ordens = await resposta.json();
    carregarOrdens();
});

document.querySelector(".cliente-card button").addEventListener("click", async () => {
    const resposta = await fetch("/api/clientes");
    const clientes = await resposta.json();
    carregarClientes();
});

document.querySelector(".relatorio-card button").addEventListener("click", async () => {
    const resposta = await fetch("/api/relatorios");
    const relatorio = await resposta.json();
    carregarRelatorios();
});