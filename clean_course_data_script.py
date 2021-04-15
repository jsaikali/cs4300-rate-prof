import json
with open('data/course_data.json') as json_file:
	data = json.load(json_file)

groups = data['enrollGroups']
keys = groups.keys()

last_names = []
first_names = []
for key in keys:
	cl = groups[key]
	for c in cl:
		sections = c['classSections']
		for sec in sections:
			if "meetings" in sec.keys():
				for meeting in sec["meetings"]:
					if "instructors" in meeting.keys():
						instructors = meeting['instructors']
						for instructor in instructors:
							last_names.append(instructor['lastName'])
							first_names.append(instructor['firstName'])

import pandas as pd
profs = pd.DataFrame({"lastnames": list(last_names), "firstnames": list(first_names)})
profs = profs.drop_duplicates()
profs.to_csv("professor_list.csv",index=False)