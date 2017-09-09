""" Инструменты для работы с вики-страницами

	Обновление страниц осуществляется в четыре шага:
		Получение шаблона вики-страницы
		Получение атрибутов
		Внесение атрибутов в шаблон
		Сохранение вики-страницы
"""

from lib.config import group_id, my_id, achi_is_active, data_folder
from lib.guilds import Guild, Player, Avatar, Achi
from lib.commands import database, api, vk


class updateGuild:
	""" Обновляет вики-страницу гильдии """
	def __init__(self, guild_id):
		self.guild = Guild(guild_id)
		if self.guild.exists:
			self.xml = self.guild.xml_element
			self.preparePage()
			self.saveNewPage()

	def preparePage(self):
		self.template = getPageTemplate("guild.txt")
		self.attributes = self.makeAttributes()
		self.page = editPageTemplate(self.attributes, self.template)

	def saveNewPage(self):
		page_id = self.guild.get("page")
		saveWikiPage(self.page, page_id)

	def makeAttributes(self):
		attr = self.getAttributes()
		players = self.getPlayers()
		attr['head'] = self.getHead()
		attr['vice'] = self.getVice()
		attr['stats'] = self.getStats()
		attr['players'] = self.getPlayerList(players)
		attr['numberofplayers'] = len(players)
		if achi_is_active:
			attr['achi'] = self.getAchi()
		else:
			self.template = self.template.replace("[achi]", "")
		return attr

	def getAttributes(self):
		xml_fields = self.xml.iterchildren()
		attributes = {f.tag:f.text for f in xml_fields}
		return attributes

	def getPlayers(self):
		all_players = database.getAll("players")
		guild_id = self.guild.get('id')
		guild_players = []
		for player in all_players:
			if player.find("guild").text == guild_id:
				player_id = player.find("id").text
				guild_players.append(player_id)
		return [Player(p) for p in guild_players]

	def getHead(self):
		heads = self.guild.heads
		return self.makeFancyList(heads)

	def getVice(self):
		vices = self.guild.vices
		if len(vices):
			return self.makeFancyList(vices)
		else:
			self.removeViceField()

	def removeViceField(self):
		template = self.template.splitlines()
		template.pop(6)
		self.template = "\n".join(template)

	def makeFancyList(self, ids):
		""" Список замов или глав """
		players = [Player(p) for p in ids]
		formatted_list = []
		for player in players:
			name = player.get("name")
			id = player.get("id")
			hyperlink = "[[id{}|{}]]".format(id, name)
			formatted_list.append(hyperlink)
		return ", ".join(formatted_list)

	def getStats(self):
		""" Получение процента побед """
		wins = self.guild.get("wins")
		loses = self.guild.get("loses")
		wins, loses = int(wins), int(loses)
		if wins > 0:
			stats = (wins * 100) / (wins + loses)
		else:
			stats = 0
		return round(stats)

	def getPlayerList(self, players):
		""" Составляет список игроков для вики-страницы

			Можно просто забить. Лично я не хочу разбираться
			в том, как это работает. Сорян.
		"""
		player_list = "{|\n|-\n"
		new_row = "|-\n"
		avatars = []
		for index, player in enumerate(players):
			if len(avatars) == 4:
				player_list += new_row
				for a in avatars:
					player_list += a
				player_list += new_row
				avatars = []
			id, name = player.get("id"), player.get("name")
			string = "! <center>[[id{}|{}]]</center>\n".format(id, name)
			player_list += string
			avatar = Avatar(player.get("avatar"))
			photo = "| [[{}|125x125px;noborder;nolink| ]]\n".format(avatar)
			avatars.append(photo)
			if index == len(players) - 1:
				player_list += new_row
				for a in avatars:
					player_list += a
		return player_list

	def getAchi(self):
		""" Создает отображение списка ачей """
		guild_achi_keys = self.guild.get("achi").split(" ")
		page = "<br><center>'''[[page-64867627_49895049|Испытания]]'''</center>"
		for index, result in enumerate(guild_achi_keys):
			achi = Achi(id=index)
			name, icon, waves = achi.get("name", "icon", "waves")
			waves = waves.split(" ")
			wave = waves[result]
			title_line = "\n=={}==".format(name)
			icon_pic = "[[{}|125px;noborder| ]]".format(icon)
			wave_pic = "[[{}|400x70px;noborder;nolink| ]]".format(wave)
			main_line = "\n{}{}".format(icon_pic, wave_pic)
			page += title_line + main_line
		return page


