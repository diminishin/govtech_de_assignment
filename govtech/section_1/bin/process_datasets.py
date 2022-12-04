from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
import pyspark
from pyspark.sql.functions import split, col, size, when, to_date, coalesce, date_format, months_between, lit, current_date, round, trim, sha2, concat, udf, regexp_replace, lower
import sys
from datetime import datetime
import logging
from pathlib import Path
import shutil
import os
import glob

app_folder = sys.argv[1]

log_file = app_folder + "/logs/process_datasets_" + datetime.now().strftime('%d%m%Y_%H%M%S') + ".log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s %(message)s")

# Cast date to string
def cast_date_string(col, formats=("yyyy-MM-dd", "dd-MM-yyyy", "yyyy/MM/dd" ,"yyyy MM dd", "MM/dd/yyyy", "yyyyMMdd")):
    return coalesce(*[date_format(to_date(col, f), 'yyyyMMdd') for f in formats])

# Cast multiple date formats to string
def cast_date(col, formats=("yyyy-MM-dd", "dd-MM-yyyy", "yyyy/MM/dd" ,"yyyy MM dd", "MM/dd/yyyy",  "yyyyMMdd")):
    return coalesce(*[to_date(col, f) for f in formats])

# Remove titles and honorifics
def replace_titles(col, titles=('\\.', 'mrs', 'mr', 'miss', 'dvm', 'md', 'dr', 'jr', 'sir', 'lady', 'lord')):
	for t in titles:
		col = regexp_replace(lower(col), t, '')
	return col

# Start spark session
def init_spark(app_name):
	logging.info("STARTING SPARK SESSION")
	spark = SparkSession.builder.appName(app_name).getOrCreate()
	spark.conf.set("spark.sql.legacy.timeParserPolicy","LEGACY")
	return spark

# Read all CSV files in the input directory
def read_input(spark):
	input_dir = app_folder + '/input/latest/' + '*.csv'	
	logging.info("READING INPUT FILES")
	return spark.read.csv(input_dir, header='true')

def set_successful_output(day_now,hour_now):
	return app_folder + '/output/successful/' + day_now + '/' + hour_now

def set_unsuccessful_output(day_now,hour_now):
	return app_folder + '/output/unsuccessful/' + day_now + '/' + hour_now

# Split name into first_name and last_name
def process_name(df):
	logging.info("PROCESSING NAMES")

	df = df.withColumn('name_formatted',replace_titles(col('name')))
	df = df.withColumn('name_formatted', when(trim(col('name_formatted'))==lit(''),None).otherwise(trim(col('name_formatted'))))
	split_col = pyspark.sql.functions.split(df['name_formatted'], ' ')
	df = df.withColumn('first_name', split_col.getItem(0))
	df = df.withColumn('last_name', split_col.getItem(size(split_col)-1))
	return df

# Format birthday field into YYYYMMDD
def process_birthday(df):
	logging.info("PROCESSING BIRTHDAYS")
	df = df.withColumn('birthday_formatted', cast_date_string(col('date_of_birth')))
	df = df.withColumn('birthday', cast_date(col('date_of_birth')))
	return df

