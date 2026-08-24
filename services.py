from datetime import datetime,timedelta
from flask import current_app
from .models import *
import uuid, qrcode, io, base64
def cleanup_expired(app=None):
 now=datetime.utcnow(); expired=ShowSeat.query.filter(ShowSeat.status=='held',ShowSeat.hold_expires_at<now).all()
 for s in expired: s.status='available'; s.hold_token=None; s.hold_user_id=None; s.hold_expires_at=None
 for o in WaitlistOffer.query.filter_by(status='active').filter(WaitlistOffer.expires_at<now).all(): o.status='expired'; e=WaitlistEntry.query.get(o.entry_id); e.status='waiting'; s=ShowSeat.query.get(o.show_seat_id); s.status='available'; s.hold_token=None; s.hold_user_id=None; s.hold_expires_at=None
 db.session.commit()
def qr(ref):
 im=qrcode.make(ref); b=io.BytesIO(); im.save(b,format='PNG'); return base64.b64encode(b.getvalue()).decode()
def offer_next(event_id, category, seat):
 e=WaitlistEntry.query.filter_by(event_id=event_id,category=category,status='waiting').order_by(WaitlistEntry.created_at).first()
 if not e:return
 e.status='offered'; t=uuid.uuid4().hex; o=WaitlistOffer(entry_id=e.id,show_seat_id=seat.id,token=t,expires_at=datetime.utcnow()+timedelta(seconds=current_app.config['OFFER_TTL_SECONDS'])); seat.status='held'; seat.hold_token='offer:'+t; seat.hold_user_id=e.user_id; seat.hold_expires_at=o.expires_at; db.session.add(o); db.session.commit(); print('WAITLIST OFFER',t)
