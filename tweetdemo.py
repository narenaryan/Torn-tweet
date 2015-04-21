import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid ,redis

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
    	#Creating 3 handlers. one for Follower,remaining for Following,one for Websockets
        handlers = [
            (r"/", MainHandler),
            (r"/client",ClientHandler),
            (r"/tweetsocket", TweetSocketHandler),
        ]
        
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

#Person who publish tweets
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=TweetSocketHandler.cache)

#Persons who receive tweets
class ClientHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("client.html", messages=TweetSocketHandler.cache)

class TweetSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200
    redis_client = redis.client.StrictRedis()
    subscriber_handle = redis_client.pubsub()

    #Over ride websocket Handler methods
    def open(self):
    	#Add open websockets to waiter's list
        TweetSocketHandler.waiters.add(self)

    def on_close(self):
    	#Remove waiter if connection closed
        TweetSocketHandler.waiters.remove(self)

    @classmethod
    def publish_tweet(cls, tweet):
    	#Let us assume we are publishing to a channel(following Twitter account) called fitness 
        cls.cache.append(tweet)
        logging.info("Published message",tweet)
        cls.redis_client.publish('fitness',tweet)

    #Send tweets to all the subscribers instantly through open web sockets
    @classmethod
    def send_tweets(cls, tweet):
    	logging.info("Sending tweets to clients!")
        for waiter in cls.waiters:
            try:
                waiter.write_message(tweet)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        tweet = {
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
            }
        tweet["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=tweet))
        
        #On message save it in Redis 
        TweetSocketHandler.publish_tweet(tweet)
        #Send same message to all clients opened
        TweetSocketHandler.send_tweets(tweet)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
