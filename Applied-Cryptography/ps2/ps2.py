#!/usr/bin/env python3

import json

# problem 1

def answer1(params):
    old_pt = bytes.fromhex(params["old_pt"])
    old_ct = bytes.fromhex(params["old_ct"])
    old_trades = []
    n = len(old_pt) // 16
    for _ in range(n):
        old_trades.append((old_pt[0:1], old_pt[2:6], int(old_pt[8:16]), old_ct[:16]))
        old_pt = old_pt[16:]
        old_ct = old_ct[16:]

    op1 = bytes(params["op_1"], encoding="utf8")
    op2 = bytes(params["op_2"], encoding="utf8")
    co1 = bytes(params["co_1"], encoding="utf8")
    co2 = bytes(params["co_2"], encoding="utf8")

    to_swap = []
    swap_ct = b''
    highest_shares = 0
    # each item:
    # 0: B/S symbol (bytes)
    # 1: company stock ticker symbol (bytes)
    # 2: number of shares (int)
    # 3: corresponding ciphertext block (bytes)
    for item in old_trades:
        if item[0] == op1 and item[1] == co1:
            to_swap.append(item[3])
        if item[0] == op2 and item[1] == co2 and item[2] > highest_shares:
            highest_shares = item[2]
            swap_ct = item[3]

    new_trades = params["new_trades"]
    output = []

    for nt in new_trades:
        # decode the hex string to bytes
        # since we haven't decoded new_trades
        ct = bytes.fromhex(nt)
        # build the correponding output element from an empty byte string
        elem = b''
        while ct:
            # iterate over each 16 byte chunk
            # since the trades are each 16 bytes
            # check if we should swap the first 16 bytes of ct
            if ct[:16] in to_swap:
                # if so, add swap_ct
                elem += swap_ct
            else:
                # otherwise, add the ciphertext as is
                elem += ct[:16]
            # drop the first 16 bytes from ct
            ct = ct[16:]
        # append hex encoded elem bytes to output
        output.append(elem.hex())

    return output

# problem 2

def answer2(params):
    old_pt = bytes.fromhex(params["old_pt"])
    old_ct = bytes.fromhex(params["old_ct"])
    new_ct = bytes.fromhex(params["new_ct"])
    res_bytes = []
    # xor
    for i in range(len(new_ct)):
        res_bytes.append(old_pt[i] ^ old_ct[i] ^ new_ct[i])
    return bytes(res_bytes).hex()

# problem 3

def answer3(params):
    ct = bytes.fromhex(params["todays_ct"])
    new_bytes = []
    for i in range(len(ct)):
        # want to change each ciphertext's first byte: B <=> S
        # "B" ^ "S" => 17
        if not i % 16:
            new_bytes.append(ct[i] ^ 17)
        else:
            new_bytes.append(ct[i])
    return bytes(new_bytes).hex()

# problem 4

# number padding
def int2bytes(n):
    b = bytes(str(n), encoding='utf-8')
    n = 8 - len(b)
    b += b" " * n
    return b

def a4_helper(trade, expected_num, actual_num):
    res = []
    # change B <=> S
    for i in range(8):
        if i == 0:
            res.append(trade[0] ^ 17)
        else:
            res.append(trade[i])
    expected_bytes = int2bytes(expected_num)
    desired_bytes = int2bytes(actual_num)

    # change each byte of the number from expected to desired
    for i in range(8):
        res.append(expected_bytes[i] ^ desired_bytes[i] ^ trade[8 + i])
    return bytes(res).hex()

def answer4(params):
    tl = [bytes.fromhex(x) for x in params["trade_list"]]
    en = params["expected_num"]
    an = params["actual_num"]
    ret = []
    for i in range(len(tl)):
        ret.append(a4_helper(tl[i], en[i], an[i]))
    return ret

# testing: reads the input from 'example-input.json'
file = open('example-input.json')
inputs_json = json.load(file)
file.close()

# submission: reads the input from sys.stdin
# inputs_json = json.load(sys.stdin)

# initialize and update the output dict
output = {}
output["problem 1"] = answer1(inputs_json["problem 1"])
output["problem 2"] = answer2(inputs_json["problem 2"])
output["problem 3"] = answer3(inputs_json["problem 3"])
output["problem 4"] = answer4(inputs_json["problem 4"])

# print output to ./output.json
f = open('output.json', 'w')
f.write(json.dumps(output, indent=4) + "\n")
f.close()
