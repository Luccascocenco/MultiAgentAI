class HistoricoService {
  constructor() {
    this.historicos = [];
  }

  criarHistorico(dados) {
    const historico = {
      id: this.historicos.length + 1,
      usuario_id: dados.usuario_id,
      pedido_id: dados.pedido_id,
      data: dados.data,
      hora: dados.hora
    };
    this.historicos.push(historico);
    return historico;
  }

  gerenciarHistorico(id, dados) {
    const historico = this.historicos.find((historico) => historico.id === id);
    if (historico) {
      Object.assign(historico, dados);
    }
    return historico;
  }
}

const historicoService = new HistoricoService();

export default historicoService;