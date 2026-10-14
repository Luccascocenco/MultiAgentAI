// Obter os elementos do HTML
const banner = document.getElementById('banner');
const produtos = document.getElementById('produtos');
const pedidos = document.getElementById('pedidos');
const contas = document.getElementById('contas');

// Exibir os produtos
const produtosUl = document.createElement('ul');
productsUl.innerHTML = `
    <li>Produto 1</li>
    <li>Produto 2</li>
    <li>Produto 3</li>
`;
produtos.appendChild(produtosUl);

// Exibir os pedidos
const pedidosUl = document.createElement('ul');
pedidosUl.innerHTML = `
    <li>Pedido 1</li>
    <li>Pedido 2</li>
    <li>Pedido 3</li>
`;
pedidos.appendChild(pedidosUl);

// Exibir as contas
const contasUl = document.createElement('ul');
contasUl.innerHTML = `
    <li>Conta 1</li>
    <li>Conta 2</li>
    <li>Conta 3</li>
`;
contas.appendChild(contasUl);