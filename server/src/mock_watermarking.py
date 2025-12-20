"""Mock watermarking methods for unit testing.

This module provides controllable mock implementations of watermarking methods
that can simulate both successful operations and various failure scenarios.
These mocks enable thorough branch coverage testing of the create-watermark
and read-watermark endpoints without relying on actual watermarking logic.
"""

import os
from typing import Optional


class MockWatermarkingMethod:
    """Base class for mock watermarking methods.
    
    Mock methods can be controlled via environment variables to simulate
    different scenarios during testing.
    """
    
    def __init__(self):
        self.name = "mock-method"
    
    def get_usage(self) -> str:
        """Return usage description for this mock method."""
        return "Mock watermarking method for unit testing"
    
    def is_applicable(self, pdf: str, position: Optional[str] = None) -> bool:
        """Check if watermarking is applicable.
        
        Can be controlled via MOCK_WM_APPLICABLE environment variable:
        - 'false' or '0': Returns False (not applicable)
        - anything else: Returns True (applicable)
        """
        return os.environ.get("MOCK_WM_APPLICABLE", "true").lower() not in ("false", "0")
    
    def apply(self, pdf: str, secret: str, key: str, position: Optional[str] = None) -> bytes:
        """Apply mock watermark.
        
        Can be controlled via MOCK_WM_APPLY_FAIL environment variable:
        - 'no_output': Returns empty bytes
        - 'exception': Raises an exception
        - 'invalid_type': Returns a string instead of bytes
        - anything else: Returns mock PDF bytes
        """
        fail_mode = os.environ.get("MOCK_WM_APPLY_FAIL", "")
        
        if fail_mode == "no_output":
            # Simulate watermarking producing no output
            return b""
        elif fail_mode == "exception":
            # Simulate watermarking failure with exception
            raise RuntimeError("Mock watermarking failed: simulated error")
        elif fail_mode == "invalid_type":
            # Simulate watermarking returning wrong type (for defensive branches)
            # Note: This cannot be covered in unit tests as Python's type system
            # won't allow this at runtime, but it's here to document the intention
            return "not bytes"  # type: ignore
        else:
            # Successful watermarking - return mock watermarked PDF
            mock_pdf = b"%PDF-1.4\n"
            mock_pdf += f"% Watermarked with secret: {secret[:10]}...\n".encode()
            mock_pdf += b"1 0 obj\n<< /Type /Catalog >>\nendobj\n"
            mock_pdf += b"%%EOF\n"
            return mock_pdf
    
    def read(self, pdf: str, key: str, position: Optional[str] = None) -> str:
        """Read mock watermark.
        
        Can be controlled via MOCK_WM_READ_FAIL environment variable:
        - 'exception': Raises an exception
        - 'not_found': Raises exception indicating watermark not found
        - anything else: Returns the mock secret
        """
        fail_mode = os.environ.get("MOCK_WM_READ_FAIL", "")
        
        if fail_mode == "exception":
            # Simulate watermark reading failure
            raise RuntimeError("Mock watermark reading failed: simulated error")
        elif fail_mode == "not_found":
            # Simulate watermark not found
            raise ValueError("No watermark found in document")
        else:
            # Successful reading - return mock secret
            return "mock-secret-extracted"


class MockWhitespaceStego(MockWatermarkingMethod):
    """Mock implementation of whitespace steganography method."""
    
    def __init__(self):
        super().__init__()
        self.name = "whitespace-stego"
    
    def get_usage(self) -> str:
        return "Mock whitespace steganography for testing"


class MockPDFObjectStream(MockWatermarkingMethod):
    """Mock implementation of PDF object stream method."""
    
    def __init__(self):
        super().__init__()
        self.name = "pdf-object-stream"
    
    def get_usage(self) -> str:
        return "Mock PDF object stream embedding for testing"


class MockAddAfterEOF(MockWatermarkingMethod):
    """Mock implementation of add-after-EOF method."""
    
    def __init__(self):
        super().__init__()
        self.name = "add-after-eof"
    
    def get_usage(self) -> str:
        return "Mock add-after-EOF for testing"


class MockBase64InvisibleComment(MockWatermarkingMethod):
    """Mock implementation of base64 invisible comment method."""
    
    def __init__(self):
        super().__init__()
        self.name = "base64-invisible-comment"
    
    def get_usage(self) -> str:
        return "Mock base64 invisible comment for testing"


# Registry of mock methods
MOCK_METHODS = {
    "whitespace-stego": MockWhitespaceStego(),
    "pdf-object-stream": MockPDFObjectStream(),
    "add-after-eof": MockAddAfterEOF(),
    "base64-invisible-comment": MockBase64InvisibleComment(),
}


def get_mock_method(name: str) -> MockWatermarkingMethod:
    """Get a mock watermarking method by name.
    
    Args:
        name: Name of the watermarking method
        
    Returns:
        MockWatermarkingMethod instance
        
    Raises:
        KeyError: If method name is not found
    """
    if name not in MOCK_METHODS:
        raise KeyError(f"Unknown mock watermarking method: {name}")
    return MOCK_METHODS[name]


def is_mock_watermarking_applicable(method: str, pdf: str, position: Optional[str] = None) -> bool:
    """Check if mock watermarking is applicable."""
    mock_method = get_mock_method(method)
    return mock_method.is_applicable(pdf, position)


def apply_mock_watermark(pdf: str, secret: str, key: str, method: str, position: Optional[str] = None) -> bytes:
    """Apply mock watermark."""
    mock_method = get_mock_method(method)
    return mock_method.apply(pdf, secret, key, position)


def read_mock_watermark(method: str, pdf: str, key: str, position: Optional[str] = None) -> str:
    """Read mock watermark."""
    mock_method = get_mock_method(method)
    return mock_method.read(pdf, key, position)
