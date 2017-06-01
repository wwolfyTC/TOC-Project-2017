import io, logging

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

	def cmd_head(self, update):
		return update.message.text[0:5] == '/head'

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



	def on_enter_home(self, update):
		self.lastResult = None

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
					'\nAfter you got some query result, you can use these commands to get more detail:\n'
					'*/head*: show the header which the item belongs to\n'
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

		update.message.reply_text('A query? let me see...')

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

			possiblilties = [p for (p, score) in process.extract(msg, nameList) if score >= 70]
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
				replyBuffer.write('*' + result['itemType'] + '*\n')
				if result['prototype'] == '':
					replyBuffer.write('```' + result['name'] + '```\n')
				else:
					replyBuffer.write('```' + result['prototype'] + '```\n')
				update.message.reply_text(replyBuffer.getvalue(), parse_mode='Markdown')

			with io.StringIO() as replyBuffer:
				replyBuffer.write(result['description'] + '\n\n')
				replyBuffer.write(result['returnVal'] + '\n')
				update.message.reply_text(replyBuffer.getvalue())
			self.found()

	def on_enter_head(self, update):
		update.message.reply_text('`%s` is defined in `%s`'%(self.lastResult['name'], self.lastResult['header']) , parse_mode='Markdown')
		self.go_back(update)

	def on_enter_link(self, update):
		update.message.reply_text('`%s` is on page\n%s'%(self.lastResult['name'], self.lastResult['link']) , parse_mode='Markdown')
		self.go_back(update)

	def on_enter_arg(self, update):
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


state = ['home', 'all', 'function', 'header', 'macro', 'type', 'help', 'head', 'arg', 'link', 'query', 'result']

trans = [
	{
		'trigger':'query',
		'source':['home', 'result'],
		'dest':'query'
	},
	{
		'trigger':'found',
		'source':'query',
		'dest':'result'
	},
	{
		'trigger':'cmd',
		'source':'result',
		'dest':'head',
		'conditions':'cmd_head'
	},
	{
		'trigger':'cmd',
		'source':'result',
		'dest':'arg',
		'conditions':'cmd_arg'
	},
	{
		'trigger':'cmd',
		'source':'result',
		'dest':'link',
		'conditions':'cmd_link'
	},
	{
		'trigger':'cmd',
		'source':'result',
		'dest':'home',
		'conditions':'cmd_home'
	},
	{
		'trigger':'cmd',
		'source':['home', 'result'],
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
		'source':['head', 'arg', 'link'],
		'dest':'result'
	},
	{
		'trigger':'go_back',
		'source':['all', 'header', 'function', 'macro', 'type', 'help', 'query'],
		'dest':'home'
	}
]