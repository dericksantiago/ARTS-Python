# ============================================
# ARTS - Almar Reporting and Tracking System
# fileio.py - File I/O Lesson
# ============================================

import os
from datetime import datetime
from functions import show_header, format_currency, press_any_key

# ---- WRITE A REPORT FILE ----

def save_invoice_report(invoice):
    """
    Saves an invoice to a text file.
    Mirrors SET ALTERNATE TO in Clipper
    """
    # Create reports folder if it doesn't exist
    if not os.path.exists("reports"):
        os.makedirs("reports")

    # Generate filename with date - e.g. invoice_20160731.txt
    today = datetime.now().strftime("%Y%m%d")
    filename = f"reports/invoice_{invoice['ponum']}_{today}.txt"

    with open(filename, "w") as f:
        f.write("=" * 50 + "\n")
        f.write("      ALMAR REPORTING & TRACKING SYSTEM\n")
        f.write("             INVOICE REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"P.O. NUMBER : {invoice['ponum']}\n")
        f.write(f"P.O. DATE   : {invoice['podat']}\n")
        f.write(f"CUSTOMER    : {invoice['customer']}\n")
        f.write(f"BROKER      : {invoice['broker']}\n")
        f.write(f"SHIP TO     : {invoice['shipto']}\n")
        f.write(f"SHIP FROM   : {invoice['shipfm']}\n")
        f.write("-" * 50 + "\n")
        f.write(f"RATE        : {format_currency(invoice['rate'])}\n")
        f.write(f"MISC CHG 1  : {format_currency(invoice['misc1'])}\n")
        f.write(f"MISC CHG 2  : {format_currency(invoice['misc2'])}\n")
        f.write(f"MISC CHG 3  : {format_currency(invoice['misc3'])}\n")
        f.write("-" * 50 + "\n")
        f.write(f"TOTAL DUE   : {format_currency(invoice['total_due'])}\n")
        f.write(f"AMOUNT PAID : {format_currency(invoice['amount_paid'])}\n")
        f.write(f"BALANCE DUE : {format_currency(invoice['balance_due'])}\n")
        f.write("=" * 50 + "\n")
        f.write(f"Printed: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}\n")

    print(f"\n  ✅ Report saved to: {filename}")
    return filename

# ---- READ A REPORT FILE ----

def read_invoice_report(filename):
    """Reads and displays a saved invoice report"""
    if not os.path.exists(filename):
        print(f"  ⚠️  File not found: {filename}")
        return

    show_header("INVOICE REPORT")
    with open(filename, "r") as f:
        print(f.read())

# ---- SAVE TO CSV ----

def save_payments_csv(payments, filename="reports/payments_export.csv"):
    """
    Exports payment records to CSV format.
    CSV = Comma Separated Values - opens in Excel!
    """
    if not os.path.exists("reports"):
        os.makedirs("reports")

    with open(filename, "w") as f:
        # Write header row
        f.write("PO Number,Check Date,Check No,Amount\n")

        # Write each payment
        for payment in payments:
            f.write(f"{payment['ponum']},{payment['checkdat']}")
            f.write(f",{payment['checkno']},{payment['amt']}\n")

    print(f"\n  ✅ Payments exported to: {filename}")
    return filename

# ---- APPEND TO LOG FILE ----

def log_activity(action, details):
    """
    Logs system activity to a log file.
    Uses append mode so history is preserved.
    """
    if not os.path.exists("reports"):
        os.makedirs("reports")

    timestamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    with open("reports/arts_activity.log", "a") as f:
        f.write(f"{timestamp} | {action} | {details}\n")

# ---- MAIN PROGRAM - Test all functions ----

if __name__ == "__main__":

    show_header("FILE I/O TEST")

    # Sample invoice data - based on real ARTS invoice screen!
    invoice = {
        "ponum"      : "000056647",
        "podat"      : "07/31/2016",
        "customer"   : "Sun Microsystem Inc.",
        "broker"     : "Karl Schroff & Associates",
        "shipto"     : "SSF4CONTS@S/155/CAN",
        "shipfm"     : "PIER 96 SFO",
        "rate"       : 620.00,
        "misc1"      : 0.00,
        "misc2"      : 0.00,
        "misc3"      : 0.00,
        "total_due"  : 620.00,
        "amount_paid": 620.00,
        "balance_due": 0.00
    }

    # Sample payments - based on real ARTS payment data!
    payments = [
        {"ponum": "000056647", "checkdat": "04/09/1992",
         "checkno": "107734", "amt": 620.00},
        {"ponum": "000056648", "checkdat": "04/15/1992",
         "checkno": "107735", "amt": 450.00},
        {"ponum": "000056649", "checkdat": "04/20/1992",
         "checkno": "107736", "amt": 380.00},
    ]

    # Test 1 - Save invoice report
    print("\n  TEST 1: Saving invoice report...")
    filename = save_invoice_report(invoice)

    # Test 2 - Read it back
    print("\n  TEST 2: Reading invoice report back...")
    press_any_key()
    read_invoice_report(filename)

    # Test 3 - Export payments to CSV
    print("\n  TEST 3: Exporting payments to CSV...")
    save_payments_csv(payments)

    # Test 4 - Log activity
    print("\n  TEST 4: Logging activity...")
    log_activity("INVOICE PRINTED", f"PO# {invoice['ponum']}")
    log_activity("PAYMENTS EXPORTED", "3 records exported to CSV")
    print("  ✅ Activity logged to: reports/arts_activity.log")

    press_any_key()
    print("\n  Check your invoicing_app/reports/ folder!")
    print("  You should see 3 new files there!")