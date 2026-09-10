# Speed-port tests (wzgram parity): crypto backend and upload-part fast length.
import os

from pyrogram import raw
from pyrogram.crypto import aes
from pyrogram.session.session import _upload_part_length

# Known-answer vectors produced by the pure-python (pyaes) reference backend:
# key = bytes(range(32)), iv = bytes(range(32)), pt = bytes((i*7) & 0xff, 64).
IGE_CT = "f07912e66e3925418bc3ae111f6b88e65c376d32ed57a127d4ddcbcfdd36e98d4bb94e1000a97230f86ede44282dcf416937f428214ff6fdb610ce155a9cb7ef"
CTR_CT = "5a690a4214d85ba7c81113705698c4fb10846e504f16c2fcfdb94decb62ef216fc8299aec6c6c6b5a3fe2d88d12a85dbc69c591744e3dd6ee1cfcb8d5dcf5fe4"


def test_ige_matches_reference_vector():
    key = bytes(range(32))
    iv = bytes(range(32))
    pt = bytes((i * 7) & 0xff for i in range(64))
    assert aes.ige256_encrypt(pt, key, iv).hex() == IGE_CT
    assert aes.ige256_decrypt(bytes.fromhex(IGE_CT), key, iv) == pt


def test_ctr_matches_reference_vector():
    key = bytes(range(32))
    pt = bytes((i * 7) & 0xff for i in range(64))
    assert aes.ctr256_encrypt(pt, key, bytearray(range(16)), bytearray(1)).hex() == CTR_CT
    assert aes.ctr256_decrypt(bytes.fromhex(CTR_CT), key, bytearray(range(16)), bytearray(1)) == pt


def test_ige_ctr_roundtrip_large():
    key = os.urandom(32)
    iv = os.urandom(32)
    data = os.urandom(512 * 1024)  # one full upload part
    assert aes.ige256_decrypt(aes.ige256_encrypt(data, key, iv), key, iv) == data
    assert aes.ctr256_decrypt(
        aes.ctr256_encrypt(data, key, bytearray(iv[:16]), bytearray(1)),
        key, bytearray(iv[:16]), bytearray(1),
    ) == data


def test_upload_part_length_matches_serialization():
    sizes = [1, 100, 252, 253, 254, 255, 1000, 512 * 1024]
    for n in sizes:
        chunk = os.urandom(n)
        small = raw.functions.upload.SaveFilePart(file_id=12345, file_part=7, bytes=chunk)
        big = raw.functions.upload.SaveBigFilePart(
            file_id=12345, file_part=7, file_total_parts=99, bytes=chunk
        )
        assert _upload_part_length(small) == len(small.write()) == len(small), n
        assert _upload_part_length(big) == len(big.write()) == len(big), n


def test_upload_part_length_none_for_other_objects():
    ping = raw.functions.Ping(ping_id=1)
    assert _upload_part_length(ping) is None
