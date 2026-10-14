class PedidoService {
  constructor() {
    this.pedidos = [];
  }

  cadastrarPedido(dados) {
    const pedido = {
      id: this.pedidos.length + 1,
      cliente_id: dados.cliente_id,
      data: dados.data,
      hora: dados.hora,
      status: 'em_andamento'
    };
    this.pedidos.push(pedido);
    return pedido;
  }

  gerenciarStatus(pedidoId, novoStatus) {
    const pedido = this.pedidos.find((pedido) => pedido.id === pedidoId);
    if (pedido) {
      pedido.status = novoStatus;
    }
    return pedido;
  }
}

const pedidoService = new PedidoService();

export default pedidoService;