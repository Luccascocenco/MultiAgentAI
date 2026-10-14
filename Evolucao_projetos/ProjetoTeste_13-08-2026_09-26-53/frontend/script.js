const loginForm = document.getElementById('login-form');
const nomeInput = document.getElementById('nome');
const emailInput = document.getElementById('email');
const senhaInput = document.getElementById('senha');

loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const dados = {
        nome: nomeInput.value,
        email: emailInput.value,
        senha: senhaInput.value
    };
    // envia os dados para o servidor para realizar o login
});