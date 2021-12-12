#!/usr/bin/env python
# pylint: disable=C0116,W0613

import instaloader
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


USER, PASS = range(2)

L = instaloader.Instaloader()

user_profiles = {}

def dont_followers(chat_id):
    profile_list_dont_followers = []
    followers = []
    following = []

    for follower in user_profiles[chat_id][3].get_followers():
        followers.append(follower.username)

    for followees in user_profiles[chat_id][3].get_followees():
        following.append(followees.username)

    for profile in following:
        if profile not in followers:
            profile_list_dont_followers.append(profile)

    return profile_list_dont_followers


def update_followers(chat_id):
    updated_dont_followers_base = []
    new_nonfollowers_base = []

    if len(user_profiles[chat_id][2]) != 0:
        updated_dont_followers_base = dont_followers(chat_id)

        for profile in updated_dont_followers_base:
            if profile not in user_profiles[chat_id][2]:
                new_nonfollowers_base.append(profile)

        user_profiles[chat_id][2] = updated_dont_followers_base
    else:
        user_profiles[chat_id][2] = dont_followers(chat_id)

    return new_nonfollowers_base


def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id 
    user_profiles[chat_id] = []
    update.message.reply_text('Olá, use /login para efetuar login com sua conta do Instagram e poder usar as outras funções')


def seek_nonfollowers(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    if len(user_profiles[chat_id]) < 4:
        update.message.reply_text('Primeiro faça login pelo comando /login')
    else:
        update.message.reply_text('Buscando perfis que não te seguem...')
        profile_list = dont_followers(chat_id)
        for profile in profile_list:
            context.bot.send_message(chat_id, text="Perfil @{}".format(profile),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='@{}'.format(profile), url='https://instagram.com/{}'.format(profile))]
                    ])
                )


def activate_notifications(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    due_time = 3600
    if len(user_profiles[chat_id]) < 4:
        update.message.reply_text('Primeiro faça login pelo comando /login')
    else:
        context.job_queue.run_once(notify_nonfollowers, due_time, context=chat_id, name=str(chat_id))
        update.message.reply_text('Notificações ativadas!')
        update.message.reply_text('Irei notificar quando alguém deixar de seguir seu perfil :D')
        update.message.reply_text('Use o comando /desativar para desativar as notificações')


def notify_nonfollowers(context: CallbackContext) -> None:
    due_time = 3600 #tempo em segundos
    chat_id = context.job
    profile_unfollowed = update_followers(chat_id)

    if len(profile_unfollowed) == 0:
        context.job_queue.run_once(notify_nonfollowers, due_time, context=chat_id, name=str(chat_id))
    else:
        for profile in profile_unfollowed:
            context.bot.send_message(chat_id, text="Alguém deixou de te seguir!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='@{}'.format(profile), url='https://instagram.com/{}'.format(profile))]
                ])
            )

        context.job_queue.run_once(notify_nonfollowers, due_time, context=chat_id, name=str(chat_id))


def disable_notifications(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    job_removed = remove_job_notify_if_exists(str(chat_id), context)
    text = 'Notificações cancelada!' if job_removed else 'Você não ativou as notificações!'
    update.message.reply_text(text)


def remove_job_notify_if_exists(name: str, context: CallbackContext) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def login(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Para continuar faça login com sua conta Instagram!')
    update.message.reply_text('Usuário:')

    return USER


def get_insta_user(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id 
    user_profiles[chat_id].append(str(update.message.text)) 
    update.message.reply_text('Senha:')

    return PASS


def get_insta_password(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Aguarde...')
    chat_id = update.message.chat_id
    user_profiles[chat_id].append(str(update.message.text)) 
    initial_profile_base = []
    user_profiles[chat_id].append(initial_profile_base)

    try:
        L.login(user_profiles[chat_id][0], user_profiles[chat_id][1])
        user_profiles[chat_id].append(instaloader.Profile.from_username(L.context, user_profiles[chat_id][0]))
        update.message.reply_text('logado com sucesso!')
        update.message.reply_text('Use o comando /notificar para receber avisos quando alguém deixa de te seguir.')
        update.message.reply_text('Ou use o comando /buscar_nao_seguidores para ter a lista dos perfis que não te seguem de volta')
    except instaloader.exceptions.BadCredentialsException:
        update.message.reply_text('Erro ao efetuar login!')
        update.message.reply_text('Usuário ou senha inválido')
        update.message.reply_text('Use o comando /login para tentar novamente.')
    except instaloader.exceptions.ConnectionException:
        update.message.reply_text('Erro de conexão, tente novamente usando o comando /login')
    except instaloader.exceptions.InvalidArgumentException:
        update.messsage.reply_text('Erro, caracteres invalidos!')

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:

    return ConversationHandler.END


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("5092523690:AAEbg_vnj_buFJkxr140dMQ4_RVc7NisBK8")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("buscar_nao_seguidores", seek_nonfollowers))
    dispatcher.add_handler(CommandHandler("ajuda", start))
    dispatcher.add_handler(CommandHandler("notificar", activate_notifications))
    dispatcher.add_handler(CommandHandler("desativar", disable_notifications))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('login', login)],
        states={
            USER: [MessageHandler(Filters.text, get_insta_user)],
            PASS: [MessageHandler(Filters.text, get_insta_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
