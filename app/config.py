import json

with open("config.json") as f:
  config_file = json.load(f)

  FREE_MINUTES = config_file.get('FREE_MINUTES')
  TIME_FRAME_HOURS = config_file.get('TIME_FRAME_HOURS')
  TIME_FRAME_TARIFFS = config_file.get('TIME_FRAME_TARIFFS')
  TOTAL_SPOTS = config_file.get('TOTAL_SPOTS')
  DATE_TIME_FORMAT = config_file.get('DATE_TIME_FORMAT')