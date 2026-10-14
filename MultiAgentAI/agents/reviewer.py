from ollama import chat
import time

inicio = time.time()

def reviewer(prompt):

    response = chat(

        model="llama3.2",

        messages=[

            {

                "role":"system",

                "content":
                """
                Você é um Engenheiro de Software Sênior especializado em revisão de projetos.

                Sua função é:

                - Encontrar erros de arquitetura.
                - Verificar a compatibilidade entre os módulos.
                - Encontrar vulnerabilidades de segurança.
                - Sugerir melhorias.
                - Verificar se há arquivos faltando.
                - Avaliar a organização do projeto.
                - Analise o codigo SQL e verifique se necessita de mudanças.

                NUNCA gere código novo.

                Você deve atuar apenas como revisor técnico do projeto.

                """

            },

            {

                "role":"user",
                "content":prompt

            }

        ]

    )

    return response.message.content

fim = time.time()
print(f"\nTempo Revisor: {fim - inicio:.2f} segundos")