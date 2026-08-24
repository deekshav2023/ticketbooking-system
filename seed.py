from .models import *
from werkzeug.security import generate_password_hash
from datetime import datetime,timedelta
def seed():
 if User.query.first(): return
 customer=User(name='Customer',email='customer@example.com',password_hash=generate_password_hash('Customer123!'),role='customer'); admin=User(name='Admin',email='admin@example.com',password_hash=generate_password_hash('Admin123!'),role='admin'); org=User(name='Organiser',email='organiser@example.com',password_hash=generate_password_hash('Organiser123!'),role='organiser'); v=Venue(name='Grand Arena',city='Salem'); db.session.add_all([customer,admin,org,v]); db.session.flush()
 for r in range(1,7):
  for c in range(1,9): db.session.add(VenueSeat(venue_id=v.id,code=f'{chr(64+r)}{c}',category='Premium' if r<=2 else 'Standard',row=r,col=c))
 db.session.flush(); e=Event(title='Sample Concert',kind='concert',venue_id=v.id,organiser_id=org.id,starts_at=datetime.utcnow()+timedelta(days=7),prices={'Premium':500,'Standard':250}); db.session.add(e); db.session.flush()
 for s in v.seats: db.session.add(ShowSeat(event_id=e.id,venue_seat_id=s.id))
 db.session.commit()
