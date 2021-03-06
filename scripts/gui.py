#!/usr/bin/env python3

from lib.errors import ErrorManager
import check_topics
import update_guilds
import tkinter as tk


def main():
	root = tk.Tk()
	GuildManager(root).pack(side="top", fill="both", expand=True)
	root.mainloop()


class GuildManager(tk.Frame):
	def __init__(self, root, *args, **kwargs):
		super().__init__(root, *args, **kwargs)
		self.root = root
		self.configure()
		self.createWidgets()
		self.packWidgets()

	def configure(self):
		self.root.resizable(0, 0)
		self.root.title("Guild Manager")

	def createWidgets(self):
		self.btn_check_topics = tk.Button(self,
			text="Обработать заявки", command=check_topics.main, height=2)
		self.btn_update_guilds = tk.Button(self,
			text="Обновить страницы гильдий", command=update_guilds.main, height=2)

	def packWidgets(self):
		self.btn_check_topics.pack(side="top", fill="x")
		self.btn_update_guilds.pack(side="top", fill="x")


if __name__ == "__main__":
	with ErrorManager("GUI"):
		main()
