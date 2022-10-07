import os
import glob

list_of_files = glob.glob('uploads/*', recursive=False) # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
remove_last = latest_file[:-5]
slimmed_file = remove_last[8:]
print(slimmed_file)

#latest_path = "exports/" + latest_file
