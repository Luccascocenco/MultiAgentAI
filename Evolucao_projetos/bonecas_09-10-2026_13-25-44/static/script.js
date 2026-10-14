async function carregarProdutos() {
  const url = "/api/produtos";
  try {
    const resposta = await fetch(url);
    const produtos = await resposta.json();
    const container = document.getElementById("produtos-container");
    container.innerHTML = "";
    produtos.forEach((produto) => {
      const card = document.createElement("div");
      card.className = "produto-card";
      card.innerHTML = `
        <img src="${produto.imagem}" alt="${produto.nome}">
        <h2>${produto.nome}</h2>
        <p>${produto.descricao}</p>
        <p>Preço: R$ ${produto.preco.toFixed(2)}</p>
        <button>Comprar</button>
      `;
      container.appendChild(card);
    });
  } catch (erro) {
    const container = document.getElementById("produtos-container");
    container.innerHTML = "<p>Não foi possível carregar os produtos.</p>";
  }
}

async function carregarProdutosCarrinho() {
  const url = "/api/produtos";
  try {
    const resposta = await fetch(url);
    const produtos = await resposta.json();
    const cart = document.getElementById("carrinho");
    cart.innerHTML = "";
    produtos.forEach((produto) => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <h2>${produto.nome}</h2>
        <p>Preço: R$ ${produto.preço.toFixed(2)}</p>
      `;
      cart.appendChild(card);
    });
  } catch (erro) {
    const cart = document.getElementById("carrinho");
    cart.innerHTML = "<p>Não foi possível carregar o carrinho.</p>";
  }
}

async function carregarProdutos() {
  carregarProdutosCarrinho();
  carregarProdutosCarrinho();
}

carregarProdutos();