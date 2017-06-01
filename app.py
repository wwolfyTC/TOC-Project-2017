import sys, logging, io

import telegram
from flask import Flask, request
from pymongo import MongoClient

from fsm import TocMachine, state, trans


API_TOKEN = '388400415:AAFx5ItNe1gIQNaO8MeC5NMlo7FK09QeCLc'
WEBHOOK_URL = 'https://e68af3b4.ngrok.io/hook'

logging.basicConfig(
	format='%(asctime)s [%(levelname)s]: %(message)s', 
	datefmt='%Y/%m/%d %X', 
	level=logging.INFO
)

# database connect
try:
	with open('../pw', 'r', encoding='utf-8') as fin:
		pw = fin.readline().strip()
except Exception:
	print('can not find password file')
	exit()

DBuri = ('mongodb://wwolfyTC:{0}@'
	'clibrary-shard-00-00-syrdm.mongodb.net:27017,'
	'clibrary-shard-00-01-syrdm.mongodb.net:27017,'
	'clibrary-shard-00-02-syrdm.mongodb.net:27017/'
	'admin?ssl=true&replicaSet=CLIbrary-shard-0'
	'&authSource=admin').format(pw)

cli = MongoClient(DBuri)
collect = cli.CLibrary.library

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)

machine = TocMachine(
	states=state,
	transitions=trans,
	initial='home',
	auto_transitions=False
)


@app.route('/hook', methods=['POST'])
def webhook_handler():
	update = telegram.Update.de_json(request.get_json(force=True), bot)
	if update.message is None:
		logging.info('no message')
		return 'ok'

	if update.message.text[0] == '/':
		machine.cmd(update)
	else:
		machine.query(update, collect)

	return 'ok'




if __name__ == "__main__":
	logging.info('initializing')

	status = bot.set_webhook(WEBHOOK_URL)
	if not status:
		logging.error('set webhook failed')
		sys.exit(1)
	else:
		logging.info('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))

	app.run(port=8080)
