import sqlite3

conn = sqlite3.connect('data/bot.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM users')
count = cursor.fetchone()[0]
print(f'✅ Users in CA table: {count}')

cursor.execute('SELECT user_id, telegram_username, tier FROM users LIMIT 3')
users = cursor.fetchall()
print('\n📋 Sample users:')
for u in users:
    print(f'   - ID: {u[0]}, Username: {u[1] or "N/A"}, Tier: {u[2]}')

conn.close()
