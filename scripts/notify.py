#!/usr/bin/env python3

from lib.config import aottg_main, sleep_time
from lib.commands import api, ban_list
from lib.errors import ErrorManager
from time import sleep


def notify(test=False):
	""" Оповещает игроков о начале сервера или еженедельника """
	message = getMessage(test)
	users = getEweekPlayers()
	users = {user for user in users if user not in ban_list}
	sendMessages(users, message)


def getMessage(test):
	if test:
		message = "Тест"
	else:
		message = "Еженедельник начался, а ты как раз записался. Приходи, если ещё не сдал!\n"
		warning = "\n(Это автоматическое сообщение. Отвечать на него не нужно.)"
		message += warning
	return message


def getEweekPlayers():
	post = api.wall.search(owner_id=-aottg_main, query="#aottg83_reg", count=1)
	post_id = post['items'][0]['id']
	comments = api.wall.getComments(
		owner_id=-aottg_main, post_id=post_id, count=30)['items']
	users = {comment['from_id'] for comment in comments}
	return users


def sendMessages(users, message):
	""" int[] users, str message """
	for user in users:
		sleep(sleep_time)
		try:
			api.messages.send(user_id=user, message=message)
		except:
			pass


if __name__ == "__main__":
	with ErrorManager("notify"):
		notify()
