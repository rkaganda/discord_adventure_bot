import os
import logging
from typing import List, Dict
import urllib.request, json

from config import config
from src import db

logger = logging.getLogger('adventures')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=config.settings['adventure_log_path'], encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


def do_text_branch(user: Dict, branch: Dict) -> str:
    message = "{} ".format(branch['text'])
    if 'choices' in branch:
        choices_text = ["{}".format(k) for k in branch['choices'].keys()]
        message = "{} ({})".format(message, ", ".join(map(str, choices_text)))
    else:
        message = "{} The End.".format(message)
        user['current_adventure'] = None
        user['current_branch'] = None
        db.update_user(user)

    return message


def do_branch(user: Dict) -> str:
    message = " you are not on an adventure."
    branch_types = {
        'text_branch': do_text_branch
    }
    branch = get_user_current_branch(user)
    print(branch)
    if branch is not None:
        message = branch_types[branch['type']](user=user, branch=branch)

    return message


def do_choice(user: Dict, choice: str):
    branch = get_user_current_branch(user)
    branch_choice = branch['choices'][choice]
    user['current_branch'] = branch_choice['next_branch']
    db.update_user(user)

    return do_branch(user)


def get_user_current_branch(user: Dict) -> Dict:
    current_branch = None
    if user['current_adventure'] is not None:
        adventure = load_adventure(user['current_adventure'])
        if adventure is not None:
            current_branch = adventure[user['current_branch']]
    return current_branch


def get_user_choices(user: Dict) -> List:
    choices = []
    if user['current_adventure'] is not None:
        branch = get_user_current_branch(user)
        choices = ["{}".format(k) for k in branch['choices'].keys()]
    return choices


def get_adventures() -> List[str]:
    adventure_list = []
    for filename in os.listdir(config.settings['adventure_path']):
        if filename.endswith(".adv"):
            adventure_list.append(filename.split('.')[0])
    return adventure_list


def start_adventure(user: Dict, adventure_name: str) -> str:
    user['current_adventure'] = adventure_name
    user['current_branch'] = 'start'
    db.update_user(user)

    return do_branch(user)


def load_adventure(adventure_name: str) -> Dict:
    try:
        with open("{}{}.adv".format(config.settings['adventure_path'], adventure_name), "r") as infile:
            return json.load(infile)
    except Exception as e:
        logger.exception(e)
        raise e


def save_adventure(name: str, adventure: Dict):
    with open("{}{}.adv".format(config.settings['adventure_path'], name), "w") as outfile:
        json.dump(adventure, outfile)


def add_adventure(filename: str, url: str):
    try:
        current_adventures = get_adventures()
        adventure_name = filename.split('.')[0]
        if filename.split('.')[-1] == 'json':  # if json file
            if adventure_name not in current_adventures:  # if no adventure with that name
                save_adventure(name=adventure_name, adventure=download_adventure(url))
                return "{} is added to adventures.".format(adventure_name)
            else:
                return "{} is already an adventure".format(adventure_name)
        return
    except Exception as e:
        logger.exception(e)
        raise e


def download_adventure(url_str: str):
    adventure = {}
    req = urllib.request.Request(
        url_str,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    with urllib.request.urlopen(req) as url:
        data = url.read().decode()
        adventure = json.loads(data)
    return adventure
