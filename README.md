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
#bot.py
...

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("YOUR_TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

...
```

## Comandos do BOT
[/start](#) --> Responde uma saudação e informa o próximo comando para iniciar outras funções.

[/nao_seguidores](#) --> Responde uma lista de perfis que não seguem de volta.

[/notificar](#) --> Ativa as notificações quando alguém deixa de seguir (Vários acessos podem sobrecarregar a API de requisições)

[/desativar](#) --> Desativa as notificações.


## Contribuições
Requisições Pull são bem vindas.

## License
[MIT](https://choosealicense.com/licenses/mit/)
