# Telegram bot for croping videos https://t.me/mp4cut_bot
# Developer https://t.me/pyonic
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from pytube import YouTube
import telebot
from telebot import types
from flask import Flask, request
import os
import sqlite3
from orm import *
token = '<bot:token>'
# secret  = 'aolddfbubu'
# url = 'https://fsfwioeafwwef.pythonanywhere.com/'+secret

bot = telebot.TeleBot(token)
admin_id = '986769710'
translation = {
	'en' : {
		'saving' : 'Saving your video, please wait...',
		'timeline' : 'Send timeline separated by spaces, example: "1:12 2:30" - where 1:12 is start and 2:30 is end.',
		'wait' : 'Please wait, downloading the video...',
		'sorry' : 'Sorry, video size is very huge(',
		'cutting' : 'Cutting video, please wait...',
		'cutted' : 'Video successfully cutted, which type of file would you like to get?',
		'wrong' : 'Wrong timline, send corrent timeline like this: "1:12 2:13"',
		'cancel' : 'Cancel',
		'calceled' : 'Cutting video canceled.',
		'thanks' : 'Thank for using and choosing us,we wish you pleasant viewing!)',
		'order_active' : 'Please wait, you alrady have active orders...',
		'video' : 'Video',
		'gif' : 'GIF',
	},
	'ru' : {
		'saving' : 'Сохраняю видео, пожалуйста подождите...',
		'wait' : 'Сохраняю видео, пожалуйста подождите...',
		'sorry' : 'Простите, размер файла слишком большой(',
		'timeline' : 'Отправьте таймлайн разделенный пробелом, например: "1:12 2:30" - где 1:12 начало и 2:30 конец.',
		'cutting' : 'Обрезаю видео,пожалуйста подождите...',
		'cutted' : 'Видео успешно создано в каком виде вы хотите его получить?',
		'wrong' : 'Не верный таймлайн, отправьте верную как в примере: "1:12 2:13"',
		'cancel' : 'Отменить',
		'calceled' : 'Действия отменены.',
		'thanks' : 'Спасибо что выбрали нашего бот, приятного просмотра!)',
		'order_active' : 'Пожалуйста подождите, у вас уже есть активные задачи...',
		'video' : 'Видео',
		'gif' : 'GIF'
	}
}

language = types.ReplyKeyboardMarkup(True, True) 
language.row('English', 'Русский')

# bot.remove_webhook()
# bot.set_webhook(url=url)
# app = Flask(__name__)
def cut_video(video_url,start,end,filename):
	ffmpeg_extract_subclip(video_url, start,end, targetname=filename)
# @app.route('/'+secret, methods = ['POST'])
# def webhook():	
# 	update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
# 	bot.process_new_updates([update])
# 	return 'ok',200
@bot.message_handler(commands = ['start'])
def on_start(message):
	# print(message)
	uid = message.chat.id
	if user_exist(uid) == False:
		insert_user(uid)
	lang = bot.send_message(uid,'🇺🇸 Hi,please select your language\n🇷🇺 Привет, пожалуйста выберите язык.',reply_markup = language)
	bot.register_next_step_handler(lang, get_lang)
	# bot.send_message(uid,'🇺🇸 Hi, this bot can cut certain part of the video by timeline, send me video file or YouTube link to start\n🇷🇺 Привет, данный бот сможет сохранить определенный участок ролика по таймлайну, отправьте видео или YouTube ссылку что бы начать.')
def get_lang(message):
	if message.text == 'English':
		update_lang(message.chat.id, language = 'en')
		bot.send_message(message.chat.id,'Nice..! So, this bot can cut certain part of the video by timeline, send me video file or YouTube link to start')
	else:
		update_lang(message.chat.id, language = 'ru')
		bot.send_message(message.chat.id, 'Отлично...! Итак, данный бот сможет сохранить определенный участок ролика по таймлайну, отправьте видео или YouTube ссылку что бы начать.')
@bot.message_handler(content_types=['video'])
def send_text(message):
	uid = message.chat.id
	try:
		if user_ordered(uid) != True:
			user_made_order(uid)
			uid = message.chat.id
			bot.send_message(message.chat.id, translation[get_language(uid)[0][0]]['saving'])
			file_info = bot.get_file(message.video.file_id)

			downloaded_file = bot.download_file(file_info.file_path)

			src =  file_info.file_path
			video_url = 'videos/' + str(message.chat.id)+'-not_ready.mp4'
			with open(video_url, 'wb') as new_file:
				new_file.write(downloaded_file)

			timeline_start = bot.send_message(message.chat.id, translation[get_language(uid)[0][0]]['timeline'])
			bot.register_next_step_handler(timeline_start, get_start_timeline)
		else:
			bot.reply_to(message, translation[get_language(uid)[0][0]]['order_active'])
	except:
		order_completed(uid)
		pass
