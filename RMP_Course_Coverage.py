'''
RMP_Course_Coverage.py

Determining how many professors from the Cornell Roster were successfully
found in RateMyProfessor.
'''

import boto3
import botocore
from botocore import UNSIGNED
from botocore.config import Config
import json
import pandas as pd
import nltk
import re

BUCKET_NAME = 'cornell-course-data-bucket'
PATH = 'course_data.json'

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

print(len(json_content))

course_profs = []
for j in json_content:
    if "firstName" in j.keys() and "lastName" in j.keys() and type(j["firstName"])==str and type(j["lastName"])==str:
        d  = {'names_list': re.findall(r"[\w']+", j['firstName']) + re.findall(r"[\w']+", j['lastName']), "fullNameRoster": " ".join([j['firstName'],j['lastName']]), "rmp_name":""}
    elif "firstName" in j.keys() and type(j["firstName"])==str :
        d  = {'names_list':re.findall(r"[\w']+", j['firstName']), "fullNameRoster": j['firstName'], "rmp_name":""}
    elif "lastName" in j.keys() and type(j["lastName"])==str :
        d  = {'names_list':re.findall(r"[\w']+", j['lastName']), "fullNameRoster": j['lastName'], "rmp_name":""}
    else:
        d = {'names_list':[], "fullNameRoster": '', "rmp_name":""}

    course_profs.append(d)

print(len(course_profs))

RMP = pd.read_csv("per_prof_metrics.csv")
RMP = RMP["prof_name"]
RMP = list(RMP)
for i in range(len(course_profs)):
    for rmp in RMP:
        rmp_name_split = re.findall(r"[\w']+", rmp)
        if rmp_name_split[0] in course_profs[i]["names_list"] and rmp_name_split[-1] in course_profs[i]["names_list"]:
            course_profs[i]["rmp_name"] = rmp



final_json = []
for roster in course_profs:
    roster.pop("names_list")
    final_json.append(roster)

final_json = pd.DataFrame(course_profs)
print("Unfiltered coverage: "  + str(final_json[final_json.rmp_name!=''].shape[0] / final_json.shape[0]))
final_json.to_csv("courseProfsUnfiltered.csv",index=False)
final_json = final_json.drop_duplicates()
print("Filtered coverage: "  + str(final_json[final_json.rmp_name!=''].shape[0] / final_json.shape[0]))
final_json.to_csv("courseProfs.csv",index=False)


# RMP = pd.read_csv("per_prof_metrics.csv",index=False)[["prof_name"]]
