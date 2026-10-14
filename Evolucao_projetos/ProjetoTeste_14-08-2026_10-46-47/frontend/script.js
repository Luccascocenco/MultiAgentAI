// script.js
const form = document.getElementById('inserir-alimento-form');

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const nome = document.getElementById('nome').value;
  const preco = parseFloat(document.getElementById('preco').value);
  // Chamada para o serviço de inserção de alimentos
});