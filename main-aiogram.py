import logging
from aiogram.types import message
import numpy
import pandas
import random
import functions as func

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory # https://github.com/har07/PySastrawi

factory = StemmerFactory()
stemmer = factory.create_stemmer()
rsp_list = pandas.read_csv("response.csv")
snt_list = pandas.read_csv("sentence.csv")



# === INIT === #
# Main token
BOT_TOKEN = "1984425169:AAGHyd_rVPFz4vjHGdd6GBc428POodtjNT4"

# Develop token (don't touch, property milik mepopo)
# BOT_TOKEN = "1961647107:AAHEEm77I_b3OKuxWFbVfBDQeaP5YV6nzz8"

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)



# === CLASS === #
class Formulir(StatesGroup):
    nama = State()
    umur = State()
    penyakitDalam = State()
    pernahCovid = State()



# === MAIN === #
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
	await message.reply("Ello")

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
		


@dp.message_handler(commands='diagnosa')
async def send_welcome(message: types.Message):
    await Formulir.nama.set()
    await message.reply("Hai! siapa namamu?")


@dp.message_handler(state='*', commands='batalkan') # bintang asterik (*) untuk selector all
@dp.message_handler(Text(equals='batalkan', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Dibatalkan..', reply_markup=types.ReplyKeyboardRemove()) # Remove button


@dp.message_handler(state=Formulir.nama)
async def handler_nama(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['nama'] = message.text

        await message.reply(f"Hai {data['nama']}, Berapa umurmu?")        

    await Formulir().next()


@dp.message_handler(state=Formulir.umur)
async def handler_umur(message: types.Message, state: FSMContext):    
    if message.text.isdigit():
        async with state.proxy() as data:
            data['umur'] = int(message.text)        

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Iya", "Tidak")        

        await message.reply("Apakah anda mempunyai riwayat penyakit dalam?", reply_markup=markup)

        await Formulir.next()
    else:
        await message.reply("Maaf, umur harus berupa angka!")
        await message.reply("Berapa umurmu?")


@dp.message_handler(state=Formulir.penyakitDalam)
async def handler_penyakitDalam(message: types.Message, state: FSMContext):
    if message.text.lower() in ["iya", "tidak"]:
        async with state.proxy() as data:
            data['penyakitDalam'] = message.text
        
        await message.reply("Apakah anda pernah terjangkit Covid-19?")

        await Formulir.next()
    else:
        await message.reply("Pilih salah satu dari opsi!")
        await message.reply("Apakah anda mempunyai riwayat penyakit dalam?")


@dp.message_handler(state=Formulir.pernahCovid)
async def handler_pernahCovid(message: types.Message, state: FSMContext):
    if message.text.lower() in ["iya", "tidak"]:
        async with state.proxy() as data:
            data['pernahCovid'] = message.text
            
            markup = types.ReplyKeyboardRemove()

            await bot.send_message(
                message.chat.id,
                md.text(
                    md.text(f"Nama: {md.bold(data['nama'])}"),
                    md.text(f"Umur: {md.code(data['umur'])}"),
                    md.text(f"Punya riwayat penyakit dalam: {md.code(data['penyakitDalam'])}"),
                    md.text(f"Pernah terjangkit Covid-19: {md.code(data['pernahCovid'])}"),
                    sep='\n',
                ),
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        await message.reply("Pilih salah satu dari opsi!")
        await message.reply("Apakah anda pernah terjangkit Covid-19?")
    
    await state.finish() # Formulir stop here..


@dp.message_handler()
async def echo(message: types.Message):
    bot_respon = []
    detected_intent = []
    pesan = message.text.lower()
    kata = pesan.split()

    if btn_text == "Hayasaka Mei":
		    reply_text = "Hayasaka Mei dayo"

    await message.reply(reply_text, reply_markup=types.ReplyKeyboardRemove())
    await message.reply()

    for item in snt_list.itertuples():                
        if stemmer.stem(item.Sentence) in pesan and item.Intent not in detected_intent:   
            bot_respon = func.add_respon(bot_respon, item.Intent)
            detected_intent += [ item.Intent ]  

    bot_respon += func.get_covid_info( stemmer.stem(func.synonymize(pesan)) )

    for item in bot_respon:
        if item is not None:
            await message.answer(item)
  



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)