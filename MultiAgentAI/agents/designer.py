from ollama import chat
import time

PROMPT_DESIGNER = """
Você é o Designer de Interfaces do projeto.

Você recebe o TEMA do site, o HTML, o CSS atual e a lista de classes que o
HTML e o JavaScript usam. Sua função é reescrever o CSS para deixar o site
bonito, moderno e com o clima visual do tema (ex: loja de jogos de terror =
fundo escuro e vermelho; loja de roupas = claro e elegante).

REGRAS:
- Altere SOMENTE o CSS. Não escreva HTML nem JavaScript.
- Mantenha TODOS os seletores (classes e ids) do CSS atual e da lista
  recebida. Você pode acrescentar seletores novos.
- Comece o arquivo com um bloco :root que defina EXATAMENTE estas variáveis,
  todas com cores em hexadecimal (#rrggbb):
    --fundo            cor de fundo da página
    --superficie       fundo de cards, cabeçalho e rodapé
    --texto            cor do texto principal (legível sobre --fundo e --superficie)
    --texto-suave      texto secundário (legível sobre --fundo e --superficie)
    --primaria         cor dos botões e destaques
    --primaria-hover   versão um pouco mais escura/clara da --primaria
    --sobre-primaria   cor do texto que fica SOBRE a --primaria (ex: dentro do botão)
    --borda            cor das bordas
  Pode acrescentar variáveis de espaçamento (--espaco), raio (--raio),
  sombra (--sombra) e fonte (--fonte).
- No :root escreva as cores DIRETAMENTE em hexadecimal (ex: --fundo: #E3F4FC;).
  NUNCA use var(--...) dentro do :root e NUNCA use variáveis que não estejam
  definidas nele. Se receber uma PALETA DO PROJETO, use exatamente essas cores.
- O texto principal deve ser escuro sobre fundo claro (e claro sobre fundo escuro).
- --fundo e --superficie precisam ser do MESMO tom: os dois claros ou os dois
  escuros (ex: fundo #f4f4f4 e superfície #ffffff, ou fundo #0d0d0d e
  superfície #1a1a1a). NUNCA fundo claro com cabeçalho escuro (nem o
  contrário), porque o mesmo texto precisa ser legível nos dois.
- Botões: NUNCA use width ou height fixos em px. Use padding (ex: 10px 20px)
  e, se quiser, min-height. Textos como "Adicionar ao carrinho" devem caber
  no botão.
- Campos de formulário (input, textarea, select): fundo var(--superficie),
  texto var(--texto) e borda var(--borda). Nunca use var(--texto) ou
  var(--texto-suave) como cor de fundo.
- Seções com imagem de fundo escura (como o #hero) devem ter texto branco.
- Use essas variáveis no resto do CSS. Texto sempre com var(--texto),
  var(--texto-suave) ou var(--sobre-primaria); nunca coloque texto escuro
  sobre fundo escuro nem texto claro sobre fundo claro.
- Botões: fundo var(--primaria), texto var(--sobre-primaria); no :hover use
  var(--primaria-hover).
- Cards: fundo var(--superficie), borda de 1px com var(--borda). No :hover do
  card, mude só a sombra e suba um pouco (transform: translateY(-4px)); NUNCA
  troque o fundo do card pela cor primária.
- Tipografia: fontes do sistema (system-ui, -apple-system, Segoe UI,
  sans-serif). Não use @import nem fontes externas.
- Layout responsivo com flexbox ou grid e uma media query para telas de até
  768px.
- Estilize cabeçalho/navegação, botões, cards, formulários, tabelas e
  rodapé, com estados :hover e :focus nos itens clicáveis.
- Não use frameworks (Bootstrap, Tailwind) nem imagens externas.

Responda SOMENTE com o CSS completo, em um único bloco:

```css
/* css aqui */
```
"""


def designer(html, css, classes, problemas=None, tema="", paleta=""):
    """Recebe o front-end gerado e devolve uma versão aprimorada do CSS."""

    inicio = time.time()

    pedido = (
        f"TEMA DO SITE (pedido original do usuário):\n{tema or '(não informado)'}\n\n"
        f"HTML DO SITE:\n```html\n{html}\n```\n\n"
        f"CSS ATUAL:\n```css\n{css}\n```\n\n"
        f"CLASSES USADAS NO HTML E NO JAVASCRIPT:\n{', '.join(classes)}"
    )

    if paleta:
        pedido += f"\n\nPALETA DO PROJETO (use estas cores):\n{paleta}"

    if problemas:
        pedido += (
            "\n\nA VERSÃO ANTERIOR DO CSS TINHA ESTES PROBLEMAS. "
            "CORRIJA TODOS:\n- " + "\n- ".join(problemas)
        )

    response = chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": PROMPT_DESIGNER},
            {"role": "user", "content": pedido},
        ],
        # O padrão do Ollama é pequeno; HTML + CSS juntos podem passar disso
        # e o modelo acabaria "esquecendo" o começo do pedido.
        options={"num_ctx": 8192},
    )

    print(f"\nTempo Designer: {time.time() - inicio:.2f} segundos")

    return response.message.content