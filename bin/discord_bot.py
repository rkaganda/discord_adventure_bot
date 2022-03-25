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
    return "$new to start a new adventure, $last to see the last message/choice of your adventure".format(
        message.author)


def new_adventure(message, user: Dict) -> str:
    return "There are no adventures to be had at the moment."


def print_branch(message, user: Dict) -> str:
    return "You are not currently on an adventure."


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


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    try:
        logger.debug(message)
        bot_commands = {
            '$help': print_help,
            '$new': new_adventure,
            '$last': print_branch,
            '$add': add_adventure
        }

        # if this is the bot
        if message.author == client.user:
            return
        # if the message is a bot command
        elif message.content in bot_commands.keys():
            # get the user
            user = db.get_discord_user("{}#{}".format(message.author.name, message.author.discriminator))
            # call the function
            await message.channel.send("@{} {}".format(message.author, bot_commands[message.content](message, user)))
        else:
            await message.channel.send("@{} type $help for commands".format(message.author))
    except Exception as e:
        logger.exception(e)
        raise e


client.run(config.settings['discord_bot_token'])
