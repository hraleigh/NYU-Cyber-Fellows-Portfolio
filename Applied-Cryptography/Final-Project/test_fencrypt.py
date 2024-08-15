'''
Unit tests
'''

from fencrypt import *
from json import load
from unittest import TestCase, main

def master_key(pwd: str, salt: str) -> str:
    mk = pbkdf2_hmac('sha256', pwd.encode('utf-8'), bytes.fromhex(salt), 250_000)
    return mk.hex()

def key_sched(_mk: str) -> dict[str, str]:
    mk = bytes.fromhex(_mk)
    left, right = mk[:16], mk[-16:]
    aes = AES.new(left, AES.MODE_ECB)
    val = aes.encrypt(right)
    keys = {}
    keys["validator"] = val.hex()
    keys["feistel"] = [ctr(aes, right, i).hex() for i in range(1, 5)]
    keys["mac"] = ctr(aes, right, 5).hex()
    keys["search_terms"] = ctr(aes, right, 6).hex()
    return keys

def aes_enc(_key: str, _data: str) -> str:
    key = bytes.fromhex(_key)
    data = bytes.fromhex(_data)
    left, right = data[:16], data[16:]
    left, right = aes_rd(key, left, right)
    return (left + right).hex()
        
def hmac_enc(_key: str, _data: str) -> str:
    key = bytes.fromhex(_key)
    data = bytes.fromhex(_data)
    left, right = data[:16], data[16:]
    left, right = hmac_rd(key, left, right)
    return (left + right).hex()

def feistel_enc(keys: list[str], _plaintext: str) -> str:
    key_1, key_2, key_3, key_4 = map(lambda k: bytes.fromhex(k), keys)
    plaintext = bytes.fromhex(_plaintext)
    left0, right0 = plaintext[:16], plaintext[16:]
    left1, right1 = aes_rd(key_1, left0, right0)
    left2, right2 = hmac_rd(key_2, left1, right1)
    left3, right3 = aes_rd(key_3, left2, right2)
    left4, right4 = hmac_rd(key_4, left3, right3)
    return (left4 + right4).hex()

def feistel_dec(keys: list[str], _ciphertext: str) -> str:
    key_1, key_2, key_3, key_4 = map(lambda k: bytes.fromhex(k), keys)
    ciphertext = bytes.fromhex(_ciphertext)
    left4, right4 = ciphertext[:16], ciphertext[16:]
    left3, right3 = hmac_rd(key_4, left4, right4)
    left2, right2 = aes_rd(key_3, left3, right3)
    left1, right1 = hmac_rd(key_2, left2, right2)
    left0, right0 = aes_rd(key_1, left1, right1)
    return (left0 + right0).hex()

def mac(_key: str, _data: str) -> str: 
    key = bytes.fromhex(_key)
    data = bytes.fromhex(_data)
    h = hmac.new(key, digestmod="sha256")
    h.update(data)
    return h.hexdigest()

def search_ascii(text: str) -> list[str]:
    uni_cats = r"[\p{L}\p{Mn}\p{Nd}\p{Pc}]+"
    words = findall(uni_cats, text)
    words = filter(lambda w: 4 <= len(w) <= 12, words)
    return sorted(list(words))

def norm(s: str) -> str:
    return normalize("NFC", s.casefold())

def search_terms(text: str) -> list[str]:
    words = search_ascii(text)
    terms = []
    for word in words:
        terms += gen_star_terms(word)
    return [norm(x) for x in terms]

def search_terms_ascii(text: str) -> list[str]:
    words = search_ascii(text)
    terms = []
    for w in words:
        terms += map(lambda t: normalize("NFC", t.casefold()), gen_star_terms(w))
    return sorted(list(terms))

def encrypt_file(fname: str, _salt: str, _pwd: str) -> bytes:
    salt = bytes.fromhex(_salt)
    pwd = _pwd.encode("utf-8")
    Encrypt(Path.cwd() / f"examples/{fname}", pwd, False, salt)
    with open(f"./examples/{fname}", "r+b") as f:
        contents = f.read()
        f.close()
    return contents

def decrypt_file(fname: str, _pwd: str) -> bytes:
    pwd = _pwd.encode("utf-8")
    Decrypt(Path.cwd() / f"examples/{fname}", pwd, False)
    with open(f"./examples/{fname}", "r+b") as f:
        contents = f.read()
        f.close()
    return contents

def get_file_salt(fname: str) -> str:
    with open(f"./examples/.fenc-meta.{fname}", "r+b") as f:
        md = load(f)
        salt = md["salt"]
        f.close()
    return salt

def get_file_expect(fname: str) -> bytes:
    with open(f"./examples/{fname}", "r+b") as f:
        expect = f.read()
        f.close()
    return expect

