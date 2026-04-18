# ============================================
# ARTS - Accounts Receivable Tracking System
# utils/errors.py - Custom Exception Classes
# Converted from ERRORSYS.PRG / ERRDISP.PRG
# ============================================

class ARTSError(Exception):
    """Base exception class for ARTS application"""
    pass

class InvalidPONumber(ARTSError):
    """Raised when PO number format is invalid"""
    pass

class CustomerNotFound(ARTSError):
    """Raised when customer lookup fails"""
    pass

class BrokerNotFound(ARTSError):
    """Raised when broker lookup fails"""
    pass

class EmployeeNotFound(ARTSError):
    """Raised when employee lookup fails"""
    pass

class InvalidAmount(ARTSError):
    """Raised when a financial amount is invalid"""
    pass

class InvalidDate(ARTSError):
    """Raised when a date format is invalid"""
    pass

class DatabaseError(ARTSError):
    """Raised when a database operation fails"""
    pass

class DuplicateRecord(ARTSError):
    """Raised when a duplicate record is detected"""
    pass