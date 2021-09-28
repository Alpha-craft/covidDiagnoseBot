import logging
import numpy
import pandas
import functions as func
import requests as req

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

    provinsi = State()    

    sesakNafas = State()
    nyeriOtot = State()
    demam = State()
    sakitKepala = State()
    nyeriDada = State()
    diare = State()
    ruam = State()

    result = State()

class Rujukan(StatesGroup):
    select = State()


# === MAIN === #

# ======= Button Start ======= #
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
# ======= Button End ======= #



# ======= Diagnosa Start ======= #
yesno = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
yesno.add("Iya", "Tidak") 

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

        await message.reply("Apakah anda mempunyai riwayat penyakit dalam?", reply_markup=yesno)

        await Formulir.next()
    else:
        await message.reply("Maaf, umur harus berupa angka!")
        await message.reply("Berapa umurmu?")


@dp.message_handler(state=Formulir.penyakitDalam)
async def handler_penyakitDalam(message: types.Message, state: FSMContext):
    if message.text.lower() in ["iya", "tidak"]:
        async with state.proxy() as data:            
            data['penyakitDalam'] = 1 if message.text.lower() == "iya" else 0
        
        await message.reply("Apakah anda pernah terjangkit Covid-19?", reply_markup=yesno)

        await Formulir.next()
    else:
        await message.reply("Pilih salah satu dari opsi!")
        await message.reply("Apakah anda mempunyai riwayat penyakit dalam?", reply_markup=yesno)


@dp.message_handler(state=Formulir.pernahCovid)
async def handler_pernahCovid(message: types.Message, state: FSMContext):
    if message.text.lower() in ["iya", "tidak"]:
        async with state.proxy() as data:
            data['pernahCovid'] = 0 if message.text.lower() == "iya" else 1

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        for item in func.provinsi_indonesia:
          markup.add(item)

        await message.reply("Pilihlah provinsi dimana kamu tinggal!", reply_markup=markup)  

        await Formulir.next()
    else:
        await message.reply("Pilih salah satu dari opsi!")
        await message.reply("Apakah anda pernah terjangkit Covid-19?", reply_markup=yesno)


@dp.message_handler(state=Formulir.provinsi)
async def handler_provinsi(message: types.Message, state: FSMContext):          
    if message.text.lower() in [x.lower() for x in func.provinsi_indonesia]:
        async with state.proxy() as data:
          data['provinsi'] = message.text

        await message.reply("Apakah anda mengalami kesulitan bernafas atau sesak nafas?", reply_markup=yesno) 

        await Formulir.next()
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        for item in func.provinsi_indonesia:
          markup.add(item)

        await message.reply("Pilihlah salah satu provinsi di Indonesia!", reply_markup=markup)


@dp.message_handler(state=Formulir.sesakNafas)
async def handler_sesakNafas(message: types.Message, state: FSMContext):          
    if message.text.lower() in ["iya", "tidak"]:
        async with state.proxy() as data:            
            data['sesakNafas'] = 1 if message.text.lower() == "iya" else 0
        
        await message.reply("Apakah anda mengalami nyeri otot?", reply_markup=yesno)

        await Formulir.next()
    else:
        await message.reply("Pilih salah satu dari opsi!")
        await message.reply("Apakah anda mengalami kesulitan bernafas atau sesak nafas?", reply_markup=yesno)   


@dp.message_handler(state=Formulir.nyeriOtot)
async def handler_nyeriOtot(message: types.Message, state: FSMContext):          
    if message.text.lower() in ["iya", "tidak"]:
        async with state.proxy() as data:            
            data['nyeriOtot'] = 1 if message.text.lower() == "iya" else 0
        
        await message.reply("Apakah tubuh anda mengalami demam atau panas dingin?", reply_markup=yesno)

        await Formulir.next()
    else:
        await message.reply("Pilih salah satu dari opsi!")
        await message.reply("Apakah anda mengalami nyeri otot?", reply_markup=yesno)


