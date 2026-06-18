"""Groq anahtari icin koruma.py _GR_ENC listesini uretir (secrets.json okur)."""
import json
import os

SEED_A = 'falimabak_koruma_v1'
SEED_B = 'org.kumar.falimabak'

yol = os.path.join(os.path.dirname(__file__), '..', 'secrets.json')
with open(yol, encoding='utf-8') as f:
    key = (json.load(f).get('groq_api_key') or '').strip()

if not key.startswith('gsk_'):
    raise SystemExit('secrets.json icinde gecerli groq_api_key yok')

enc = [
    ord(key[i]) ^ ord(SEED_A[i % len(SEED_A)]) ^ ord(SEED_B[(i * 3) % len(SEED_B)])
    for i in range(len(key))
]
dec = ''.join(
    chr(enc[i] ^ ord(SEED_A[i % len(SEED_A)]) ^ ord(SEED_B[(i * 3) % len(SEED_B)]))
    for i in range(len(enc))
)
assert dec == key
print('_GR_ENC =', enc)
