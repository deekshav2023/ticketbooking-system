# API Documentation
|Method|Endpoint|Auth|Purpose|
|-|-|-|-|
|POST|/api/auth/register|No|Register customer/organiser|
|POST|/api/auth/login|No|Login and receive JWT|
|GET|/api/events|No|Search/filter events|
|GET|/api/events/:id|No|Event details|
|GET|/api/events/:id/seats|No|Current seat map|
|POST|/api/events/:id/hold|JWT|Atomically hold available seats; 409 on conflict|
|POST|/api/bookings/confirm|JWT|Confirm valid, unexpired hold|
|GET|/api/bookings|JWT|Booking history|
|POST|/api/bookings/:ref/cancel|JWT|Cancel and release seats|
|POST|/api/events/:id/waitlist|JWT|Join category queue|
|GET/POST|/api/venues|Admin|Manage venues|
|POST|/api/events|Organiser/Admin|Create event and event-specific seats|
|GET|/api/organiser/events/:id/summary|Organiser/Admin|Bookings and revenue|

Errors use JSON `{ "error": "..." }` with 400, 401, 403, 404 or 409 as appropriate. Register/login accept `{name,email,password,role?}` and `{email,password}`. Hold accepts `{seat_ids:[1,2]}`; confirmation accepts `{hold_token:"..."}`.
