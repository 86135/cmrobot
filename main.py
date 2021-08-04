import requests as req
from json import dumps,loads
from pprint import pprint
import time
"""bcm robot"""
class baserobot(object):
	"""机器人基类，如果需要继承，需重写jumpto和run方法。"""
	def __init__(bot):
		bot.cookie=''
		bot.cmds={}
		bot.func=lambda:''
		bot.wcm=lambda:''
		bot._=''
	def welcomefunc(bot,func):
		bot.wcm=func
		return func
	def set_welcome_text(bot,text):
		bot.welcomefunc(lambda:text)
	def log_in(bot,cookie):
		bot.cookie=cookie
	def _cmd(bot,func):
		bot.cmds[bot._]=func
		return func
	def cmd(bot,s):
		bot._=s
		return bot._cmd
	def other(bot,func):
		bot.func=func
		return func
	def _get_reply(bot,s):
		for i,j in bot.cmds.items():
			if s.startswith(i+' '):
				return j(s)
		return bot.func(s)
	def jumpto(bot,_id,mess=''):
		"""重写这个方法"""
		raise NotImplementedError
	def run(bot,startid):
		"""重写这个方法"""
		raise NotImplementedError
class PostsRobot(baserobot):
	"""帖子下的聊天机器人。"""
	def jumpto(bot,_id,mess=''):
		a=mess
		if mess=='':
			a=bot.wcm()
		bot.sess.post('https://api.codemao.cn/web/forums/posts/{}/replies'.format(_id),data=dumps({"content":a}),headers={'Content-Type': 'application/json',"cookie":bot.cookie})
	def run(bot,startid,username):
		bot.sess=req.Session()
		bot.jumpto(startid)
		while True:
			time.sleep(0.1)
			r=bot.sess.get("https://api.codemao.cn/web/message-record?query_type=COMMENT_REPLY&limit=10&offset=0",headers={"cookie":bot.cookie}).json()
			if len(r['items'])==0:
				continue
			if r['items'][0]['read_status']=='READ':
				continue
			if r['items'][0]['type'] not in ['POST_REPLY','POST_REPLY_REPLY']:
				continue
			data=loads(r['items'][0]['content'])
			if r['items'][0]['type']=='POST_REPLY':
				a=bot.sess.post('https://api.codemao.cn/web/forums/replies/{}/comments'.format(data['message']['replied_id']),data=dumps({"content":bot._get_reply(data['message']['reply']),"parent_id":0}),headers={'Content-Type': 'application/json',"cookie":bot.cookie})
			else:
				post=bot.sess.get('https://api.codemao.cn/web/forums/posts/{}/replies?page=1&limit=10&sort=-created_at'.format(data['message']['business_id'])).json()['items']
				if len(post)==0 or post[0]['user']['nickname']!=username:
					continue
				a=bot.sess.post('https://api.codemao.cn/web/forums/replies/{}/comments'.format(post[0]['id']),data=dumps({"content":bot._get_reply(data['message']['reply']),"parent_id":data['message']['reply_id']}),headers={'Content-Type': 'application/json',"cookie":bot.cookie})
			if a.status_code!=201:
				pprint(a.json())
				exit(1)
