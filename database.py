# ============================================
# ARTS - Almar Reporting and Tracking System
# database.py - Database Setup & Operations
# Replaces all 26 DBF files with arts.db
# ============================================

import sqlite3
import os
from datetime import datetime
from functions import show_header, format_currency

# ---- DATABASE CONNECTION ----

def get_connection():
    """
    Creates and returns a database connection.
    Creates arts.db if it doesn't exist.
    Like USE <dbfile> in Clipper
    """
    conn = sqlite3.connect("arts.db")
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# ---- CREATE TABLES ----

def create_tables():
    """
    Creates all ARTS database tables.
    Mirrors the structure of your DBF files.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # CUSTOMER table - mirrors CUSTOMER.DBF
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            code        TEXT PRIMARY KEY,
            lookupid    TEXT,
            custnam     TEXT,
            street      TEXT,
            city        TEXT,
            zip         TEXT,
            phone       TEXT,
            fax         TEXT,
            attn        TEXT,
            shipto      TEXT,
            shipfm      TEXT,
            rate        REAL DEFAULT 0
        )
    """)

    # BROKER table - mirrors BROKER.DBF
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS broker (
            code        TEXT PRIMARY KEY,
            lookupid    TEXT,
            brkrnam     TEXT,
            street      TEXT,
            city        TEXT,
            zip         TEXT,
            phone       TEXT,
            fax         TEXT,
            attn        TEXT
        )
    """)

    # INVOICE table - mirrors INVOICE.DBF
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice (
            ponum       TEXT PRIMARY KEY,
            podat       TEXT,
            custmr      TEXT,
            cnsnee      TEXT,
            broker      TEXT,
            shipper     TEXT,
            vessel      TEXT,
            voyage      TEXT,
            dest        TEXT,
            papdat      TEXT,
            prepay      TEXT,
            billto      TEXT,
            shipto      TEXT,
            shipfm      TEXT,
            rate        REAL DEFAULT 0,
            congestion  REAL DEFAULT 0,
            port_fee    REAL DEFAULT 0,
            admin_fee   REAL DEFAULT 0,
            drop_chg    REAL DEFAULT 0,
            overweight  REAL DEFAULT 0,
            genset      REAL DEFAULT 0,
            reefer      REAL DEFAULT 0,
            yard        REAL DEFAULT 0,
            transfer_fee REAL DEFAULT 0,
            misc1       REAL DEFAULT 0,
            commnt1     TEXT,
            misc2       REAL DEFAULT 0,
            commnt2     TEXT,
            misc3       REAL DEFAULT 0,
            commnt3     TEXT,
            baldue      REAL DEFAULT 0,
            invdat      TEXT,
            amtpaid     REAL DEFAULT 0,
            origbal     REAL DEFAULT 0,
            comp        TEXT DEFAULT 'N',
            FOREIGN KEY (custmr) REFERENCES customer(code),
            FOREIGN KEY (broker) REFERENCES broker(code)
        )
    """)

    # PAYMENTS table - mirrors PAYMENTS.DBF
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ponum       TEXT,
            checkdat    TEXT,
            checkno     TEXT,
            amt         REAL DEFAULT 0,
            FOREIGN KEY (ponum) REFERENCES invoice(ponum)
        )
    """)

    # EMPLOYEE table - mirrors EMPLOYEE.DBF
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee (
            emp_id      TEXT PRIMARY KEY,
            emplname    TEXT,
            street      TEXT,
            city        TEXT,
            zip         TEXT,
            phone       TEXT,
            pager       TEXT,
            sss         TEXT,
            dlicense    TEXT,
            truckno     TEXT,
            alias       TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("  ✅ All tables created successfully!")

# ---- INSERT FUNCTIONS ----

def add_customer(code, lookupid, custnam, street="",
                 city="", zip="", phone="", fax="",
                 attn="", shipto="", shipfm="", rate=0):
    """Adds a new customer - like APPEND BLANK + field updates in Clipper"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO customer VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (code, lookupid, custnam, street, city,
              zip, phone, fax, attn, shipto, shipfm, rate))
        conn.commit()
        print(f"  ✅ Customer added: {custnam}")
    except sqlite3.IntegrityError:
        print(f"  ⚠️  Customer code {code} already exists!")
    finally:
        conn.close()

def add_payment(ponum, checkdat, checkno, amt):
    """Adds a payment record - like APPEND BLANK in PAYMENTS.DBF"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO payments (ponum, checkdat, checkno, amt)
        VALUES (?,?,?,?)
    """, (ponum, checkdat, checkno, amt))
    conn.commit()
    conn.close()

