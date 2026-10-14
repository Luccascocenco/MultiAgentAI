const fetchUrl = "https://example.com/api/produtos"; // URL do servidor
const fetchOptions = {
    method: "GET",
    headers: {
        "Content-Type": "application/json"
    }
};

function carregarProdutos() {
    fetch(fetchUrl, fetchOptions)
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("produtos-container");
            const cardTemplate = `
                <div class="produto-card">
                    <h3>${produto.nome}</h3>
                    <p>${produto.descricao}</p>
                    <p>R$ ${produto.preco.toFixed(2)}</p>
                    <button>Adicionar ao pedido</button>
                </div>
            `;
            container.innerHTML = "";
            data.forEach(produto => {
                const card = document.createElement("div");
                card.innerHTML = cardTemplate;
                container.appendChild(card);
            });
        })
        .catch(error => {
            console.error(error);
            const mensagem = document.getElementById("mensagem-status");
            mensagem.innerHTML = "Erro ao carregar produtos.";
            mensagem.style.color = "red";
        });
}

carregarProdutos();

// Eventos de botões
document.getElementById("cardapio").addEventListener("click", carregarCardapio);
document.getElementById("unidades").addEventListener("click", carregarUnidades);
document.getElementById("pedidos").addEventListener("click", carregarPedidos);
document.getElementById("fazer-pedido").addEventListener("click", carregarPedidos);

function carregarCardapio() {
    // Exemplo de código para carregar cardápio (não implementado)
}

function carregarUnidades() {
    // Exemplo de código para carregar unidades (não implementado)
}

function carregarPedidos() {
    // Exemplo de código para carregar pedidos (não implementado)
}
