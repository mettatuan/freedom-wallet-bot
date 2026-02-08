"""
Basic Tests for Freedom Wallet Bot
"""
import pytest
from bot.handlers.message import search_faq


def test_search_faq_greeting():
    """Test FAQ search for greeting"""
    result = search_faq("xin chào")
    assert result["found"] == True
    assert result["category"] == "greeting"


def test_search_faq_transaction():
    """Test FAQ search for transaction question"""
    result = search_faq("làm sao thêm giao dịch")
    assert result["found"] == True
    assert "Giao dịch" in result["category"]


def test_search_faq_jars():
    """Test FAQ search for 6 jars"""
    result = search_faq("6 hũ tiền là gì")
    assert result["found"] == True
    assert result["answer"] is not None


def test_search_faq_not_found():
    """Test FAQ search when question not in database"""
    result = search_faq("random question xyz")
    assert result["found"] == False
    assert result["answer"] is None


def test_search_faq_thanks():
    """Test FAQ search for thanks"""
    result = search_faq("cảm ơn")
    assert result["found"] == True
    assert result["category"] == "thanks"


# Add more tests for:
# - Support ticket creation
# - GPT-4 integration (Phase 2)
# - Database operations
# - Rate limiting
# - Admin commands (Phase 3)
