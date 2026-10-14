// Adicionar evento ao botão de adicionar ao carrinho
const botoesAdicionarCarrinho = document.querySelectorAll('.btn-adicionar-carrinho');

botoesAdicionarCarrinho.forEach((botao) => {
    botao.addEventListener('click', () => {
        const produto = botao.parentNode;
        const nome = produto.querySelector('h3').textContent;
        const preco = produto.querySelector('p').textContent;
        console.log(`Adicionando ${nome} ao carrinho por ${preco}`);
    });
});