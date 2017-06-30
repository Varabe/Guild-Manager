# -*- coding: utf-8 -*-

"""
Эта библиотека содержит набор средств для упрощённой работы с гильдменеджером
"""

from vk.exceptions import VkAPIError
from vk import Session, API

from os.path import realpath
from os import chdir

from lib.config import my_id, group_id, sleep_time, token_path, database_path
from lib.database import Database
from traceback import format_exc
from time import sleep


class ErrorManager:
	def __init__(self, name):
		self.name = name

	def __enter__(self):
		pass

	def __exit__(self, *args):
		if args[0] is not None:
			exception = format_exc()
			message = "{}:\n{}".format(self.name, exception)
			api.messages.send(user_id=my_id, message=message)


def getApi():
	""" Логинится в вк и возвращает готовую к работе сессию """
	with open(token_path) as token:
		token = token.read()
		token.rstrip()
		session = Session(access_token=token)
		api = API(session, v='5.52', lang='ru')
		return api


def getToken():
	""" Создает токен для заданного приложения """
	import webbrowser as wb
	client_id = str(5747467)    # Id приложения
	scope = str(2047391)        # Код доступа, который мы запрашиваем
	other_stuff = "display=page&redirect_uri=http://vk.com&response_type=token&v=5.60"
	url = "https://oauth.vk.com/authorize?"
	url += "client_id={}&{}&scope={}".format(
		client_id, other_stuff, scope)
	wb.open(url, new=2)


def vkCap(method, **kwargs):
	""" Не позволяет программе вылететь, когда вк просит ввести капчу """
	try:
		sleep(sleep_time)
		return method(**kwargs)
	except VkAPIError:
		sleep(10)
		return vkCap(method, **kwargs)


def getBanned():
	bans = api.groups.getBanned(group_id=group_id)['items']
	banned = [user['id'] for user in bans]
	return banned


def setCurrentDirectory():
	path = realpath(__file__)
	index = path.index("/lib") - 1
	path = path[:index]
	chdir(path)


setCurrentDirectory()
api = getApi()
database = Database(database_path)
