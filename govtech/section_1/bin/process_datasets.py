from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
import pyspark
from pyspark.sql.functions import split, col, size, when, to_date, coalesce, date_format, months_between, lit, current_date, round, trim, sha2, concat
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

# Start spark session
def init_spark(app_name):
	logging.info("STARTING SPARK SESSION")
	spark = SparkSession.builder.appName(app_name).getOrCreate()
	spark.conf.set("spark.sql.legacy.timeParserPolicy","LEGACY")
	return spark

def read_input(spark):
	input_dir = app_folder + '/input/latest/' + '*.csv'
	# Read all CSV files in the input directory
	logging.info("READING INPUT FILES")
	return spark.read.csv(input_dir, header='true')

def set_successful_output(day_now,hour_now):
	return app_folder + '/output/successful/' + day_now + '/' + hour_now

def set_unsuccessful_output(day_now,hour_now):
	return app_folder + '/output/unsuccessful/' + day_now + '/' + hour_now

# Split name into first_name and last_name
def process_name(df):
	logging.info("PROCESSING NAMES")
	df = df.withColumn('name', when(trim(col('name'))==lit(''),None).otherwise(col('name')))
	split_col = pyspark.sql.functions.split(df['name'], ' ')
	df = df.withColumn('first_name', split_col.getItem(0))
	df = df.withColumn('last_name', split_col.getItem(size(split_col)-1))
	return df

# Format birthday field into YYYYMMDD
def process_birthday(df):
	logging.info("PROCESSING BIRTHDAYS")
	df = df.withColumn('birthday_formatted', cast_date_string(col('date_of_birth')))
	df = df.withColumn('birthday', cast_date(col('date_of_birth')))
	return df

# Remove any rows which do not have a name field (treat this as unsuccessful applications)
def process_unsuccessful_applications(df):
	logging.info("PROCESSING UNSUCCESSFUL APPLICATIONS")
	df = df.withColumn('unsuccessful', when(col('name').isNull(),True)
		.when(trim(col('name').cast('string'))=='',True)
		.otherwise(False)
		)
	return df

# Create a new field named above_18 based on the applicant's birthday
def process_above_18(df):
	logging.info("PROCESSING AGES")
	df = df.withColumn("above_18",when(months_between(current_date(),col('birthday'))/lit(12) > 18.0,True)
		.otherwise(False))
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
	successful_df   = df.filter(col('unsuccessful')==False)

	successful_df = successful_df.select(col('first_name'),col('last_name'),col('birthday_formatted'),col('above_18'),col('membership_id'))
	unsuccessful_df = unsuccessful_df.select(col('first_name'),col('last_name'),col('birthday_formatted'),col('above_18'),col('membership_id'))

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