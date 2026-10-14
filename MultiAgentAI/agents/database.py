from ollama import chat
import time


def database(architecture):

    print("\n>>> DATABASE: iniciando...")

    inicio = time.time()

    try:

        print(">>> DATABASE: enviando pedido para Ollama...")

        response = chat(

            model="llama3.2",

            messages=[

                {
                    "role": "system",

                    "content": """
Você é um Engenheiro de Banco de Dados Sênior.

Sua função é desenvolver SOMENTE o Banco de Dados do sistema.

REGRAS:

- Não gere Front-End.
- Não gere Back-End.
- Baseie-se exclusivamente na arquitetura recebida.
- Crie tabelas, relacionamentos, índices e restrições necessárias.
- Gere SQL funcional.
- Gere o arquivo UMA ÚNICA VEZ. Não repita o mesmo arquivo duas vezes.
- Antes de cada bloco de código, informe o nome do arquivo, EXATAMENTE
  no formato abaixo, sem negrito, aspas ou qualquer outro símbolo além
  do que está no exemplo.
- SEMPRE feche o bloco de código com crase tripla (```) ao final.
- Não escreva nada fora dos blocos de código (nem antes, nem depois,
  nem entre um FILE: e outro).

FORMATO OBRIGATÓRIO (siga exatamente este exemplo, incluindo o
fechamento com crase tripla):

FILE: database.sql
```sql
CREATE TABLE exemplo (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL
);
```

Use o banco de dados definido pela arquitetura.
"""
},
            {
                "role": "user",
                "content": architecture
            }

        ],

        options={
            "num_ctx": 8192
        }

    )

        print(">>> DATABASE: Ollama respondeu!")

        resultado = response.message.content

        fim = time.time()

        print(
            f">>> DATABASE: tempo de execução: "
            f"{fim - inicio:.2f} segundos"
        )

        return resultado

    except Exception as erro:

        print("\n!!! ERRO NO DATABASE !!!")
        print(erro)

        return ""