# ---- QUERY FUNCTIONS ----

def find_customer(code):
    """Find customer by code - like SEEK in Clipper"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customer WHERE code = ?", (code,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_customers():
    """Returns all customers - like USE CUSTOMER / LIST in Clipper"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customer ORDER BY custnam")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_payments_for_invoice(ponum):
    """Gets all payments for a PO number"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM payments
        WHERE ponum = ?
        ORDER BY checkdat
    """, (ponum,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_invoice_summary(ponum):
    """Gets invoice with total payments and balance"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            i.*,
            c.custnam,
            COALESCE(SUM(p.amt), 0) as total_paid,
            i.origbal - COALESCE(SUM(p.amt), 0) as balance
        FROM invoice i
        LEFT JOIN customer c ON i.custmr = c.code
        LEFT JOIN payments p ON i.ponum = p.ponum
        WHERE i.ponum = ?
        GROUP BY i.ponum
    """, (ponum,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# ---- UPDATE FUNCTIONS ----

def update_customer_rate(code, new_rate):
    """Updates customer rate - like REPLACE RATE WITH in Clipper"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customer SET rate = ? WHERE code = ?
    """, (new_rate, code))
    conn.commit()
    conn.close()
    print(f"  ✅ Rate updated for customer {code}")

# ---- DELETE FUNCTIONS ----

def delete_payment(payment_id):
    """Deletes a payment by ID - like DELETE + PACK in Clipper"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()

# ---- MAIN PROGRAM - Test everything ----

if __name__ == "__main__":

    # Delete test database if exists so we start fresh
    if os.path.exists("arts.db"):
        os.remove("arts.db")
        print("  🗑️  Old test database removed")

    show_header("DATABASE SETUP TEST")

    # Step 1 - Create tables
    print("\n  STEP 1: Creating database tables...")
    create_tables()

    # Step 2 - Add sample customers from real ARTS data
    print("\n  STEP 2: Adding sample customers...")
    add_customer("0032", "SUNMIC", "Sun Microsystem Inc.",
                 "123 Main St", "San Jose, Ca", "95101",
                 "408-555-1234", "", "John Smith",
                 "SSF4CONTS", "PIER 96 SFO", 620.00)

    add_customer("1933", "1933SPI", "1933 Spirits LLC",
                 "11 Davis Drive", "Belmont, Ca", "94002",
                 "650-280-0773", "", "Carme Rodriguez",
                 "BELMONT", "OAKLAND", 450.00)

    add_customer("0001", "KARLSC", "Karl Schroff & Associates",
                 "2955 San Bruno Ave", "San Francisco, Ca", "94134",
                 "415-555-9876", "", "Romy",
                 "SFO", "PIER 80", 380.00)

    # Step 3 - Find a customer
    print("\n  STEP 3: Looking up customer 0032...")
    customer = find_customer("0032")
    if customer:
        print(f"  Found: {customer['custnam']}")
        print(f"  City : {customer['city']}")
        print(f"  Rate : {format_currency(customer['rate'])}")

    # Step 4 - Add payments
    print("\n  STEP 4: Adding payment records...")
    add_payment("000056647", "04/09/1992", "107734", 620.00)
    add_payment("000056647", "04/15/1992", "107735", 450.00)
    add_payment("000056648", "04/20/1992", "107736", 380.00)
    print("  ✅ 3 payments added!")

    # Step 5 - List all customers
    print("\n  STEP 5: Listing all customers...")
    customers = get_all_customers()
    print(f"  {'CODE':<6} {'NAME':<30} {'RATE':>10}")
    print("  " + "-" * 48)
    for c in customers:
        print(f"  {c['code']:<6} {c['custnam']:<30} "
              f"{format_currency(c['rate']):>10}")

    # Step 6 - Get payments for invoice
    print("\n  STEP 6: Payments for PO# 000056647...")
    payments = get_payments_for_invoice("000056647")
    print(f"  {'CHECK DATE':<12} {'CHECK NO':<10} {'AMOUNT':>10}")
    print("  " + "-" * 34)
    for p in payments:
        print(f"  {p['checkdat']:<12} {p['checkno']:<10} "
              f"{format_currency(p['amt']):>10}")

    total = sum(p['amt'] for p in payments)
    print(f"  {'TOTAL PAID:':<22} {format_currency(total):>10}")

    print("\n  ✅ Database test complete!")
    print("  📁 arts.db has been created in your project folder!")