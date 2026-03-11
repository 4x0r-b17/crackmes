# QERR0R — ASCII_CRACK

![Platform](https://img.shields.io/badge/Platform-Linux%20x86--64-informational?style=flat&logo=linux&logoColor=white&color=222222)
![Language](https://img.shields.io/badge/Language-C%2B%2B-informational?style=flat&logo=cplusplus&logoColor=white&color=00599C)
![Difficulty](https://img.shields.io/badge/Difficulty-2.0%20%2F%205.0-yellow?style=flat)
![Tools](https://img.shields.io/badge/Tools-strings%20%7C%20Ghidra%20%7C%20Python-informational?style=flat&color=555555)
![Source](https://img.shields.io/badge/Source-crackmes.one-informational?style=flat&color=8A2BE2)

---

## Overview

A C++ crackme that takes its input as a command-line argument rather than stdin. Unlike the previous challenges in this series, the binary does not store the expected password in plaintext — instead it applies a positional encoding to the user's input before comparing it against a stored encoded string. Recovering the flag requires understanding and reversing the encoding function.

---

## Reconnaissance

The binary takes input as an argument:

```bash
$ ./ascii
Usage: ./script <flag>

$ ./ascii test
Try again! You can do it!
```

Running `strings` reveals the encoded target string among the usual C++ runtime noise:

```
IYJ~U4cQ1Q[<mL[(U;`'Ynk/M-i
```

Unlike previous crackmes, this string is not the password itself — submitting it directly fails. The symbol table also exposes two critical function names: `_Z6encodeci` (`encode(char, int)`) and `_Z6verifyNSt7...` (`verify(std::string)`), signaling that input is transformed before comparison.

---

## Static Analysis with Ghidra

### The `verify()` Function

Ghidra decompiles `verify()` at `0x001022bd` as a straightforward equality check between the transformed user input and the stored encoded flag:

```c
bool verify(string *param_1)
{
  bool bVar1;

  bVar1 = std::operator==(param_1, (string *)encoded_flag[abi:cxx11]);
  return bVar1;
}
```

The encoded target is a global C++ string object `encoded_flag` initialized at `0x00103082`:

```
00103082  ds  "IYJ~U4cQ1Q[<mL[(U;`'Ynk/M-i"
```

The comparison is against the *encoded* version of the user's input — meaning the flag must be encoded to match, not decoded after extraction.

### The `encode()` Function

The encoding function is simple:

```c
char encode(char param_1, int param_2)
{
  return (char)param_2 + param_1;
}
```

Each character is shifted by an integer offset `param_2`. The main loop reveals how that offset is calculated per character:

```c
while (true) {
  uVar7 = (ulong)local_9c;           // current index
  uVar5 = std::__cxx11::string::length();
  if (uVar5 <= uVar7) break;
  iVar2 = 6 - local_9c;             // offset = 6 - index
  pcVar4 = (char *)std::__cxx11::string::operator[]((ulong)local_88);
  cVar1 = encode(*pcVar4, iVar2);   // encoded_char = original_char + (6 - index)
  std::__cxx11::string::operator+=(local_68, cVar1);
  local_9c = local_9c + 1;
}
```

The encoding scheme is:

```
encoded[i] = input[i] + (6 - i)
```

For index 0 the offset is `+6`, for index 1 it is `+5`, decreasing by 1 each position. At index 6 the offset is 0, and from index 7 onwards it becomes negative.

---

## Reversing the Encoding

To recover the original flag, invert the operation for each character:

```
input[i] = encoded[i] - (6 - i)
```

Python script to decode:

```python
encoded = "IYJ~U4cQ1Q[<mL[(U;`'Ynk/M-i"

for i, ch in enumerate(encoded):
    offset = 6 - i
    print(chr((ord(ch) - offset) % 256), end='')
```

Output:

```
CTF{S3cR3T_AsSc1_Fl4g}{@_@}
```

---

## Verification

```bash
$ ./ascii "CTF{S3cR3T_AsSc1_Fl4g}{@_@}"
You cracked me!
```

---

## Flag

```
CTF{S3cR3T_AsSc1_Fl4g}{@_@}
```

---

## Key Takeaway

This is the first challenge in this series that requires active analysis rather than passive string extraction. The encoded string is visible in the binary, but submitting it directly fails — understanding *why* requires tracing the encoding path through `encode()` and the main loop. Once the transformation `encoded[i] = input[i] + (6 - i)` is identified, reversal is trivial arithmetic. The encoding is weak by design, but it demonstrates the concept of pre-comparison transformation that underlies more serious obfuscation schemes.

---

## Lessons Learned

- A single layer of encoding is enough to defeat `strings`-only analysis — the stored value is visible but not directly usable. This is a meaningful step up in complexity from plaintext storage.
- Function names surviving in the symbol table (`encode`, `verify`) still described the program's logic clearly. Stripping these would have required the analyst to infer the encoding from raw disassembly rather than named functions.
- The encoding scheme `input[i] + (6 - i)` is a positional Caesar cipher — each character shifted by a position-dependent offset. It is trivially reversible once identified, but it illustrates the general class of byte-level transformations used in real obfuscation.
- Identifying the offset formula `iVar2 = 6 - local_9c` in the decompiled loop is the critical step. Without it, the encoded string cannot be reversed. Reading decompiler output carefully — particularly loop variables and arithmetic on indices — is a core skill for this class of challenge.
- Python is the natural tool for encoding reversal: short, readable, and handles modular arithmetic (`% 256`) cleanly to stay within the byte range.

---

## Mitigation

- **Use a cryptographic hash instead of a reversible encoding.** A positional Caesar cipher is trivially invertible once the formula is identified. Storing `SHA-256(flag)` and comparing hashes at runtime prevents direct recovery of the plaintext — though short or predictable flags remain vulnerable to offline brute force.
- **Strip debug symbols and function names.** The symbol names `encode` and `verify` described the program's architecture in plain English. Without them the analyst must reconstruct intent from raw assembly, which meaningfully increases the time cost of analysis.
- **Increase encoding complexity.** A position-dependent additive shift is one of the simplest possible transformations. Multi-round encodings, non-linear key schedules, or XOR with a non-repeating keystream all raise the cost of reversal. None are unbreakable, but complexity buys time.
- **Avoid global string initialization for encoded secrets.** The `encoded_flag` global object is initialized at a fixed address (`0x00103082`) and referenced directly in the symbol table under a recognizable mangled name. Storing the encoded bytes as an anonymous local array assembled at runtime is harder to locate statically.
- **Validate input length before encoding.** The loop encodes and compares without any early exit on length mismatch. Adding a length check before the encoding loop leaks less information about the expected input format and closes one avenue of side-channel inference.
