"""Janela de chat para o MultiAgentAI.

Como usar: salve este arquivo dentro da pasta MultiAgentAI (ao lado do main.py
e do orchestrator.py) e rode com:

    .venv\\Scripts\\python.exe MultiAgentAI\\chat_app.py

Usa apenas Tkinter, que já vem com o Python (nada para instalar).
"""
import contextlib
import os
import queue
import re
import socket
import subprocess
import sys
import threading
import tkinter as tk
import traceback
import webbrowser
from tkinter import scrolledtext

# Garante que "agents" e "orchestrator" sejam encontrados e que a pasta
# generated_projects continue sendo criada dentro de MultiAgentAI,
# não importa de onde o app foi aberto.
PASTA_APP = os.path.dirname(os.path.abspath(__file__))
if PASTA_APP not in sys.path:
    sys.path.insert(0, PASTA_APP)
os.chdir(PASTA_APP)


# =====================================================================
#  LIGAÇÃO COM OS SEUS AGENTES
# =====================================================================
# Pasta do último projeto gerado (usada pelo botão "Abrir site").
ULTIMO_PROJETO = None


def limpar_nome(nome: str) -> str:
    """Deixa o nome digitado seguro para virar nome de pasta no Windows."""
    nome = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", nome).strip(" .")
    nome = re.sub(r"\s+", "_", nome)
    return nome or "Projeto"


def responder(nome_projeto: str, mensagem: str) -> str:
    """Roda o orquestrador com o nome e a descrição dados e devolve a resposta.

    Tudo que o orquestrador der print() (progresso, "Arquiteto trabalhando...")
    aparece no chat como log cinza.
    """
    global ULTIMO_PROJETO
    ULTIMO_PROJETO = None
    from orchestrator import criar_projeto

    pasta_base = os.path.join(PASTA_APP, "generated_projects")
    antes = set(os.listdir(pasta_base)) if os.path.isdir(pasta_base) else set()

    criar_projeto(mensagem, nome_projeto=nome_projeto)

    # criar_projeto não devolve o caminho, então descobrimos qual pasta é nova.
    depois = set(os.listdir(pasta_base)) if os.path.isdir(pasta_base) else set()
    novas = [os.path.join(pasta_base, n) for n in depois - antes]

    if not novas:
        return "Projeto finalizado!"

    caminho = max(novas, key=os.path.getmtime)
    ULTIMO_PROJETO = caminho
    return (
        "Projeto finalizado!\n\n"
        f"Pasta: {caminho}\n\n"
        "Clique em \"Abrir site\" (canto inferior direito) para ver o "
        "site funcionando com o banco de dados."
    )


# =====================================================================
#  INTERFACE
# =====================================================================
BG = "#1e1e1e"
BG_ENTRADA = "#252526"
BOLHA_USER = "#2b5fd9"
BOLHA_BOT = "#2d2d30"
TEXTO = "#e6e6e6"
CINZA = "#8b8b8b"
VERMELHO = "#ff6b6b"


class _FilaWriter:
    """Captura os print() dos agentes e manda para o chat."""

    def __init__(self, fila):
        self.fila = fila

    def write(self, texto):
        if texto and texto.strip():
            self.fila.put(("log", texto.rstrip()))
        return len(texto)

    def flush(self):
        pass


