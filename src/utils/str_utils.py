class StrUtils:
    """Utility class for string operations."""

    @staticmethod
    def truncate(text: str, max_length: int) -> str:
        """Truncate a string to maximum length with ellipsis if needed.

        Args:
            text: The string to truncate.
            max_length: Maximum length including ellipsis.

        Returns:
            Truncated string with '...' at the end if it exceeds max_length.
        """
        if len(text) > max_length:
            return text[:max_length - 1] + "..."
        return text
