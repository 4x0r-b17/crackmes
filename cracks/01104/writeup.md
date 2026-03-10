# I3a4dam — Plain Sight

![Platform](https://img.shields.io/badge/Platform-Linux%20x86--64-informational?style=flat&logo=linux&logoColor=white&color=222222)
![Language](https://img.shields.io/badge/Language-C%2B%2B-informational?style=flat&logo=cplusplus&logoColor=white&color=00599C)
![Difficulty](https://img.shields.io/badge/Difficulty-1.0%20%2F%205.0-brightgreen?style=flat)
![Tools](https://img.shields.io/badge/Tools-strings%20%7C%20Ghidra-informational?style=flat&color=555555)
![Source](https://img.shields.io/badge/Source-crackmes.one-informational?style=flat&color=8A2BE2)

---

## Overview

A beginner-friendly C++ crackme whose title is also its solution hint — the answer is hidden in plain sight. The binary presents a single password prompt, compares input against a hardcoded string using C++ `std::operator==`, and prints either `Welcome!` or `Wrong password!`. No obfuscation, no encoding, no anti-debug measures.

---

## Solution 1 — `strings`

Running `strings` on the binary is sufficient to recover the password immediately:

```bash
$ strings plain_sight
```

The key appears visually isolated in the `.rodata` section by delimiter lines:

```
----------------
do_not_hardcode
----------------
```

The surrounding response strings confirm which is which:

```
Welcome!
Wrong password!
```

The source filename `plain_sight.cpp` is also present in the symbol table, confirming this is an unstripped build. The name itself is a self-referential joke — the password is literally in plain sight in the binary.

---

## Solution 2 — Static Analysis with Ghidra

For completeness, Ghidra decompiles the validation logic into a `Login()` function that makes the control flow explicit:

```c
void Login(void)
{
  bool bVar1;
  ostream *poVar2;
  string local_38 [40];

  std::__cxx11::string::string(local_38);
  std::operator<<((ostream *)std::cout, "Enter the password: ");
  std::operator>>((istream *)std::cin, local_38);
  bVar1 = std::operator==(local_38, "do_not_hardcode");
  if (bVar1) {
    poVar2 = std::operator<<((ostream *)std::cout, "Welcome!");
    std::ostream::operator<<(poVar2, std::endl<>);
  }
  else {
    poVar2 = std::operator<<((ostream *)std::cout, "Wrong password!");
    std::ostream::operator<<(poVar2, std::endl<>);
  }
  std::__cxx11::string::~string(local_38);
  return;
}
```

The comparison `std::operator==(local_38, "do_not_hardcode")` is a direct equality check between user input and the hardcoded string literal. The buffer is allocated with a fixed size of 40 bytes (`string local_38 [40]`), consistent with the expected password length. No other validation logic exists — a single boolean branch determines the outcome.

One detail worth noting: unlike the previous crackmes which used C-style `strcmp`, this binary uses C++ `std::string::operator==`. Both resolve to a string equality check, but the C++ version is slightly less obvious in the import table — `_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7compareEPKc` (the mangled name for `std::string::compare`) rather than a plain `strcmp` symbol. The principle is the same.

---

## Verification

```bash
$ ./plain_sight
Enter the password: do_not_hardcode
Welcome!
```

---

## Password

```
do_not_hardcode
```

---

## Key Takeaway

The title is the hint. The password `do_not_hardcode` is the author's self-aware commentary on exactly the vulnerability being demonstrated. Despite using C++ string objects instead of C-style char arrays, the comparison is semantically identical — a plaintext string literal in `.rodata` matched against user input — and recoverable in the same way.

---

## Lessons Learned

- C++ `std::string::operator==` offers no security advantage over C `strcmp` when the comparand is a string literal. Both embed the secret in `.rodata` as plaintext.
- Mangled C++ symbol names (`_ZNKSt7...compareEPKc`) can obscure the comparison mechanism in the import table compared to a bare `strcmp`, but the decompiled pseudocode in Ghidra makes the logic immediately clear regardless.
- The fixed-size local buffer (`string local_38 [40]`) leaks the expected input length as a secondary data point, useful when no other hints are available.
- An unstripped binary retains the source filename (`plain_sight.cpp`) and all internal function names, reducing the analyst's work to simply reading the decompiled output rather than reconstructing intent from raw bytes.
- The password itself — `do_not_hardcode` — is a direct statement of the core mistake being demonstrated. It is a good reminder that naming conventions and embedded strings can carry meaningful information beyond their functional role.

---

## Mitigation

- **Do not hardcode secrets — the password says it itself.** Any string literal passed directly to a comparison function is permanently embedded in the binary and recoverable with `strings` in seconds.
- **Strip binaries before distribution.** The source filename `plain_sight.cpp` and function name `Login` survived into the final binary. Stripping removes these and forces the analyst to work from raw disassembly rather than named functions.
- **Replace client-side equality checks with server-side validation.** A `Login()` function that runs entirely on the user's machine and returns a boolean is unconditionally bypassable — by patching the branch, by extracting the key, or by hooking the comparison at runtime.
- **If client-side validation is unavoidable, apply a cryptographic transformation.** Store a salted hash of the expected value and compare hashes at runtime. This prevents direct string extraction, though short or predictable secrets remain vulnerable to offline cracking against the stored hash.
- **Use a constant-time comparison.** Even when hashing is applied, a naive equality check leaks timing information. Use a constant-time comparison routine to eliminate timing side-channels from the validation path.
