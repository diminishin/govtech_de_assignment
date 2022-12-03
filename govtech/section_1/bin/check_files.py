import sys
from datetime import datetime
import logging
import os

app_folder = sys.argv[1]
log_file = app_folder + "/logs/check_files_" + datetime.now().strftime('%d%m%Y_%H%M%S') + ".log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s %(message)s")

if __name__ == "__main__":
	src_path = app_folder + '/input/latest'
	if any(File.endswith(".csv") for File in os.listdir(src_path)):
		logging.info("CSV files exists")
	else:
		logging.info("No CSV files found")
		sys.exit(1)