def get_meta_json(fname: str):
    with open(f"./examples/.fenc-meta.{fname}", "r", encoding="utf-8") as f:
        expect = load(f)
        f.close()
    with open(f"./.fenc-meta.{fname}.plain", "r", encoding="utf-8") as f:
        result = load(f)
        f.close()
    assert result["salt"] == expect["salt"]
    assert result["validator"] == expect["validator"]
    assert result["mac"] == expect["mac"]
    assert result["terms"] == expect["terms"]


# get input
with open("./example-input.json", "r", encoding="utf-8") as f:
    input = load(f)
    prob1_pwd   = input["problem 1"]["password"]
    prob1_salt  = input["problem 1"]["salt"]
    prob2_mk    = input["problem 2"]
    prob3_key   = input["problem 3"]["key"]
    prob3_data  = input["problem 3"]["data"]
    prob4_key   = input["problem 4"]["key"]
    prob4_data  = input["problem 4"]["data"]
    prob5_keys  = input["problem 5"]["keys"]
    prob5_data  = input["problem 5"]["plaintext"]
    prob6_keys  = input["problem 6"]["keys"]
    prob6_data  = input["problem 6"]["ciphertext"]
    prob7_key   = input["problem 7"]["key"]
    prob7_data  = input["problem 7"]["data"]
    prob8_text  = input["problem 8"]
    prob9_text  = input["problem 9"]
    prob10_text = input["problem 10"]
    prob11_text = input["problem 11"]
    f.close()

# get expected output
with open("./example-output.json", "r", encoding="utf-8") as f:
    expected_output = load(f)
    prob1_expect  = expected_output["problem 1"]
    prob2_expect  = expected_output["problem 2"]
    prob3_expect  = expected_output["problem 3"]
    prob4_expect  = expected_output["problem 4"]
    prob5_expect  = expected_output["problem 5"]
    prob6_expect  = expected_output["problem 6"]
    prob7_expect  = expected_output["problem 7"]
    prob8_expect  = expected_output["problem 8"]
    prob9_expect  = expected_output["problem 9"]
    prob10_expect = expected_output["problem 10"]
    prob11_expect = expected_output["problem 11"]
    f.close()

class Test1(TestCase):
    def test_prob1(self):
        assert master_key(prob1_pwd, prob1_salt) == prob1_expect    
        
    def test_prob2(self):
        assert key_sched(prob2_mk) == prob2_expect
    
    def test_prob3(self):
        assert aes_enc(prob3_key, prob3_data) == prob3_expect
                        
    def test_prob4(self):
        assert hmac_enc(prob4_key, prob4_data) == prob4_expect

    def test_prob5(self):
        assert feistel_enc(prob5_keys, prob5_data) == prob5_expect
    
    def test_prob6(self):
        assert feistel_dec(prob6_keys, prob6_data) == prob6_expect
    
    def test_prob7(self):
        assert mac(prob7_key, prob7_data) == prob7_expect

    def test_prob8(self):
        assert search_ascii(prob8_text) == prob8_expect

    def test_prob9(self):
        assert search_ascii(prob9_text) == prob9_expect

    def test_prob10(self):
        assert search_terms_ascii(prob10_text) == sorted(prob10_expect)

    def test_prob11(self):
        assert search_terms(prob11_text) == prob11_expect

    def test_encrypt_aeschylus(self):
        fname = "aeschylus.txt"
        salt = get_file_salt(fname)
        assert encrypt_file(f"{fname}.plain", salt, fname) == get_file_expect(fname)
        get_meta_json(fname)
    
    def test_encrypt_macbeth(self):
        fname = "macbeth.txt"
        salt = get_file_salt(fname)
        assert encrypt_file(f"{fname}.plain", salt, fname) == get_file_expect(fname)
        get_meta_json(fname)

    def test_encrypt_ecb(self):
        fname = "ecb.jpg"
        salt = get_file_salt(fname)
        assert encrypt_file(f"{fname}.plain", salt, fname) == get_file_expect(fname)
        get_meta_json(fname)

    # def test_decrypt_aeschylus(self):
    #     fname = "aeschylus.txt"
    #     assert decrypt_file(fname, fname) == get_file_expect(f"{fname}.plain")
    
    # def test_decrypt_macbeth(self):
    #     fname = "macbeth.txt"
    #     assert decrypt_file(fname, fname) == get_file_expect(f"{fname}.plain")

    # def test_decrypt_ecb(self):
    #     fname = "ecb.jpg"
    #     assert decrypt_file(fname, fname) == get_file_expect(f"{fname}.plain")

if __name__ == "__main__": main()
