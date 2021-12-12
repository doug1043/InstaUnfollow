# InstaUnfollow Telegram BOT

InstaUnfollow é um BOT para analisar os perfis que não seguem de volta na sua conta do Instagram utilizando a ferramenta [Instaloader](https://github.com/instaloader/instaloader).

## Instalação

Use o gerenciador de pacotes [pip](https://pip.pypa.io/en/stable/) para instalar as ferramentas:

```bash
pip install python-telegram-bot
pip install instaloader
```

## Configuração

Insira o TOKEN do seu BOT criado via API de criação de BOTs [Telegram](https://core.telegram.org/bots/api)
```python
#config.py

import instaloader

BOT_TOKEN = "YOUR_BOT_TOKEN"

USER, PASS = range(2)

L = instaloader.Instaloader()

user_profiles = {

}

```

## Comandos do BOT
[/start](#) --> Apresenta o BOT e informações sobre os principais comandos.

[/buscar_nao_seguidores](#) --> BOT responde uma lista de perfis que não seguem de volta o usuário logado.

[/notificar](#) --> Ativa avisos quando algum seguidor deixa de seguir o  usuário logado (Vários acessos podem sobrecarregar a API de requisições)

[/desativar](#) --> Desativa os avisos.

[/sair](#) --> Sai da conta.


## Contribuições
Requisições Pull são bem vindas.

## License
[MIT](https://choosealicense.com/licenses/mit/)
