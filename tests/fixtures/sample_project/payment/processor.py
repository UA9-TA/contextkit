def process_payment(amount: float, currency: str) -> bool:
    """Process a payment."""
    if amount <= 0:
        return False
    return True
