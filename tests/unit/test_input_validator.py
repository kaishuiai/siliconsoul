import pytest

from src.core.input_validator import InputValidator


class TestValidateText:
    def test_validate_text_none(self):
        ok, err = InputValidator.validate_text(None)
        assert ok is False
        assert err

    def test_validate_text_whitespace(self):
        ok, err = InputValidator.validate_text("   ")
        assert ok is False
        assert err

    def test_validate_text_too_long(self):
        text = "a" * (InputValidator.MAX_TEXT_LENGTH + 1)
        ok, err = InputValidator.validate_text(text)
        assert ok is False
        assert "too long" in err.lower()

    def test_validate_text_ok(self):
        ok, err = InputValidator.validate_text("hello")
        assert ok is True
        assert err == ""


class TestValidateUserId:
    def test_validate_user_id_none(self):
        ok, err = InputValidator.validate_user_id(None)
        assert ok is False
        assert err

    def test_validate_user_id_empty(self):
        ok, err = InputValidator.validate_user_id(" ")
        assert ok is False
        assert err

    def test_validate_user_id_too_long(self):
        user_id = "u" * (InputValidator.MAX_USER_ID_LENGTH + 1)
        ok, err = InputValidator.validate_user_id(user_id)
        assert ok is False
        assert "too long" in err.lower()

    def test_validate_user_id_ok(self):
        ok, err = InputValidator.validate_user_id("user_1")
        assert ok is True
        assert err == ""


class TestSecurityChecks:
    def test_check_xss(self):
        found, pattern = InputValidator.check_xss("<script>alert(1)</script>")
        assert found is True
        assert pattern

    def test_check_sql_injection(self):
        found, pattern = InputValidator.check_sql_injection("SELECT * FROM users;")
        assert found is True
        assert pattern

    def test_check_path_traversal(self):
        found, pattern = InputValidator.check_path_traversal("../etc/passwd")
        assert found is True
        assert pattern

    def test_sanitize_text_removes_obvious_patterns(self):
        text = "<script>alert(1)</script> ../etc/passwd"
        sanitized = InputValidator.sanitize_text(text)
        assert "script" not in sanitized.lower()
        assert ".." not in sanitized


class TestValidateAndSanitize:
    def test_validate_and_sanitize_invalid_text(self):
        ok, err, sanitized, user_id = InputValidator.validate_and_sanitize(" ", "user")
        assert ok is False
        assert err
        assert sanitized is None
        assert user_id is None

    def test_validate_and_sanitize_invalid_user_id(self):
        ok, err, sanitized, user_id = InputValidator.validate_and_sanitize("hello", " ")
        assert ok is False
        assert err
        assert sanitized is None
        assert user_id is None

    def test_validate_and_sanitize_ok(self):
        ok, err, sanitized, user_id = InputValidator.validate_and_sanitize(" hello ", " user_1 ")
        assert ok is True
        assert err == ""
        assert sanitized is not None
        assert user_id == " user_1 "

    @pytest.mark.parametrize(
        "text",
        [
            "<script>alert(1)</script> hi",
            "UNION SELECT password FROM users",
            "../etc/passwd",
        ],
    )
    def test_validate_and_sanitize_logs_but_allows(self, text):
        ok, err, sanitized, user_id = InputValidator.validate_and_sanitize(text, "user_1")
        assert ok is True
        assert err == ""
        assert sanitized is not None
        assert user_id == "user_1"
