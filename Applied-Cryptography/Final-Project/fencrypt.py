import json
import sys
import hmac
from getpass import getpass
from secrets import token_bytes
from argparse import ArgumentParser, Namespace
from pathlib import Path
from Crypto.Cipher import AES
from unicodedata import normalize
from hashlib import pbkdf2_hmac
from typing import Union
from regex import findall

####################
### Encrypt task ###
####################

class Encrypt:
    def __init__(self, fpath: Path, pwd: bytes = b"", j_flag: bool=False, salt: bytes = b""):
        if not pwd:
            exit_error("Error: Must supply password to encrypt.")
        self.path = fpath
        self.pwd = pwd
        self.keys = {}
        self.metadata = {}
        self.searchable = is_text(fpath)
        name = f'.fenc-meta.{fpath.name}'
        self.name = name
        if not fpath.exists():
            error_msg("Error: No such file.")
        with fpath.open("r+b") as f:
            plaintext = f.read()
            f.close()
        self.plaintext = plaintext
        self.j_flag = j_flag
        mk = masterkey(self, salt_gen())
        j_master_keys = {self.path.name: mk.hex()}
        if self.j_flag: 
            print(json.dumps(j_master_keys, indent=4), file=sys.stdout)
        self.__encrypt(plaintext, salt)

    def __gen_search_terms(self):
        '''
        Generate the star search term macs
        '''
        if not self.searchable:
            self.metadata["terms"] = []
        else:
            plaintext = self.plaintext.decode("utf-8")
            uni_cats = r"[\p{L}\p{Mn}\p{Nd}\p{Pc}]+"
            words = findall(uni_cats, plaintext)
            words = filter(lambda w: 4 <= len(w) <= 12, words)
            terms = []
            for w in words:
                terms += map(lambda t: normalize("NFC", t.casefold()), gen_star_terms(w))
            macs = set()
            for t in terms:
                mac = hash_mac(self.keys["search"], t.encode("utf-8"))
                macs.add(mac)
            self.metadata["terms"] = sorted(macs)

    def prep_metadata(self):
        '''
        Hex-encode the bytes values in `self.metadata`
        '''
        md = self.metadata
        # "terms" and "mac" are already hex-encoded
        md["salt"] = md["salt"].hex()
        md["validator"] = md["validator"].hex()
    
    def __write_metadata_file(self):
        name = self.name
        md_file_path = Path.cwd() / name
        md_fd = open(md_file_path, "w", encoding="utf-8")
        self.prep_metadata()
        md_fd.write(json.dumps(self.metadata, indent=4))
        md_fd.close()

    def __encrypt(self, plaintext: bytes, salt: bytes = b""):
        key_sched(self, masterkey(self, salt))
        self.__gen_search_terms()
        key_1, key_2, key_3, key_4 = self.keys["feistel"]
        mac_key = self.keys["mac"]
        left0 = plaintext[:16]  # iv
        right0 = plaintext[16:] # message to be encrypted
        left1, right1 = aes_rd(key_1, left0, right0)
        left2, right2 = hmac_rd(key_2, left1, right1)
        left3, right3 = aes_rd(key_3, left2, right2)
        left4, right4 = hmac_rd(key_4, left3, right3)
        ct =  left4 + right4
        self.metadata["mac"] = hash_mac(mac_key, ct)
        self.__write_metadata_file()
        with self.path.open("wb") as f:
            f.write(ct)
            f.close()
        # print(f"Success! {self.path.name} is encrypted.", file=sys.stderr)

####################
### Decrypt task ###
####################

class Decrypt:
    def __init__(self, fpath: Path, pwd: bytes, j_flag: bool):
        self.metadata = read_metadata(fpath.name)
        self.pwd = pwd
        self.keys = {}
        self.terms = []
        self.path = fpath
        self.enc_file = fpath.name
        self.j_flag = j_flag
        self.decrypt()

    def decrypt(self):
        salt = bytes.fromhex(str(self.metadata["salt"]))
        mk = masterkey(self, salt)
        key_sched(self, mk)
        with self.path.open('r+b') as f:
            ciphertext = f.read()
            f.close()
            j_master_keys = {self.enc_file: mk.hex()}
            if self.j_flag: 
                print(json.dumps(j_master_keys, indent=4), file=sys.stdout)
            self.__decrypt(ciphertext)

    def __decrypt(self, ciphertext: bytes):
        key_1, key_2, key_3, key_4 = self.keys["feistel"]
        left4 = ciphertext[:16]
        right4 = ciphertext[16:]
        left3, right3 = hmac_rd(key_4, left4, right4)
        left2, right2 = aes_rd(key_3, left3, right3)
        left1, right1 = hmac_rd(key_2, left2, right2)
        left0, right0 = aes_rd(key_1, left1, right1)
        pt = left0 + right0
        with self.path.open("wb") as f:
            f.write(pt)
            f.close()
        Path.unlink(get_metadata_file(self.path))
        print(f"Success! {self.path.name} is decrypted.", file=sys.stderr)
            