@bot.message_handler(commands = ['adv'])
def on_adv(message):
	if str(message.chat.id) == admin_id:
		adv_text = bot.send_message(message.chat.id, 'Отправьте текст сообщения')
		bot.register_next_step_handler(adv_text, get_adv)
def get_adv(message):
	sent_count = 0
	for user in get_users():
		try:
			bot.send_message(user[0], message.text)
			sent_count = sent_count + 1
		except:
			pass
	bot.send_message(admin_id, f'Could sent to {sent_count} users')
@bot.message_handler(commands = ['stat'])
def get_status(message):
	uid = message.chat.id
	user_count = get_users_count()
	bot.send_message(uid,f'Пользователей: {user_count}')
@bot.message_handler(content_types = ['text'])
def on_text(message):
	uid = message.chat.id
	try:
		if user_ordered(uid) != True:
			user_made_order(uid)
			link = message.text
			yt = YouTube(link)
			bot.send_message(message.chat.id, translation[get_language(uid)[0][0]]['wait'])
			video360 = yt.streams.filter(res="360p").first().filesize
			videoFull = yt.streams.get_highest_resolution().filesize
			accepted = True
			filename = str(uid)+'-not_ready.mp4'
			if videoFull < 100000000:
				yt.streams.get_highest_resolution().download('videos/', filename = filename)
			elif video360 < 100000000:
				yt.streams.filter(res="360p").first().download('videos/', filename = filename)
			else:
				bot.send_message(message.chat.id, translation[get_language(uid)[0][0]]['sorry'])
				order_completed(uid)
				accepted = False
			if accepted:
				timeline_start = bot.send_message(message.chat.id, translation[get_language(uid)[0][0]]['timeline'])
				bot.register_next_step_handler(timeline_start, get_start_timeline)
		else:
			bot.reply_to(message, translation[get_language(uid)[0][0]]['order_active'])
	except:
		lang = get_language(uid)[0][0]
		print(lang)
def get_start_timeline(message):
	uid = message.chat.id
	if message.text != "Cancel" or message.text != 'Отменить':
		cancel = types.ReplyKeyboardMarkup(True, True)
		cancel.row(translation[get_language(uid)[0][0]]['cancel'])
		try: 
			times = str(message.text).strip().split(' ')
			if len(times) == 2:
				#Start timeline
				timeline_start = str(times[0]).split(':')
				minutes = int(timeline_start[0])*60
				seconds = int(timeline_start[1])
				start_time = minutes + seconds
				#End timeline
				timeline_end = str(times[1]).split(':')
				minutes = int(timeline_end[0])*60
				seconds = int(timeline_end[1])
				end_time = minutes + seconds
				bot.send_message(message.chat.id, translation[get_language(uid)[0][0]]['cutting'])
				video_url = 'videos/' + str(message.chat.id)+'-not_ready.mp4'
				output = 'videos/' + str(message.chat.id)+'-ready.mp4'
				cut_video(video_url,start_time,end_time,output)
				menu = types.ReplyKeyboardMarkup(True, True)
				menu.row(translation[get_language(uid)[0][0]]['video'], translation[get_language(uid)[0][0]]['gif'])
				video_type = bot.send_message(message.chat.id, translation[get_language(uid)[0][0]]['cutted'], reply_markup = menu)
				bot.register_next_step_handler(video_type, get_type)
				# bot.send_document(message.chat.id,open(output, 'rb'))
				# os.remove(video_url)
				# os.remove(output)
			else:
				time = bot.send_message(message.chat.id, translation[get_language(uid)[0][0]]['wrong'], reply_markup = cancel)
				bot.register_next_step_handler(time, get_start_timeline)
		except Exception as e:
			bot.send_message(message.chat.id, translation[get_language(uid)[0][0]]['wrong'], reply_markup = cancel)
	else:
		bot.send_message(message.chat.id, translation[get_language(uid)[0][0]]['canceled'],reply_markup=types.ReplyKeyboardRemove())
def get_type(message):
	uid = message.chat.id
	output = 'videos/' + str(message.chat.id)+'-ready.mp4'
	if message.text == "Video" or message.text == "Видео":
		bot.send_document(message.chat.id,open(output, 'rb'))
		# os.remove(video_url)
		os.remove(output)
	else:
		gif_file = output+'.gif'
		os.rename(output, gif_file)
		bot.send_document(message.chat.id,open(gif_file, 'rb'))
		# os.remove(video_url)
		os.remove(gif_file)
	bot.send_message(message.chat.id, translation[get_language(uid)[0][0]]['thanks'],reply_markup=types.ReplyKeyboardRemove())
	order_completed(uid)
bot.polling()