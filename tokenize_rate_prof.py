
import boto3, botocore, json
from botocore import UNSIGNED
from botocore.config import Config
import html
import pandas as pd
import re

import nltk
# from nltk.corpus import stopwords 
# stop_words = stopwords.words('english')
nltk.download('punkt')
from nltk.stem import PorterStemmer
stemmer = PorterStemmer()

BUCKET_NAME = 'cornell-course-data-bucket'
PATH = 'rate_my_professor.json'
s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
content_object = s3.Object(BUCKET_NAME, PATH)
file_content = content_object.get()['Body'].read().decode('utf-8')
json_content = json.loads(file_content)

def tokenizer1(json_dict):
    """
    Tokenize the comments
    """
    new_json = []
    for review in json_content:
        comment = review["comment"]
        cleaned_tokens = []
        try:
            comment = html.unescape(comment)
            tokens = nltk.word_tokenize(comment)
            for w in tokens:
                w = stemmer.stem(w.lower())
                if "@" in w: cleaned_tokens += w.split("@")
                else: cleaned_tokens.append(w)
        except TypeError as e:
            print("e: {}".format(e))
            review["comment"] = ""
        new_review = review
        new_review["comment_toks1"] = cleaned_tokens
        new_json.append(new_review)
    return new_json

def tokenizer2(json_dict):
    """
    Tokenize the comments
    """
    new_json = []
    for review in json_content:
        comment = review["comment"]
        comment = html.unescape(comment)
        tokens = [x for x in re.findall(r"[a-z]+", comment.lower())]
        new_review = review
        new_review["comment_toks2"] = tokens
        new_json.append(new_review)
    return new_json

final_json = tokenizer1(json_content)
final_json = tokenizer2(json_content)

with open("rate_my_professor_with_toks.json","w") as outfile:
    json.dump(final_json,outfile)

final_df = pd.DataFrame(final_json)
final_df.to_csv("rate_my_professor_with_toks.csv",index=False)

