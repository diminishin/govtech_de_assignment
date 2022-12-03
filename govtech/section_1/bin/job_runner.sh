app_folder="/Users/eechuanchang/workdir/govtech/section_1"

spark-submit \
  --master local \
  --deploy-mode client \
  process_datasets.py $app_folder