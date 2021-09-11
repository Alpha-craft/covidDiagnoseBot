# https://stackoverflow.com/questions/66294257/python-telegram-bot-forcereply-callback

import numpy
import pandas
import random
import functions as func

from telegram.ext import Updater,CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ForceReply, ReplyKeyboardMarkup

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory # https://github.com/har07/PySastrawi

TOKEN = "1961647107:AAHEEm77I_b3OKuxWFbVfBDQeaP5YV6nzz8"
# TOKEN = "1984425169:AAGHyd_rVPFz4vjHGdd6GBc428POodtjNT4"

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



def start(update,context):
    update.message.reply_text("Start")
    keyboard = [
        [
          InlineKeyboardButton("Apa Itu Covid-19", callback_data="Apa Itu Covid-19")
        ],
        [
          InlineKeyboardButton("Jenis Varian Covid-19", callback_data='Jenis Varian Covid-19')
        ],
        [
          InlineKeyboardButton("Jenis Penanganan", callback_data='Jenis Penanganan')
        ],
        [
          InlineKeyboardButton("Beberapa Pembatasan Pemerintah", callback_data="Pembatasan Pemerintah"),
        ],
        [
          InlineKeyboardButton("Informasi WHO Terhadap Covid-19", callback_data="Informasi WHO"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard) #keyboard button

    update.message.reply_text('Informasi Apa Yang Ingin Anda Dapatkan:', reply_markup=reply_markup)


def button(update, context) -> None:
    query = update.callback_query

    query.edit_message_text(text=f"Informasi yang ingin anda cari: {query.data}")

    if query.data == 'Apa Itu Covid-19':        
        query.message.reply_text("""
        Virus Corona atau severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) adalah virus yang menyerang sistem pernapasan. Penyakit karena infeksi virus ini disebut COVID-19. Virus Corona bisa menyebabkan gangguan ringan pada sistem pernapasan, infeksi paru-paru yang berat, hingga kematian.""")
        
    if query.data == 'Jenis Varian Covid-19':
        query.message.reply_text("""Varian Alfa (B.1.1.7) yang pada awalnya ditemukan di Inggris sejak September 2020.\nVarian Beta (B.1.351/B.1.351.2/B.1.351.3) yang pada awalnya ditemukan di Afrika Selatan sejak Mei 2020.\nVarian Gamma (P.1/P.1.1/P.1.2) yang pada awalnya ditemukan di Brazil sejak November 2020.\nVarian Delta (B.1.617.2/AY.1/AY.2/AY.3) yang pada awalnya ditemukan di India sejak Oktober 2020.\nVarian Eta (B.1.525) yang penyebarannya ditemukan di banyak negara sejak Desember 2020.\nVarian Iota (B.1526) yang pada awalnya ditemukan di Amerika sejak November 2020.\nVarian Kappa (B.1617.1) yang pada awalnya ditemukan di India sejak Oktober 2020.\nVarian Lamda (c.37) yang pada awalnya ditemukan di Peru sejak Desember 2020.\n""")
      
    if query.data == 'Jenis Penanganan':
        query.message.reply_text("Rapid test, untuk mendeteksi antibodi (IgM dan IgG) yang diproduksi oleh tubuh untuk melawan virus Corona.\n\nRapid test antigen, untuk mendeteksi antigen yaitu protein yang ada di bagian terluar virus.\n\nSwab test atau tes PCR (polymerase chain reaction), untuk mendeteksi virus Corona di dalam dahak.\n\nCT scan atau Rontgen dada, untuk mendeteksi infiltrat atau cairan di paru-paru.\nTes darah lengkap, untuk memeriksa kadar sel darah putih, D-dimer dan C-reactive protein")
    
    if query.data == 'Pembatasan Pemerintah':
        query.message.reply_text("•	PSBB\n•	PSBB Jawa Bali\n•	PPKM Mikro\n•	Penebalan PPKM Mikro\n•	PPKM Darurat\n•	PPKM Level 3-4")

    if query.data == 'Informasi WHO':
        query.message.reply_text("https://www.who.int/emergencies/diseases/novel-coronavirus-2019?gclid=EAIaIQobChMI0fvzzLfk8gIVS5JmAh2DKwniEAAYASAAEgLLBPD_BwE")
        query.message.reply_text("https://www.alodokter.com/virus-corona")
        query.message.reply_text("https://news.detik.com/berita/d-5650873/gonta-ganti-nama-pembatasan-corona-psbb-ppkm-ppkm-darurat-ppkm-level-3-4")

# TO DO (work in progress)
# def diagnosa(update, context):
#     pesan = update.message.text.lower()
#     markup = ForceReply(selective=False, input_field_placeholder="Insert...")
#     x = context.bot.send_message(update.message.chat.id, "Send me another word:", reply_markup=markup)
#     print(pesan)

# def tanya_umur():
#     msg = update.bot.reply_to(update.message, "Berapa umurmu?")

# def diagnosa(update, context):
#     msg = update.bot.reply_to(update.message, "Siapa namamu?")
#     update.bot.register_next_step_handler(msg, tanya_umur)

def echo(update, context):
    bot_respon = []
    detected_intent = []
    pesan = update.message.text.lower()
    kata = pesan.split()

    for item in snt_list.itertuples():    
        if func.inside(pesan, covtrig):
            bot_respon = func.get_covid_info(pesan)

        if stemmer.stem(item.Sentence) in pesan and item.Intent not in detected_intent:   
            bot_respon = func.add_respon(bot_respon, item.Intent)
            detected_intent += [ item.Intent ]  

    for item in bot_respon:
        update.message.reply_text(item)
        

updater = Updater(TOKEN, use_context=True)

dp = updater.dispatcher
dp.add_handler(CallbackQueryHandler(button))
dp.add_handler(CommandHandler("start", start))
# dp.add_handler(CommandHandler("diagnosa", diagnosa))
dp.add_handler(MessageHandler(Filters.text, echo))
#run Bot
print("jamlan")
updater.start_polling()

updater.idle()