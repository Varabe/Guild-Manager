#!/usr/bin/env python3

from lib.commands import error
from shutil import copyfile
from time import strftime


def backup():
	title = strftime("database_backups/%d.%m.%Y.xml")
	path = "../../Data/"
	copyfile(path + "database.xml", path + title)


if __name__ == "__main__":
	try:
		backup()
	except:
		error("backup")
