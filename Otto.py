import google.generativeai as palm # https://developers.generativeai.google/api/python/google/generativeai
import logging

def ask(model, prompt:str, n_attempts:int=5):
	response = None
	temperature = .1
	while response is None or response.result is None or n_attempts>0:
		response = palm.generate_text(
			model = model,
			prompt = prompt,
			temperature = temperature,
			max_output_tokens = 2222,
		)
		n_attempts -= 1
		if response.result is None:
			temperature **= .5 # Progressively increase the temperature so it becomes more creative, this reduces the probability of Google blocking the answer (probably because the original with low T contains too much German, and they don't like that as od October 2023.
			logging.debug(f'Failed to obtain an answer, will ask again with temperature {temperature}')
	return response

def ask_Otto(word:str, sentence:str):
	def generate_prompt(word:str, sentence:str):
		return f"""
		You are a German teacher and I am your student. Below there is a sentence I have formulated using the expression {repr(word)} or a variation of it. Please tell if it contains any mistake and fix if yes. Very important: Write strictly in English, except for the sentence itself if it needs corrections.

		{sentence}
		"""
	
	response = "Don't know, sorry"
	try:
		r = ask(
			model = 'models/text-bison-001', 
			prompt = generate_prompt(word, sentence), 
			n_attempts = 5,
		)
		if isinstance(r.result, str):
			response = r.result
	except Exception as e:
		logging.debug(f'Cannot get an answer, reason: {repr(e)}')
	finally:
		return response

if __name__ == '__main__':
	import sys
	import pandas
	from SECRET import GOOGLE_API_KEY
	
	logging.basicConfig(
		stream = sys.stderr, 
		level = logging.DEBUG,
		format = '%(asctime)s|%(levelname)s|%(message)s',
		datefmt = '%H:%M:%S',
	)
	
	palm.configure(api_key=GOOGLE_API_KEY)
	
	vocabulary = pandas.read_csv('vocabulary.csv').set_index('DE')
	
	while True:
		for word, translations in vocabulary.sample(frac=1).iterrows():
			response = ask_Otto(
				word = word,
				sentence = input(f'Schreibe eine Satz mit {repr(word)} ({translations["EN"]}): '),
			)
			print(response)
