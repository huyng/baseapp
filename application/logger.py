import os
import sys
import logging
import warnings

ALREADY_RUN = False

def setup():
    global ALREADY_RUN
    if ALREADY_RUN is True:
        warnings.warn("You've already setup logging. Only run the setup function once")
        return
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) # only publish INFO messages and above, you can dynamically change this later

    # output formats in order from highly detailed to sparse
    # choose from any one of these to add to your handlers
    
    mega_format  = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-7s [Thread:%(thread)d] line:%(lineno)-4s ----\n\n%(message)s', datefmt='%Y-%m-%d|%H:%M:%S')
    kilo_format  = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-7s line:%(lineno)-4s ----\n\n%(message)s', datefmt='%Y-%m-%d|%H:%M:%S')
    micro_format = logging.Formatter('%(asctime)s %(levelname)-7s ---- %(message)s', datefmt='%Y-%m-%d|%H:%M:%S')
    nano_format  = logging.Formatter('%(asctime)s ---- %(message)s', datefmt='%Y-%m-%d|%H:%M:%S')
    pico_format  = logging.Formatter('%(message)s', datefmt='%Y-%m-%d|%H:%M:%S')
    
    # logging levels: DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50
    # handlers can choose the lowest log level that they want to output
    
    # log to stderr by default output handler
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.DEBUG)
    stderr_handler.setFormatter(micro_format)
    root_logger.addHandler(stderr_handler)
    root_logger.info("logging to stderr")
    
    ## uncomment to log to file, defaults to var/app.log
    # import env
    # import os.path as P
    # log_fname = P.join(env.VAR_DIR, "app.log")
    # if not P.exists(env.VAR_DIR):
    #     os.system("mkdir -p '%s' && chmod 755 '%s'" % (env.VAR_DIR, env.VAR_DIR))
    # if not P.exists(log_fname):
    #     os.system("touch '%s' && chmod 666 '%s'" %  (log_fname,log_fname))
    # file_handler = logging.FileHandler(log_fname)
    # file_handler.setLevel(logging.DEBUG)
    # file_handler.setFormatter(micro_format)
    # root_logger.addHandler(file_handler)
    
    
    ## uncomment to send critical or error log messages to redis for further debugging
    # redis_handler   = RedisHandler(host='localhost', port=6379, log_key='MYAPP')
    # redis_handler.setLevel(logging.ERROR)
    # redis_handler.setFormatter(micro_format)
    # root_logger.addHandler(redis_handler)

    
    ALREADY_RUN = True
    




class RedisLogHandler:
    """ 
    Log handler for logging logs into some redis list
    
    performs a LPUSH onto /logs/<log_key>.backlog
    performs a PUBLISH onto /logs/<log_key>.pubsub
    
    - log_key       this is a redis key where you want to store logs for your application
    - host          the redis host (localhost)
    - port          the redis port (6379)
    - db            the database number (0)
    - capped        if this is an integer greather than 0, this specifies how many log records to keep
    
    """
    def __init__(self, log_key, host='localhost', port=6379, db=0, capped=None):
        import redis
        self._formatter = logging.Formatter()
        self._redis = redis.Redis(host=host, port=port, db=db)
        self.redis_backlog_key    = '/logs/%s.backlog' % log_key
        self.redis_pubsub_channel = '/logs/%s.channel' % log_key
        self.capped = capped
        self._level = logging.DEBUG
        self._redis_db = db
        self._redis_host = host
        self._redis_port = port
        

    def handle(self, record):
        try:
            # Perform LPUSH & PUBLISH
            pipeline = self._redis.pipeline()
            pipeline.lpush(self.redis_backlog_key, self._formatter.format(record)) 
            
            # trim the list if capping is turned on
            if isinstance(self.capped, int) and self.capped > 0:
                pipeline.ltrim(self.redis_backlog_key, 0, self.capped - 1)
            pipeline.publish(self.redis_pubsub_channel, "+")
            pipeline.execute()
            
        except:
            # can't do much here; probably redis have stopped responding...
            import warnings
            warnings.warn("Could not log to messages to redis at %s:%s" % (self._redis_host, self._redis_port))

    def setFormatter(self, formatter):
        self._formatter = formatter
        
    @property
    def level(self):
        return self._level
        
    def setLevel(self, val):
        self._level = val

def print_log_targets():
    """Displays the current logging targets"""
    
    def find_level_name(lvl):
        if lvl == logging.DEBUG:
            return "DEBUG"
        elif lvl == logging.INFO:
            return "INFO"
        elif lvl == logging.WARN:
            return "WARN"
        elif lvl == logging.ERROR:
            return "ERROR"
        elif lvl == logging.CRITICAL:
            return "CRITICAL"
        else:
            return "UNKNOWN:%s" % lvl

    log = logging.getLogger()
    handlers = log.handlers
    
    for h in handlers:
        kind = h.__class__.__name__
        if isinstance(h, RedisLogHandler):
            log.info("using %s with level=%s to redis://%s:%s db=%s key=%s", 
                     kind, find_level_name(h.level), h._redis_host, 
                     h._redis_port, h._redis_db, h.redis_backlog_key)
        elif isinstance(h, logging.StreamHandler):
            log.info("using %s with level=%s to %s", 
                     kind, find_level_name(h.level), h.stream.name)
        elif isinstance(h, logging.FileHandler):
            log.info("using %s with level=%s to %s",
                     kind, find_level_name(h.level), h.baseFilename)
        else:
            log.info("using %s with level=%s",
                     kind, find_level_name(h.level))
            
            
class LoggingTimer():
    def __init__(self, action, log_fn=logging.info):
        self.action = action
        self.log_fn = log_fn

    def __enter__(self):
        import time
        self.start = time.time()

    def __exit__(self, *args):
        import time
        self.log_fn("%s took:%d seconds" % (self.action, (time.time() - self.start)))

