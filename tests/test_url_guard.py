"""Unit tests for url_guard.assert_safe_url (构建网络入口的 URL 边界)."""
import os
import sys

import pytest

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS = os.path.join(_REPO, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from url_guard import assert_safe_url  # noqa: E402


@pytest.mark.parametrize("url", [
    "https://artificialanalysis.ai/leaderboards/providers",
    "http://livebench.ai/table.csv",
])
def test_allows_public_http_urls(url):
    assert assert_safe_url(url) == url


@pytest.mark.parametrize("url", [
    "ftp://example.com/x",
    "file:///etc/passwd",
    "https://localhost/x",
    "http://127.0.0.1/x",
    "http://10.0.0.1/x",
    "http://192.168.1.1/x",
    "http://172.16.0.1/x",
    "http://169.254.169.254/latest/meta-data",  # 云元数据端点
    "http://[::1]/x",
    "http://0.0.0.0/x",
])
def test_blocks_unsafe_urls(url):
    with pytest.raises(ValueError):
        assert_safe_url(url)
