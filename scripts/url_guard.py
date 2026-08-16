"""对外请求 URL 的统一安全校验（构建脚本所有网络入口共用）。

仅允许 http/https，并拒绝 localhost、环回、私有与保留地址。
URL 均来自仓库内常量数据源清单，此处为纵深防御：配置被篡改时
构建直接失败，而不是向内网地址发请求。纯字面量判断，不做 DNS 解析。
"""
import ipaddress
from urllib.parse import urlparse


def assert_safe_url(url):
    parts = urlparse(url)
    if parts.scheme not in ("http", "https"):
        raise ValueError(f"blocked: only http/https URLs are allowed: {url}")
    host = (parts.hostname or "").strip()
    if not host:
        raise ValueError(f"blocked: URL has no host: {url}")
    if host.lower() == "localhost":
        raise ValueError(f"blocked: localhost is not allowed: {url}")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return url  # 普通域名，非 IP 字面量
    if (ip.is_private or ip.is_loopback or ip.is_reserved
            or ip.is_link_local or ip.is_multicast or ip.is_unspecified):
        raise ValueError(
            f"blocked: private/reserved address is not allowed: {url}")
    return url
