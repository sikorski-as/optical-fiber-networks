import requests
import geomanip
from os.path import isfile


style_urls = {
	# needs placeholders for api parameters: center_long, center_lati, zoom, map_width, map_height, api_token
	'dark': 'https://api.mapbox.com/styles/v1/mapbox/dark-v9/static/{},{},{}/{}x{}?access_token={}',
	'countries_basic': 'https://api.mapbox.com/styles/v1/mcsqueezie/cjuzqthv51t001fs6e6mmelrl/static/{},{},{}/{}x{}?access_token={}',
}


def _request_link(style: str, projection: geomanip.Projection, api_token: str):
	link = style_urls[style].format(
		projection.center_long,
		projection.center_lati,
		projection.zoom,
		projection.map_width,
		projection.map_height,
		api_token
	)
	return link


def get_map_as_file(filename, style: str, projection: geomanip.Projection, api_token: str, replace: bool = True):
	if not replace and isfile(filename):
		return False
	try:
		url = _request_link(style, projection=projection, api_token=api_token)
		r = requests.get(url, allow_redirects=True)
		if r.status_code != requests.codes.ok:
			return False
		with open(filename, 'wb') as f:
			f.write(r.content)
		return True
	except Exception as e:
		print(e)
		return False
