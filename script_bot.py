import requests
from initial_data import *
from commands import *
import vk_api as api, vk_api.bot_longpoll as api_bot
from pprint import pprint as pp
from politeh import *
import datetime

current_group = None

class IncorrectGroupError(Exception):
	def __init__(self, correctness):
		super().__init__()
		self.correctness = correctness


def parse_user_msg(msg):
	try:
		if msg.startswith('команды'):
			if msg == 'команды':
				return help_command, None
			else:
				command = msg.split(maxsplit=1)[1]
				if command in COMMANDS:
					return help_command, command, None
				else:
					return None, None, 'Такой команды ({}) не существует.\
					Наберите "команды" для вызова помощи.'.format(command)



		stud_group, command = msg.split(maxsplit=1)

		
		global current_group
		current_group = StudentsGroup(string_name=stud_group)
		group_correctness = is_group_correct(current_group)
		
		if group_correctness != 'correct':
			raise IncorrectGroupError(group_correctness)

		if command.startswith('на указ неделю'):
			date_str = msg.split('на указ неделю ', maxsplit=1)[1]
			separator = ''
			
			for poss_separator in POSSIBLE_DATE_SEPARATORS:
				if poss_separator in date_str:
					separator = poss_separator
					break				
			
			if separator:
				try:
					day_in_week = datetime.datetime.strptime(date_str, 	'%d{0}%m{0}%Y'.format(separator))
					return specified_week, day_in_week, None
				except ValueError:
					pass
			
			return None, None, 'Неверно введена дата ({}). Попробуйте еще раз.'.format(date_str)
		
		pp(COMMANDS.keys())
		print(command)
		command_list = COMMANDS[command]
		handler = command_list[0]

		print(current_group.name, command, group_correctness, handler, sep='|')

		return handler, None, None

	except KeyError as e:
		print(1, e)
		return None, None, 'Команды "{}" не существует. Наберите "команды" для помощи'.format(command)
	except (IndexError, ValueError) as e:
		print(2, e)
		return None, None, 'Неверный формат команды. Наберите "команды" для помощи'
	except IncorrectGroupError as e:
		print(3)
		if e.correctness == 'many_variants':
			err_msg = 'По введённому запросу ({}) нашлось слишком много групп. Уточните, пожалуйста.'.format(stud_group)
		elif e.correctness == 'not_exist':
			err_msg = 'Группа "{}" не существует.'.format(stud_group)
		else:
			raise ValueError("Incorrect value returned from 'is_group_correct'")

		return None, None, err_msg

def use_longpoll(longpoll, vk):
	for event in longpoll.listen():
		if event.type == api_bot.VkBotEventType.MESSAGE_NEW:
			msg = event.object.text
			command_handler, argument, err_msg = parse_user_msg(msg)
			# print("Ошибка:", err_msg)

			if err_msg is None:
				print(command_handler, current_group, argument)
				message_text = command_handler(current_group, argument)
				vk.messages.send(
					user_id=event.object.from_id,
					message=message_text,
					random_id=event.object.random_id
				)
			else:
				# print(event)
				vk.messages.send(
					user_id=event.object.from_id,
					message=err_msg,
					random_id=event.object.random_id
				)


if __name__ == '__main__':
	vk_session = api.VkApi(token=TOKEN)
	vk = vk_session.get_api()
	longpoll = api_bot.VkBotLongPoll(vk_session, GROUP_ID)

	print('start')
	use_longpoll(longpoll, vk)


