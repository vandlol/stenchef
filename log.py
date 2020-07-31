import logging
import misc
config = misc.read_config()

logFormatter = '%(asctime)s -  %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)
# TODO add loglevel handling via config
logging.basicConfig(format=logFormatter, level=logging.DEBUG)

# handler = logging.FileHandler('myLogs.log')
# logger.addHandler(handler)
