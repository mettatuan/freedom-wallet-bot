"""
NLP Utilities - Financial Assistant Core
Extract amounts and parse Vietnamese financial text
"""
import re
from typing import Optional, Tuple


# 1 USD = this many VND (fixed rate)
USD_TO_VND = 26_236


def extract_amount(text: str) -> Optional[int]:
    """
    Extract amount from Vietnamese text.
    
    Supported formats:
    - "35k" → 35000
    - "35000" → 35000
    - "35,000" → 35000
    - "35.000" → 35000
    - "2.5tr" → 2500000
    - "2.5m" → 2500000
    - "100 triệu" → 100000000
    - "$50" / "50 usd" / "50 dollar" / "50 đô" → 50 * 26,236 VND
    
    Args:
        text: Input text (e.g., "Cà phê 35k", "Lương 15 triệu")
    
    Returns:
        Amount in VND (integer), or None if not found
    """
    # ── USD / Dollar detection (before any cleaning) ──────────────────────────
    # Supported: $50 / 50$ / +50$ / 50 usd / 50 dollar / 50 đô / 50 USD
    usd_patterns = [
        r'[+\-]?\$\s*(\d+(?:[.,]\d+)?)',                        # $50  +$50  $1,000
        r'[+\-]?(\d+(?:[.,]\d+)?)\s*\$',                        # 50$  +50$  50 $
        r'(\d+(?:[.,]\d+)?)\s*(?:usd|dollar|đô)(?:\s|$|[^a-z])',  # 50 usd / 50 đô
    ]
    for pat in usd_patterns:
        m = re.search(pat, text.lower())
        if m:
            try:
                num = float(m.group(1).replace(",", "."))
                return int(num * USD_TO_VND)
            except (ValueError, AttributeError):
                pass

    # ── VND amounts ────────────────────────────────────────────────────────────
    # Remove commas and dots from numbers
    text = text.replace(",", "").replace(".", "")
    
    # Pattern: number + optional unit (k, tr, triệu, m, triệu, tỷ)
    patterns = [
        # Format: "35k", "35 k"
        r'(\d+(?:\.\d+)?)\s*k(?:\s|$)',
        # Format: "2.5tr", "2.5 tr", "2.5triệu", "2.5 triệu"
        r'(\d+(?:\.\d+)?)\s*(?:tr|triệu|m)(?:\s|$)',
        # Format: "1tỷ", "1 tỷ", "1ty"
        r'(\d+(?:\.\d+)?)\s*(?:tỷ|ty)(?:\s|$)',
        # Format: plain number "35000"
        r'(\d{4,})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            number_str = match.group(1)
            number = float(number_str)
            
            # Determine unit multiplier
            if 'k' in text[match.start():match.end()].lower():
                return int(number * 1000)
            elif any(unit in text[match.start():match.end()].lower() for unit in ['tr', 'triệu', 'm']):
                return int(number * 1000000)
            elif any(unit in text[match.start():match.end()].lower() for unit in ['tỷ', 'ty']):
                return int(number * 1000000000)
            else:
                # Plain number
                return int(number)
    
    return None


def detect_transaction_type(text: str) -> str:
    """
    Detect if transaction is income or expense.
    
    Income indicators: + prefix, lương, nhận, thu, kinh doanh, bán
    Expense indicators: - prefix, chi, mua, trả, đóng
    
    Default: expense (most transactions are expenses)
    
    Args:
        text: Transaction text
    
    Returns:
        "income" or "expense"
    """
    text_stripped = text.strip()
    text_lower    = text_stripped.lower()

    # ── Explicit sign prefix (+/−) overrides everything ──────────────────
    # Match leading +/- before digits or $ (e.g. "+50$", "-35k", "+ 100k")
    import re as _re
    if _re.match(r'^\+', text_stripped):
        return "income"
    if _re.match(r'^-', text_stripped):
        return "expense"

    # Income keywords
    income_keywords = [
        "lương", "salary", "nhận", "receive", "thu", "income",
        "kinh doanh", "business", "bán", "sell", "sale",
        "lãi", "profit", "thưởng", "bonus"
    ]
    
    # Expense keywords  (unused for now — default falls through)
    expense_keywords = [
        "chi", "spend", "mua", "buy", "trả", "pay",
        "đóng", "payment", "tiền"
    ]
    
    # Check income first (less common)
    for keyword in income_keywords:
        if keyword in text_lower:
            return "income"
    
    # Default to expense
    return "expense"


def extract_description(text: str, amount: int) -> str:
    """
    Extract clean description from transaction text.
    
    Removes amount and units, keeps meaningful text.
    
    Args:
        text: Original text ("Cà phê 35k")
        amount: Extracted amount (35000)
    
    Returns:
        Clean description ("Cà phê")
    """
    # Remove amount patterns
    text_clean = text

    # Remove USD/dollar patterns first
    usd_pats = [
        r'[+\-]?\$\s*\d+(?:[.,]\d+)?',       # +$50  $1,000
        r'[+\-]?\d+(?:[.,]\d+)?\s*\$',        # 50$  +50$
        r'\d+(?:[.,]\d+)?\s*(?:usd|dollar|đô)(?:\s|$|[^a-z])',
    ]
    for p in usd_pats:
        text_clean = re.sub(p, '', text_clean, flags=re.IGNORECASE)

    # Remove leading + or - sign standing alone
    text_clean = re.sub(r'^[+\-]\s*', '', text_clean.strip())

    # Remove number + unit patterns
    patterns = [
        r'\d+(?:\.\d+)?\s*k(?:\s|$)',
        r'\d+(?:\.\d+)?\s*(?:tr|triệu|m)(?:\s|$)',
        r'\d+(?:\.\d+)?\s*(?:tỷ|ty)(?:\s|$)',
        r'\d{4,}',
        r'[\d,\.]+',
    ]
    
    for pattern in patterns:
        text_clean = re.sub(pattern, '', text_clean, flags=re.IGNORECASE)
    
    # Clean up whitespace
    text_clean = ' '.join(text_clean.split())
    
    # If too short, use original (strip leading sign)
    if len(text_clean) < 2:
        return re.sub(r'^[+\-]\s*', '', text.strip())
    
    return text_clean.strip()


def format_vnd(amount: int) -> str:
    """
    Format amount in Vietnamese dong.
    
    Examples:
    - 35000 → "35,000đ"
    - 2500000 → "2,500,000đ"
    - 15000000 → "15,000,000đ"
    
    Args:
        amount: Amount in VND
    
    Returns:
        Formatted string with thousand separators
    """
    # Add thousand separators
    formatted = f"{abs(amount):,}".replace(",", ".")
    
    # Add currency symbol
    if amount < 0:
        return f"-{formatted}đ"
    else:
        return f"{formatted}đ"


def parse_natural_language_transaction(text: str) -> dict:
    """
    Parse natural language transaction into structured data.
    
    Examples:
    - "Cà phê 35k" → {amount: -35000, category: "Ăn uống", description: "Cà phê", type: "expense"}
    - "Lương 15tr" → {amount: 15000000, category: "Lương", description: "Lương", type: "income"}
    
    Args:
        text: Natural language input
    
    Returns:
        Dictionary with parsed transaction data
    """
    from bot.core.categories import detect_category
    
    # Extract amount
    amount = extract_amount(text)
    
    if amount is None:
        return {
            "error": "Không tìm thấy số tiền. VD: 'Cà phê 35k'"
        }
    
    # Detect type
    transaction_type = detect_transaction_type(text)
    
    # Detect category
    category = detect_category(text, transaction_type)
    
    # Extract description
    description = extract_description(text, amount)
    
    # Make amount negative for expenses
    if transaction_type == "expense":
        amount = -abs(amount)
    else:
        amount = abs(amount)
    
    return {
        "amount": amount,
        "category": category,
        "description": description,
        "type": transaction_type,
        "original_text": text
    }
