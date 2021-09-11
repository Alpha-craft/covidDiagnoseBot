import logging
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


@dp.message_handler()
async def echo(message: types.Message):
    bot_respon = []
    detected_intent = []
    pesan = message.text.lower()
    kata = pesan.split()

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