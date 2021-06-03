'''
Class for extracting reviews of Cornell professors

Example Usage: poetry run python get_rate_prof.py --input courseProfsSpring.csv

Author: Joanna Saikali
Date:   April 3, 2021
'''
import ratemyprofessor
import pandas as pd
import datetime
import argparse

def generate_dataset(input_csv, firstname="firstName", lastname="lastName"):
	# Read in file containing prof names of interest
	# and extract their last name only for querying
	professor_df = pd.read_csv(input_csv)
	small_df = professor_df[[firstname,lastname]]
	small_df['fullname'] = small_df[firstname]+" "+small_df[lastname]
	small_df = small_df.drop_duplicates()
	lastnames = list(set(small_df[lastname]))
	lastnames_split = [name.split()[-1] for name in lastnames if type(name)==str]
	prof_last_names = list(set(lastnames+lastnames_split))
	prof_last_names = [x for x in prof_last_names if type(x)==str]
	# Get list of Cornell schools
	# 	Last runtime this produced something like:
	# 	['Cornell University', 'Cornell College', 'Cornell Law School', ...
	schools_list = ratemyprofessor.get_schools_by_name("Cornell")

	# Get instances of Professor class for each prof last name at each school
	all_professors = []
	for school in schools_list:
		for prof_name in prof_last_names:
			prof = ratemyprofessor.get_professors_by_school_and_name(school, prof_name)
			if len(prof)==20: 
				print("Reached maximum output for name="+prof_name+". May need to refine search")
				fullnames = list(set(small_df[small_df[lastname]==prof_name]['fullname']))
				for f in  fullnames:
					prof += ratemyprofessor.get_professors_by_school_and_name(school, f)
					print("Searched for "+f)
			all_professors+=prof

	# Try to filter any duplicate profs
	all_professors_unique = []
	[all_professors_unique.append(x) for x in all_professors if x not in all_professors_unique]

	# Get actual ratings of professors
	records = []
	for prof in all_professors_unique:
		ratings = prof.get_ratings()
		for r in ratings:
			record = {"prof_name": prof.name, "prof_id":prof.id, "prof_dept":prof.department,
					"class_name": r.class_name, "attendance_mandatory":r.attendance_mandatory,
					"comment":r.comment, "credit": r.credit, "date":r.date, "difficulty":r.difficulty,
					"grade": r.grade, "online_class":r.online_class,"rating":r.rating,"take_again":r.take_again,
					"thumbs_down":r.thumbs_down, "thumbs_up":r.thumbs_up}
			records.append(record)

	# Write out ratings dataframe
	record_df = pd.DataFrame.from_records(records)
	timestamp = datetime.datetime.now().strftime(format="%Y%m%d%H%M%S")
	record_df.to_csv("output/rate_my_professor_{}.csv".format(timestamp),index=False)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create ratemyprofessor dataset')
    parser.add_argument('--input', dest="input", required=True, help="The CSV file path containing professor names")           
    args = parser.parse_args()

    generate_dataset(args.input)

