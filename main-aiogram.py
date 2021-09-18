import logging
import numpy
import pandas
import functions as func

import aiogram.utils.markdown as md
from aiogram.types import message
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
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)

    markup = (
        ('Apa Itu Covid-19?', "0"),
        ('Macam Varian Covid-19', "1"),
        ('Jenis Treatment', "2"),
        ('Pembatasan Pemerintah', "3"),
    )

    keyboard_markup = (types.InlineKeyboardButton(text, callback_data=data) for text, data in markup)

    inline_keyboard.add(*keyboard_markup)
    inline_keyboard.add(types.InlineKeyboardButton('Informasi WHO', url='https://www.who.int/emergencies/diseases/novel-coronavirus-2019?gclid=EAIaIQobChMI0fvzzLfk8gIVS5JmAh2DKwniEAAYASAAEgLLBPD_BwE'))

    await message.reply(func.add_respon([], "salam_normal")[0], reply_markup=inline_keyboard)


@dp.callback_query_handler(text="0")
@dp.callback_query_handler(text="1")
@dp.callback_query_handler(text="2")
@dp.callback_query_handler(text="3")
async def start_button(query: types.CallbackQuery):
    answer_data = int(query.data)
    await query.answer(f'Menampilkan hasil untuk: {query.message.reply_markup.inline_keyboard[answer_data][0].text}')

    if answer_data == 0:        
        await bot.send_message(  
            query.message.chat.id,
            md.text(f"{md.bold('Virus Corona')} atau {md.bold('severe acute respiratory syndrome coronavirus 2')} (SARS-CoV-2) adalah virus yang menyerang sistem pernapasan. Penyakit karena infeksi virus ini disebut COVID-19. Virus Corona bisa menyebabkan gangguan ringan pada sistem pernapasan, infeksi paru-paru yang berat, hingga kematian."),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif answer_data == 1:
        await bot.send_message(  
            query.message.chat.id,
            md.text(f"{md.bold('Varian Alfa')} (B.1.1.7) yang pada awalnya ditemukan di Inggris sejak September 2020\n\n{md.bold('Varian Beta')} (B.1.351/B.1.351.2/B.1.351.3) yang pada awalnya ditemukan di Afrika Selatan sejak Mei 2020\n\n{md.bold('Varian Gamma')} (P.1/P.1.1/P.1.2) yang pada awalnya ditemukan di Brazil sejak November 2020\n\n{md.bold('Varian Delta')} (B.1.617.2/AY.1/AY.2/AY.3) yang pada awalnya ditemukan di India sejak Oktober 2020\n\n{md.bold('Varian Eta')} (B.1.525) yang penyebarannya ditemukan di banyak negara sejak Desember 2020\n\n{md.bold('Varian Iota')} (B.1526) yang pada awalnya ditemukan di Amerika sejak November 2020\n\n{md.bold('Varian Kappa')} (B.1617.1) yang pada awalnya ditemukan di India sejak Oktober 2020\n\n{md.bold('Varian Lamda')} (c.37) yang pada awalnya ditemukan di Peru sejak Desember 2020"),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif answer_data == 2:
        await bot.send_message(  
            query.message.chat.id,
            md.text(f"{md.bold('Rapid test')}, untuk mendeteksi antibodi (IgM dan IgG) yang diproduksi oleh tubuh untuk melawan virus Corona\n\n{md.bold('Rapid test antigen')}, untuk mendeteksi antigen yaitu protein yang ada di bagian terluar virus\n\n{md.bold('Swab test')} atau tes {md.bold('PCR')} (polymerase chain reaction), untuk mendeteksi virus Corona di dalam dahak\n\n{md.bold('CT scan atau Rontgen dada')}, untuk mendeteksi infiltrat atau cairan di paru-paru\n\nTes darah lengkap, untuk memeriksa kadar sel darah putih, D-dimer dan C-reactive protein"),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif answer_data == 3:
		    await bot.send_message(  
            query.message.chat.id,
            f"• PSBB\n• PSBB Jawa Bali\n• PPKM Mikro\n• Penebalan PPKM Mikro\n• PPKM Darurat\n• PPKM Level 3-4",
        )


@dp.message_handler(commands='diagnosa')
async def formulir_start(message: types.Message):
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

    for item in snt_list.itertuples():                
        if stemmer.stem(item.Sentence) in stemmer.stem(pesan) and item.Intent not in detected_intent:   
            bot_respon = func.add_respon(bot_respon, item.Intent)
            detected_intent += [ item.Intent ]  

    bot_respon += func.get_covid_info( stemmer.stem(func.synonymize(pesan)) )

    for item in bot_respon:
        if item is not None:
            await message.answer(item)
  



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)