import os
import logging
from typing import List, Dict
import urllib.request, json

from config import config

logger = logging.getLogger('adventures')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=config.settings['adventure_log_path'], encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


def get_adventures() -> List[str]:
    adventure_list = []
    for filename in os.listdir(config.settings['adventure_path']):
        if filename.endswith(".adv"):
            adventure_list.append(filename.split('.')[0])
    return adventure_list


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


def save_adventure(name: str, adventure: Dict):
    with open("{}{}.adv".format(config.settings['adventure_path'], name), "w") as outfile:
        json.dump(adventure, outfile)


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
