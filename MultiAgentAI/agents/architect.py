from ollama import chat
import time

inicio = time.time()

def architect(prompt):

    response = chat(

        model="llama3.2",

        messages=[

            {
                "role":"system",

                "content":
                """
                Você é um Arquiteto de Software Senior.

                Sua função é:
                1 - Entender o projeto solicitado.

                2 - Dividir o sistema em módulos.

                3 - Definir:
                - funcionalidades
                - telas
                - tecnologias
                - estrutura das pastas
                - arquivos necessários
                - banco de dados necessário

                NUNCA gere código.
                Sua única função é criar a arquitetura completa do sistema.
                """
            },

            {
                "role":"user",
                "content":prompt
            }

        ],

        options={
            "num_ctx": 8192
        }

    )

    return response.message.content

fim = time.time()
print(f"\nTempo Arquiteto: {fim - inicio:.2f} segundos")