@dp.message_handler(state=Formulir.demam)
async def handler_demam(message: types.Message, state: FSMContext):              
    if message.text.lower() in ["iya", "tidak"]:
        async with state.proxy() as data:            
            data['demam'] = 1 if message.text.lower() == "iya" else 0
        
        await message.reply("Apakah anda mengalami sakit kepala?", reply_markup=yesno)
        
        await Formulir.next()
    else:
        await message.reply("Pilih salah satu dari opsi!")
        await message.reply("Apakah tubuh anda mengalami demam atau panas dingin?", reply_markup=yesno)  


@dp.message_handler(state=Formulir.sakitKepala)
async def handler_sakitKepala(message: types.Message, state: FSMContext):              
    if message.text.lower() in ["iya", "tidak"]:
        async with state.proxy() as data:            
            data['sakitKepala'] = 1 if message.text.lower() == "iya" else 0
        
        await message.reply("Apakah dada anda terasa nyeri?", reply_markup=yesno)
        
        await Formulir.next()
    else:
        await message.reply("Pilih salah satu dari opsi!")
        await message.reply("Apakah anda mengalami sakit kepala?", reply_markup=yesno)


@dp.message_handler(state=Formulir.nyeriDada)
async def handler_nyeriDada(message: types.Message, state: FSMContext):              
    if message.text.lower() in ["iya", "tidak"]:
        async with state.proxy() as data:            
            data['nyeriDada'] = 1 if message.text.lower() == "iya" else 0
        
        await message.reply("Apakah anda mengalami diare?", reply_markup=yesno)
        
        await Formulir.next()
    else:
        await message.reply("Pilih salah satu dari opsi!")
        await message.reply("Apakah dada anda terasa nyeri?", reply_markup=yesno)


@dp.message_handler(state=Formulir.diare)
async def handler_diare(message: types.Message, state: FSMContext):              
    if message.text.lower() in ["iya", "tidak"]:
        async with state.proxy() as data:            
            data['diare'] = 1 if message.text.lower() == "iya" else 0
        
        await message.reply("Apakah tubuh anda terdapat ruam atau bercak-bercak kemerahan?", reply_markup=yesno)
        
        await Formulir.next()
    else:
        await message.reply("Pilih salah satu dari opsi!")
        await message.reply("Apakah anda mengalami diare?", reply_markup=yesno)


@dp.message_handler(state=Formulir.ruam)
async def handler_ruam(message: types.Message, state: FSMContext):              
    if message.text.lower() in ["iya", "tidak"]:
        # === end proccesing ===
        async with state.proxy() as data:
            data['ruam'] = 1 if message.text.lower() == "iya" else 0

        await message.reply("Apakah anda berpergian jauh beberapa hari yang lalu?", reply_markup=yesno)
        await Formulir.next()
    else:
        await message.reply("Pilih salah satu dari opsi!")
        await message.reply("Apakah tubuh anda terdapat ruam atau bercak-bercak kemerahan?", reply_markup=yesno)


@dp.message_handler(state=Formulir.result)
async def handler_result(message: types.Message, state: FSMContext):              
    if message.text.lower() in ["iya", "tidak"]:
        berpergian = 1 if message.text.lower() == "iya" else 0

        # === end proccesing ===
        async with state.proxy() as data:             
            umur = data['umur']
            provinsi = data['provinsi']
            point = data['penyakitDalam'] + data['sesakNafas'] + data['nyeriOtot'] + data['demam'] + data['sakitKepala'] + data['nyeriDada'] + data['diare'] + data['ruam'] + func.is_topcases_province(provinsi) + berpergian

            result = (point * 100) / 11
            stats = func.get_province_stats(provinsi)            
            txt = f"Berikut <a href='{stats['img_url']}'>ini</a> adalah statistik covid di provinsi anda tinggal\n\nTotal kasus: {stats['kasus']}\nDirawat: {stats['dirawat']}\nSembuh: {stats['sembuh']}\nMeninggal: {stats['meninggal']}"

            await message.reply(f"Anda memiliki persentase {round(result, 1)}% terkena Covid-19", reply_markup=types.ReplyKeyboardRemove())
            await message.reply(txt, parse_mode=ParseMode.HTML)

        await state.finish()
    else:
        await message.reply("Pilih salah satu dari opsi!")
        await message.reply("Apakah anda berpergian jauh beberapa hari yang lalu?", reply_markup=yesno)
