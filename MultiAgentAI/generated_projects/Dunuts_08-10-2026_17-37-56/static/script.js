async function carregarProdutos() {
    const container = document.getElementById("produtos-container");
    try {
        const resposta = await fetch("/api/diagramas");
        const diagramas = await resposta.json();
        container.innerHTML = "";

        diagramas.forEach((diagrama) => {
            const card = document.createElement("div");
            card.className = "produto-card";
            card.innerHTML = `
                <h3>${diagrama.nome}</h3>
                <p>${diagrama.conteúdo}</p>
                <button>Ver mais</button>
            `;
            container.appendChild(card);
        });
    } catch (erro) {
        container.innerHTML = "<p>Não foi possível carregar os diagramas.</p>";
    }
}

async function carregarNomes() {
    const resposta = await fetch("/api/nomes");
    const nomes = await resposta.json();
    const container = document.getElementById("nomes-container");
    container.innerHTML = "";

    nomes.forEach((nome) => {
        const card = document.createElement("div");
        card.className = "produto-card";
        card.innerHTML = `
            <h3>${nome.nome}</h3>
            <p>${nome.tipo}</p>
        `;
        container.appendChild(card);
    });
}

async function carregarConteudo() {
    const resposta = await fetch("/api/conteudo");
    const conteudos = await resposta.json();
    const container = document.getElementById("conteudo-container");
    container.innerHTML = "";

    conteudos.forEach((conteudo) => {
        const card = document.createElement("div");
        card.className = "produto-card";
        card.innerHTML = `
            <h3>${conteudo.nome}</h3>
            <p>Quantidade: ${conteudo.quantidade}</p>
            <p>Preço: R$ ${conteudo.preço.toFixed(2)}</p>
        `;
        container.appendChild(card);
    });
}

const buttonDiagramas = document.getElementById("button-diagramas");
const buttonNomes = document.getElementById("button-nomes");
const buttonConteudo = document.getElementById("button-conteudo");

buttonDiagramas.addEventListener("click", carregarProdutos);
buttonNomes.addEventListener("click", carregarNomes);
buttonConteudo.addEventListener("click", carregarConteudo);

const buttonRelatorio = document.getElementById("button-relatorio");

buttonRelatorio.addEventListener("click", () => {
    const resposta = fetch("/api/relatorio")
        .then((res) => res.json())
        .then((relatorio) => {
            const container = document.getElementById("relatorio-container");
            container.innerHTML = "";
            relatorio.forEach((linha) => {
                const card = document.createElement("div");
                card.className = "produto-card";
                card.innerHTML = `
                    <h3>${linha[0]}</h3>
                    <p>${linha[1]}</p>
                    <p>${linha[2]}</p>
                `;
                container.appendChild(card);
            });
        })
        .catch((erro) => {
            const container = document.getElementById("relatorio-container");
            container.innerHTML = "<p>Não foi possível carregar o relatório.</p>";
        });
});