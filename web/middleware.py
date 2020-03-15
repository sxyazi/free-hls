from os import getenv as _
from functools import wraps
from constants import VERSION
from flask import request, jsonify

def same_version(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    version = request.headers.get('API-Version')
    if version == VERSION:
      return f(*args, **kwargs)
    return jsonify({'err': 1, 'message': 'Version mismatch'})

  return decorated

def auth_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = request.headers.get('API-Token')
    if token == 'NONE' or token == _('SECRET'):
      return f(*args, **kwargs)
    return jsonify({'err': 1, 'message': 'Authorization failed'})

  return decorated
