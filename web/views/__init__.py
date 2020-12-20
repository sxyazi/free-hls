import os
from flask import Flask
from os import getenv as _
from constants import VERSION

app = Flask(__name__, root_path=os.getcwd())
# app.config['MAX_CONTENT_LENGTH'] = 20 << 20

app.add_template_global(name='VERSION', f=VERSION)
app.add_template_global(name='SECRET', f=_('SECRET'))

from . import api, home, manage, static
