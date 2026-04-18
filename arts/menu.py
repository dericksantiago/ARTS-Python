# ============================================
# ARTS - Accounts Receivable Tracking System
# menu.py - Main Menu
# Converted from MENUMAIN.PRG
# ============================================

from .utils.functions import show_header, show_footer
from .utils.functions import press_any_key, confirm
from .modules.customers import customer_menu
from datetime import datetime

def main_menu():
    """
    ARTS Main Menu.
    Mirrors the original ARTS main menu screen.
    """
    while True:
        show_header("MAIN MENU")
        now = datetime.now()
        print(f"  {'Date:':<10} "
              f"{now.strftime('%m/%d/%Y'):<20}"
              f"Time: {now.strftime('%H:%M:%S')}")
        print()
        print("    [1]  Delivery Order")
        print("    [2]  Container Maintenance")
        print("    [3]  Invoice")
        print("    [4]  Payments")
        print("    [5]  Customer Table")
        print("    [6]  Broker Table")
        print("    [7]  Employee Table")
        print("    [8]  Reports Menu")
        print()
        print("    [\\]  EXIT")
        show_footer()

        choice = input("  CHOICE: ").strip()

        if choice == "1":
            print("\n  🚧 Delivery Order — Coming Soon!")
            press_any_key()

        elif choice == "2":
            print("\n  🚧 Container Maintenance — Coming Soon!")
            press_any_key()

        elif choice == "3":
            print("\n  🚧 Invoice — Coming Soon!")
            press_any_key()

        elif choice == "4":
            print("\n  🚧 Payments — Coming Soon!")
            press_any_key()

        elif choice == "5":
            customer_menu()

        elif choice == "6":
            print("\n  🚧 Broker Table — Coming Soon!")
            press_any_key()

        elif choice == "7":
            print("\n  🚧 Employee Table — Coming Soon!")
            press_any_key()

        elif choice == "8":
            print("\n  🚧 Reports Menu — Coming Soon!")
            press_any_key()

        elif choice == "\\":
            if confirm("Exit ARTS?"):
                print("\n  Goodbye! 👋")
                break

        else:
            print("  ⚠️  Invalid choice!")