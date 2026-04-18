# ============================================
# ARTS - Accounts Receivable and Tracking System
# main.py - Application Entry Point
# Converted from ARTS.PRG
# ============================================

from .utils.database import init_database
from .utils.functions import draw_box
from .menu import main_menu

def run():
    """Main entry point for ARTS application"""

    # Initialize database on first run
    init_database()

    # Clear screen
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

    # Show splash screen using YOUR draw_box function!
    from .utils.functions import draw_box
    draw_box([
        "",
        "ACCOUNTS RECEIVABLE REPORTING AND",
        "TRACKING SYSTEM",
        "",
        "A  R  T  S",
        "",
        "Python Edition  —  Version 1.0",
        "Converted from Clipper Summer '87",
        "",
        "*** PRESS ENTER TO BEGIN ***",
        ""
    ])
    input()

    # Launch main menu
    main_menu()