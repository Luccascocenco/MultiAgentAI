// Função para carregar conteúdo da página
function carregarConteudo() {
    // Conexão com o servidor
    fetch('/api/index')
        .then(response => response.json())
        .then(data => {
            // Mostrar conteúdo na página
            document.getElementById('conteudo').innerHTML = data.conteudo;
        })
        .catch(error => console.error(error));
}

// Evento para carregar conteúdo da página
document.addEventListener('DOMContentLoaded', carregarConteudo);