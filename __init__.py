from flask import Flask
from .models import db
from .routes import bp
from .services import cleanup_expired
import os
def create_app():
 a=Flask(__name__,static_folder='static',template_folder='templates'); a.config.from_mapping(SECRET_KEY=os.getenv('SECRET_KEY','dev-secret'),SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL','sqlite:///ticket_booking.db'),SQLALCHEMY_TRACK_MODIFICATIONS=False,HOLD_TTL_SECONDS=int(os.getenv('HOLD_TTL_SECONDS','600')),OFFER_TTL_SECONDS=int(os.getenv('OFFER_TTL_SECONDS','900'))); db.init_app(a)
 with a.app_context(): db.create_all(); cleanup_expired(a); from .seed import seed; seed()
 a.register_blueprint(bp); return a