# Process tag unsuccessful applications 
def process_unsuccessful_applications(df):
	logging.info("PROCESSING UNSUCCESSFUL APPLICATIONS")

	#check for 8 digits while ignoring whitespaces
	eight_digits_regex = """^\\s*(\\d\\s*){8}$"""

	#(?!\.) don't allow . at start
	#(?!.*\.\.) don't allow consecutive dots
	#(?!.*\.$) don't allow dots at the end
	#(\\.com|\\.net) must end with either .com or .net
	#[^.]@[^.] don't allow dots infront or behind @
	#[a-zA-Z0-9._%+-] allow a-Z, A-Z, 0-9, .%+-
	#[a-zA-Z0-9.+-] allow a-z, A-Z, 0-9, .+-
	email_regex = """^(?!\\.)(?!.*\\.$)(?!.*\\.\\.)[a-zA-Z0-9._%+-]+[^.]@[^.][a-zA-Z0-9.+-]+(\\.com|\\.net)$"""

	df = df.withColumn('start_of_year',lit('2022-01-01'))

	#Check invalid names
	df = df.withColumn('invalid_name',when(col('name').isNull(),True)
		.when(trim(col('name').cast('string'))=='',True)
		.otherwise(False))

	#check invalid mobile numbers
	df = df.withColumn('invalid_mobile',when(col('mobile_no').rlike(eight_digits_regex)==False,True).otherwise(False))

	#Check invalid emails
	df = df.withColumn('invalid_email',when(col('email').rlike(email_regex)==False,True).otherwise(False))

	#Check if age is below 18 years old as of 2022-01-01
	df = df.withColumn('below_18',when(months_between(col('start_of_year'),col('birthday'))/lit(12) < 18.0,True).otherwise(False))

	df = df.withColumn('unsuccessful', when(col('invalid_name'),True)
		.when(col('invalid_mobile'),True)
		.when(col('invalid_email'),True)
		.when(col('below_18'),True)
		.otherwise(False))

	return df

# Create a new field named above_18 based on the applicant's birthday.
def process_above_18(df):
	logging.info("PROCESSING AGES")
	df = df.withColumn("above_18",when(col('below_18'),False)
		.otherwise(True))
	return df

# Membership IDs for successful applications should be the user's last name, 
# followed by a SHA256 hash of the applicant's birthday, 
# truncated to first 5 digits of hash (i.e <last_name>_<hash(YYYYMMDD)>)
def process_membership_id(df):
	logging.info("PROCESSING MEMBERSHIP IDs")
	df = df.withColumn("membership_id", concat(col('last_name'), lit('_'), sha2(cast_date_string(col('birthday')),256).substr(0,5)) )
	return df

def filter_and_write(df):
	# Filtering unsuccessful applications
	unsuccessful_df = df.filter(col('unsuccessful')==True)
	unsuccessful_df = unsuccessful_df.withColumn('unsuccessful_reason', when(col('invalid_name'),'invalid name')
		.when(col('invalid_mobile'),'invalid mobile')
		.when(col('invalid_email'),'invalid email')
		.when(col('below_18'),'below 18')
		.otherwise('NA'))
	successful_df   = df.filter(col('unsuccessful')==False)

	successful_df = successful_df.select(col('first_name'),col('last_name'),col('birthday_formatted'),col('above_18'),col('membership_id'))
	unsuccessful_df = unsuccessful_df.select(col('name'),col('email'),col('date_of_birth'),col('mobile_no'),col('unsuccessful_reason'))

	# Get current date time
	now = datetime.now()
	day_now = now.strftime('%Y%m%d')
	hour_now = now.strftime('%H')

	# Set output directory appended with current date time
	successful_output_dir = set_successful_output(day_now,hour_now)
	unsuccessful_output_dir = set_unsuccessful_output(day_now,hour_now)

	# Write output to csv
	# If output needs to be written to a single file, use coalesce(1) or FileUtils.copyMerge
	logging.info("WRITING TO OUTPUT FILES")
	successful_df.write.option('header',True).mode("overwrite").csv(successful_output_dir)
	unsuccessful_df.write.option('header',True).mode("overwrite").csv(unsuccessful_output_dir)


# Set input directory to read in files
def main():

	logging.info("JOB STARTED")

	spark = init_spark('process_datasets')

	df = read_input(spark)

	df = process_name(df)

	df = process_birthday(df)

	df = process_unsuccessful_applications(df)

	df = process_above_18(df)

	df = process_membership_id(df)

	filter_and_write(df)
	
	logging.info("JOB COMPLETED, ARCHIVING FILES...")

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		logging.error("Exception: " + str(e))
		sys.exit(1)