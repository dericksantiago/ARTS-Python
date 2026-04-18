# ============================================
# ARTS - Almar Reporting and Tracking System
# utils/database.py - Database Layer
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
    """Creates all ARTS database tables"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            code        TEXT PRIMARY KEY,
            lookupid    TEXT,
            custnam     TEXT NOT NULL,
            street      TEXT DEFAULT '',
            city        TEXT DEFAULT '',
            zip         TEXT DEFAULT '',
            phone       TEXT DEFAULT '',
            fax         TEXT DEFAULT '',
            attn        TEXT DEFAULT '',
            shipto      TEXT DEFAULT '',
            shipfm      TEXT DEFAULT '',
            rate        REAL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS broker (
            code        TEXT PRIMARY KEY,
            lookupid    TEXT,
            brkrnam     TEXT NOT NULL,
            street      TEXT DEFAULT '',
            city        TEXT DEFAULT '',
            zip         TEXT DEFAULT '',
            phone       TEXT DEFAULT '',
            fax         TEXT DEFAULT '',
            attn        TEXT DEFAULT ''
        )
    """)

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
            alias       TEXT DEFAULT ''
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice (
            ponum       TEXT PRIMARY KEY,
            podat       TEXT,
            custmr      TEXT,
            cnsnee      TEXT DEFAULT '',
            broker      TEXT DEFAULT '',
            shipper     TEXT DEFAULT '',
            vessel      TEXT DEFAULT '',
            voyage      TEXT DEFAULT '',
            dest        TEXT DEFAULT '',
            papdat      TEXT DEFAULT '',
            lastdat     TEXT DEFAULT '',
            prepay      TEXT DEFAULT 'N',
            billto      TEXT DEFAULT '',
            billcod     TEXT DEFAULT '',
            comp        TEXT DEFAULT 'N',
            duedat      TEXT DEFAULT '',
            shipto      TEXT DEFAULT '',
            shipfm      TEXT DEFAULT '',
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
            tfrto       TEXT DEFAULT '',
            tfrfm       TEXT DEFAULT '',
            misc1       REAL DEFAULT 0,
            commnt1     TEXT DEFAULT '',
            misc2       REAL DEFAULT 0,
            commnt2     TEXT DEFAULT '',
            misc3       REAL DEFAULT 0,
            commnt3     TEXT DEFAULT '',
            baldue      REAL DEFAULT 0,
            invdat      TEXT DEFAULT '',
            amtpaid     REAL DEFAULT 0,
            origbal     REAL DEFAULT 0,
            FOREIGN KEY (custmr) REFERENCES customer(code),
            FOREIGN KEY (broker) REFERENCES broker(code)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ponum       TEXT NOT NULL,
            checkdat    TEXT,
            checkno     TEXT,
            amt         REAL DEFAULT 0,
            FOREIGN KEY (ponum) REFERENCES invoice(ponum)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pocont (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ponum       TEXT NOT NULL,
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
            FOREIGN KEY (ponum) REFERENCES invoice(ponum)
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