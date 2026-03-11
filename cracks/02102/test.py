def decode_pin(pin):
    decoded = ""

    for i in range(4):
        local_10 = ord(pin[i]) - 0x35
        if local_10 < 0:
            local_10 = ord(pin[i]) - 0x2b

        decoded += chr(local_10 + ord('0'))

    return decoded


def decode_string(encoded, key):
    decoded = ""
    input_len = len(key)

    for i in range(len(encoded)):
        local_10 = ord(encoded[i]) - ord(key[i % input_len])

        if local_10 < 0x20 or local_10 > 0x7e:
            local_10 = (local_10 + 0x3f) % 0x5f + 0x20

        decoded += chr(local_10)

    return decoded

encoded_string = "}|.wOlHtc}j@z9jf3 O Q"
pin = "=99;"

decoded_pin = decode_pin(pin)

print("Decoded PIN:", decoded_pin)

if decoded_pin == "8446":
    print("Correct PIN entered!")
    result = decode_string(encoded_string, pin)
    print("Decoded String:", result)
else:
    print("Wrong PIN")