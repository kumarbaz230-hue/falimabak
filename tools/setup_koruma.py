"""Tek seferlik: koruma.py içindeki şifreli parçaları üretir (key burada kalır, commit etme)."""
import hashlib
import json
import os

KEY = open(os.path.join(os.path.dirname(__file__), '..', 'secrets.json'), encoding='utf-8')
KEY = json.load(KEY)['gemini_api_key']

SEED_A = 'falimabak_koruma_v1'
SEED_B = 'org.kumar.falimabak'

enc = [ord(KEY[i]) ^ ord(SEED_A[i % len(SEED_A)]) ^ ord(SEED_B[(i * 3) % len(SEED_B)]) for i in range(len(KEY))]
dec = ''.join(chr(enc[i] ^ ord(SEED_A[i % len(SEED_A)]) ^ ord(SEED_B[(i * 3) % len(SEED_B)])) for i in range(len(enc)))
assert dec == KEY

butunluk = hashlib.sha256((SEED_A + SEED_B + str(len(enc))).encode()).hexdigest()
print('_ENC =', enc)
print('_BUTUNLUK =', butunluk)
print('len', len(enc))