class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MultiAgent AI")
        self.geometry("900x680")
        self.minsize(520, 420)
        self.configure(bg=BG)

        self.fila = queue.Queue()
        self.ocupado = False
        self.nome_projeto = None  # None = ainda esperando o nome da aplicação
        self.ultimo_projeto = None
        self.servidor = None
        self._log_servidor = None
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        self._montar_chat()
        self._montar_entrada()

        self._adicionar(
            "bot",
            "Olá! Qual vai ser o nome da aplicação?",
        )
        self.entrada.focus_set()
        self.after(100, self._verificar_fila)

    # ---------- layout ----------
    def _montar_chat(self):
        self.chat = scrolledtext.ScrolledText(
            self,
            wrap="word",
            state="disabled",
            bg=BG,
            fg=TEXTO,
            bd=0,
            highlightthickness=0,
            padx=14,
            pady=10,
            font=("Segoe UI", 11),
            cursor="arrow",
        )
        self.chat.pack(fill="both", expand=True)

        base = dict(spacing1=2, spacing3=2)
        self.chat.tag_configure(
            "user", justify="right", background=BOLHA_USER,
            lmargin1=160, lmargin2=160, rmargin=8, **base,
        )
        self.chat.tag_configure(
            "bot", background=BOLHA_BOT,
            lmargin1=8, lmargin2=8, rmargin=160, **base,
        )
        self.chat.tag_configure(
            "log", foreground=CINZA, font=("Consolas", 9),
            lmargin1=8, lmargin2=8, rmargin=60,
        )
        self.chat.tag_configure(
            "erro", foreground=VERMELHO, font=("Consolas", 9),
            lmargin1=8, lmargin2=8, rmargin=60,
        )
        self.chat.tag_configure(
            "nome", foreground=CINZA, font=("Segoe UI", 8, "bold"), background=BG,
        )

    def _montar_entrada(self):
        barra = tk.Frame(self, bg=BG, padx=12, pady=10)
        barra.pack(fill="x", side="bottom")

        topo = tk.Frame(barra, bg=BG)
        topo.pack(fill="x", pady=(0, 4))

        self.status = tk.Label(
            topo, text="", bg=BG, fg=CINZA, anchor="w", font=("Segoe UI", 9)
        )
        self.status.pack(side="left", fill="x", expand=True)

        self.botao_site = tk.Button(
            topo, text="Abrir site", command=self.abrir_site, state="disabled",
            bg="#2d7d46", fg="white", activebackground="#226036",
            activeforeground="white", disabledforeground="#777777", bd=0,
            padx=12, pady=3, font=("Segoe UI", 9, "bold"), cursor="hand2",
        )
        self.botao_site.pack(side="right")

        linha = tk.Frame(barra, bg=BG)
        linha.pack(fill="x")

        self.entrada = tk.Text(
            linha, height=3, wrap="word", bg=BG_ENTRADA, fg=TEXTO,
            insertbackground=TEXTO, bd=0, highlightthickness=1,
            highlightbackground="#3c3c3c", highlightcolor=BOLHA_USER,
            padx=10, pady=8, font=("Segoe UI", 11),
        )
        self.entrada.pack(side="left", fill="x", expand=True)
        self.entrada.bind("<Return>", self._ao_apertar_enter)
        self.entrada.bind("<Shift-Return>", lambda e: None)  # quebra de linha

        self.botao = tk.Button(
            linha, text="Enviar", command=self.enviar, bg=BOLHA_USER, fg="white",
            activebackground="#1f4bb0", activeforeground="white", bd=0,
            padx=18, pady=10, font=("Segoe UI", 10, "bold"), cursor="hand2",
        )
        self.botao.pack(side="right", padx=(10, 0), fill="y")

    # ---------- comportamento ----------
    def _ao_apertar_enter(self, _evento):
        self.enviar()
        return "break"  # impede de inserir a quebra de linha

    def _adicionar(self, quem, texto):
        nomes = {"user": "Você", "bot": "Agentes"}
        self.chat.configure(state="normal")
        if quem in nomes:
            self.chat.insert("end", nomes[quem] + "\n", ("nome",))
            self.chat.insert("end", f" {texto} \n\n", (quem,))
        else:  # log / erro
            self.chat.insert("end", texto + "\n", (quem,))
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def enviar(self):
        if self.ocupado:
            return
        mensagem = self.entrada.get("1.0", "end").strip()
        if not mensagem:
            return
        self.entrada.delete("1.0", "end")
        self._adicionar("user", mensagem)

        # Primeira resposta: o nome da aplicação.
        if self.nome_projeto is None:
            self.nome_projeto = limpar_nome(mensagem)
            self._adicionar(
                "bot",
                f"Ótimo, o projeto vai se chamar \"{self.nome_projeto}\".\n"
                "Agora descreva o site que você quer criar.",
            )
            return

        self._definir_ocupado(True)
        threading.Thread(
            target=self._executar,
            args=(self.nome_projeto, mensagem),
            daemon=True,
        ).start()

    def _executar(self, nome_projeto, mensagem):
        """Roda em outra thread para a janela não travar."""
        writer = _FilaWriter(self.fila)
        try:
            with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
                resposta = responder(nome_projeto, mensagem)
            self.fila.put(("bot", str(resposta)))
            if ULTIMO_PROJETO:
                self.fila.put(("projeto", ULTIMO_PROJETO))
        except Exception:
            self.fila.put(("erro", traceback.format_exc()))
        finally:
            self.fila.put(("fim", ""))

    def _verificar_fila(self):
        try:
            while True:
                tipo, texto = self.fila.get_nowait()
                if tipo == "projeto":
                    self.ultimo_projeto = texto
                    self.botao_site.configure(state="normal")
                elif tipo == "fim":
                    self._definir_ocupado(False)
                    # Volta ao começo para criar outra aplicação.
                    self.nome_projeto = None
                    self._adicionar(
                        "bot",
                        "Quer criar outra aplicação? Me diga o nome dela.",
                    )
                else:
                    self._adicionar(tipo, texto)
        except queue.Empty:
            pass
        self.after(100, self._verificar_fila)

    # ---------- servidor do site gerado ----------
    def abrir_site(self):
        """Sobe o backend.py do último projeto e abre o site no navegador."""
        if not self.ultimo_projeto:
            return

        self._parar_servidor()

        # Prefere a porta 5000 (a que o agente costuma usar no backend.py);
        # se estiver ocupada, escolhe uma livre e passa em PORT.
        porta = 5000
        try:
            with socket.socket() as s:
                s.bind(("127.0.0.1", porta))
        except OSError:
            with socket.socket() as s:
                s.bind(("127.0.0.1", 0))
                porta = s.getsockname()[1]

        caminho_log = os.path.join(self.ultimo_projeto, "servidor.log")
        env = dict(os.environ, PORT=str(porta), PYTHONIOENCODING="utf-8")

        try:
            self._log_servidor = open(caminho_log, "w", encoding="utf-8")
            self.servidor = subprocess.Popen(
                [sys.executable, "backend.py"],
                cwd=self.ultimo_projeto,
                env=env,
                stdout=self._log_servidor,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        except Exception:
            self._adicionar("erro", traceback.format_exc())
            return

        self._adicionar("log", f"Iniciando o site na porta {porta}...")
        self.after(500, lambda: self._esperar_servidor(porta, caminho_log, 0))

    def _ler_log_servidor(self, caminho_log):
        try:
            with open(caminho_log, encoding="utf-8", errors="replace") as f:
                return f.read()[-4000:]
        except OSError:
            return "(sem detalhes)"

    def _esperar_servidor(self, porta, caminho_log, tentativa):
        """Espera o servidor responder (até ~10 s) e então abre o navegador."""
        if self.servidor is None:
            return

        if self.servidor.poll() is not None:
            # O servidor caiu logo ao iniciar: mostra o motivo no chat.
            saida = self._ler_log_servidor(caminho_log)
            self._adicionar("erro", "O servidor não iniciou:\n" + saida)
            if "No module named" in saida and "flask" in saida.lower():
                self._adicionar(
                    "bot",
                    "Falta instalar o Flask. No terminal, na pasta ProjetoPy, "
                    "rode: uv add flask  (depois clique em Abrir site de novo).",
                )
            return

        try:
            with socket.create_connection(("127.0.0.1", porta), timeout=0.3):
                pronto = True
        except OSError:
            pronto = False

        if pronto:
            webbrowser.open(f"http://localhost:{porta}")
            self._adicionar(
                "log",
                f"Site aberto em http://localhost:{porta} "
                "(fica rodando enquanto esta janela estiver aberta).",
            )
            return

        if tentativa >= 20:
            self._adicionar(
                "erro",
                f"O servidor não respondeu na porta {porta}. "
                "Talvez o backend.py use outra porta. Saída dele:\n"
                + self._ler_log_servidor(caminho_log),
            )
            return

        self.after(500, lambda: self._esperar_servidor(porta, caminho_log, tentativa + 1))

    def _parar_servidor(self):
        if self.servidor is not None and self.servidor.poll() is None:
            self.servidor.terminate()
        self.servidor = None
        if self._log_servidor is not None:
            try:
                self._log_servidor.close()
            except OSError:
                pass
            self._log_servidor = None

    def _ao_fechar(self):
        self._parar_servidor()
        self.destroy()

    def _definir_ocupado(self, ocupado):
        self.ocupado = ocupado
        self.botao.configure(state="disabled" if ocupado else "normal")
        self.status.configure(text="Os agentes estão trabalhando..." if ocupado else "")
        if not ocupado:
            self.entrada.focus_set()


if __name__ == "__main__":
    ChatApp().mainloop()