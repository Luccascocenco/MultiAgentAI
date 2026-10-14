// ===== script.js refeito automaticamente pelo verificador =====
// O script original tinha erros que deixavam a página sem dados. Este monta
// as listas direto da API (/api/...) e liga os botões às seções da página.
const CONFIG = {
    "status": "mensagem-status",
    "classeCard": "produto-card",
    "textoBotao": "Ver",
    "colecoes": [
        {
            "tabela": "matriculas",
            "rota": "/api/matriculas",
            "container": "matriculas-container",
            "principal": true,
            "nome": null,
            "imagem": null,
            "categoria": null,
            "descricao": null,
            "relacoes": {}
        },
        {
            "tabela": "turmas",
            "rota": "/api/turmas",
            "container": "turmas-container",
            "principal": false,
            "nome": "nome",
            "imagem": "imagem",
            "categoria": "categoria",
            "descricao": "descricao",
            "relacoes": {}
        },
        {
            "tabela": "unidades",
            "rota": "/api/unidades",
            "container": "unidades-container",
            "principal": false,
            "nome": "nome",
            "imagem": null,
            "categoria": null,
            "descricao": null,
            "relacoes": {}
        }
    ],
    "ligacoes": []
};

function criar(tag, classe, texto) {
    const elemento = document.createElement(tag);
    if (classe) { elemento.className = classe; }
    if (texto !== undefined && texto !== null) { elemento.textContent = texto; }
    return elemento;
}

function rotulo(chave) {
    const texto = chave.replace(/_/g, " ");
    return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function formatar(chave, valor) {
    if (/preco|valor|total/i.test(chave) && valor !== null && valor !== "" && !isNaN(Number(valor))) {
        return "R$ " + Number(valor).toFixed(2).replace(".", ",");
    }
    return valor;
}

let temporizador = null;

function mostrarMensagem(texto) {
    const area = document.getElementById(CONFIG.status);
    if (!area) { return; }
    area.textContent = texto;
    clearTimeout(temporizador);
    temporizador = setTimeout(() => { area.textContent = ""; }, 4000);
}

async function buscar(rota) {
    const resposta = await fetch(rota);
    if (!resposta.ok) { throw new Error(rota + " respondeu " + resposta.status); }
    return resposta.json();
}

async function carregarColecao(colecao) {
    const container = document.getElementById(colecao.container);
    if (!container) { return; }

    try {
        const itens = await buscar(colecao.rota);
        const nomes = {};

        for (const campo of Object.keys(colecao.relacoes)) {
            const relacao = colecao.relacoes[campo];
            const lista = await buscar(relacao.rota);
            nomes[campo] = {};
            lista.forEach((registro) => { nomes[campo][registro.id] = registro[relacao.nome]; });
        }

        container.innerHTML = "";

        if (!itens.length) {
            container.textContent = "Nada cadastrado por enquanto.";
            return;
        }

        itens.forEach((item) => {
            const card = criar("div", CONFIG.classeCard);
            const relacionados = Object.keys(colecao.relacoes);
            let titulo = colecao.nome ? item[colecao.nome] : null;

            if (!titulo && relacionados.length) {
                titulo = nomes[relacionados[0]][item[relacionados[0]]];
            }
            if (!titulo) { titulo = rotulo(colecao.tabela) + " " + item.id; }

            if (colecao.imagem && item[colecao.imagem]) {
                const imagem = criar("img", "card-img");
                imagem.src = item[colecao.imagem];
                imagem.alt = String(titulo);
                imagem.loading = "lazy";
                imagem.onerror = () => { imagem.style.display = "none"; };
                card.appendChild(imagem);
            }

            card.appendChild(criar("h3", "", titulo));

            if (colecao.categoria && item[colecao.categoria]) {
                card.appendChild(criar("span", "etiqueta", item[colecao.categoria]));
            }

            if (colecao.descricao && item[colecao.descricao]) {
                card.appendChild(criar("p", "", item[colecao.descricao]));
            }

            const jaMostrados = [
                "id", colecao.nome, colecao.imagem, colecao.categoria, colecao.descricao,
            ];

            Object.keys(item).forEach((chave) => {
                if (jaMostrados.includes(chave) || chave in colecao.relacoes) { return; }
                if (item[chave] === null || item[chave] === "") { return; }
                card.appendChild(criar("p", "", rotulo(chave) + ": " + formatar(chave, item[chave])));
            });

            Object.keys(colecao.relacoes).forEach((campo) => {
                const relacionado = nomes[campo][item[campo]];
                if (relacionado && relacionado !== titulo) {
                    card.appendChild(criar("p", "", rotulo(campo.replace(/_id$/, "")) + ": " + relacionado));
                }
            });

            if (colecao.principal) {
                const botao = criar("button", "", CONFIG.textoBotao);
                botao.addEventListener("click", () => {
                    mostrarMensagem("Você escolheu: " + titulo + ".");
                });
                card.appendChild(botao);
            }

            container.appendChild(card);
        });
    } catch (erro) {
        console.error(erro);
        container.textContent = "Não foi possível carregar os dados. O servidor está rodando?";
    }
}

CONFIG.colecoes.forEach(carregarColecao);

CONFIG.ligacoes.forEach(([idBotao, idAlvo]) => {
    const botao = document.getElementById(idBotao);
    if (!botao) { return; }
    botao.addEventListener("click", () => {
        if (idAlvo === "topo") {
            window.scrollTo({ top: 0, behavior: "smooth" });
            return;
        }
        const alvo = document.getElementById(idAlvo);
        if (alvo) { alvo.scrollIntoView({ behavior: "smooth" }); }
    });
});
