'''
Class for extracting reviews of Cornell professors

Author: Joanna Saikali
Date:   April 3, 2021
'''
import ratemyprofessor
import pandas as pd
import datetime
import argparse

# Reached maximum output for name=Daniel. May need to refine search
# Reached maximum output for name=Alexander. May need to refine search
# Reached maximum output for name=Michael. May need to refine search
# Reached maximum output for name=John. May need to refine search
# Reached maximum output for name=Stephen. May need to refine search
# Reached maximum output for name=Paul. May need to refine search
# Reached maximum output for name=Thomas. May need to refine search
# Reached maximum output for name=Cornell. May need to refine search

def generate_dataset(input_csv, prof_fullname_col):
	# Read in file containing prof names of interest
	# and extract their last name only for querying
	professor_df = pd.read_csv(input_csv)
	professor_list = list(professor_df[prof_fullname_col])
	prof_last_names = [name.split()[-1] for name in professor_list]
	prof_last_names = list(set(prof_last_names))

	# Get list of Cornell schools
	# 	Last runtime this produced something like:
	# 	['Cornell University', 'Cornell College', 'Cornell Law School', ...
	schools_list = ratemyprofessor.get_schools_by_name("Cornell")

	# Get instances of Professor class for each prof last name at each school
	all_professors = []
	for school in schools_list:
		for prof_name in prof_last_names:
			prof = ratemyprofessor.get_professors_by_school_and_name(school, prof_name)
			if len(prof)==20: print("Reached maximum output for name="+prof_name+". May need to refine search")
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
    parser.add_argument('--name-col', dest="name_col", required=True, help="Column name for professor full names")           
    args = parser.parse_args()

    generate_dataset(args.input, args.name_col)

