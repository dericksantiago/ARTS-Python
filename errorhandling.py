# ============================================
# ARTS - Almar Reporting and Tracking System
# errorhandling.py - Error Handling Lesson
# Like ERRORSYS.PRG and ERRDISP.PRG in Clipper
# ============================================

import sqlite3
import os
from functions import show_header, format_currency, press_any_key

# ---- BASIC TRY/EXCEPT ----

def safe_divide(a, b):
    """
    Safely divides two numbers.
    Without try/except this would crash if b = 0!
    """
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("  ⚠️  Cannot divide by zero!")
        return 0

# ---- SAFE INPUT FUNCTIONS ----

def get_valid_float(prompt, min_val=None, max_val=None):
    """
    Keeps asking until user enters a valid number.
    Replaces manual validation we did in earlier lessons.
    """
    while True:
        try:
            value = float(input(prompt))

            if min_val is not None and value < min_val:
                print(f"  ⚠️  Value must be at least {min_val}")
                continue

            if max_val is not None and value > max_val:
                print(f"  ⚠️  Value must be no more than {max_val}")
                continue

            return value

        except ValueError:
            print("  ⚠️  Please enter a valid number!")

def get_valid_date(prompt):
    """
    Keeps asking until user enters a valid date MM/DD/YYYY.
    Like DATECHG.PRG validation in Clipper.
    """
    from datetime import datetime
    while True:
        try:
            date_str = input(prompt).strip()
            datetime.strptime(date_str, "%m/%d/%Y")
            return date_str
        except ValueError:
            print("  ⚠️  Invalid date! Please use MM/DD/YYYY format.")

def get_valid_string(prompt, max_length=None, required=True):
    """
    Gets a valid non-empty string from user.
    """
    while True:
        try:
            value = input(prompt).strip()

            if required and value == "":
                print("  ⚠️  This field is required!")
                continue

            if max_length and len(value) > max_length:
                print(f"  ⚠️  Maximum {max_length} characters allowed!")
                continue

            return value

        except Exception as e:
            print(f"  ⚠️  Input error: {e}")

# ---- DATABASE ERROR HANDLING ----

def safe_add_customer(code, custnam, rate):
    """
    Safely adds a customer with full error handling.
    Handles duplicate keys, database errors, etc.
    """
    conn = None
    try:
        conn = sqlite3.connect("arts.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customer (code, lookupid, custnam, rate)
            VALUES (?, ?, ?, ?)
        """, (code, code, custnam, rate))
        conn.commit()
        print(f"  ✅ Customer added: {custnam}")
        return True

    except sqlite3.IntegrityError:
        print(f"  ⚠️  Customer code '{code}' already exists!")
        return False

    except sqlite3.OperationalError as e:
        print(f"  ❌ Database error: {e}")
        print(f"  ❌ Is arts.db in the right folder?")
        return False

    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

    finally:
        if conn:
            conn.close()  # ALWAYS close connection!

def safe_find_customer(code):
    """
    Safely finds a customer with full error handling.
    """
    conn = None
    try:
        conn = sqlite3.connect("arts.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM customer WHERE code = ?", (code,))
        row = cursor.fetchone()

        if row is None:
            print(f"  ⚠️  Customer '{code}' not found!")
            return None

        return dict(row)

    except sqlite3.OperationalError as e:
        print(f"  ❌ Database error: {e}")
        return None

    finally:
        if conn:
            conn.close()

# ---- FILE ERROR HANDLING ----

def safe_read_file(filename):
    """
    Safely reads a file with error handling.
    """
    try:
        if not os.path.exists(filename):
            print(f"  ⚠️  File not found: {filename}")
            return None

        with open(filename, "r") as f:
            content = f.read()
            return content

    except PermissionError:
        print(f"  ❌ Permission denied: {filename}")
        return None

    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return None

# ---- CUSTOM ARTS EXCEPTIONS ----

class ARTSError(Exception):
    """Base exception class for ARTS application"""
    pass

class InvalidPONumber(ARTSError):
    """Raised when PO number format is invalid"""
    pass

class CustomerNotFound(ARTSError):
    """Raised when customer lookup fails"""
    pass

class InvalidAmount(ARTSError):
    """Raised when a financial amount is invalid"""
    pass

def validate_po_number(ponum):
    """
    Validates PO number format - must be 9 digits.
    Raises InvalidPONumber if format is wrong.
    """
    if not ponum.isdigit():
        raise InvalidPONumber(
            f"PO number must contain only digits: {ponum}")
    if len(ponum) != 9:
        raise InvalidPONumber(
            f"PO number must be 9 digits: {ponum}")
    return True

def validate_amount(amount):
    """
    Validates a financial amount.
    Raises InvalidAmount if amount is invalid.
    """
    if amount < 0:
        raise InvalidAmount(
            f"Amount cannot be negative: {amount}")
    if amount > 999999.99:
        raise InvalidAmount(
            f"Amount exceeds maximum: {amount}")
    return True

# ---- MAIN PROGRAM ----

if __name__ == "__main__":

    show_header("ERROR HANDLING TEST")

    # Test 1 - Division by zero
    print("\n  TEST 1: Safe division...")
    print(f"  10 / 2 = {safe_divide(10, 2)}")
    print(f"  10 / 0 = {safe_divide(10, 0)}")

    # Test 2 - Duplicate customer
    print("\n  TEST 2: Duplicate customer handling...")
    safe_add_customer("0032", "Sun Microsystem Inc.", 620.00)
    safe_add_customer("9999", "New Test Customer", 500.00)

    # Test 3 - Customer not found
    print("\n  TEST 3: Customer lookup with error handling...")
    safe_find_customer("0032")
    safe_find_customer("XXXX")

    # Test 4 - File not found
    print("\n  TEST 4: Safe file reading...")
    content = safe_read_file("reports/arts_activity.log")
    if content:
        lines = content.strip().split("\n")
        print(f"  ✅ Log file has {len(lines)} entries")
        print(f"  Last entry: {lines[-1]}")

    safe_read_file("reports/nonexistent_file.txt")

    # Test 5 - PO number validation
    print("\n  TEST 5: PO number validation...")
    test_ponums = ["000056647", "ABC123", "123", "000056648"]
    for ponum in test_ponums:
        try:
            validate_po_number(ponum)
            print(f"  ✅ Valid PO#: {ponum}")
        except InvalidPONumber as e:
            print(f"  ⚠️  Invalid PO#: {e}")

    # Test 6 - Amount validation
    print("\n  TEST 6: Amount validation...")
    test_amounts = [620.00, -100.00, 0.00, 9999999.99]
    for amount in test_amounts:
        try:
            validate_amount(amount)
            print(f"  ✅ Valid amount: {format_currency(amount)}")
        except InvalidAmount as e:
            print(f"  ⚠️  Invalid amount: {e}")

    # Test 7 - Safe input (INTERACTIVE!)
    print("\n  TEST 7: Safe input validation...")
    print("  Try typing letters first, then a valid number!")
    rate = get_valid_float("  Enter a shipping rate: $",
                           min_val=0, max_val=9999)
    print(f"  ✅ Rate accepted: {format_currency(rate)}")

    print("\n  Now try an invalid date, then a valid one!")
    date = get_valid_date("  Enter invoice date (MM/DD/YYYY): ")
    print(f"  ✅ Date accepted: {date}")

    press_any_key()
    print("\n  ✅ Error handling test complete!")