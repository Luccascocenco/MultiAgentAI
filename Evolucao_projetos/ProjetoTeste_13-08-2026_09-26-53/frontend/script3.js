class ContaService {
  constructor() {
    this.contas = [];
  }

  criarConta(dados) {
    const conta = {
      id: this.contas.length + 1,
      nome: dados.nome,
      email: dados.email,
      senha: dados.senha
    };
    this.contas.push(conta);
    return conta;
  }

  gerenciarConta(id, dados) {
    const conta = this.contas.find((conta) => conta.id === id);
    if (conta) {
      Object.assign(conta, dados);
    }
    return conta;
  }
}

const contaService = new ContaService();

export default contaService;