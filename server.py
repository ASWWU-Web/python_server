import logging
import signal
import tornado.autoreload
import tornado.web
import os
from tornado.options import define
import asyncio


# environment variables
from dotenv import load_dotenv
load_dotenv()

# import settings
from settings import config

if __name__ == "__main__":
    # TODO: generate env
    if not os.environ['ENVIRONMENT'] or not os.environ['HMAC_KEY'] or not os.environ['SAML_ENDPOINT_KEY']:
        print("Environment variables are not set. Please set them in the .env file.")
        exit(1)
    env = os.environ['ENVIRONMENT']


    # allow command line arguments e.g. `python server.py --port=8881`
    define("port", default=config.server.get('port'), help="run on the given port", type=int)
    define("log_name", default=config.logging.get('log_name'), help="name of the logfile")
    define("current_year", default=config.mask.get('current_year'), help="current school year")
    tornado.options.parse_command_line()

    
    # setup logger
    logger = logging.getLogger(config.logging.get('log_name'))
    logger.setLevel(config.logging.get('level'))
    fh = logging.FileHandler("src/aswwu/"+tornado.options.options.log_name+".log")
    formatter = logging.Formatter("{'timestamp': %(asctime)s, 'loglevel' : %(levelname)s %(message)s }")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    print("Running in the " + env + " environment")
    assert env != "pytest"  # the pytest environment should never be used here
    from src.aswwu.application import start_server, stop_server
    signal.signal(signal.SIGINT, stop_server)
    signal.signal(signal.SIGTERM, stop_server)
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt as e:
        stop_server(e, None)
