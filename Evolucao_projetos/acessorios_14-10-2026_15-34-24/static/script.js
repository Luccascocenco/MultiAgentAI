let produtos = [
    {
        id: 1,
        nome: 'Camiseta Básica Premium',
        descricao: 'Camiseta de algodão com modelagem confortável e design minimalista.',
        preco: 69.90,
        avaliacao: 4.5
    },
    {
        id: 2,
        nome: 'Blusa Canelada',
        descricao: 'Blusa versátil com textura delicada para combinações casuais.',
        preco: 79.90,
        avaliacao: 4.2
    },
    // Adicionar mais produtos aqui
];

let cart = [];

function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    container.innerHTML = '';

    produtos.forEach(produto => {
        const card = document.createElement("div");
        card.className = "produto-card";

        const h3 = document.createElement("h3");
        h3.textContent = produto.nome;

        const p = document.createElement("p");
        p.textContent = produto.descricao;

        const preco = document.createElement("p");
        preco.textContent = `R$ ${produto.preco.toFixed(2)}`;
        preco.className = "preco";

        const botao = document.createElement("button");
        botao.textContent = 'Comprar';
        botao.onclick = () => adicionarAoCarrinho(produto.id);
        botao.className = "botao-comprar";

        card.appendChild(h3);
        card.appendChild(p);
        card.appendChild(preco);
        card.appendChild(botao);

        container.appendChild(card);
    });
}

function adicionarAoCarrinho(id) {
    const produtoEncontrado = produtos.find(produto => produto.id == id);
    const produtoExiste = cart.find(produto => produto.id == id);
    if (!produtoExiste) {
        cart.push(produtoEncontrado);
        const preco = produtoEncontrado.preco;
        const subtotal = preco * 1;
        const mensagem = `Produto adicionado ao carrinho com sucesso! R$ ${subtotal.toFixed(2)}`;
        document.getElementById("mensagem-status").innerHTML = mensagem;
    } else {
        const index = cart.indexOf(produtoEncontrado);
        cart[index].quantidade++;
        const preco = produtoEncontrado.preco;
        const subtotal = preco * cart[index].quantidade;
        const mensagem = `Quantidade de ${produtoEncontrado.nome} aumentada com sucesso! R$ ${subtotal.toFixed(2)}`;
        document.getElementById("mensagem-status").innerHTML = mensagem;
    }
}

function calcularSubtotal() {
    const subtotal = cart.reduce((total, produto) => total + produto.preco * produto.quantidade, 0);
    return subtotal;
}

carregarProdutos();