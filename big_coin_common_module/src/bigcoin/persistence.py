import sys
import os.path
import bigcoin.date as bcdate

# Get a date from the first line of the file. Return the date in a valid format (YYY-mm-dd), None otherwise.
def get_date_from_file(filepath_and_name):
	if(not os.path.isfile(filepath_and_name)):
		return None
	try:
		with open(filepath_and_name,'r') as f:
			maybe_date = f.readline()
	except IOError:
		sys.exit(40)# Exit with file error
	if bcdate.is_date_format_yyyy_mm_dd_valid(maybe_date):
		return maybe_date
	return None

# Save the given date string to the given file
def save_date_to_file(filepath_and_name,date_string):
	try:
		with open(filepath_and_name,'w') as f:
			f.write(date_string)
	except IOError:
		sys.exit(40)# Exit with file error