###################
### Search task ###
###################

class Search:
    def __init__(self, terms: "list[str]", j_flag: bool):
        self.metadata = {}
        self.keys = {}
        self.pwd = get_pwd()
        self.terms = terms
        self.j_flag = j_flag
        self.search()

    def search(self):
        search_macs = []
        mds = list(Path.cwd().glob(".fenc-meta.*"))
        j_master_keys = {}
        for md in mds:
            fname = md.name[len(".fenc-meta."):]
            mac_key = gen_keys(self, fname)["search"]
            for t in self.terms:
                mac = hash_mac(mac_key, t.encode("utf-8"))
                search_macs.append(mac)
            md_dict = read_metadata(md.name, False)
            md_terms = md_dict["terms"]
            mk = masterkey(self, bytes.fromhex(str(md_dict["salt"])))
            left, right = mk[:16], mk[-16:]
            aes = AES.new(left, AES.MODE_ECB)
            val = aes.encrypt(right)
            if val.hex() != md_dict["validator"]:
                error_msg(f"{fname}: Password does not match.")
            else:
                j_master_keys[fname] = mk.hex()
                for sm in search_macs:
                    if sm in md_terms:
                        print(fname)
        if self.j_flag: 
            print(json.dumps(j_master_keys, indent=4), file=sys.stdout)
            
                            
###############
### Helpers ###
###############

#TODO: Verify Message or Exit

class Noop:
    def __init__(self, pwd: bytes):
        self.pwd = pwd
        self.keys = {}

def error_msg(error):
	print(error, file=sys.stderr)

def exit_error(error):
	print(error, file=sys.stderr)
	sys.exit(1)

def hash_mac(key: bytes, text: bytes) -> str:
    h = hmac.new(key, digestmod="sha256")
    h.update(text)
    return h.hexdigest()

def get_pwd(fname: str="") -> bytes:
    if sys.stdin.isatty():
        if not fname:
            pwd = getpass("Please Enter Password: ").encode("utf-8")
        else:
            pwd = getpass(f"Please Enter Password for {fname}: ").encode("utf-8")
    else:
        pwd = sys.stdin.readline().strip().encode("utf-8")
    if not pwd:
        error_msg("Invalid Password.")
    return pwd

def pwd_authen(pwd: bytes, md: str) -> bool:
    md_dict = json.load(open(md, "r"))
    salt = md_dict["salt"]
    return md_dict["validator"] == validator(pwd, salt)

def mac_authen(pwd: bytes, md: str, fname: str) -> bool: 
    md_dict = json.load(open(md, "r"))
    noop = Noop(pwd)
    key_sched(noop, masterkey(noop, bytes.fromhex(md_dict["salt"])))
    mac_key = noop.keys["mac"]
    with open(fname, "r+b") as f:
        ct = f.read()
        f.close()
    mac = hash_mac(mac_key, ct)
    return md_dict["mac"] == mac

def salt_gen() -> bytes:
    return token_bytes(16)

def masterkey(task: Union[Encrypt, Decrypt, Search, Noop], salt: bytes = b"") -> bytes:
    if not salt:
        salt = salt_gen()
    mk = pbkdf2_hmac('sha256', task.pwd, salt, 250_000)
    if type(task) == Encrypt:
        task.metadata["salt"] = salt
    return mk

def validator(pwd: bytes, salt: str) -> str:
    mk = pbkdf2_hmac('sha256', pwd, bytes.fromhex(salt), 250_000)
    left, right = mk[:16], mk[-16:]
    aes = AES.new(left, AES.MODE_ECB)
    val = aes.encrypt(right)
    return val.hex()

def key_sched(task: Union[Encrypt, Decrypt, Search, Noop], mk: bytes):
    left, right = mk[:16], mk[-16:]
    aes = AES.new(left, AES.MODE_ECB)
    val = aes.encrypt(right)
    if type(task) == Encrypt:
        task.metadata["validator"] = val
    task.keys["val"] = val
    task.keys["feistel"] = [ctr(aes, right, i) for i in range(1, 5)]
    task.keys["mac"] = ctr(aes, right, 5)
    task.keys["search"] = ctr(aes, right, 6)

