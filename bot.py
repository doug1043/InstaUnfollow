#!/usr/bin/env python
# pylint: disable=C0116,W0613

import instaloader
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


USER, PASS = range(2)

L = instaloader.Instaloader()

user_profiles = {}

# Obtain profile metadata
# profile = instaloader.Profile.from_username(L.context, username)

def nao_seguem(chat_id): #Função retorna os perfis que não estão seguindo
    nsegue = []
    seguidores = []
    seguindo = []

    for followers in user_profiles[chat_id][3].get_followers():
        seguidores.append(followers.username)

    for following in user_profiles[chat_id][3].get_followees():
        seguindo.append(following.username)

    for perfil in seguindo:
        if perfil not in seguidores:
            nsegue.append(perfil)

    return nsegue


#Função em desenvolvimento!
# def fantasmas(): #Função retorna os perfis que nunca curtiram nenhuma postagem
#     fant = []
#     likes = set()
#     print("Buscando curtidas em todas as postagens do perfil {}.".format(profile.username))
#     for post in profile.get_posts():
#         print(post)
#         likes = likes | set(post.get_likes())

#     print("Buscando seguidores do perfil {}.".format(profile.username))
#     followers = set(profile.get_followers())

#     ghosts = followers - likes

#     print("Buscando fantasmas")
#     for ghost in ghosts:
#         fant.append(ghost.username)
    
#     return fant

def monitorarseg(chat_id): #Função retorna os perfis que deixaram de seguir
    base_perfis_atualizada = []
    base_perfis_nova = []

    if len(user_profiles[chat_id][2]) != 0:
        base_perfis_atualizada = nao_seguem(chat_id)
        for perfil in base_perfis_atualizada:
            if perfil not in user_profiles[chat_id][2]:
                base_perfis_nova.append(perfil)
        user_profiles[chat_id][2] = base_perfis_atualizada
    else:
        user_profiles[chat_id][2] = nao_seguem(chat_id)
    print(base_perfis_nova)
    return base_perfis_nova


def processar_notific(context: CallbackContext) -> None:
    due = 3600 #tempo em segundos
    job = context.job
    resp = monitorarseg(job.context)
    if len(resp) == 0:
        context.job_queue.run_once(processar_notific, due, context=job.context, name=str(job.context))
    else:
        
        for a in resp:
            context.bot.send_message(job.context, text="Alguém deixou de te seguir!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='@{}'.format(a), url='https://instagram.com/{}'.format(a))]
                ])
            )

        context.job_queue.run_once(processar_notific, due, context=job.context, name=str(job.context))


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


#Funções do bot abaixo:
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Olá, use /login para efetuar login com sua conta do Instagram e poder usar as outras funções')


def nao_seguidores(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if chat_id not in user_profiles:
        update.message.reply_text('Primeiro faça login pelo comando /login')
    elif len(user_profiles[chat_id]) < 4:
        update.message.reply_text('Primeiro faça login pelo comando /login')
    else:
        update.message.reply_text('Buscando perfis que não te seguem...')
        resp = nao_seguem(chat_id)
        for a in resp:
            context.bot.send_message(chat_id, text="Perfil",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='@{}'.format(a), url='https://instagram.com/{}'.format(a))]
                    ])
                )


def notificar(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if chat_id not in user_profiles:
        update.message.reply_text('Primeiro faça login pelo comando /login')
    elif len(user_profiles[chat_id]) < 4:
        update.message.reply_text('Primeiro faça login pelo comando /login')
    else:
        due = 10  
        # job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(processar_notific, due, context=chat_id, name=str(chat_id))
        update.message.reply_text('Notificações ativadas!')
        update.message.reply_text('Irei notificar quando alguém deixar de seguir seu perfil :D')


def desativar(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Notificações cancelada!' if job_removed else 'Você não ativou as notificações!'
    update.message.reply_text(text)

#funções handler para efetuar o login ########
def login(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Para continuar faça login com sua conta Instagram!')
    update.message.reply_text('Usuário:')

    return USER


def usuario(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id 
    user_profiles[chat_id] = []
    user_profiles[chat_id].append(str(update.message.text)) 
    update.message.reply_text('Senha:')

    return PASS


def senha(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Aguarde...')
    chat_id = update.message.chat_id
    user_profiles[chat_id].append(str(update.message.text)) 
    base = []
    user_profiles[chat_id].append(base)

    try:
        L.login(user_profiles[chat_id][0], user_profiles[chat_id][1])  # (login)
        user_profiles[chat_id].append(instaloader.Profile.from_username(L.context, user_profiles[chat_id][0]))
        update.message.reply_text('logado com sucesso!')
        update.message.reply_text('Use o comando /notificar para receber avisos quando alguém deixa de te seguir.')
        update.message.reply_text('Ou use o comando /nao_seguidores para ter a lista dos perfis que não te seguem de volta')
    except instaloader.exceptions.BadCredentialsException:
        update.message.reply_text('Erro ao efetuar login!')
        update.message.reply_text('Usuário ou senha inválido')
        update.message.reply_text('Use o comando /login para tentar novamente.')
    except instaloader.exceptions.ConnectionException:
        update.message.reply_text('Erro de conexão, tente novamente usando o comando /login')
    except instaloader.exceptions.InvalidArgumentException:
        update.messsage.reply_text('Erro, caracteres invalidos!')

    print(user_profiles)

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:

    return ConversationHandler.END


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("YOUR_TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("nao_seguidores", nao_seguidores))
    dispatcher.add_handler(CommandHandler("ajuda", start))
    dispatcher.add_handler(CommandHandler("notificar", notificar))
    dispatcher.add_handler(CommandHandler("desativar", desativar))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('login', login)],
        states={
            USER: [MessageHandler(Filters.text, usuario)],
            PASS: [MessageHandler(Filters.text, senha)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
