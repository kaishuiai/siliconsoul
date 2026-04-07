"""
Input Validator

Provides user-friendly input validation and sanitization.
Replaces raw Pydantic errors with helpful messages.
"""

import re
from typing import Tuple, Optional
from src.logging.logger import get_logger

logger = get_logger("input_validator")


class InputValidator:
    """Validates and sanitizes user input"""

    # Security patterns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
    ]

    SQL_PATTERNS = [
        r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)",
        r"(--|#|;).*?$",
    ]

    PATH_PATTERNS = [
        r'\.\./+',
        r'\.\.\\+',
    ]

    # Configuration
    MAX_TEXT_LENGTH = 10000
    MIN_TEXT_LENGTH = 1
    MAX_USER_ID_LENGTH = 256
    MIN_USER_ID_LENGTH = 1

    @staticmethod
    def validate_text(text: Optional[str]) -> Tuple[bool, str]:
        """
        Validate user input text.

        Args:
            text: User input text

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Check if text is provided
        if text is None:
            return False, "Input cannot be empty. Please provide a text query."

        if isinstance(text, str):
            text = text.strip()

        # Check if empty after stripping
        if not text:
            return False, "Input cannot be empty or whitespace only. Please provide a text query."

        # Check length
        if len(text) < InputValidator.MIN_TEXT_LENGTH:
            return False, f"Input is too short (min {InputValidator.MIN_TEXT_LENGTH} character)"

        if len(text) > InputValidator.MAX_TEXT_LENGTH:
            return (
                False,
                f"Input is too long (max {InputValidator.MAX_TEXT_LENGTH} characters). "
                f"Current length: {len(text)}",
            )

        return True, ""

    @staticmethod
    def validate_user_id(user_id: Optional[str]) -> Tuple[bool, str]:
        """
        Validate user ID.

        Args:
            user_id: User identifier

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if user_id is None:
            return False, "User ID is required."

        if isinstance(user_id, str):
            user_id = user_id.strip()

        if not user_id:
            return False, "User ID cannot be empty."

        if len(user_id) < InputValidator.MIN_USER_ID_LENGTH:
            return False, f"User ID is too short (min {InputValidator.MIN_USER_ID_LENGTH} character)"

        if len(user_id) > InputValidator.MAX_USER_ID_LENGTH:
            return False, f"User ID is too long (max {InputValidator.MAX_USER_ID_LENGTH} characters)"

        return True, ""

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize text to prevent common attacks.

        Args:
            text: Text to sanitize

        Returns:
            str: Sanitized text
        """
        if not text:
            return text

        # Remove XSS patterns
        for pattern in InputValidator.XSS_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

        # Remove SQL injection patterns (optional - depends on backend)
        # Disabled by default as these patterns might appear in legitimate queries
        # for pattern in InputValidator.SQL_PATTERNS:
        #     if re.search(pattern, text, flags=re.IGNORECASE):
        #         logger.warning(f"Potential SQL injection detected: {text[:100]}")

        # Remove path traversal patterns
        for pattern in InputValidator.PATH_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        return text

    @staticmethod
    def check_xss(text: str) -> Tuple[bool, str]:
        """
        Check if text contains XSS patterns.

        Args:
            text: Text to check

        Returns:
            Tuple[bool, str]: (contains_xss, pattern_found)
        """
        for pattern in InputValidator.XSS_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL):
                return True, pattern
        return False, ""

    @staticmethod
    def check_sql_injection(text: str) -> Tuple[bool, str]:
        """
        Check if text contains SQL injection patterns.

        Args:
            text: Text to check

        Returns:
            Tuple[bool, str]: (contains_sql_injection, pattern_found)
        """
        for pattern in InputValidator.SQL_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
                return True, pattern
        return False, ""

    @staticmethod
    def check_path_traversal(text: str) -> Tuple[bool, str]:
        """
        Check if text contains path traversal patterns.

        Args:
            text: Text to check

        Returns:
            Tuple[bool, str]: (contains_path_traversal, pattern_found)
        """
        for pattern in InputValidator.PATH_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return True, pattern
        return False, ""

    @staticmethod
    def validate_and_sanitize(
        text: Optional[str], user_id: Optional[str]
    ) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """
        Comprehensive validation and sanitization.

        Args:
            text: User input text
            user_id: User identifier

        Returns:
            Tuple[bool, str, str, str]:
                - is_valid: Whether input is valid
                - error_message: Error message if invalid
                - sanitized_text: Sanitized text if valid
                - validated_user_id: Validated user ID if valid
        """
        # Validate text
        text_valid, text_error = InputValidator.validate_text(text)
        if not text_valid:
            logger.warning(f"Invalid text input: {text_error}")
            return False, text_error, None, None

        # Validate user ID
        user_id_valid, user_id_error = InputValidator.validate_user_id(user_id)
        if not user_id_valid:
            logger.warning(f"Invalid user ID: {user_id_error}")
            return False, user_id_error, None, None

        # Check for security issues (log but don't block)
        xss_found, xss_pattern = InputValidator.check_xss(text)
        if xss_found:
            logger.warning(f"Potential XSS pattern detected: {xss_pattern}")

        sql_found, sql_pattern = InputValidator.check_sql_injection(text)
        if sql_found:
            logger.warning(f"Potential SQL injection pattern detected: {sql_pattern}")

        path_found, path_pattern = InputValidator.check_path_traversal(text)
        if path_found:
            logger.warning(f"Potential path traversal pattern detected: {path_pattern}")

        # Sanitize (optional - remove obviously malicious patterns)
        sanitized = InputValidator.sanitize_text(text)

        return True, "", sanitized, user_id
