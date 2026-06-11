import pytest
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from app.services.workspace_service import slugify


class TestSecurity:
    def test_password_hash_and_verify(self):
        password = "SecurePass123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("WrongPass", hashed)

    def test_access_token_creation(self):
        token = create_access_token("user-123")
        assert isinstance(token, str)
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["type"] == "access"

    def test_refresh_token_creation(self):
        token = create_refresh_token("user-456")
        payload = decode_token(token)
        assert payload["sub"] == "user-456"
        assert payload["type"] == "refresh"

    def test_invalid_token_raises(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid.token.here")
        assert exc_info.value.status_code == 401


class TestSlugify:
    def test_basic_slug(self):
        assert slugify("My Company") == "my-company"

    def test_special_chars(self):
        assert slugify("Acme Corp. & Sons!") == "acme-corp-sons"

    def test_spaces_to_dashes(self):
        assert slugify("Hello World") == "hello-world"

    def test_already_slug(self):
        assert slugify("already-slug") == "already-slug"


class TestEmailStyles:
    def test_email_style_values(self):
        from app.models.models import EmailStyle
        assert EmailStyle.PROFESSIONAL == "professional"
        assert EmailStyle.FRIENDLY == "friendly"
        assert EmailStyle.STARTUP == "startup"
        assert EmailStyle.ENTERPRISE == "enterprise"


class TestLeadStatus:
    def test_lead_score_to_status(self):
        def score_to_status(score: int) -> str:
            if score >= 70:
                return "hot"
            elif score >= 40:
                return "warm"
            return "cold"

        assert score_to_status(90) == "hot"
        assert score_to_status(70) == "hot"
        assert score_to_status(50) == "warm"
        assert score_to_status(40) == "warm"
        assert score_to_status(39) == "cold"
        assert score_to_status(0) == "cold"
