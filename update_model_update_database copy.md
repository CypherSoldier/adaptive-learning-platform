Your error is very clear:

```
sqlite3.OperationalError: table users has no column named full_name
```

Your **SQLAlchemy model includes `full_name`**, but the **actual SQLite table does not**. So when SQLAlchemy runs:

```sql
INSERT INTO users (id, email, full_name, password_hash)
```

SQLite fails because that column doesn't exist in the table schema.

---

# Why this happens

This usually happens when you:

1. **Created the database before adding the `full_name` field**
2. Then **updated the SQLAlchemy model**
3. But **never updated the actual database schema**

SQLite doesn't automatically update tables when models change.

---

# Quick Fix (Development Only)

If you're in development and **don't care about losing data**, just reset the database.

### 1️⃣ Delete the SQLite database file

Example:

```
rm database.db
```

or manually delete:

```
backend/database.db
```

---

### 2️⃣ Restart the server

When FastAPI runs:

```python
Base.metadata.create_all(bind=engine)
```

SQLAlchemy will recreate the tables with the **correct schema** including `full_name`.

---

# Better Fix (Recommended – Migration)

If you want to keep the data, run a migration.

### Option A — Manual SQLite fix

Run this in SQLite:

```sql
ALTER TABLE users ADD COLUMN full_name TEXT;
```

You can do this using:

```
sqlite3 database.db
```

Then:

```sql
ALTER TABLE users ADD COLUMN full_name TEXT;
```

---

### Option B — Proper migrations (Best practice)

Use **Alembic**.

Install:

```bash
pip install alembic
```

Then:

```
alembic init alembic
alembic revision --autogenerate -m "add full_name to users"
alembic upgrade head
```

This keeps schema synced with models.

---

# Also fix this (small bug)

Your log shows:

```
id = 0
```

Which means you're probably doing:

```python
id: int = 0
```

Instead of letting the DB autogenerate it.

Make sure your model uses:

```python
id = Column(Integer, primary_key=True, index=True)
```

NOT

```python
id = 0
```

---

# Correct SQLAlchemy Model Example

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
```

---

# Quick checklist

✅ Model has `full_name`
❌ Database table doesn't
➡ Solution: **migration or recreate DB**

---

If you want, paste your **`User` model and `register_user()` function**, and I can help you fix the architecture properly (FastAPI + SQLAlchemy best practices).