# ======= Diagnosa End ======= #




# ======= RS Start ======= #
@dp.message_handler(commands='rujukan')
async def rujukan(message: types.Message):    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for item in func.provinsi_indonesia:
      markup.add(item)

    await message.reply("Pilihlah provinsi dimana kamu tinggal!", reply_markup=markup)
    await Rujukan.select.set()

@dp.message_handler(state=Rujukan.select)
async def select_rs_rujukan(message: types.Message, state: FSMContext):  
    rs_response = req.get("https://dekontaminasi.com/api/id/covid19/hospitals")
    rs_lists = rs_response.json() 

    if message.text.lower() in [x.lower() for x in func.provinsi_indonesia]:
      async with state.proxy() as data:
          result = md.text(md.bold(f'Daftar Rumah Sakit Rujukan Covid-19 di {message.text}:\n\n'))

          for item in rs_lists:
            if item['province'].lower() == message.text.lower():
              result += md.text(
                  md.text(md.bold(item['name'])),
                  md.text(f"Alamat: {item['address']}"),
                  md.text(f"No Telp: {md.bold(item['phone'])}"),
                  md.text("\n"),
                  sep='\n',
              )
      await message.reply(result.replace('\\', ''), reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)      
    else:
      await message.reply("Tolong masukan salah satu provinsi di Indonesia!", reply_markup=types.ReplyKeyboardRemove())

    await state.finish()
# ======= RS End ======= #


# ======= Covid-Stats Start ======= #
@dp.message_handler(commands='statistik')
async def stats_covid(message: types.Message):
    await message.reply("Sedang memuat data, mohon tunggu..")
    img_url = func.get_covid_stats()    

    if img_url is not False:
        await message.reply(f"Berikut <a href='{img_url}'>ini</a> adalah statistik kasus covid 7 hari terakhir dan prediksi 3 hari kedepan", parse_mode=ParseMode.HTML)
    else:
        await message.reply("Ada gangguan pada server, tolong coba lain kali")
# ======= Covid-Stats End ======= #



# ======= About Start ======= #
@dp.message_handler(commands='about')
async def stats_covid(message: types.Message):
    txt = "Ini adalah bot informasi covid yang dibuat untuk keperluan project <a href='https://ipm.oreon.ai/'>Intel Prakarsa Muda</a>"
    sumberdata = "Sumber data:\n-<a href='https://github.com/Reynadi531/api-covid19-indonesia-v2'>Kasus Covid</a>\n-<a href='https://dekontaminasi.com/api/id/covid19/hospitals'>Daftar Rumah sakit rujukan covid</a>"
    referensi = "Referensi: \n-<a href='https://www.kaggle.com/chaudharijay2000/prediction-of-death-and-confirmed-cases-covid-19'>Prediksi covid</a>\n-<a href='https://devtrik.com/python/steeming-bahasa-indonesia-python-sastrawi/'>Sastrawi</a>"
    api = "Layanan API: -<a href='https://documentation.image-charts.com/'>Embed chart services</a>"

    await message.reply(f"{txt}\n\n {sumberdata}\n\n{referensi}\n\n{api}", parse_mode=ParseMode.HTML)
# ======= About End ======= #






@dp.message_handler()
async def echo(message: types.Message):
    bot_respon = []
    detected_intent = []
    pesan = message.text.lower()
    kata = pesan.split()

    func.get_responses(kata, detected_intent, bot_respon)      
    bot_respon += func.get_covid_info( stemmer.stem(func.synonymize(pesan)) )

    for item in bot_respon:
        if item is not None:
            await message.answer(item)
  



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

#Oke Sip TTD Ahmad Rafli
