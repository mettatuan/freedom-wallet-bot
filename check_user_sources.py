#!/usr/bin/env python3
"""Check user count by activation_source in bot database"""

from bot.utils.database import SessionLocal, User
from sqlalchemy import func

db = SessionLocal()

print("Total users in bot DB:", db.query(func.count(User.id)).scalar())
print("\nBy activation_source:")
for src, cnt in db.query(User.activation_source, func.count(User.id)).group_by(User.activation_source).all():
    print(f"  {src or 'NULL'}: {cnt}")

print("\nBy is_registered:")
for reg, cnt in db.query(User.is_registered, func.count(User.id)).group_by(User.is_registered).all():
    print(f"  {'Registered' if reg else 'Not registered'}: {cnt}")

db.close()
