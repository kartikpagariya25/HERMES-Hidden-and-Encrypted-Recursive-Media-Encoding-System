"""
HERMES Crypto Module
====================
Two encryption modes:

1. PASSWORD MODE  — AES-256-GCM + PBKDF2
   - User types a shared password
   - PBKDF2 derives a strong 256-bit key from it
   - AES-GCM encrypts the payload
   - Salt + nonce stored in the output (safe to expose, useless without password)

2. KEYPAIR MODE   — RSA-OAEP + AES-256-GCM  (hybrid encryption)
   - Receiver generates a keypair once (generate_keypair)
   - Receiver shares public key (.pem) with sender
   - Sender encrypts:  RSA-OAEP encrypts a random AES key  →  AES-GCM encrypts the payload
   - Only receiver's private key can decrypt

Both modes return plain bytes that can be passed directly into any HERMES
steganography encoder, and accepted directly from any HERMES decoder.

Payload wire format
-------------------
Password mode:
  [1 byte mode=0x01] [16 bytes salt] [12 bytes nonce] [encrypted bytes...]

Keypair mode:
  [1 byte mode=0x02] [2 bytes rsa_len big-endian] [rsa_len bytes encrypted AES key]
  [12 bytes nonce] [encrypted bytes...]
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

_PBKDF2_ITERATIONS = 390_000          # OWASP 2023 recommendation for SHA-256
_MODE_PASSWORD     = b'\x01'
_MODE_KEYPAIR      = b'\x02'


# ── Helpers ──────────────────────────────────────────────────────────────────

def _derive_key(password: str, salt: bytes) -> bytes:
    """PBKDF2-HMAC-SHA256 → 32-byte AES key."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=_PBKDF2_ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode("utf-8"))


# ── Password mode ─────────────────────────────────────────────────────────────

def encrypt_with_password(data: bytes, password: str) -> bytes:
    """
    Encrypt *data* using AES-256-GCM with a key derived from *password*.
    Returns the full payload (mode byte + salt + nonce + ciphertext).
    """
    if not password:
        raise ValueError("Password cannot be empty")

    salt  = os.urandom(16)
    nonce = os.urandom(12)
    key   = _derive_key(password, salt)

    ciphertext = AESGCM(key).encrypt(nonce, data, None)
    return _MODE_PASSWORD + salt + nonce + ciphertext


def decrypt_with_password(payload: bytes, password: str) -> bytes:
    """
    Decrypt a payload produced by *encrypt_with_password*.
    Raises ValueError on wrong password or tampered data.
    """
    if not password:
        raise ValueError("Password cannot be empty")
    if len(payload) < 1 + 16 + 12 + 1:
        raise ValueError("Payload too short — not a valid HERMES encrypted blob")
    if payload[0:1] != _MODE_PASSWORD:
        raise ValueError("Payload was not encrypted with password mode")

    salt       = payload[1:17]
    nonce      = payload[17:29]
    ciphertext = payload[29:]
    key        = _derive_key(password, salt)

    try:
        return AESGCM(key).decrypt(nonce, ciphertext, None)
    except Exception:
        raise ValueError("Decryption failed — wrong password or corrupted data")


# ── Keypair mode ──────────────────────────────────────────────────────────────

def generate_keypair() -> tuple[bytes, bytes]:
    """
    Generate a fresh RSA-2048 keypair.
    Returns (private_pem_bytes, public_pem_bytes).
    Both are PEM-encoded and can be saved as .pem files.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_pem, public_pem


def encrypt_with_public_key(data: bytes, public_pem: bytes) -> bytes:
    """
    Hybrid encryption: random AES key encrypted with RSA-OAEP,
    then data encrypted with AES-256-GCM.

    Wire format:
      [0x02] [2B rsa_len] [rsa_len B encrypted AES key] [12B nonce] [ciphertext]
    """
    public_key = serialization.load_pem_public_key(public_pem, backend=default_backend())

    aes_key = os.urandom(32)
    nonce   = os.urandom(12)

    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    ciphertext = AESGCM(aes_key).encrypt(nonce, data, None)

    rsa_len = len(encrypted_aes_key).to_bytes(2, "big")
    return _MODE_KEYPAIR + rsa_len + encrypted_aes_key + nonce + ciphertext


def decrypt_with_private_key(payload: bytes, private_pem: bytes) -> bytes:
    """
    Decrypt a payload produced by *encrypt_with_public_key*.
    Raises ValueError on wrong key or tampered data.
    """
    if len(payload) < 1 + 2 + 12 + 1:
        raise ValueError("Payload too short — not a valid HERMES encrypted blob")
    if payload[0:1] != _MODE_KEYPAIR:
        raise ValueError("Payload was not encrypted with keypair mode")

    rsa_len           = int.from_bytes(payload[1:3], "big")
    encrypted_aes_key = payload[3 : 3 + rsa_len]
    nonce             = payload[3 + rsa_len : 3 + rsa_len + 12]
    ciphertext        = payload[3 + rsa_len + 12:]

    private_key = serialization.load_pem_private_key(
        private_pem, password=None, backend=default_backend()
    )

    try:
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return AESGCM(aes_key).decrypt(nonce, ciphertext, None)
    except Exception:
        raise ValueError("Decryption failed — wrong private key or corrupted data")


# ── Auto-detect decrypt (convenience) ────────────────────────────────────────

def decrypt_auto(payload: bytes, *, password: str = "", private_pem: bytes = b"") -> bytes:
    """
    Detect mode from the first byte and call the right decrypt function.
    Pass either *password* or *private_pem*, not both.
    """
    if not payload:
        raise ValueError("Empty payload")

    mode = payload[0:1]
    if mode == _MODE_PASSWORD:
        if not password:
            raise ValueError("This payload requires a password to decrypt")
        return decrypt_with_password(payload, password)
    elif mode == _MODE_KEYPAIR:
        if not private_pem:
            raise ValueError("This payload requires a private key (.pem) to decrypt")
        return decrypt_with_private_key(payload, private_pem)
    else:
        raise ValueError("Unknown encryption mode — payload may be unencrypted or corrupted")