def ctr(aes, a_byte: bytes, b: int) -> bytes:
    a_byte = bytearray(a_byte)
    i = 15
    byte_index = a_byte[i] + b
    while byte_index > 255:
        if i < 0:
            break
        carry = byte_index >> 8
        a_byte[i] = byte_index % 256
        i = i - 1
        byte_index = a_byte[i] + carry
    if byte_index <= 255:
        a_byte[i] = byte_index
    return aes.encrypt(bytes(a_byte))

def get_metadata_file(fpath: Path) -> Path:
    if fpath.parent.name == "examples":
        fpath = fpath.parent.parent / fpath.name
    return fpath.parent / f".fenc-meta.{fpath.name}"

def read_metadata(fname: str, b: bool = True) -> "dict[str, Union[str, list[str]]]":
    if b:
        f = get_metadata_file(Path(fname))
    else:
        f = Path(fname)
    with f.open('r', encoding="utf-8") as f:
        contents = json.load(f)
        f.close()
    return contents

def gen_keys(task: Union[Decrypt, Search], fname: str="") -> "dict[str, bytes]":
    if type(task) == Decrypt:
        task.metadata = read_metadata(task.path.name)
    if type(task) == Search:
        task.metadata = read_metadata(fname)
    mk = masterkey(task, bytes.fromhex(str(task.metadata["salt"])))
    key_sched(task, mk)
    return task.keys

def aes_rd(key: bytes, left: bytes, right: bytes) -> "list[bytes]":
    numbytes = len(right)
    aes = AES.new(key, AES.MODE_ECB)
    keystream = b""
    count = 0
    while len(keystream) < numbytes:
        keystream += ctr(aes, left, count)
        count += 1
    return [left, xor_byte_func(keystream, right)]

def xor_byte_func(c: bytes, d: bytes) -> bytes:
    return bytes([x ^ y for x, y in zip(c, d)])

def hmac_rd(key: bytes, left: bytes, right: bytes) -> "list[bytes]":
    hash = hmac.new(key, digestmod="sha256")
    hash.update(right)
    return [xor_byte_func(hash.digest(), left), right]

def is_text(fpath: Path) -> bool:
    '''
    Checks if the file is text
    '''
    with fpath.open("r", encoding="utf-8") as f:
        try:
            f.read()
            return True
        except UnicodeDecodeError:
            return False
        finally:
            f.close()

def gen_star_terms(word: str) -> "list[str]":
    star_terms = []
    for i in range(4, len(word)):
        star_terms.append(word[:i] + "*")
    star_terms.append(word)
    return star_terms

def check_args(args: Namespace):
    if args.e and args.d:
        exit_error("Error: can't perform multiple functions at the same time.")
    if args.s and (args.e or args.d):
        exit_error("Error: can't combine search with other functions.")
    if not args.s:
        files = args.input
        if not all([Path(f).exists() for f in files]):
            exit_error("Error: missing file.")
        if args.e:    
            if not all([Path(f).stat().st_size >= 32 for f in files]):
                exit_error("Error: file is too small.")
        if args.d:
            files = list(map(Path, files))
            if not all([Path(".fenc-meta." + f.name).exists() for f in files]):
                exit_error("Error: missing metadata file.")
    if not args.input:
        exit_error("Error: no input provided.")

# parser

if __name__ == "__main__":
    # sys.stdout = sys.stderr # Default to std.out
    parser = ArgumentParser(description="Fencrypt")
    parser.add_argument("-e", action="store_true", help="encrypt")
    parser.add_argument("-d", action="store_true", help="decrypt")
    parser.add_argument("-s", action="store_true", help="search")
    parser.add_argument("-j", action="store_true", help="json")
    parser.add_argument("input", nargs="*", help="file or search terms")
    args = parser.parse_args()
    check_args(args)
    if args.d:
        pwds = []
        for d in args.input:
            pwd = get_pwd(d)
            pwds.append(pwd)
            mdf = list(Path.cwd().glob(f".fenc-meta.{Path(d).name}."))
            if not mdf:
                exit_error(f"No metadata file for: {d}")
            else:
                md = str(mdf[0])
                if not pwd_authen(pwd, md):
                    exit_error("")
                if not mac_authen(pwd, md, d):
                    exit_error("")
        for i, d in enumerate(args.input):
            Decrypt(Path(d), pwds[i], args.j)
    if args.s:
        md_files = list(Path.cwd().glob(".fenc-meta.*"))
        if not md_files:
            exit_error("No files exit.")
        Search(args.input, args.j)
    if not args.d and not args.s:
        for f in args.input:
            md_files = list(Path.cwd().glob(f".fenc-meta.{Path(f).name}"))
            if md_files:
                exit_error(f"Error: {f} Already Encrypted.")
        for f in args.input:
            Encrypt(Path(f), get_pwd(), args.j)
    # print(args)
