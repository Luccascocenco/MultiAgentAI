fetch('/api/produtos')
    .then(response => response.json())
    .then(data => {
        const produtosContainer = document.getElementById('produtos-container');
        data.forEach(produto => {
            const produtoCard = document.createElement('div');
            produtoCard.classList.add('produto-card');
            produtoCard.innerHTML = `
                <img src="${produto.imagem}" alt="${produto.nome}">
                <h3>${produto.nome}</h3>
                <p>${produto.descricao_produto}</p>
                <button>Comprar</button>
            `;
            produtosContainer.appendChild(produtoCard);
        });
    })
    .catch(error => console.error(error));