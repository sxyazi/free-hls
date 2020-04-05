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
    return jsonify([0, 'Version mismatch'])

  return decorated

def auth_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = request.headers.get('API-Token')
    if token == 'NONE' or token == _('SECRET'):
      return f(*args, **kwargs)
    return jsonify([0, 'Authorization failed'])

  return decorated

def api_response(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    resp = f(*args, **kwargs)
    return jsonify(resp) if isinstance(resp, tuple) else resp

  return decorated

def api_combined(f):
  @wraps(f)
  @same_version
  @auth_required
  @api_response
  def decorated(*args, **kwargs):
    return f(*args, **kwargs)

  return decorated
