from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from typing import Tuple

_PRIVATE_KEY_PEM: str = None
_PUBLIC_KEY_PEM: str = None

def generate_or_get_keypair() -> Tuple[str, str]:
    """Generates RSA-2048 keypair or returns cached PEM strings."""
    global _PRIVATE_KEY_PEM, _PUBLIC_KEY_PEM
    
    if _PRIVATE_KEY_PEM and _PUBLIC_KEY_PEM:
        return _PRIVATE_KEY_PEM, _PUBLIC_KEY_PEM
        
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    _PRIVATE_KEY_PEM = private_pem
    _PUBLIC_KEY_PEM = public_pem
    
    return private_pem, public_pem
