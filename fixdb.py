import sqlite3

conn = sqlite3.connect('arts/data/arts.db')

# Fix contact_type C → CUSTOMER
conn.execute("""
    UPDATE contact
    SET contact_type = 'CUSTOMER'
    WHERE contact_type = 'C'
""")

# Fix Anthropic active = N → Y
conn.execute("""
    UPDATE contact
    SET active = 'Y'
    WHERE active = 'N'
""")

conn.commit()

# Show results
rows = conn.execute("""
    SELECT code, name,
           contact_type, active
    FROM contact
""").fetchall()

print("Contacts after fix:")
for r in rows:
    print(f"  {r}")

conn.close()
print("Done!")