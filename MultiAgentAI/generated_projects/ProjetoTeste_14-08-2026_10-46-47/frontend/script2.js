// script.js
const form = document.getElementById('pedido-form');

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const data = new Date();
  const hora = new Date().getHours() + ':' + new Date().getMinutes();
  const total = parseFloat(document.getElementById('total').value);
  // Chamada para o serviço de pagamento
});