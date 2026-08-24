# Ticket Booking System
A complete Flask full-stack assignment project for movies and events. Core features include JWT authentication, Customer/Organiser/Admin roles, event-specific visual seat maps, transactional holds, TTL expiry, conflict handling, bookings, QR tickets, cancellation, waitlists and organiser revenue summaries.

## Stack
Python, Flask, SQLAlchemy, SQLite (easy local setup; PostgreSQL-compatible model design), PyJWT and qrcode. The frontend is responsive vanilla HTML/CSS/JavaScript with 3-second polling for practical near-real-time seat updates.

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows; configure if desired
python run.py
```
Open `http://localhost:5000`. Seeded accounts: `admin@example.com / Admin123!` and `organiser@example.com / Organiser123!`. Customers can register from the UI.

## Database design
`User`, `Venue`, `VenueSeat`, `Event`, `ShowSeat`, `Booking`, `BookingSeat`, `WaitlistEntry`, and `WaitlistOffer` separate physical venue layout from event availability. `ShowSeat` is unique per `(event_id, venue_seat_id)`, allowing A1 to be booked for one event and available for another.

## TTL and concurrency
See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md). Holds have expiry timestamps and are cleaned during seat reads and booking actions. Acquisition rechecks all requested seats atomically and rejects conflicts with 409. For larger production deployments use PostgreSQL and a short-interval scheduler calling the same cleanup service.

## Waitlist and offers
Cancellation releases seats and offers each released category seat to the oldest waiting customer. Offers reserve the exact seat for `OFFER_TTL_SECONDS`; expired offers are released and queue processing can continue. The console email fallback prints offer tokens; SMTP configuration can be added through environment variables without storing secrets.

## QR and email
Confirmed bookings generate a QR PNG containing the booking reference and return it for display. `MAIL_MODE=console` is the development fallback. Configure SMTP variables for production delivery.

## API and deployment
See [API.md](API.md). Deploy the Flask service on Render/Railway with PostgreSQL, set `SECRET_KEY`, `DATABASE_URL`, `APP_URL` and email variables, and run `python run.py` or a production WSGI command. Do not deploy the SQLite database for multi-instance production.

## Submission hygiene
The ZIP excludes virtual environments, `node_modules`, build output, real `.env` files and secrets.
