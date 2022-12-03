from pathlib import Path
import shutil
import os
import glob
import sys
from datetime import datetime
import logging

app_folder = sys.argv[1]
log_file = app_folder + "/logs/archive_files_" + datetime.now().strftime('%d%m%Y_%H%M%S') + ".log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s %(message)s")

def main():
	logging.info("JOB STARTED")
	src_path = app_folder + '/input/latest'
	arc_path = app_folder + '/input/archive'

	for src_file in Path(src_path).glob('*.csv'):
		shutil.move(os.path.join(src_path,src_file),arc_path)

	logging.info("JOB COMPLETED")

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		logging.error("Exception: " + str(e))