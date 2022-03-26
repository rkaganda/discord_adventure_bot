import discord
import logging
from typing import Dict

from config import config
from src import db
from src import adventures

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=config.settings['discord_log_path'], encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = discord.Client()


def print_help(message, user: Dict) -> str:
    message = ["{} {}. ".format(k, bot_commands[k]['desc']) for k in bot_commands.keys()]
    return " ".join(message)


def do_new_command(message, user: Dict):
    response_message = ""
    adventure_names = adventures.get_adventures()
    if user['current_adventure'] is not None:  # if user is already on an adventure
        response_message = "you are already on an adventure."
    elif len(message.content.split(' ')) < 2:  # if no new adventure was chosen
        if len(adventure_names) > 0:
            response_message = "type $start and then the name of the adventure you want to start ({}).".format(
                ", ".join(map(str, adventure_names)))
        else:
            response_message = " there are no adventures at this time."
    else:
        adventure_name = message.content.split(' ')[1]
        if adventure_name in adventure_names:
            response_message = adventures.start_adventure(user, adventure_name)
        else:
            response_message = "there is no adventure called {}.".format(adventure_name)
    return response_message


def print_branch(message, user: Dict) -> str:
    return adventures.do_branch(user=user)


def add_adventure(message, user: Dict) -> str:
    response_message = "something went wrong."
    if user['name'] != 'runningshoes/ruku#3087':  # hacky AF
        return ""

    current_adventures = adventures.get_adventures()
    logger.debug("current_adventures = {}".format(current_adventures))
    if len(message.attachments) > 1:
        response_message = "I only add one adventure at a time."
    elif len(message.attachments) > 0:
        attachment = message.attachments[0]
        response_message = adventures.add_adventure(attachment.filename, attachment.url)
    return response_message


def end_adventure(message, user: Dict) -> str:
    return adventures.end_adventure(user=user)


bot_commands = {
            '$help': {"function": print_help, "desc": " to see available commands"},
            '$start': {"function": do_new_command, "desc": " to start a new adventure"},
            '$choices': {"function": print_branch, "desc": " to where you are in your adventure"},
            '$end': {"function": end_adventure, "desc": " to end your current adventure"},
            '$add': {"function": add_adventure, "desc": " to add a new adventure"},
        }


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    try:
        # if this is the bot
        if message.author == client.user:
            return

        bot_command = message.content.split(' ')[0]
        user = db.get_discord_user("{}#{}".format(message.author.name, message.author.discriminator))
        adventure_choices = adventures.get_user_choices(user)

        if message.content in adventure_choices:
            await message.channel.send(
                "{} {}".format(message.author.mention, adventures.do_choice(user=user, choice=message.content)))
        # if the message is a bot command
        elif bot_command in bot_commands.keys():
            # call the function
            await message.channel.send("{} {}".format(
                message.author.mention, bot_commands[bot_command]['function'](message, user)))
        else:
            await message.channel.send("{} type $help for commands".format(message.author.mention))
    except Exception as e:
        logger.exception(e)
        raise e


client.run(config.settings['discord_bot_token'])
