import ipaddress
import socket
from urllib.parse import urlparse

ALLOWED_SCHEMES = {"http", "https"}


class BlockedUrl(Exception):
    pass


def resolve(host, port):
    return [info[4][0] for info in socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)]


def ensure_public(url, resolver=resolve):
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.hostname:
        raise BlockedUrl(f"solo puedo leer páginas http o https públicas, no {url}")
    try:
        addresses = resolver(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror:
        raise BlockedUrl(f"no encontré el sitio {parsed.hostname}")
    for address in addresses:
        if not ipaddress.ip_address(address.split("%")[0]).is_global:
            raise BlockedUrl(f"{parsed.hostname} es una dirección de la red local y no puedo leerla")
    return url
