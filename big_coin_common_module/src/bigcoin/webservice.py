import sys
import requests


# Call the provided api address and return the resulting JSON.
# Exit when return code is not ok or the api timed out
def get_json_from_address(api_address):
	try:
		res = requests.get(api_address,timeout=10)
		if res.status_code == requests.codes.ok:
			return res.json()
		else:
			sys.exit(20) #Exit with response not ok error
	except requests.exceptions.Timeout:
		sys.exit(10) #Exit with timeout error code
