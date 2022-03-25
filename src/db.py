import sqlalchemy as sqla
from sqlalchemy import Column, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

import logging
from typing import Dict

from config import config

logger = logging.getLogger('db')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=config.settings['db_log_path'], encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

Base = declarative_base()


class DiscordUser(Base):
    __tablename__ = "discord_user"
    name = Column(String, primary_key=True)
    current_adventure = Column(String)
    current_branch = Column(String)
    adventure_state = Column(String)


def get_session() -> sessionmaker:
    engine = sqla.create_engine(f"sqlite:///{config.settings['db_path']}")
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

    return sessionmaker(engine)


def add_discord_user(name: str) -> Dict:
    session = get_session()

    with session() as session:
        discord_user = DiscordUser(name=name, current_adventure=None, current_branch=None, adventure_state=None)
        session.add(discord_user)
        session.commit()
        session.close()

    return get_discord_user(name)


def get_discord_user(name: str) -> Dict:
    session = get_session()

    with session() as session:
        discord_user = session.query(DiscordUser).where(DiscordUser.name == name).first()
        session.close()

    if discord_user is None:
        discord_user = add_discord_user(name=name)
    else:
        discord_user = discord_user.__dict__
        if '_sa_instance_state' in discord_user:  # remove orm stuff
            del discord_user['_sa_instance_state']

    return discord_user


def update_user(user: Dict):
    session = get_session()

    with session() as session:
        discord_user = session.query(DiscordUser).where(DiscordUser.name == user['name']).first()
        for key, value in user.items():
            setattr(discord_user, key, value)
        session.commit()
        session.close()







