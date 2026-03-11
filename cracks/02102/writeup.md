# authorize — PIN & String Decoder

![Platform](https://img.shields.io/badge/Platform-Linux%20x86--64-informational?style=flat&logo=linux&logoColor=white&color=222222)
![Language](https://img.shields.io/badge/Language-C-informational?style=flat&logo=c&logoColor=white&color=00599C)
![Difficulty](https://img.shields.io/badge/Difficulty-2.0%20%2F%205.0-yellow?style=flat)
![Tools](https://img.shields.io/badge/Tools-strings%20%7C%20Ghidra%20%7C%20Python-informational?style=flat&color=555555)
![Source](https://img.shields.io/badge/Source-crackmes.one-informational?style=flat&color=8A2BE2)

---

## Overview

A C crackme that accepts a PIN as a command-line argument. The binary decodes the user's input before comparing it against a hardcoded target PIN, then uses the same input as a key to decode a second encrypted string. The plaintext PIN `8446` is visible in `strings` output but submitting it directly fails — the binary expects the *pre-decoded* form of that PIN, meaning the analyst must invert the decoding function to find what input produces `8446` after transformation.

---

## Reconnaissance

```bash
$ strings authorize
```

The output immediately surfaces several points of interest:

```
Usage: %s <pin>
8446
This is not right
Correct PIN entered!
}|.wOlHtc}j@z9jf3 O Q
Decoded String: %s
```

The symbol table also exposes three meaningful function names: `encode_pin`, `decode_pin`, and `decode_string` — confirming that two separate transformations are in play. The string `8446` is the target PIN after decoding, and `}|.wOlHtc}j@z9jf3 O Q` is a secondary encrypted string revealed only on correct entry.

Testing `8446` directly fails:

```bash
$ ./authorize 8446
This is not right
```

---

## Static Analysis with Ghidra

### `main()`

The decompiled `main()` makes the validation flow explicit:

```c
undefined8 main(int param_1, undefined8 *param_2)
{
  char *__s1;
  size_t sVar2;
  size_t sVar3;

  if (param_1 == 2) {
    __s1 = (char *)decode_pin(param_2[1]);       // decode user input
    sVar2 = strlen((char *)param_2[1]);
    sVar3 = strlen("8446");
    iVar1 = strncmp(__s1, "8446", sVar3);        // compare decoded result to "8446"
    if ((iVar1 == 0) && (sVar2 == sVar3)) {
      puts("Correct PIN entered!");
      uVar4 = decode_string("}|.wOlHtc}j@z9jf3 O Q", param_2[1]);
      printf("Decoded String: %s\n", uVar4);
      return 0;
    }
    puts("This is not right");
  }
}
```

The user's input is first passed through `decode_pin()`, and the result is compared against `"8446"`. This means the correct input is whatever value `decode_pin()` maps to `"8446"` — not `"8446"` itself. On success, the raw input is also used as the key for `decode_string()`.

### `decode_pin()`

```c
undefined5 * decode_pin(long param_1)
{
  int local_10;

  for (local_c = 0; local_c < 4; local_c++) {
    local_10 = *(char *)(param_1 + local_c) - 0x35;
    if (local_10 < 0) {
      local_10 = *(char *)(param_1 + local_c) - 0x2b;
    }
    decoded_pin[local_c] = (char)local_10 + '0';
  }
}
```

For each character of the input, the function subtracts `0x35` (53) and adds `'0'` (48). If the result would be negative, it subtracts `0x2b` (43) instead. To produce the digit `'8'` (ASCII 56) from this function, the input character must satisfy:

```
input - 0x35 + 0x30 = 0x38   →   input = 0x38 + 0x35 - 0x30 = 0x3d = '='
```

Applying this to each digit of `8446`:

| Target digit | Target ASCII | Input ASCII | Input char |
|---|---|---|---|
| `8` | 0x38 | 0x3d | `=` |
| `4` | 0x34 | 0x39 | `9` |
| `4` | 0x34 | 0x39 | `9` |
| `6` | 0x36 | 0x3b | `;` |

The correct input is `=99;`.

### `decode_string()`

Once the correct PIN is entered, the input is used as a repeating key to decode the secondary string:

```c
for (local_c = 0; local_c < target_len; local_c++) {
    local_10 = param_1[local_c] - param_2[local_c % input_len];
    if (local_10 < 0x20 || local_10 > 0x7e) {
        local_10 = (local_10 + 0x3f) % 0x5f + 0x20;
    }
    decoded_str[local_c] = (char)local_10;
}
```

Each byte of the encoded string is reduced by the corresponding byte of the key (cycling), with a wrapping correction to stay within printable ASCII range (`0x20`–`0x7e`).

---

## Python Reversal

```python
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
print("Decoded PIN:", decoded_pin)          # 8446

if decoded_pin == "8446":
    result = decode_string(encoded_string, pin)
    print("Decoded String:", result)        # @CT<q3n9&D1d=_1+UFuDs
```

---

## Verification

```bash
$ ./authorize "=99;"
Correct PIN entered!
Decoded String: @CT<q3n9&D1d=_1+UFuDs
```

---

## Correct Input

```
=99;
```

---

## Key Takeaway

This crackme introduces a meaningful inversion problem: the visible plaintext `8446` is the *output* of the decoding function, not the input. Submitting it directly fails because the binary decodes whatever you provide and compares the result — not the raw input — against the target. Solving it requires reading the decoding logic carefully, inverting the arithmetic for each character position, and confirming the result. The secondary `decode_string()` layer adds a second transformation keyed on the same input, demonstrating how a single secret can serve dual roles as both a password and an encryption key.

---

## Lessons Learned

- Visible plaintext in `strings` output is not always the direct input — it may be the *expected result* of a transformation applied to the input. Attempting the obvious value first is still good practice, but the failure case must prompt deeper analysis of the validation path.
- Tracing the data flow through `main()` is essential before attempting any reversal: input → `decode_pin()` → `strncmp()` against `"8446"`. Understanding this chain prevents wasted effort trying to reverse the wrong function.
- Inverting a simple arithmetic transformation per-character is straightforward once the formula is isolated. The subtraction offsets `0x35` and `0x2b` with the conditional branch are the entire encoding — no key material, no state, fully reversible with pencil and paper or a short Python script.
- The dual use of the input as both a PIN and a decryption key is a simple demonstration of key derivation — a concept central to real cryptographic protocols where a single secret seeds multiple operations.
- The symbol names `encode_pin`, `decode_pin`, and `decode_string` remaining in the binary made function identification trivial. Without them, the analyst would need to infer purpose from the arithmetic patterns in the assembly.

---

## Mitigation

- **Do not expose the decoded target in plaintext.** The string `"8446"` appears verbatim in the binary as the `strncmp` comparand. Storing it encoded — or as a hash — prevents direct extraction of the target value and forces the analyst to fully understand both directions of the transformation.
- **Strip function names.** `decode_pin`, `decode_string`, and `encode_pin` described the program's architecture immediately. A stripped binary with no symbol table requires the analyst to reconstruct intent from raw arithmetic patterns in the disassembly.
- **Replace reversible transforms with one-way functions.** A per-character arithmetic shift is trivially invertible. Replacing it with a keyed hash or HMAC makes the transformation one-way: the expected hash can be stored in the binary, but the input that produced it cannot be mechanically recovered.
- **Avoid using raw user input directly as a decryption key.** Passing the PIN directly to `decode_string()` ties the decryption key to a value that must be shared with the user. In production, derive a key from the PIN using a proper KDF (e.g. PBKDF2, Argon2) rather than using the raw input.
- **Validate input length before decoding.** The `decode_pin()` loop iterates a fixed four times regardless of actual input length, creating an out-of-bounds read for inputs shorter than four characters. Input length should be validated before any character-level processing begins.
