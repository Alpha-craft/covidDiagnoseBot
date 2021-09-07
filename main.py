from telegram.ext import Updater,CommandHandler,MessageHandler,Filters,CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update,ForceReply,ReplyKeyboardMarkup
TOKEN = "1984425169:AAGHyd_rVPFz4vjHGdd6GBc428POodtjNT4"

def start(update,context):
	update.message.reply_text("Start")
	keyboard = [
			[InlineKeyboardButton("Hayasaka Mei",callback_data="tems1")],
			[
					#param pertama adalah yang ditampilkan sedangkan callback_data adalah data yang dapat diolah
					InlineKeyboardButton("Kanzaki Rio", callback_data='tems2'),
					InlineKeyboardButton("Eula Lawrance", callback_data='tems3'),
			],
			[
				InlineKeyboardButton("Amber", callback_data='tems4'),
				InlineKeyboardButton("Frederica Baumann", callback_data='tems5'),
			],
			[
				InlineKeyboardButton("Rita Rossweisse", callback_data="tems6"),
			]
	]
	reply_markup = InlineKeyboardMarkup(keyboard) #keyboard button

	update.message.reply_text('Pilih Waifu mu:', reply_markup=reply_markup)


def button(update,context) -> None:
	query = update.callback_query
	if query.data == 'tems1':
			query.edit_message_text(text=f"Waifu yang dipilih: {query.data}")
			query.message.reply_text("Hayasaka Mei dayo")
			
	if query.data == 'tems2':
			query.edit_message_text(text=f"Waifu yang dipilih: {query.data}")
			query.message.reply_text("Kanzaki Rio desu obeite kinasai")

def echo(update,context):
	pesan = update.message.text.lower().split()
	#Mimror
	if update.message.text:
			update.message.reply_text(update.message.text)
        

updater = Updater(TOKEN,use_context=True)

dp = updater.dispatcher
dp.add_handler(CallbackQueryHandler(button))
dp.add_handler(CommandHandler("start",start))
dp.add_handler(MessageHandler(Filters.text,echo))
#run Bot
print("jamlan")
updater.start_polling()

updater.idle()