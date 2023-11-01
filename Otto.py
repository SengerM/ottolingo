import google.generativeai as palm # https://developers.generativeai.google/api/python/google/generativeai
import logging

def ask(prompt:str, n_attempts:int=5, model='models/text-bison-001', initial_temperature=.1):
	response = None
	temperature = initial_temperature
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
		Below there is a sentence in German that you have to revise. If you don't find any mistake, I want you to reply with "The scentence conatins no mistakes.", otherwise please answer with a correction of the sentence.
		
		Important:
		1. Any explanation that you provide has to be strictly in English.
		2. If you provide a corrected version of the sentence, the sentence itself must be in German.
		
		This is the sentence:
		{repr(sentence)}
		"""
	
	response = "Don't know, sorry"
	try:
		r = ask(
			prompt = generate_prompt(word, sentence), 
			n_attempts = 5,
		)
		if isinstance(r.result, str):
			response = r.result
	except Exception as e:
		logging.debug(f'Cannot get an answer, reason: {repr(e)}')
	finally:
		return response

def generate_example_with(word:str):
	prompt = f"""
		Provide an example in German using {repr(word)}.
		
		Important:
		1. The example MUST be longer than 8 words and be creative.
		2. Your answer must be in the following format: <german_example>|<english_translation>|<25_words_in_english>.
		3. You replace <german_example> with the example.
		4. You replace <english_translation> with the translation to English.
		5. You replace <25_words_in_english> with 25 random words in English 
		6. Your answer doesn't have anything else.
		7. Your example must be longer than 8 words.
		"""
	# The 25 words in English in the prompt are because Google blocks answers that are not in English, so I have to make it look like it is in English.
	response = "Don't know, sorry"
	try:
		r = ask(
			prompt = prompt,
			n_attempts = 5,
			initial_temperature = .9,
		)
		if isinstance(r.result, str):
			response = r.result
			logging.debug(f'Example with {repr(word)}: {response}')
			response = response.replace('<','').replace('>','').replace('german_example','').replace('english_translation','')
			response = response.split('|')[:-1]
			response = response[0] + ' (' + response[1] + ')'
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
	
	vocabulary = pandas.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vSHqT2RQ8-hQiK59S463CW5XNNhy81n_NCY3ihB00E9azvCk7ePsv_GtpNns5dOVRLsosEmRP_36ug8/pub?gid=0&single=true&output=csv').set_index('DE')
	
	while True:
		for word, translations in vocabulary.sample(frac=1).iterrows():
			response = ask_Otto(
				word = word,
				sentence = input(f'Schreibe eine Satz mit {repr(word)} ({translations["EN"]}), z.B: {generate_example_with(word)}\n'),
			)
			print(response)
