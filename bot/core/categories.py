"""
Category Detection - Financial Assistant Core
Detect transaction categories from Vietnamese text
"""

# Standard expense categories
EXPENSE_CATEGORIES = {
    "Ăn uống": [
        "ăn", "uống", "cơm", "phở", "bún", "cà phê", "cafe", "trà", "nước",
        "nhà hàng", "quán", "buffet", "lẩu", "nướng", "bánh", "kem",
        "food", "drink", "coffee", "restaurant", "rice", "breakfast", "lunch", "dinner"
    ],
    "Di chuyển": [
        "grab", "xe", "xăng", "dầu", "taxi", "bus", "xe buýt", "gửi xe",
        "đỗ xe", "bãi xe", "uber", "gojek", "be", "vé xe", "tàu", "máy bay",
        "transport", "gas", "parking", "fuel", "bike", "car", "train", "flight"
    ],
    "Mua sắm": [
        "mua", "shop", "shopping", "quần áo", "giày", "dép", "túi xách",
        "mỹ phẩm", "đồ dùng", "siêu thị", "chợ", "mart", "clothes", "shoes"
    ],
    "Giải trí": [
        "phim", "movie", "cinema", "game", "chơi", "du lịch", "travel",
        "vui chơi", "bar", "pub", "karaoke", "concert", "show", "netflix",
        "spotify", "youtube premium"
    ],
    "Sức khỏe": [
        "thuốc", "bệnh viện", "khám", "bác sĩ", "medicine", "hospital",
        "doctor", "vaccine", "tiêm chủng", "y tế", "health", "gym", "yoga"
    ],
    "Học tập": [
        "học", "học phí", "sách", "vở", "trường", "khóa học", "course",
        "book", "education", "tuition", "udemy", "coursera"
    ],
    "Nhà ở": [
        "tiền nhà", "tiền phòng", "thuê nhà", "rent", "house", "home",
        "điện", "nước", "internet", "wifi", "electric", "water", "bill"
    ],
    "Quà tặng": [
        "quà", "gift", "sinh nhật", "birthday", "tặng", "present", "đám cưới",
        "wedding", "lì xì", "red envelope"
    ],
    "Đầu tư": [
        "đầu tư", "investment", "forex", "xau", "xauusd", "gold",
        "crypto", "btc", "eth", "coin", "chứng khoán", "stock",
        "trading", "trade"
    ],
    "Khác": [
        "khác", "other", "linh tinh", "misc"
    ]
}

# Income categories
INCOME_CATEGORIES = {
    "Lương": [
        "lương", "salary", "wage", "pay", "income", "bonus", "thưởng"
    ],
    "Kinh doanh": [
        "kinh doanh", "business", "bán", "sell", "sale", "doanh thu", "revenue"
    ],
    "Đầu tư": [
        "đầu tư", "investment", "lãi", "profit", "dividend", "cổ tức",
        "chứng khoán", "stock", "crypto"
    ],
    "Quà tặng": [
        "quà", "gift", "nhận", "receive", "lì xì", "red envelope"
    ],
    "Khác": [
        "khác", "other", "thu nhập khác"
    ]
}


def detect_category(text: str, transaction_type: str = "expense") -> str:
    """
    Detect category from transaction text.
    
    Args:
        text: Transaction description (e.g., "Cà phê 35k", "Grab về nhà")
        transaction_type: "expense" or "income"
    
    Returns:
        Category name (e.g., "Ăn uống", "Di chuyển")
    """
    # Normalize text
    text_lower = text.lower()
    
    # Select category set
    categories = EXPENSE_CATEGORIES if transaction_type == "expense" else INCOME_CATEGORIES
    
    # Match keywords
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category
    
    # Default to "Khác"
    return "Khác"


def get_all_categories(transaction_type: str = "expense") -> list[str]:
    """Get list of all categories for a transaction type"""
    if transaction_type == "expense":
        return list(EXPENSE_CATEGORIES.keys())
    else:
        return list(INCOME_CATEGORIES.keys())


def get_category_keywords(category: str, transaction_type: str = "expense") -> list[str]:
    """Get keywords for a specific category"""
    categories = EXPENSE_CATEGORIES if transaction_type == "expense" else INCOME_CATEGORIES
    return categories.get(category, [])
