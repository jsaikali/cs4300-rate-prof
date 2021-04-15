import boto3
import botocore
from botocore import UNSIGNED
from botocore.config import Config
import json
import numpy as np
from collections import Counter
import pandas as pd
import nltk
nltk.download('words')
real_words = list(set(nltk.corpus.words.words()))

# from nltk.corpus import stopwords
# stop_words = stopwords.words('english')

BUCKET_NAME = 'cornell-course-data-bucket'
PATH = 'rate_my_professor.json'
from tokenize_rate_prof import tokenizer2

s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
json_content = []

try:
	content_object = s3.Object(BUCKET_NAME, PATH)
	file_content = content_object.get()['Body'].read().decode('utf-8')
	json_content = json.loads(file_content)
except botocore.exceptions.ClientError as e:
	if e.response['Error']['Code'] == "404":
		print("The object does not exist.")
	else:
		raise

ratings = []
for j in json_content:
	d  = {'prof_id':j['prof_id'],'prof_name':j['prof_name'], 'rating':j['rating'], 'difficulty': j['difficulty']}
	ratings.append(d)

ratings_df = pd.DataFrame(ratings)
ratings_df = ratings_df.groupby('prof_id') \
       .agg({'prof_name':'size', 'rating':'mean', 'difficulty':'mean'}) \
       .rename(columns={'prof_name':'num_ratings','difficulty':'avg_difficulty','rating':'avg_rating'}) \
       .reset_index()

def create_word_occurrence_matrix(
		input_transcripts,
		input_speakers_to_analyze,
		input_words_to_analyze):
	"""Returns a numpy array of shape n_speakers by n_words_to_analyze such that the
	entry (ij) indicates how often speaker i says word j.

	Params: {tokenize_function: Function (a -> b),
			 input_transcripts: Tuple List,
			 input_speakers_to_analyze: List,
			 input_words_to_analyze: List}
	Returns: Numpy Array
	"""
	# create list of tuples with (speaker_name, [tokens]) across the entire corpus.
	# each tuple is 1 line from the corpus
	entire_corpus = []
	for t in input_transcripts:
		entire_corpus += [(t['prof_id'], t['comment_toks2'])]

	# create a dictionary with format {speaker_name: [all tokens across entire corpus]}
	speaker_tokens = {key: [] for key in input_speakers_to_analyze}
	for item in entire_corpus:
		if item[0] in speaker_tokens:
			speaker_tokens[item[0]] += item[1]

	# for each speaker, get value counts for tokens and update numpy array accordingly
	np_arr = np.zeros((len(input_speakers_to_analyze), len(input_words_to_analyze)))
	for i in range(len(input_speakers_to_analyze)):
		tokens = speaker_tokens[input_speakers_to_analyze[i]]
		tokens = [t for t in tokens if t in input_words_to_analyze]
		counts = dict(Counter(tokens))
		for k in list(counts.keys()):
			np_arr[i, input_words_to_analyze.index(k)] = counts[k]

	return np_arr

words_to_analyze = set()
speakers_to_analyze = set()
prof_id_to_name = dict()
for doc in json_content:
	toks = doc["comment_toks2"]
	words_to_analyze.update(toks)
	speakers_to_analyze.add(doc["prof_id"])
	prof_id_to_name[doc["prof_id"]] = doc["prof_name"]

words_to_analyze = list(words_to_analyze)
words_to_analyze = [word for word in words_to_analyze if word in real_words]

speakers_to_analyze = list(speakers_to_analyze)

word_matrix = create_word_occurrence_matrix(json_content,speakers_to_analyze,words_to_analyze)

def create_weighted_word_freq_array(input_word_array):
	"""Returns a numpy array of shape n_speakers by n_words_to_analyze such that the
	entry (ij) indicates how often speaker i says word j weighted by the above ratio.

	Note: You must add 1 to the sum of each column to avoid divison by 0 issues.

	Params: {input_word_array: Numpy Array}
	Returns: Numpy Array
	"""
	return input_word_array / (input_word_array.sum(axis=0, keepdims=True) + 1)

weighted_words = create_weighted_word_freq_array(word_matrix)

sorted_frequency = np.argsort(weighted_words, axis=1)
top_10 = sorted_frequency[:,-10:]

top_words = []
for i in range(len(speakers_to_analyze)):
	prof_id = speakers_to_analyze[i]
	word_freqs = top_10[i]
	words_and_weights = [(words_to_analyze[k],weighted_words[i][k]) for k in word_freqs]
	words_and_weights_ordered = sorted(words_and_weights, key=lambda x: (-x[1], x[0]),)
	data_dict = {'prof_id': prof_id, 'prof_name': prof_id_to_name[prof_id], 'top10words': words_and_weights_ordered[:10]}
	top_words.append(data_dict)


words_df = pd.DataFrame.from_records(top_words)
final_df = words_df.merge(ratings_df,on="prof_id")
final_df.to_csv("per_prof_metrics.csv",index=False)
