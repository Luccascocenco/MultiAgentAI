async function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    try {
        const resposta = await fetch("/api/plantas");
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
        container.innerHTML = "<p>Não foi possível carregar os produtos.</p>";
    }
}

async function carregarVasos() {
    const container = document.getElementById("vasos-container");
    try {
        const resposta = await fetch("/api/vasos");
        const vasos = await resposta.json();
        container.innerHTML = "";
        vasos.forEach((vasso) => {
            const card = document.createElement("div");
            card.className = "vasso-card";
            card.innerHTML = `
                <img src="${vasso.imagem}" alt="${vasso.tipo}">
                <h3>${vasso.tipo}</h3>
                <p>${vasso.tamanho}</p>
                <p>R$ ${vasso.preco.toFixed(2)}</p>
                <button>Comprar</button>
            `;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar os vasos.</p>";
    }
}

async function carregarJardinagem() {
    const container = document.getElementById("jardinagem-container");
    try {
        const resposta = await fetch("/api/produtos");
        const jardinagem = await resposta.json();
        container.innerHTML = "";
        jardinagem.forEach((itens) => {
            const card = document.createElement("div");
            card.className = "itens-card";
            card.innerHTML = `
                <img src="${itens.imagem}" alt="${itens.nome}">
                <h3>${itens.nome}</h3>
                <p>${itens.descricao}</p>
                <p>R$ ${itens.preco.toFixed(2)}</p>
                <button>Comprar</button>
            `;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar a jardinagem.</p>";
    }
}

async function carregarAcessorios() {
    const container = document.getElementById("acessorios-container");
    try {
        const resposta = await fetch("/api/produtos");
        const acessorios = await resposta.json();
        container.innerHTML = "";
        acessorios.forEach((acessorio) => {
            const card = document.createElement("div");
            card.className = "acessorio-card";
            card.innerHTML = `
                <img src="${acessorio.imagem}" alt="${acessorio.nome}">
                <h3>${acessorio.nome}</h3>
                <p>${acessorio.descricao}</p>
                <p>R$ ${acessorio.preco.toFixed(2)}</p>
                <button>Comprar</button>
            `;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar os acessórios.</p>";
    }
}

async function carregarOfertas() {
    const container = document.getElementById("ofertas-container");
    try {
        const resposta = await fetch("/api/produtos");
        const ofertas = await resposta.json();
        container.innerHTML = "";
        ofertas.forEach((oferta) => {
            const card = document.createElement("div");
            card.className = "oferta-card";
            card.innerHTML = `
                <img src="${oferta.imagem}" alt="${oferta.nome}">
                <h3>${oferta.nome}</h3>
                <p>${oferta.descricao}</p>
                <p>R$ ${oferta.preco.toFixed(2)}</p>
                <button>Comprar</button>
            `;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar as ofertas.</p>";
    }
}

carregarProdutos();
carregarVasos();
carregarJardinagem();
carregarAcessorios();
carregarOfertas();
