import datetime
from politeh import *

def next_school_day(group, excess=None):
	next_school_day_shedule = get_next_school_day(datetime.datetime.today(), group)
	return str(next_school_day_shedule)

def this_week(group, excess=None):
	week_shedule = get_week(datetime.datetime.today(), group)
	return str(week_shedule)

def next_week(group, excess=None):
	week_shedule = get_week(datetime.datetime.today() + datetime.timedelta(weeks=1), group)
	return str(week_shedule)

def specified_week(group, day_in_week):
	week_shedule = get_week(day_in_week, group)
	return str(week_shedule)

def help_command(excess_group=None, command=None):
	if command:
		return '{}:\n{}'.format(command, COMMANDS[command][1]) 
	else:
		return HELP_TEXT

POSSIBLE_DATE_SEPARATORS = ('\\', '/', '.', '-', '|', ':', '_', ' ')

COMMANDS = {
	'на след учебный день': [next_school_day, "Выводит расписание на следующий учебный день"],
	'на эту неделю': [this_week, "Выводит расписание на текущую неделю"],
	'на след неделю': [next_week, "Выводит расписание на следующую неделю"],
	'на указ неделю': [specified_week, "Выводит расписание на указанную неделю \
	(формат даты — день/месяц/год, \
	допускаются разделители: {})".format(
		"  ".join(["'" + elt + "'" for elt in POSSIBLE_DATE_SEPARATORS]))],
}

HELP_TEXT = """
Формат: номер_группы команда параметр команды (параметр есть только у команды 'на указ неделю').
Команды:\n{}""".format(
	'\n'.join(
		["{} — {}".format(val, key[1]) for val, key in COMMANDS.items()]
		)
	)