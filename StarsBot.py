#!/usr/bin/env python

import logging
import starserver
from telegram.ext import Updater, CommandHandler
from functools import wraps


#  TG TOKEN given by BotFather
tg_token = starserver.config['BOT']['TG TOKEN']

#  Group id for game events notification
group_id = starserver.config['BOT']['GROUP ID']

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

players = []
for player_n in range(1, 17):
    if starserver.config['PLAYER' + str(player_n)]['ROLE'].upper() == 'PLAYER':
        players.append([player_n,
                        starserver.config['PLAYER' + str(player_n)]['TG_ID'],
                        starserver.config['PLAYER' + str(player_n)]['TG_NAME']])

LIST_OF_ADMINS = []
for tg_id in players:
    LIST_OF_ADMINS.append(tg_id[1])


def restricted(func):
    """ This function restricts access to Bot commands not from players """
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped


@restricted
def command_list(update):
    """ List of Bot commands"""
    logger.info('User {} send command /help'.
                format(update.message.from_user.id))
    reply = """ List of commands:
    /help - this list
    /list - Notification of submitted turn player, will add @ in chat for personal notification
    /turn - Current year
    """
    update.message.reply_text(reply)


@restricted
def turn_list(update):
    """ Notification of submitted turn player, will add @ in chat for personal notification """
    logger.info('User {} send command /list'.
                format(update.message.from_user.id))

    answer = ""
    for player in players:
        if starserver.check_submitted(player[0]):
            answer += player[2]
            answer += " submitted turn\n"
        else:
            #  Notificate players not submitted turn
            answer += "@"
            answer += player[2]
            answer += " have not submitted turn\n"
    update.message.reply_text(answer)


@restricted
def turn(update):
    """ Will send current year """
    logger.info('User {} send command /turn'.
                format(update.message.from_user.id))
    answer = "Current year: "
    answer += str(starserver.config['GAME']['YEAR'])
    update.message.reply_text(answer)


def turn_load():
    """ For local tracking of new turn """
    f = open("last_turn", "r")
    last_turn = f.read()
    f.close()
    return int(last_turn)


def turn_save(last_turn):
    """ For local tracking of new turn """
    f = open("last_turn", "w")
    f.write("{:d}".format(last_turn))
    f.close()


#  Check if new turn have been made
def read_turn(context):
    current_turn = turn_load()
    new_turn = starserver.turn_year(starserver.config['PATHS']['CRADLE'] + starserver.config['GAME']['NAME'] + ".hst")
    if new_turn > current_turn:
        """ Message to group """
        context.bot.send_message(chat_id=group_id, text="New "+str(new_turn)+" year. New turn!")

        """ Message to users """
        for user in LIST_OF_ADMINS:
            context.bot.send_message(chat_id=user,
                                     text="New " + str(new_turn) + " year. New turn!")
        turn_save(new_turn)
        # TODO: Subscription mechanic for notification


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    updater = Updater(tg_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    j = updater.job_queue

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", command_list))
    dp.add_handler(CommandHandler("list", turn_list))
    dp.add_handler(CommandHandler("turn", turn))

    # Проверка раз в 10 секунд новых ходов
    j.run_repeating(read_turn,
                    interval=10,
                    first=0)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
