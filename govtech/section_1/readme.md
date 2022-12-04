## Section1: Data Pipelines

Explaination of solution.

Airflow choosen as the scheduling tool. Kindly refer to spark_dag_runner.py for the dag configuration. It is currently set up to run at minute 0 hourly.

There are three stages in the dag.

1. Check if input files exist. If yes, proceed to next. (check_files.py)
2. Process input datasets according to requirements. Once done, output files into successful and unsuccessful folders. (process_datasets.py)
3. Archive input files. (archive_files.py)

Spark is choosen as the processing tool.

Code is written in pyspark.

Validation performed:
1. Mobile number is 8 digits. Spaces are allowed. Examples of allowed numbers, 62111122, 6211 1122.
2. Applicant is 18 years old as of 1 Jan 2022.
3. Valid email with following checks:
	a. No "." allowed infront and end,
	b. No consecutives ".." allowed,
	c. No "." allowed infront and end of "@",
	d. ends with either ".com" or ".net"
	e. follows with the generic format of an email address.
4. Empty name fields are not allowed.

Files
1. Original input datasets file are placed in /input/latest folder. After job completes successfully, the files are archived into /input/archived folder.
2. Successful and unsuccessful application output files can be found in /output folder.
3. Application logs can be found in /logs folder.
