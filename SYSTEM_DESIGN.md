# System Design

## 1. Seat hold and TTL mechanism
Each event has its own `ShowSeat` records, so the same physical seat can have a different state for every event. A hold changes available seats to `held` and stores the owner, random token and expiry timestamp. Every seat-map read and booking operation calls expiry cleanup. A deployment can additionally run cleanup on a periodic scheduler; the timestamp remains the source of truth, so stale seats are never bookable merely because a job was delayed. Confirmation rejects expired holds.

## 2. Concurrency prevention
The backend, not the browser, is authoritative. Seat acquisition reads the requested event seats in one transaction, locks rows where supported, rechecks that every seat is available, and then updates all of them together. The unique `(event_id, venue_seat_id)` constraint guarantees one state record per physical seat per event. SQLite serializes concurrent writers; production PostgreSQL can use row-level `SELECT FOR UPDATE`. A conflicting request receives HTTP 409. Booking confirmation verifies token ownership, user and expiry before converting seats to booked.

## 3. Waitlist auto-assignment
Waitlist entries are stored per event and category with creation time. On cancellation, each released seat is passed to the queue processor. It selects the oldest `waiting` entry, marks it offered, creates a random offer token and temporarily holds that exact seat for the customer. The customer can then complete booking using the normal hold-confirmation path. If no entry exists, the seat remains available.

## 4. Time-limited offers
An offer has an independent expiry timestamp. Cleanup marks expired offers expired, returns the waitlist entry to waiting, releases the seat and allows processing of the next queue entry. During the offer period the seat is held and therefore unavailable to ordinary customers. The design uses timestamps plus idempotent cleanup so delayed background execution does not create a permanently blocked seat. In production, a scheduled worker can invoke cleanup and queue processing at short intervals; request-time cleanup preserves correctness between worker runs.
