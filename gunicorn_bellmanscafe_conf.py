# stolen from https://stackoverflow.com/questions/49909806/
#    logging-in-gunicorn-log-file-is-not-detailed

bind = '0.0.0.0:8000'
workers = '8'
worker_class = 'sync'
accesslog = '/var/log/gunicorn/access_log_bellmanscafe.log'
# accesslog = 'access_log_bellmanscafe.log'
acceslogformat = "%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
errorlog = '/var/log/gunicorn/error_log_bellmanscafe.log'
# errorlog = 'error_log_bellmanscafe.log'
# also send app.logger.info messages to errorlog
capture_output = "True"

app.config['SECRET_KEY'] = 'ultra secret key, only set in server copy of this file'
