# InstaUnfollow Telegram BOT

InstaUnfollow é um BOT para analisar os perfis que não seguem de volta na sua conta do Instagram utilizando a ferramenta [Instaloader](https://github.com/instaloader/instaloader).

## Installation

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

## Contributing
Requisições Pull são bem vindas.

## License
[MIT](https://choosealicense.com/licenses/mit/)
