# ------------ gunicorn settings -----------
# hostname and port at which application will be served
bind = '0.0.0.0:8000'

# when starting gunicorn, print it's current configuration
print_config = False

# number of cores being busy with the cafe system
workers = 8

# timeout of workers, i.e. cap execution time
# currently, set to an hour!!
timeout = 3610

worker_class = 'sync'

acceslogformat = "%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"

# file path for access logging
accesslog = 'LOGS/access_log_bellmanscafe.log'

# file path for error logging
errorlog = 'LOGS/error_log_bellmanscafe.log'

# also send app.logger.info messages to errorlog
capture_output = True

loglevel = "debug"

# ------------ flask settings --------------
DEBUG = False

# ---------- bellman's cafe settings -------

# the Cafe shall let users interact with a collection of Bellman's GAP
# programs like Needleman-Wunsch or ElMamun. The FP_GAPUSERSOURCES variable
# must point to the path containing these sources.
FP_GAPC_PROGRAMS = "../ADP_collection/"

# user submission leads to compilation and execution of new algera products
# if the user re-submits the same algebra product (also called instance) it
# does not need to be re-computed, therefore we are using a cache. JUST
# this instance with user inputs have to be run.
FP_CACHE = "DOCKER/bcafe_cache/"

# don't forget to leave a changelog message
CAFE_VERSION = "2.4"

# maximum number of allowed algebras
MAX_ALGEBRAS = 5

# limit tikZ image generation to:
LIMIT_CANDIDATE_TREES = 20

# maximum output lines:
MAX_OUTPUT_LINES = 5000

MAX_CPU_TIME = timeout - 10  # an hour +/- 10 seconds
