from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db=SQLAlchemy()
class User(db.Model):
 id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(80)); email=db.Column(db.String(120),unique=True,nullable=False); password_hash=db.Column(db.String(256)); role=db.Column(db.String(20),default='customer')
class Venue(db.Model):
 id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120)); city=db.Column(db.String(80)); seats=db.relationship('VenueSeat',cascade='all,delete-orphan')
class VenueSeat(db.Model):
 id=db.Column(db.Integer,primary_key=True); venue_id=db.Column(db.Integer,db.ForeignKey('venue.id')); code=db.Column(db.String(20)); category=db.Column(db.String(30)); row=db.Column(db.Integer); col=db.Column(db.Integer); __table_args__=(db.UniqueConstraint('venue_id','code'),)
class Event(db.Model):
 id=db.Column(db.Integer,primary_key=True); title=db.Column(db.String(160)); kind=db.Column(db.String(30)); venue_id=db.Column(db.Integer,db.ForeignKey('venue.id')); organiser_id=db.Column(db.Integer,db.ForeignKey('user.id')); starts_at=db.Column(db.DateTime); prices=db.Column(db.JSON,default=dict); venue=db.relationship('Venue')
class ShowSeat(db.Model):
 id=db.Column(db.Integer,primary_key=True); event_id=db.Column(db.Integer,db.ForeignKey('event.id')); venue_seat_id=db.Column(db.Integer,db.ForeignKey('venue_seat.id')); status=db.Column(db.String(15),default='available'); hold_token=db.Column(db.String(64)); hold_user_id=db.Column(db.Integer); hold_expires_at=db.Column(db.DateTime); venue_seat=db.relationship('VenueSeat'); __table_args__=(db.UniqueConstraint('event_id','venue_seat_id'),)
class Booking(db.Model):
 id=db.Column(db.Integer,primary_key=True); reference=db.Column(db.String(32),unique=True); user_id=db.Column(db.Integer,db.ForeignKey('user.id')); event_id=db.Column(db.Integer,db.ForeignKey('event.id')); status=db.Column(db.String(20),default='confirmed'); created_at=db.Column(db.DateTime,default=datetime.utcnow); seats=db.relationship('BookingSeat',cascade='all,delete-orphan'); event=db.relationship('Event')
class BookingSeat(db.Model):
 id=db.Column(db.Integer,primary_key=True); booking_id=db.Column(db.Integer,db.ForeignKey('booking.id')); show_seat_id=db.Column(db.Integer,db.ForeignKey('show_seat.id')); show_seat=db.relationship('ShowSeat'); __table_args__=(db.UniqueConstraint('booking_id','show_seat_id'),)
class WaitlistEntry(db.Model):
 id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey('user.id')); event_id=db.Column(db.Integer,db.ForeignKey('event.id')); category=db.Column(db.String(30)); created_at=db.Column(db.DateTime,default=datetime.utcnow); status=db.Column(db.String(20),default='waiting')
class WaitlistOffer(db.Model):
 id=db.Column(db.Integer,primary_key=True); entry_id=db.Column(db.Integer,db.ForeignKey('waitlist_entry.id')); show_seat_id=db.Column(db.Integer,db.ForeignKey('show_seat.id')); token=db.Column(db.String(64),unique=True); expires_at=db.Column(db.DateTime); status=db.Column(db.String(20),default='active')
