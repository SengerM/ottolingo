from Otto import ask_Otto
from telegram import Update # https://github.com/python-telegram-bot/python-telegram-bot
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes # https://github.com/python-telegram-bot/python-telegram-bot
import pandas
from random import shuffle

class ListIterator:
	def __init__(self, l:list):
		self.l = l
		self._current_idx = 0
	
	def current(self):
		return self.l[self._current_idx]
	
	def next(self):
		self._current_idx += 1
		if len(self.l) > self._current_idx:
			return self.current()
		else:
			raise StopIteration
	
	def reset(self):
		self._current_idx = 0
	
	def shuffle(self):
		shuffle(self.l)

# ~ vocabulary = pandas.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vSHqT2RQ8-hQiK59S463CW5XNNhy81n_NCY3ihB00E9azvCk7ePsv_GtpNns5dOVRLsosEmRP_36ug8/pub?gid=0&single=true&output=csv').set_index('DE')
# ~ words = ListIterator(list(vocabulary.index))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	
	globals()['vocabulary'] = pandas.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vSHqT2RQ8-hQiK59S463CW5XNNhy81n_NCY3ihB00E9azvCk7ePsv_GtpNns5dOVRLsosEmRP_36ug8/pub?gid=0&single=true&output=csv').set_index('DE')
	globals()['words'] = ListIterator(list(globals()['vocabulary'].index))
	globals()['words'].shuffle()
	
	await context.bot.send_message(
		chat_id = update.effective_chat.id, 
		text = f"Hallo, ich bin Otto, dein Lehrer! Bitte schreiben Sie eine Satzt mit {repr(words.current())} ({vocabulary.loc[words.current(),'EN']}) oder einen variation.",
	)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if 'vocabulary' not in globals():
		response = 'Please initialize Otto by sending /start'
	else:
		response = ask_Otto(
			word = words.current(),
			sentence = update.message.text,
		)
		response += '\n\n'
		try:
			response += f'Jetzt mit {repr(words.next())} ({vocabulary.loc[words.current(),"EN"]}).'
		except StopIteration:
			response += 'Gratulazionen! Sie haben alle Wörter geubungt. Wir fangen wieder an.\n\n'
			words.shuffle()
			words.reset()
			response += f'Bitte schreiben Sie eine Satzt mit {repr(words.current())} ({vocabulary.loc[words.current(),"EN"]}) oder einen variation.'
	await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

if __name__ == '__main__':
	from SECRET import GOOGLE_API_KEY, TELEGRAM_BOT_TOKEN
	import google.generativeai as palm # https://developers.generativeai.google/api/python/google/generativeai
	
	palm.configure(api_key=GOOGLE_API_KEY)
	
	application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
	
	echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
	start_handler = CommandHandler('start', start)
	
	application.add_handler(start_handler)
	application.add_handler(echo_handler)
	
	print('Otto is live!')
	application.run_polling()
