## Section1: Data Pipelines

Explaination of solution.

Airflow choosen as the scheduling tool. Kindly refer to spark_dag_runner.py for the dag configuration. It is currently set up to run at minute 0 hourly.

There are three stages in the dag.

1. Check if input files exist. If yes, proceed to next. (check_files.py)
2. Process input datasets according to requirements. Once done, output files into successful and unsuccessful folders. (process_datasets.py)
3. Archive input files. (archive_files.py)

Spark is choosen as the processing tool.

Code is written in pyspark.
