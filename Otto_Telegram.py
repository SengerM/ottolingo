from Otto import ask_Otto
from telegram import Update # https://github.com/python-telegram-bot/python-telegram-bot
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes # https://github.com/python-telegram-bot/python-telegram-bot

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

import pandas

vocabulary = pandas.read_csv('vocabulary.csv').set_index('DE')
vocabulary = vocabulary.sample(frac=1)
words = ListIterator(list(vocabulary.index))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	words.reset()
	await context.bot.send_message(
		chat_id = update.effective_chat.id, 
		text = f"Hallo, ich bin Otto, dein Lehrer! Bitte schreiben Sie eine Satzt mit {repr(words.current())} ({vocabulary.loc[words.current(),'EN']}) oder einen variation.",
	)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
	response = ask_Otto(
		word = words.current(),
		sentence = update.message.text,
	)
	response += '\n\n'
	try:
		response += f'Bitte schreiben Sie eine Satzt mit {repr(words.next())} ({vocabulary.loc[words.current(),"EN"]}) oder einen variation.'
	except StopIteration:
		response += 'Gratulazionen! Sie haben alle Wörter geubungt.'
	await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

if __name__ == '__main__':
	import pandas
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
