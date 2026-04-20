# ============================================
# ARTS - Accounts Receivable Reporting and Tracking System
# utils/database.py - Database Layer
# ARTS Database Layer
# Replaces all 26 DBF files
# ============================================

import sqlite3
import os

# Database location
DB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "arts.db")

def get_connection():
    """Returns a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """
    Creates all ARTS database tables.
    Schema v4.0 - contact/Role model
    
    Business Rules:
    - Customer, Consignee, Broker, Shipper 
      are all contacts
    - A contact can play multiple roles
    - Any contact can be the billing contact
    - Rates are stored per contact
    """
    conn = get_connection()
    cursor = conn.cursor()

    # CONTACT table
    # Replaces CUSTOMER.DBF and BROKER.DBF
    # Stores all external business contacts
    # contact_type: CUSTOMER, BROKER,
    #               TERMINAL, BOTH
    # Sub-haulers are in EMPLOYEE table
    # because they get paid not billed
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact (
            code            TEXT PRIMARY KEY,
            lookupid        TEXT UNIQUE,
            name            TEXT NOT NULL,
            street          TEXT DEFAULT '',
            city            TEXT DEFAULT '',
            zip             TEXT DEFAULT '',
            phone           TEXT DEFAULT '',
            fax             TEXT DEFAULT '',
            attn            TEXT DEFAULT '',
            contact_type    TEXT DEFAULT 'CUSTOMER',
            active          TEXT DEFAULT 'Y'
        )
    """)

    # CONTACT_RATES table
    # Rate schedule per contact
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_rates (
            id              INTEGER PRIMARY KEY
                            AUTOINCREMENT,
            contact_code    TEXT NOT NULL,
            charge_type     TEXT NOT NULL,
            amount          REAL DEFAULT 0,
            effective_date  TEXT DEFAULT '',
            end_date        TEXT DEFAULT '',
            active          TEXT DEFAULT 'Y',
            FOREIGN KEY (contact_code)
                REFERENCES contact(code),
            UNIQUE(contact_code, charge_type,
                   effective_date)
        )
    """)

  # EMPLOYEE table
    # Stores drivers AND sub-haulers
    # emp_type: D=Driver, S=Sub-hauler
    # Sub-haulers get paid per delivery
    # but are never invoiced by ARTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee (
            emp_id      TEXT PRIMARY KEY,
            emplname    TEXT NOT NULL,
            street      TEXT DEFAULT '',
            city        TEXT DEFAULT '',
            zip         TEXT DEFAULT '',
            phone       TEXT DEFAULT '',
            pager       TEXT DEFAULT '',
            sss         TEXT DEFAULT '',
            dlicense    TEXT DEFAULT '',
            truckno     TEXT DEFAULT '',
            alias       TEXT DEFAULT '',
            emp_type    TEXT DEFAULT 'D',
            active      TEXT DEFAULT 'Y'
        )
    """)

   # DELIVERY ORDER table
    # All roles reference CONTACT table
    # except drivers which reference EMPLOYEE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS delivery_order (
            donum           TEXT PRIMARY KEY,
            dodat           TEXT DEFAULT '',
            custmr          TEXT DEFAULT '',
            cnsnee          TEXT DEFAULT '',
            broker          TEXT DEFAULT '',
            shipper         TEXT DEFAULT '',
            vessel          TEXT DEFAULT '',
            voyage          TEXT DEFAULT '',
            dest            TEXT DEFAULT '',
            papdat          TEXT DEFAULT '',
            lastdat         TEXT DEFAULT '',
            prepay          TEXT DEFAULT 'N',
            billto          TEXT DEFAULT 'CUSTOMER',
            billcod         TEXT DEFAULT '',
            comp            TEXT DEFAULT 'N',
            duedat          TEXT DEFAULT '',
            FOREIGN KEY (custmr)
                REFERENCES contact(code),
            FOREIGN KEY (cnsnee)
                REFERENCES contact(code),
            FOREIGN KEY (broker)
                REFERENCES contact(code),
            FOREIGN KEY (shipper)
                REFERENCES contact(code),
            FOREIGN KEY (billcod)
                REFERENCES contact(code)
        )
    """)

    # DO_CHARGES table - invoice line items
    # from_rate = Y means auto-filled from
    # contact_rates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS do_charges (
            id          INTEGER PRIMARY KEY
                        AUTOINCREMENT,
            donum       TEXT NOT NULL,
            charge_type TEXT NOT NULL,
            amount      REAL DEFAULT 0,
            comment     TEXT DEFAULT '',
            tfrto       TEXT DEFAULT '',
            tfrfm       TEXT DEFAULT '',
            from_rate   TEXT DEFAULT 'N',
            FOREIGN KEY (donum)
                REFERENCES delivery_order(donum)
        )
    """)

# DO_CONTAINER table
    # outdrvr, deldrvr, indrvr reference
    # employee table (drivers AND sub-haulers)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS do_container (
            id          INTEGER PRIMARY KEY
                        AUTOINCREMENT,
            donum       TEXT NOT NULL,
            refno       TEXT DEFAULT '',
            size        TEXT DEFAULT '',
            contnum     TEXT DEFAULT '',
            chassis     TEXT DEFAULT '',
            outdat      TEXT DEFAULT '',
            deldat      TEXT DEFAULT '',
            indat       TEXT DEFAULT '',
            outdrvr     TEXT DEFAULT '',
            deldrvr     TEXT DEFAULT '',
            indrvr      TEXT DEFAULT '',
            trandat     TEXT DEFAULT '',
            tranfm      TEXT DEFAULT '',
            frmcust     TEXT DEFAULT '',
            tranto      TEXT DEFAULT '',
            tocust      TEXT DEFAULT '',
            splitrec    TEXT DEFAULT 'N',
            FOREIGN KEY (donum)
                REFERENCES delivery_order(donum),
            FOREIGN KEY (outdrvr)
                REFERENCES employee(emp_id),
            FOREIGN KEY (deldrvr)
                REFERENCES employee(emp_id),
            FOREIGN KEY (indrvr)
                REFERENCES employee(emp_id)
        )
    """)

    # PAYMENTS table
    # Payment records against delivery orders
    # Replaces PAYMENTS.DBF (50,102 records!)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id          INTEGER PRIMARY KEY
                        AUTOINCREMENT,
            donum       TEXT NOT NULL,
            checkdat    TEXT DEFAULT '',
            checkno     TEXT DEFAULT '',
            amt         REAL DEFAULT 0,
            FOREIGN KEY (donum)
                REFERENCES delivery_order(donum)
        )
    """)

    conn.commit()
    conn.close()
    print("  ✅ Database tables ready!")

def init_database():
    """
    Initializes the database.
    Call this once when app starts.
    """
    data_dir = os.path.join(
        os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    create_tables()