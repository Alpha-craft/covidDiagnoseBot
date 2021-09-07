from telegram.ext import Updater,CommandHandler,MessageHandler,Filters,CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update,ForceReply,ReplyKeyboardMarkup
TOKEN = "1984425169:AAGHyd_rVPFz4vjHGdd6GBc428POodtjNT4"

def start(update,context):
	update.message.reply_text("Start")
	keyboard = [
			[InlineKeyboardButton("Apa Itu Covid-19",callback_data="apa itu covid")],
			# [
					#param pertama adalah yang ditampilkan sedangkan callback_data adalah data yang dapat diolah
			[InlineKeyboardButton("Jenis Varian Covid-19", callback_data='jenis varian covid')],

			[InlineKeyboardButton("Jenis Penanganan", callback_data='jenis treatment')],
			# ],
			[
				InlineKeyboardButton("Beberapa Pembatasan Pemerintah", callback_data="pembatasan pemerintah"),
			],
			[
				InlineKeyboardButton("Informasi WHO Terhadap Covid-19", callback_data="informasi who"),
			]
	]
	reply_markup = InlineKeyboardMarkup(keyboard) #keyboard button

	update.message.reply_text('Informasi Apa Yang Ingin Anda Dapatkan:', reply_markup=reply_markup)


def button(update,context) -> None:
	query = update.callback_query
	if query.data == 'apa itu covid':
			query.edit_message_text(text=f"Informasi yang ingin anda cari: {query.data}")
			query.message.reply_text("""
			Virus Corona atau severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) adalah virus yang menyerang sistem pernapasan. Penyakit karena infeksi virus ini disebut COVID-19. Virus Corona bisa menyebabkan gangguan ringan pada sistem pernapasan, infeksi paru-paru yang berat, hingga kematian.""")
			
	if query.data == 'jenis varian covid':
			query.edit_message_text(text=f"Informasi yang ingin anda cari: {query.data}")
			query.message.reply_text("""Varian Alfa (B.1.1.7) yang pada awalnya ditemukan di Inggris sejak September 2020.\nVarian Beta (B.1.351/B.1.351.2/B.1.351.3) yang pada awalnya ditemukan di Afrika Selatan sejak Mei 2020.\nVarian Gamma (P.1/P.1.1/P.1.2) yang pada awalnya ditemukan di Brazil sejak November 2020.\nVarian Delta (B.1.617.2/AY.1/AY.2/AY.3) yang pada awalnya ditemukan di India sejak Oktober 2020.\nVarian Eta (B.1.525) yang penyebarannya ditemukan di banyak negara sejak Desember 2020.\nVarian Iota (B.1526) yang pada awalnya ditemukan di Amerika sejak November 2020.\nVarian Kappa (B.1617.1) yang pada awalnya ditemukan di India sejak Oktober 2020.\nVarian Lamda (c.37) yang pada awalnya ditemukan di Peru sejak Desember 2020.\n""")
		
	if query.data == 'jenis treatment':
		query.edit_message_text(text=f"Informasi yang ingin anda cari: {query.data}")
		query.message.reply_text("Rapid test, untuk mendeteksi antibodi (IgM dan IgG) yang diproduksi oleh tubuh untuk melawan virus Corona.\n\nRapid test antigen, untuk mendeteksi antigen yaitu protein yang ada di bagian terluar virus.\n\nSwab test atau tes PCR (polymerase chain reaction), untuk mendeteksi virus Corona di dalam dahak.\n\nCT scan atau Rontgen dada, untuk mendeteksi infiltrat atau cairan di paru-paru.\nTes darah lengkap, untuk memeriksa kadar sel darah putih, D-dimer dan C-reactive protein")
	
	if query.data == 'pembatasan pemerintah':
		query.edit_message_text(text=f"Informasi yang ingin anda cari: {query.data}")
		query.message.reply_text("•	PSBB\n•	PSBB Jawa Bali\n•	PPKM Mikro\n•	Penebalan PPKM Mikro\n•	PPKM Darurat\n•	PPKM Level 3-4")

	if query.data == 'informasi who':
		query.edit_message_text(text=f"Informasi yang ingin anda cari: {query.data}")
		query.message.reply_text("https://www.who.int/emergencies/diseases/novel-coronavirus-2019?gclid=EAIaIQobChMI0fvzzLfk8gIVS5JmAh2DKwniEAAYASAAEgLLBPD_BwE")
		query.message.reply_text("https://www.alodokter.com/virus-corona")
		query.message.reply_text("https://news.detik.com/berita/d-5650873/gonta-ganti-nama-pembatasan-corona-psbb-ppkm-ppkm-darurat-ppkm-level-3-4")

	# if query.data == 'jenis treatment':
	# 	query.edit_message_text(text=f"Informasi yang ingin anda cari: {query.data}")
	# 	query.message.reply_text()

	# if query.data == 'jenis treatment':
	# 	query.edit_message_text(text=f"Informasi yang ingin anda cari: {query.data}")
	# 	query.message.reply_text()

def echo(update,context):
	pesan = update.message.text.lower().split()
	#Mimror
	# if update.message.text:
	# 	update.message.reply_text(update.message.text)
	if update.message.text.lower() == "halo":
		update.message.reply_text("halo")
        

updater = Updater(TOKEN,use_context=True)

dp = updater.dispatcher
dp.add_handler(CallbackQueryHandler(button))
dp.add_handler(CommandHandler("start",start))
dp.add_handler(MessageHandler(Filters.text,echo))
#run Bot
print("jamlan")
updater.start_polling()

updater.idle()