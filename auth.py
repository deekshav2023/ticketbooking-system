from functools import wraps
from flask import request,jsonify,current_app
import jwt
from datetime import datetime,timedelta
def token(user): return jwt.encode({'sub':str(user.id),'role':user.role,'exp':datetime.utcnow()+timedelta(hours=24)},current_app.config['SECRET_KEY'],algorithm='HS256')
def auth(roles=None):
 def deco(f):
  @wraps(f)
  def w(*a,**k):
   h=request.headers.get('Authorization','');
   try: d=jwt.decode(h.split()[1],current_app.config['SECRET_KEY'],algorithms=['HS256']); uid=int(d['sub'])
   except: return jsonify(error='Authentication required'),401
   if roles and d['role'] not in roles:return jsonify(error='Forbidden'),403
   return f(uid,*a,**k)
  return w
 return deco
