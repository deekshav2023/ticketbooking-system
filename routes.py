from flask import Blueprint,request,jsonify,send_from_directory
from .models import *
from .auth import auth,token
from .services import cleanup_expired,qr,offer_next
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,timedelta
import uuid
bp=Blueprint('api',__name__)
def event_json(e): return {'id':e.id,'title':e.title,'kind':e.kind,'venue':e.venue.name,'city':e.venue.city,'starts_at':e.starts_at.isoformat(),'prices':e.prices}
@bp.route('/')
def home(): return send_from_directory(bp.root_path+'/static','index.html')
@bp.route('/api/auth/register',methods=['POST'])
def register():
 d=request.json or {};
 if not d.get('email') or not d.get('password'): return jsonify(error='email and password required'),400
 if User.query.filter_by(email=d['email']).first():return jsonify(error='Email exists'),409
 u=User(name=d.get('name','User'),email=d['email'],password_hash=generate_password_hash(d['password']),role=d.get('role','customer')); db.session.add(u); db.session.commit(); return jsonify(token=token(u),user={'id':u.id,'role':u.role})
@bp.route('/api/auth/login',methods=['POST'])
def login():
 d=request.json or {}; u=User.query.filter_by(email=d.get('email')).first()
 if not u or not check_password_hash(u.password_hash,d.get('password','')): return jsonify(error='Invalid credentials'),401
 return jsonify(token=token(u),user={'id':u.id,'role':u.role,'name':u.name})
@bp.route('/api/events')
def events():
 q=Event.query; s=request.args.get('search'); kind=request.args.get('kind');
 if s:q=q.filter(Event.title.ilike('%'+s+'%'))
 if kind:q=q.filter_by(kind=kind)
 return jsonify([event_json(e) for e in q.order_by(Event.starts_at).all()])
@bp.route('/api/events',methods=['POST'])
@auth(['organiser','admin'])
def create_event(uid):
 d=request.json or {}; e=Event(title=d['title'],kind=d.get('kind','event'),venue_id=d['venue_id'],organiser_id=uid,starts_at=datetime.fromisoformat(d['starts_at']),prices=d.get('prices',{})); db.session.add(e); db.session.flush()
 for s in VenueSeat.query.filter_by(venue_id=e.venue_id): db.session.add(ShowSeat(event_id=e.id,venue_seat_id=s.id))
 db.session.commit(); return jsonify(event_json(e)),201
@bp.route('/api/events/<int:eid>')
def event(eid): return jsonify(event_json(Event.query.get_or_404(eid)))
@bp.route('/api/events/<int:eid>/seats')
def seats(eid):
 cleanup_expired(); return jsonify([{'id':s.id,'code':s.venue_seat.code,'category':s.venue_seat.category,'row':s.venue_seat.row,'col':s.venue_seat.col,'status':s.status,'expires_at':s.hold_expires_at.isoformat() if s.hold_expires_at else None} for s in ShowSeat.query.filter_by(event_id=eid).all()])
@bp.route('/api/events/<int:eid>/hold',methods=['POST'])
@auth(['customer','organiser','admin'])
def hold(uid,eid):
 cleanup_expired(); ids=(request.json or {}).get('seat_ids',[]);
 if not ids:return jsonify(error='Select seats'),400
 # SQLite serializes writers; re-check status inside transaction before updating.
 now=datetime.utcnow(); exp=now+timedelta(seconds=bp.current_app.config['HOLD_TTL_SECONDS']) if False else now+timedelta(seconds=600)
 seats=ShowSeat.query.filter(ShowSeat.event_id==eid,ShowSeat.id.in_(ids)).with_for_update().all()
 if len(seats)!=len(ids) or any(s.status!='available' for s in seats): return jsonify(error='One or more seats are unavailable'),409
 t=uuid.uuid4().hex
 for s in seats:s.status='held';s.hold_token=t;s.hold_user_id=uid;s.hold_expires_at=exp
 db.session.commit(); return jsonify(hold_token=t,expires_at=exp.isoformat())
@bp.route('/api/bookings/confirm',methods=['POST'])
@auth()
def confirm(uid):
 cleanup_expired(); d=request.json or {}; t=d.get('hold_token'); now=datetime.utcnow(); ss=ShowSeat.query.filter_by(hold_token=t,hold_user_id=uid,status='held').all()
 if not ss or any(s.hold_expires_at<=now for s in ss):return jsonify(error='Hold expired'),409
 ref='TB-'+uuid.uuid4().hex[:10].upper(); b=Booking(reference=ref,user_id=uid,event_id=ss[0].event_id); db.session.add(b); db.session.flush()
 for s in ss:s.status='booked';s.hold_token=None;s.hold_user_id=None;s.hold_expires_at=None;db.session.add(BookingSeat(booking_id=b.id,show_seat_id=s.id))
 db.session.commit(); return jsonify(reference=ref,qr_base64=qr(ref),seats=[s.venue_seat.code for s in ss])
@bp.route('/api/bookings')
@auth()
def bookings(uid):
 return jsonify([{'reference':b.reference,'status':b.status,'event':b.event.title,'seats':[x.show_seat.venue_seat.code for x in b.seats]} for b in Booking.query.filter_by(user_id=uid).all()])
@bp.route('/api/bookings/<ref>/cancel',methods=['POST'])
@auth()
def cancel(uid,ref):
 b=Booking.query.filter_by(reference=ref,user_id=uid).first_or_404()
 if b.status!='confirmed':return jsonify(error='Not cancellable'),409
 b.status='cancelled'; released=[]
 for x in b.seats:
  s=x.show_seat;s.status='available';released.append(s)
 db.session.commit()
 for s in released: offer_next(b.event_id,s.venue_seat.category,s)
 return jsonify(message='Cancelled')
@bp.route('/api/events/<int:eid>/waitlist',methods=['POST'])
@auth()
def waitlist(uid,eid):
 cat=(request.json or {}).get('category');
 if WaitlistEntry.query.filter_by(user_id=uid,event_id=eid,category=cat,status='waiting').first():return jsonify(error='Already waiting'),409
 w=WaitlistEntry(user_id=uid,event_id=eid,category=cat);db.session.add(w);db.session.commit();return jsonify(id=w.id,status=w.status),201
@bp.route('/api/venues',methods=['GET','POST'])
@auth(['admin'])
def venues(uid):
 if request.method=='GET':return jsonify([{'id':v.id,'name':v.name,'city':v.city} for v in Venue.query.all()])
 d=request.json;v=Venue(name=d['name'],city=d.get('city',''));db.session.add(v);db.session.commit();return jsonify(id=v.id),201
@bp.route('/api/organiser/events/<int:eid>/summary')
@auth(['organiser','admin'])
def summary(uid,eid):
 e=Event.query.get_or_404(eid); bs=Booking.query.filter_by(event_id=eid,status='confirmed').all(); rev=0
 for b in bs:
  for x in b.seats: rev+=float(e.prices.get(x.show_seat.venue_seat.category,0))
 return jsonify(bookings=len(bs),revenue=rev)
