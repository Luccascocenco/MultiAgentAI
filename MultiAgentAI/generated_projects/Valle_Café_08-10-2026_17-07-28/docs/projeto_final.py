from flask import Flask, request, jsonify
from flask_oauthlib.client import OAuth

app = Flask(__name__)

# Configuração do OAuth
oauth = OAuth(app)
client_id = 'SEU_CLIENT_ID'
client_secret = 'SEU_CLIENT_SECRET'
authorization_base_url = 'https://SEU_URL/authorize'
token_url = 'https://SEU_URL/token'

# Configuração do OAuth
def criar_oauth_client():
    return oauth.remote_app(
        'seu_oauth',
        consumer_key=client_id,
        consumer_secret=client_secret,
        base_url=authorization_base_url,
        request_token_params={
            'scope': 'seu_scopo',
            'state': 'seu_estado'
        },
        access_token_params={
            'grant_type': 'authorization_code',
            'code': request.args.get('code')
        },
        request_token_params={
            'display': 'popup',
            'scope': 'seu_scopo',
            'state': 'seu_estado'
        },
        access_token_url=token_url,
        on_token_updater=lambda self, res: res.json(),
        onAuthorizationFailed=lambda self, res: res.json(),
    )

# Endpoint de autenticação
@app.route('/seu_endpoint', methods=['GET'])
@oauth.authorized_handler(['seu_scopo'])
def seu_endpoint(accessToken, *args, **kwargs):
    return jsonify({'accessToken': accessToken})

# Endpoint de atualização de dados
@app.route('/atualizar-dados', methods=['POST'])
@oauth.authorized_handler(['seu_scopo'])
def atualizar_dados(accessToken, *args, **kwargs):
    return jsonify({'message': 'Dados atualizados'})

# Endpoint de atualização de dados
@app.route('/atualizar-dados', methods=['POST'])
def atualizar_dados_sem_auth():
    return jsonify({'message': 'Dados não atualizados'})

# Endpoint de atualização de dados
@app.route('/atualizar-dados', methods=['POST'])
@oauth.authorized_handler(['seu_scopo'])
def atualizar_dados_sem_auth(accessToken, *args, **kwargs):
    return jsonify({'message': 'Dados não atualizados'})

if __name__ == '__main__':
    app.run(debug=True)