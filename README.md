# cs4300-rate-prof

## Setup

Install Python 3.9.1 and confirm that the repo is using it:

```bash
pip install pyenv # or brew install pyenv
pyenv install 3.9.1
pyenv local 3.9.1
eval "$(pyenv init -)"
pyenv local # Ensure that this outputs 3.9.1
python --version # Ensure that this outputs Python 3.9.1
```

[Install Poetry](https://python-poetry.org/docs/), then install the dependencies in a new virtual environment:

```bash
poetry env use python # Creating virtualenv unrapid in...
poetry install # Installing dependencies from lock file...
```
## Usage
Execute the script via a command like the following:

```bash
poetry run python get_rate_prof.py --input data/prof_names.csv --name-col name
```

This execution is based on an input file `prof_names.csv` where full names of professors at Cornell are in the "name" column. 

This will output a file of ratemyprofessor reviews looking like the following:

| prof_name      | prof_id | prof_dept        | class_name | attendance_mandatory | comment                                         | credit | date         | difficulty | grade | online_class | rating | take_again | thumbs_down | thumbs_up | 
|----------------|---------|------------------|------------|----------------------|-------------------------------------------------|--------|--------------|------------|-------|--------------|--------|------------|-------------|-----------| 
| Tom Avedisian  | 873434  | Engineering      | MAE324     |                      | "One of the least helpful classes I..."         | FALSE  | 8/9/06 15:05 | 3          |       | FALSE        | 1      |            | 0           | 0         | 
| Lorenzo Alvisi | 2234527 | Computer Science | CS5414     |                      | hws and exams don't accurately...               | TRUE   | 2/12/21 4:30 | 5          | F     | FALSE        | 1      | FALSE      | 0           | 1         | 
| Lorenzo Alvisi | 2234527 | Computer Science | CS5414     | FALSE                | "The course content was really interesting ..." | TRUE   | 1/6/21 8:36  | 5          | B-    | FALSE        | 3      | TRUE       | 0           | 0         | 



