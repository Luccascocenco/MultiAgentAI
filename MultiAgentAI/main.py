from orchestrator import criar_projeto


print("\n========== MULTI AGENT AI ==========\n")


while True:

    prompt = input("Você: ")

    if prompt.lower() == "sair":
        break

    criar_projeto(prompt)