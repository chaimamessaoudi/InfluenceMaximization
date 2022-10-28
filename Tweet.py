class Tweet:
	def __init__(self, idt, text, pre, lang, topics, nb_likes, nb_replies, nb_retweets, opinion):
		self.idt = idt
		self.text = text
		self.pre = pre
		self.lang = lang
		self.topics = topics
		self.nb_likes = nb_likes
		self.nb_replies = nb_replies
		self.nb_retweets = nb_retweets
		self.opinion=opinion 