"""Тесты реферальной системы / Referral tests."""

from app.services.referral import generate_referral_code


def test_generate_referral_code_length():
    code = generate_referral_code(8)
    assert len(code) == 8
    assert code.isalnum()
    assert code == code.upper()


def test_generate_referral_code_unique():
    codes = {generate_referral_code() for _ in range(50)}
    assert len(codes) >= 45


def test_generate_referral_code_max_20():
    code = generate_referral_code(20)
    assert len(code) <= 20
