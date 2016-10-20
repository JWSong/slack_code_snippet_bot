import os

DEBUG = os.environ.get('DEBUG', 0)
TOKEN = os.environ.get('SLACK_BOT_TOKEN')
TIMEOUT = os.environ.get('TIMEOUT', 30)
