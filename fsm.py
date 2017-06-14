import io, logging
from random import randint

from transitions import Machine
from fuzzywuzzy import process


class TocMachine(object):
	def __init__(self, **machine_configs):
		self.machine = Machine(
			model = self,
			**machine_configs
		)
		self.mode = 'all'
		self.lastResult = None


	def cmd_home(self, update):
		return update.message.text[0:5] == '/home'
	"""
	def cmd_head(self, update):
		return update.message.text[0:5] == '/head'
	"""

	def cmd_link(self, update):
		return update.message.text[0:5] == '/link'

	def cmd_arg(self, update):
		return update.message.text[0:4] == '/arg'

	def cmd_help(self, update):
		return update.message.text[0:5] == '/help'

	def cmd_all(self, update):
		return update.message.text[0:5] == '/all'

	def cmd_function(self, update):
		return update.message.text[0:9] == '/function'

	def cmd_header(self, update):
		return update.message.text[0:7] == '/header'

	def cmd_macro(self, update):
		return update.message.text[0:6] == '/macro'

	def cmd_type(self, update):
		return update.message.text[0:5] == '/type'



	def on_enter_help(self, update):
		with io.StringIO() as replyBuffer:
			replyBuffer.write(
					'OK, here are some commands:\n'
					'*/help*: show this help message\n'
					'*/all*: switch query mode to _all_\n'
					'*/function*: switch query mode to _function_\n'
					'*/header*: switch query mode to _header_\n'
					'*/macro*: switch query mode to _macro_\n'
					'*/type*: switch query mode to _type_\n'
					'*/arg N*: show the description of Nth argument, where N is a non-negitive integer\n'
					'*/link*: show the link of the web page which conains full description of this item\n'
				)
			update.message.reply_text(replyBuffer.getvalue(), parse_mode="Markdown")
			self.go_back(update)

	def on_enter_all(self, update):
		logging.info('mode switch to "all"')
		update.message.reply_text("ok, switch mode to _all_", parse_mode='Markdown')
		self.mode = 'all'
		self.go_back(update)

	def on_enter_function(self, update):
		logging.info('mode switch to "function"')
		update.message.reply_text('ok, switch mode to _function_', parse_mode='Markdown')
		self.mode = 'function'
		self.go_back(update)

	def on_enter_header(self, update):
		logging.info('mode switch to "header"')
		update.message.reply_text('ok, switch mode to _header_\n', parse_mode='Markdown')
		self.mode = 'header'
		self.go_back(update)

	def on_enter_macro(self, update):
		logging.info('mode switch to "macro"')
		update.message.reply_text('ok, switch mode to _macro_\n', parse_mode='Markdown')
		self.mode = 'macro'
		self.go_back(update)

	def on_enter_type(self, update):
		logging.info('mode switch to "type"')
		update.message.reply_text('ok, switch mode to _type_\n', parse_mode='Markdown')
		self.mode = 'type'
		self.go_back(update)

	def on_enter_query(self, update, collect):
		msg = update.message.text
		logging.info('receive query: {}'.format(msg))

		rd = randint(1, 3)
		if rd == 1:
			update.message.reply_text('A query? let me see...')
		elif rd == 2:
			update.message.reply_text('OK, just gimme a few seconds...')
		elif rd == 3:
			update.message.reply_text('Alright, let\'s look about that...')
		

		if self.mode == 'all':
			result = collect.find_one({'name':msg})
		else:
			result = collect.find_one({'name':msg, 'itemType':self.mode})

		self.lastResult = result

		if result is None:
			if self.mode == 'all':
				nameList = [item['name'] for item in collect.find({})]
			else:
				nameList = [item['name'] for item in collect.find({'itemType':self.mode})]

			possiblilties = [p for (p, score) in process.extract(msg, nameList, limit=7) if score >= 70]
			with io.StringIO() as replyBuffer:
				if len(possiblilties) == 0:
					replyBuffer.write('No matched result')
				else:
					replyBuffer.write('No matched result, maybe you mean one of these?\n\n')
					for p in possiblilties:
						replyBuffer.write('> ' + p + '\n')
				update.message.reply_text(replyBuffer.getvalue())
			self.go_back(update)
		else:
			with io.StringIO() as replyBuffer:
				replyBuffer.write('<i>%s</i> defined in <i>&lt;%s&gt;</i>\n'%(result['itemType'], result['header']))
				if result['prototype'] == '':
					replyBuffer.write('<code>' + result['name'] + '</code>\n')
				else:
					replyBuffer.write('<code>' + result['prototype'] + '</code>\n')

				replyBuffer.write('<b>' + result['description'] + '</b>\n')
				replyBuffer.write('return value: ' + result['returnVal'] + '\n')
				replyBuffer.write('<a href="%s">(full introduction)</a>\n'%(result['link']))
				update.message.reply_text(replyBuffer.getvalue(), parse_mode='HTML')
			self.go_back(update)

	"""
	def on_enter_head(self, update):
		update.message.reply_text('`%s` is defined in `%s`'%(self.lastResult['name'], self.lastResult['header']) , parse_mode='Markdown')
		self.go_back(update)
	"""

	def on_enter_link(self, update):
		if self.lastResult is None:
			update.message.reply_text('No query history, please do some query first')
		else:
			update.message.reply_text('OK, you can fine it <a href="%s">here</a>'%(self.lastResult['link']) , parse_mode='HTML')
		self.go_back(update)

	def on_enter_arg(self, update):
		if self.lastResult is None:
			update.message.reply_text('No query history, please do some query first')
			self.go_back(update)
			return

		if len(self.lastResult['params']) == 0:
			update.message.reply_text("there's no argument for this item")
			self.go_back(update)
			return

		try:
			idx = int(update.message.text[5:])
			if idx < 0 or idx >= len(self.lastResult['params']):
				raise ValueError('out of bound')
		except:
			update.message.reply_text('Invalid argument')
			self.go_back(update)
			return

		par = self.lastResult['params'][idx]
		update.message.reply_text('*%s*\n'%(par['name']), parse_mode='Markdown')
		update.message.reply_text('%s\n'%(par['description']))

		self.go_back(update)


state = ['home', 'all', 'function', 'header', 'macro', 'type', 'help', 'arg', 'link', 'query']

trans = [
	{
		'trigger':'query',
		'source':'home',
		'dest':'query'
	},
	{
		'trigger':'cmd',
		'source':'home',
		'dest':'arg',
		'conditions':'cmd_arg'
	},
	{
		'trigger':'cmd',
		'source':'home',
		'dest':'link',
		'conditions':'cmd_link'
	},
	{
		'trigger':'cmd',
		'source':'home',
		'dest':'help',
		'conditions':'cmd_help'
	},
	{
		'trigger':'cmd',
		'source':'home',
		'dest':'all',
		'conditions':'cmd_all'
	},
	{
		'trigger':'cmd',
		'source':'home',
		'dest':'function',
		'conditions':'cmd_function'
	},
	{
		'trigger':'cmd',
		'source':'home',
		'dest':'header',
		'conditions':'cmd_header'
	},
	{
		'trigger':'cmd',
		'source':'home',
		'dest':'macro',
		'conditions':'cmd_macro'
	},
	{
		'trigger':'cmd',
		'source':'home',
		'dest':'type',
		'conditions':'cmd_type'
	},
	{
		'trigger':'go_back',
		'source':'*',
		'dest':'home'
	}
]