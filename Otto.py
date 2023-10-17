import pprint
import google.generativeai as palm # https://developers.generativeai.google/api/python/google/generativeai
import numpy
import logging
import sys
import pandas

def generate_prompt(word:str, sentence:str):
	return f"""
	You are a German teacher and I am your student. Below there is a sentence I have formulated using the expression {repr(word)} or a variation of it. Please tell if it contains any mistake and fix if yes. Very important: Write strictly in English, except for the sentence itself if it needs corrections.

	{sentence}
	"""

def ask(model, word:str, sentence:str, n_attempts:int=5):
	response = None
	temperature = .1
	while response is None or response.result is None or n_attempts>0:
		response = palm.generate_text(
			model = model,
			prompt = generate_prompt(word, sentence),
			temperature = temperature,
			max_output_tokens = 2222,
		)
		n_attempts -= 1
		if response.result is None:
			temperature **= .5 # Progressively increase the temperature so it becomes more creative, this reduces the probability of Google blocking the answer (probably because the original with low T contains too much German, and they don't like that as od October 2023.
	return response

if __name__ == '__main__':
	from SECRET import get_api_key
	
	logging.basicConfig(
		stream = sys.stderr, 
		level = logging.INFO,
		format = '%(asctime)s|%(levelname)s|%(message)s',
		datefmt = '%H:%M:%S',
	)
	
	palm.configure(api_key=get_api_key())
	
	vocabulary = pandas.read_csv('vocabulary.csv').set_index('DE')
	
	while True:
		for word, translations in vocabulary.iterrows():
			response = ask(
				model = 'models/text-bison-001',
				word = word,
				sentence = input(f'Schreibe eine Satz mit {repr(word)} ({translations["EN"]}): '),
			)
			print(response.result)
