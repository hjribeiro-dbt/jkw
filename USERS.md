### Development Users

The following users are created by the management command `seed_users` for local development and manual testing.

Run:

```
python manage.py seed_users
```

Created on: 2026-05-12 09:36 (local time)

Users:
- Admin (superuser)
  - username: `admin`
  - password: `admin`
  - email: `admin@example.com`
- Regular user
  - username: `alice`
  - password: `alice123`
  - email: `alice@example.com`
- Regular user
  - username: `bob`
  - password: `bob123`
  - email: `bob@example.com`

Notes:
- These credentials are for development only. Do not use them in production.
- The command is idempotent; running it multiple times will not duplicate users. If a user already exists, the command leaves their existing password unchanged.