class refreshGuilds:
	""" Обновляет страницу гильдий """
	def __init__(self):
		page_id = 47292063
		self.preparePage()
		saveWikiPage(self.page, page_id)

	def preparePage(self):
		self.template = getPageTemplate("all_guilds.txt")
		self.attributes = self.makeAttributes()
		self.page = editPageTemplate(self.attributes, self.template)

	def makeAttributes(self):
		attr = dict()
		attr['all_guilds'], count = self.getGuildList()
		attr['guildnumber'] = count
		attr['playernumber'] = self.getPlayerCount()
		return attr

	def getGuildList(self):
		guilds = database.getAll("guilds", "id")
		guilds = [Guild(g) for g in guilds]
		return self.makeFancyGuildList(guilds), len(guilds)

	def makeFancyGuildList(self, guilds):
		""" Создает список гильдий """
		page, id_line, guild_line = self.getGuildLineTemplates()
		total_waves = self.getTotalAmountOfWaves()
		self.makeGuildPercentages(guilds, total_waves)
		self.sortGuilds(guilds)
		for guild in guilds:
			page += id_line.format(guild.percent)
			banner = guild.get('banner')
			link = guild.get('page')
			page += guild_line.format(banner, link)
		page += "\n|}"
		return page

	def getGuildLineTemplates(self):
		""" Базовые шаблоны, которыми наполняется список гильдий """
		if achi_is_active:
			page = "{|\n|-\n!<center>Рейтинг</center>\n!<center>Гильдия</center>\n|-"
			id_line = "\n!<center>{}%</center>"
		else:
			page = "{|\n|-\n!<center>ID</center>\n!<center>Гильдия</center>\n|-"
			id_line = "\n!<center>{}</center>"
		guild_line = "\n|<center>[[{}|450px;noborder|page-64867627_{}]]</center>\n|-"
		return page, id_line, guild_line

	def getTotalAmountOfWaves(self):
		""" Получение всех волн всех ачей для подсчета прохождения """
		if achi_is_active:
			all_achi_waves = database.getAll("achis", "waves")
			all_achi_waves = [len(w.split(" ")) - 1 for w in all_achi_waves]
			return sum(all_achi_waves)

	def makeGuildPercentages(self, guilds, total_waves):
		""" Проценты прохождения ачей """
		for guild in guilds:
			if achi_is_active:
				achi_results = guild.get("achi").split(" ")
				achi_results = [int(r) for r in achi_results]
				complete_waves = sum(achi_results)
				percent = complete_waves / total_waves
				guild.percent = round(percent)
			else:
				guild.percent = int(guild.get("id"))

	def sortGuilds(self, guilds):
		""" Если ачи -- то наибольший рейтинг сверху
			Если нет ачей -- наименьший ID сверху """
		reverse = achi_is_active
		guilds.sort(key=lambda g: g.percent, reverse=reverse)

	def getPlayerCount(self):
		""" Возвращает только игроков с гильдией """
		all_players = database.getAll("players")
		counter = 0
		for player in all_players:
			if player.find("guild").text != "0":
				counter += 1
		return counter


def getPageTemplate(file_name):
	path = data_folder + "page_templates/" + file_name
	with open(path, encoding="UTF-8") as file:
		return file.read()


def editPageTemplate(attributes, template):
	""" Заменяет поля в шаблоне значениями атрибутов """
	for key, value in attributes.items():
		key = "[{}]".format(key)
		value = str(value)
		template = template.replace(key, value)
	return template


def saveWikiPage(page, page_id, group=group_id):
	vk(api.pages.save,
		suspend_time=1,
		text=page,
		user_id=my_id,
		page_id=page_id,
		group_id=group)
