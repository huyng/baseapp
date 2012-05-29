import os.path as P

APP_DIR              = P.dirname(P.abspath(__file__)) 
PROJECT_DIR          = P.dirname(APP_DIR)
DEPLOY_CONTAINER_DIR = P.dirname(PROJECT_DIR)
VAR_DIR              = P.join(PROJECT_DIR, 'var') # data generated at runtime

VENV_DIR               = P.join(PROJECT_DIR, 'env')
VENV_ACTIVATE_THIS     = P.join(VENV_DIR, 'bin/activate_this.py')
ALREADY_RUN            = False

def setup():
    global ALREADY_RUN
    if ALREADY_RUN:
        raise EnvSetupError
    execfile(VENV_ACTIVATE_THIS, dict(__file__=VENV_ACTIVATE_THIS))
    ALREADY_RUN = True

class EnvSetupError(Exception):
    def __init__(self):
        Exception.__init__(self, "You have already setup the environment. Only run the setup() function once")



    



