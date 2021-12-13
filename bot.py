#!/usr/bin/env python
# pylint: disable=C0116,W0613

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import L, BOT_TOKEN, user_profiles, USER, PASS
from instaunfollow import dont_followers, update_followers



def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id 
    if chat_id not in user_profiles:
        user_profiles[chat_id] = {'usuario' : None, 'senha' : None, 'base' : None, 'profile_data' : None}
        update.message.reply_text('Olá, use /login para efetuar login com sua conta do Instagram e poder usar as outras funções')
    else:
        if user_profiles[chat_id].get('profile_data') == None:
            update.message.reply_text('Use /login para efetuar login com sua conta do Instagram')
        else:
            update.message.reply_text('Bem vindo de volta! use /buscar_nao_seguidores para saber quais os perfis que não te seguem de volta')
            update.message.reply_text('Use /login para saber quais os perfis que não te seguem de volta')
            update.message.reply_text('Use /buscar_nao_seguidores para saber quais os perfis que não te seguem de volta')
            update.message.reply_text('Use /notificar para ativar avisos quando algum perfil deixar de te seguir')
            update.message.reply_text('Use /desativar para desativar avisos')
            update.message.reply_text('Use /sair para sair de sua conta e apagar os dados inseridos')


def seek_nonfollowers(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    if user_profiles[chat_id].get('profile_data') == None:
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
    if user_profiles[chat_id].get('profile_data') == None:
        update.message.reply_text('Primeiro faça login pelo comando /login')
    else:
        context.job_queue.run_once(notify_nonfollowers, due_time, context=chat_id, name=str(chat_id))
        update.message.reply_text('Notificações ativadas!')
        update.message.reply_text('Irei notificar quando alguém deixar de seguir seu perfil :D')
        update.message.reply_text('Use o comando /desativar para desativar as notificações')


def notify_nonfollowers(context: CallbackContext) -> None:
    due_time = 3600 #tempo em segundos
    chat_id = context.job
    profile_unfollowed = update_followers(chat_id.context)
    if len(profile_unfollowed) == 0:
        context.job_queue.run_once(notify_nonfollowers, due_time, context=chat_id.context, name=str(chat_id.context))
    else:
        for profile in profile_unfollowed:
            context.bot.send_message(chat_id.context, text="Alguém deixou de te seguir!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='@{}'.format(profile), url='https://instagram.com/{}'.format(profile))]
                ])
            )

        context.job_queue.run_once(notify_nonfollowers, due_time, context=chat_id.context, name=str(chat_id.context))


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
    chat_id = update.message.chat_id 
    logged = ConversationHandler.END
    not_logged = USER
    if chat_id in user_profiles:
        if user_profiles[chat_id].get('profile_data') != None:
            update.message.reply_text('Você ja está logado, use o comando /sair para sair de sua conta') 
            new_step = logged
        else:
            update.message.reply_text('Para continuar faça login com sua conta Instagram!')
            update.message.reply_text('Usuário:')
            new_step = not_logged
    else:
        user_profiles[chat_id] = {'usuario' : None, 'senha' : None, 'base' : None, 'profile_data' : None}
        update.message.reply_text('Para continuar faça login com sua conta Instagram!')
        update.message.reply_text('Usuário:')
        new_step = not_logged

    return new_step


def get_insta_user(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id  
    user_profiles[chat_id].update({'usuario' : str(update.message.text)})
    update.message.reply_text('Senha:')
        
    return PASS


def get_insta_password(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Aguarde...')
    chat_id = update.message.chat_id
    user_profiles[chat_id].update({'senha' : str(update.message.text)}) 

    try:
        L.login(user_profiles[chat_id].get('usuario'), user_profiles[chat_id].get('senha'))
        user_profiles[chat_id].update({'profile_data' : instaloader.Profile.from_username(L.context, user_profiles[chat_id].get('usuario'))})
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
        update.message.reply_text('Erro, caracteres invalidos, tente novamente usando o comando /login')

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:

    return ConversationHandler.END


def get_out(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if chat_id in user_profiles:
        del user_profiles[chat_id]
        update.message.reply_text('Você saiu, para efetuar login novamente use /login')
    else:
        update.message.reply_text('Você não está logado.')


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("buscar_nao_seguidores", seek_nonfollowers))
    dispatcher.add_handler(CommandHandler("ajuda", start))
    dispatcher.add_handler(CommandHandler("notificar", activate_notifications))
    dispatcher.add_handler(CommandHandler("desativar", disable_notifications))
    dispatcher.add_handler(CommandHandler("sair", get_out))

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
