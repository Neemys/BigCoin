import re
import datetime

# Global values
date_y_m_d_pattern = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}$")

# Test if a date format is valid. Format is YYYY-mm-dd
def is_date_format_yyyy_mm_dd_valid(date_string):
	if isinstance(date_string, basestring) and date_y_m_d_pattern.match(date_string):
		return True
	return False


# Return the given datetime as a string date format valid (YYYY-mm-dd). Return today's date if no datetime given
def get_date_string_yyyy_mm_dd_from_datetime(date_time):
	if not isinstance(date_time,datetime.datetime):
		date_time = datetime.datetime.today()
	return date_time.strftime("%Y-%m-%d")

# Get a datetime object from a string date with the format YYYY-mm-dd, return None if string don't have correct format
def get_datetime_from_string(date_string):
	if date_string  is not None and is_date_format_yyyy_mm_dd_valid(date_string):
		year,month,day = date_string.split('-')
		return datetime.datetime(int(year),int(month),int(day))
	return None

# Add a day to the given date as string and return the new date as string. If the date format is not valid, return None
def increment_a_day_from_date_as_string(date_string):
	if date_string  is not None and is_date_format_yyyy_mm_dd_valid(date_string):
		new_date = get_datetime_from_string(date_string) + datetime.timedelta(days=1)
		return get_date_string_yyyy_mm_dd_from_datetime(new_date)
	return None
