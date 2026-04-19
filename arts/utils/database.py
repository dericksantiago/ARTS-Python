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
    Schema v4.0 - Party/Role model
    
    Business Rules:
    - Customer, Consignee, Broker, Shipper 
      are all PARTIES
    - A party can play multiple roles
    - Any party can be the billing party
    - Rates are stored per party
    """
    conn = get_connection()
    cursor = conn.cursor()

    # PARTY table
    # Replaces both CUSTOMER.DBF and BROKER.DBF
    # A party can be a customer, broker, or both
    # party_type: C=Customer, B=Broker, X=Both
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS party (
            code        TEXT PRIMARY KEY,
            lookupid    TEXT UNIQUE,
            name        TEXT NOT NULL,
            street      TEXT DEFAULT '',
            city        TEXT DEFAULT '',
            zip         TEXT DEFAULT '',
            phone       TEXT DEFAULT '',
            fax         TEXT DEFAULT '',
            attn        TEXT DEFAULT '',
            party_type  TEXT DEFAULT 'C',
            active      TEXT DEFAULT 'Y'
        )
    """)

    # PARTY_RATES table
    # Rate schedule per party per charge type
    # Business Rules:
    # - Each party has unique rates
    # - Rate fixed until rate change
    # - Not all charges apply to every party
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS party_rates (
            id              INTEGER PRIMARY KEY
                            AUTOINCREMENT,
            party_code      TEXT NOT NULL,
            charge_type     TEXT NOT NULL,
            amount          REAL DEFAULT 0,
            effective_date  TEXT DEFAULT '',
            end_date        TEXT DEFAULT '',
            active          TEXT DEFAULT 'Y',
            FOREIGN KEY (party_code)
                REFERENCES party(code),
            UNIQUE(party_code, charge_type,
                   effective_date)
        )
    """)

    # EMPLOYEE table
    # Drivers and staff
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
            active      TEXT DEFAULT 'Y'
        )
    """)

    # DELIVERY ORDER table - header
    # All parties reference the PARTY table
    # custmr  = who ordered the delivery
    # cnsnee  = where container delivered to
    # shipper = pickup location/terminal
    # broker  = customs broker
    # billto  = who pays (CUST/CONS/BROK/SHPR)
    # billcod = actual party code who pays
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS delivery_order (
            donum       TEXT PRIMARY KEY,
            dodat       TEXT DEFAULT '',
            custmr      TEXT DEFAULT '',
            cnsnee      TEXT DEFAULT '',
            broker      TEXT DEFAULT '',
            shipper     TEXT DEFAULT '',
            vessel      TEXT DEFAULT '',
            voyage      TEXT DEFAULT '',
            dest        TEXT DEFAULT '',
            papdat      TEXT DEFAULT '',
            lastdat     TEXT DEFAULT '',
            prepay      TEXT DEFAULT 'N',
            billto      TEXT DEFAULT 'CUST',
            billcod     TEXT DEFAULT '',
            comp        TEXT DEFAULT 'N',
            duedat      TEXT DEFAULT '',
            FOREIGN KEY (custmr)
                REFERENCES party(code),
            FOREIGN KEY (cnsnee)
                REFERENCES party(code),
            FOREIGN KEY (broker)
                REFERENCES party(code),
            FOREIGN KEY (shipper)
                REFERENCES party(code),
            FOREIGN KEY (billcod)
                REFERENCES party(code)
        )
    """)

    # DO_CHARGES table - invoice line items
    # from_rate = Y means auto-filled from
    # party_rates table
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

    # DO_CONTAINER table - container tracking
    # One DO can have multiple containers
    # Drivers reference employee table
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