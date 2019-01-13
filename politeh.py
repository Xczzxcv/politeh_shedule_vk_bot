import requests
from bs4 import BeautifulSoup
from pprint import pprint as pp
import datetime

class StudentsGroup:
	def __init__(self, faculty_id=None, group_id=None, string_name=None):
		self.faculty_id = faculty_id
		self.group_id = group_id
		self.name = string_name

	def __str__(self):
		return self.name

	def __repr__(self):
		return "StudentsGroup object: {}({}, {})".format(self.name, self.faculty_id, self.group_id)

class Lesson:
	def __init__(self, subject_name='', time='', les_type='', groups=[], teachers=[], places=[]):
		self.subject_name = subject_name
		self.time = time
		self.les_type = les_type
		self.groups = groups
		self.teachers = teachers
		self.places = places

	def __str__(self):
		return '{} {}\n{} {}\n{} {}'.format(
			self.time, self.subject_name,\
			self.les_type, ', '.join(self.teachers),\
			', '.join([str(group) for group in self.groups]), ', '.join(self.places)
			)

	def __repr__(self):
		return 'Lesson object: ' + self.__str__()

class DayShedule:
	def __init__(self, day_string, lessons=[]):
		self.day = day_string
		self.lessons = lessons

	def __str__(self):
		return self.day + '\n' + '\n\n'.join([str(lesson) for lesson in self.lessons])

class WeekShedule:
	def __init__(self, day_in_week, days_shedules_list=[]):
		weekday = day_in_week.weekday()
		self.monday = day_in_week - datetime.timedelta(days=weekday)
		self.sunday = day_in_week + datetime.timedelta(days=6-weekday)
		self.days_shedules_list = days_shedules_list

	def __str__(self):
		return 'Расписание на неделю {}—{}:\n{}'.format(
			self.monday.strftime('%d.%m.%Y'),
			self.sunday.strftime('%d.%m.%Y'),
			'\n\n'.join([str(day_shedule) for day_shedule in self.days_shedules_list])
		)

MONTHS = [ "январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]
WEEKDAYS = [ "пн", "вт", "ср", "чт", "пт", "сб", "вс"]

def parse_group_a_elt(a_elt, group_to_enter):
	if not (group_to_enter.faculty_id and group_to_enter.group_id): 
		url_list = a_elt['href'].split('/')
		group_to_enter.faculty_id = url_list[2]
		group_to_enter.group_id = url_list[4]
	if not group_to_enter.name:
		group_to_enter.name = a_elt.contents[0]

def parse_day(day_elt):
	pp(day_elt)
	day_shedule = DayShedule(day_elt.div.contents[0], lessons=[])	
	lessons_list = day_elt.ul.contents
	# day_shedule.lessons.extend(
	# 	[parse_lesson(lesson) for lesson in lessons_list]
	# 	)
	for lesson in lessons_list:
		lesson_obj = parse_lesson(lesson)
		# print("(parse_day):\n", lesson_obj)
		day_shedule.lessons.append(lesson_obj)
	# print(day_shedule)
	return day_shedule

def parse_lesson(lesson_elt):
	lesson = Lesson(teachers=[], places=[], groups=[])
	
	try:
		lesson_title = lesson_elt.find('div', 'lesson__subject')
		lesson.subject_name = lesson_title.contents[-1].contents[0]
		lesson.time = ''.join([span.contents[0] for span in lesson_title.find('span', 'lesson__time').contents])
	except AttributeError:
		pass
	
	try:
		lesson_params = lesson_elt.find('div', 'lesson__params')
		
		try:
			lesson.les_type = lesson_params.find('div', 'lesson__type').contents[0]
		except AttributeError:
			pass
	
		try:
			lesson_groups_elt_list = lesson_params.contents[1].find('div', 'lesson-groups__list').contents[1:]
			for group_elt in lesson_groups_elt_list:
				curr_group = StudentsGroup()
				parse_group_a_elt(group_elt.a, curr_group)
				lesson.groups.append(curr_group)
		except AttributeError:
			pass
	
		try:
			lesson_teachers_elt_list = lesson_params.find('div', 'lesson__teachers').contents
			for teacher_elt in lesson_teachers_elt_list:
				teacher_name = teacher_elt.a.contents[-1].contents[0]
				# print(teacher_name)
				lesson.teachers.append(teacher_name)
		except AttributeError:
			pass
	
		try:
			lesson_places_elt_list = lesson_params.find('div', 'lesson__places').contents
			for place_elt in lesson_places_elt_list:
				building_place_name = place_elt.a.contents[0].contents[0].contents[0]
				auditorium_place_name = ''.join([elt.contents[0] for elt in place_elt.a.contents[1].contents])
				lesson.places.append('{}, {}'.format(building_place_name, auditorium_place_name))
		except AttributeError:
			pass
	
	except AttributeError:
		pass
	# print("(parse_lesson):\n", lesson)

	return lesson

def get_week_shedule_list(weekday_datetime, group):
	day_string = weekday_datetime.strftime('%Y-%m-%d')
	request_url = 'https://ruz.spbstu.ru/faculty/{}/groups/{}?date={}'.format(
		group.faculty_id, group.group_id, day_string)
	response = requests.get(request_url)

	print("url", request_url)
	soap = BeautifulSoup(response.text, 'lxml')
	try:
		schedule = soap.find('ul', 'schedule')
		school_days_list = schedule.contents
	except Exception:
		school_days_list =  []
	return school_days_list

def get_weekday_num(ru_weekday_string):
	for weekday_num, weekday_string in enumerate(WEEKDAYS):
		if ru_weekday_string == weekday_string:
			return weekday_num

def is_group_correct(group):
	request_url = 'https://ruz.spbstu.ru/search/groups?q={}'.format(group.name)
	response = requests.get(request_url)
	soap = BeautifulSoup(response.text, 'lxml')
	group_list = soap.find('ul', 'groups-list')

	if group_list is None:
		correctness = 'not_exist'
	elif len(group_list) == 1:
		parse_group_a_elt(group_list.li.a, group)
		# print(url_list)
		correctness = 'correct'
	elif len(group_list) > 1:
		correctness = 'many_variants'

	return correctness

def get_next_school_day(today_datetime, group):
	school_days_list = get_week_shedule_list(today_datetime, group)
	# print("(g_n_s_d) s_d_l:", school_days_list)
	if school_days_list:
		# print(response.text)
		# print(day_string)
		# pp(school_days_list)
		last_day_elt = school_days_list[-1]
		last_weekday_str = last_day_elt.div.contents[0][-2:]
		print("last weekday:", last_weekday_str)
		# print("last_day_elt:", last_day_elt)

	if not school_days_list or (today_datetime.weekday() > get_weekday_num(last_weekday_str)):
		# if there is no more learning this week
		# than we need look for appropriate day next week
		while True:
			next_week = today_datetime + datetime.timedelta(weeks=1)
			school_days_list = get_week_shedule_list(next_week, group)
			# print(school_days_list)
			if school_days_list:
				first_day_elt = school_days_list[0]
				day_shedule = parse_day(first_day_elt)
				return day_shedule
	else:
		day_shedule = parse_day(last_day_elt)
		return day_shedule

def get_week(day_in_week, group):
	print('(g_w):', day_in_week, group)
	week_shedule = WeekShedule(day_in_week)
	schoold_days_elts = get_week_shedule_list(day_in_week, group)
	week_shedule.days_shedules_list.extend(
		[parse_day(day) for day in schoold_days_elts]
		)
	return week_shedule
	