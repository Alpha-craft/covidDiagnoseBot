import logging
from aiogram.types import message
import numpy
import pandas
import random
import functions as func

from aiogram import Bot, Dispatcher, executor, types
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory # https://github.com/har07/PySastrawi

factory = StemmerFactory()
stemmer = factory.create_stemmer()
rsp_list = pandas.read_csv("response.csv")
snt_list = pandas.read_csv("sentence.csv")

covtrig = [
  'covid',
  'covid-19',
  'corona',
  'korona',
  'coronavirus',
  'sars-cov-2',
  'virus baru',
  'pandemi saat ini',
  'novel-corona-virus',
  'rontgen',
  'pcr',
  'tes darah',
  'ct scan',
  'swab',
  'rapid'
]



# === INIT === #
BOT_TOKEN = "1984425169:AAGHyd_rVPFz4vjHGdd6GBc428POodtjNT4"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)



# === MAIN === #

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
	await message.reply("Ello")

# @dp.message_handler(commands='tems')
# async def start_cmd_handler(message: types.Message):
# 	keyboard_markup = types.InlineKeyboardMarkup(row_width=3,resize_keyboard=True,one_time_keyboard=True)
# 	# default row_width is 3, so here we can omit it actually
# 	# kept for clearness

# 	text_and_data = [
# 		('Hayasaka Mei'),
# 		('Kanzaki Rio'),
# 	]
# 	# in real life for the callback_data the callback data factory should be used
# 	# here the raw string is used for the simplicity
# 	row_btns = (types.InlineKeyboardButton(text) for text in text_and_data)

# 	keyboard_markup.add(*row_btns)
# 	# keyboard_markup.add(
# 	#     # url buttons have no callback data
# 	#     types.InlineKeyboardButton('aiogram source'),
# 	# )

# 	await message.reply("Hi", reply_markup=keyboard_markup)
# 		# await keyboard_markup.remove()

@dp.message_handler(commands='tems')
async def start_cmd_handler(message: types.Message):
    keyboard_markup = types.ReplyKeyboardMarkup(row_width=3)
    # default row_width is 3, so here we can omit it actually
    # kept for clearness

    btns_text = ('Hayasaka Mei', 'Kanzaki Rio')
    keyboard_markup.row(*(types.KeyboardButton(text) for text in btns_text))
    # adds buttons as a new row to the existing keyboard
    # the behaviour doesn't depend on row_width attribute

    more_btns_text = (
        "I don't know",
        "Who am i?",
        "Where am i?",
        "Who is there?",
    )
    keyboard_markup.add(*(types.KeyboardButton(text) for text in more_btns_text))
    # adds buttons. New rows are formed according to row_width parameter

    await message.reply("Choose dude", reply_markup=keyboard_markup)


# Use multiple registrators. Handler will execute when one of the filters is OK
@dp.callback_query_handler(text='tems1')  # if cb.data == 'no'
@dp.callback_query_handler(text='tems2')  # if cb.data == 'yes'
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
	answer_data = query.data
	# always answer callback queries, even if you have nothing to say
	await query.answer(f'You answered with {answer_data}')

	if answer_data == 'tems1':
		text = 'ini tems 1!'
	elif answer_data == 'tems2':
		text = 'ini tems2'
	else:
		text = f'Unexpected callback data {answer_data}!'

		# await bot.send_message(text)
	await query.answer(text)
	await query.answer(text, reply_markup=types.ReplyKeyboardRemove())
		


@dp.message_handler()
async def echo(message: types.Message):
	bot_respon = []
	detected_intent = []
	pesan = message.text.lower()
	kata = pesan.split()
	btn_text = message.text
	
	if btn_text == "Hayasaka Mei":
		reply_text = "Hayasaka Mei dayo"

	await message.reply(reply_text, reply_markup=types.ReplyKeyboardRemove())
  await message.reply()
  
	for item in snt_list.itertuples():    
		if func.inside(pesan, covtrig):
			bot_respon = func.get_covid_info(pesan)

		if stemmer.stem(item.Sentence) in pesan and item.Intent not in detected_intent:   
			bot_respon = func.add_respon(bot_respon, item.Intent)
			detected_intent += [ item.Intent ]  

	for item in bot_respon:
		await message.answer(item)
  





if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)

print("jamlan")