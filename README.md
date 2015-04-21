# Torn-tweet

A Tornado written Twitter like stream with WebSockets

Do you need a twitter like Follower - Following real time tweeting , that too scalable with Websockets and has Tornado simplicity. Then Use this Torn-tweet.

Before using this just install tornado and redis

```
$ pip install tornado

$ pip install redis
```


Now run as

```
$ python tweetdemo.py
```

Now Go to default tornado running address ,http://localhost:8888/ to tweet 

open http://localhost:8888/client to recieve those messages instantly.

Extending Torn-Tweet 

We can also have specific subscribers for a channel. It is a work of doing isSubscribed on redis to a channel. Channel is the user whom clients are following. In our application we hardcoded channel as "fitness". You can extend it as your requirements.i gave a running tempate for Web-sockets.
