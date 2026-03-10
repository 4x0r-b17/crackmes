# sftmlg — Quite a Simple Crackme

![Platform](https://img.shields.io/badge/Platform-Linux%20x86--64-informational?style=flat&logo=linux&logoColor=white&color=222222)
![Language](https://img.shields.io/badge/Language-C%2B%2B-informational?style=flat&logo=cplusplus&logoColor=white&color=00599C)
![Difficulty](https://img.shields.io/badge/Difficulty-1.0%20%2F%205.0-brightgreen?style=flat)
![Tool](https://img.shields.io/badge/Tool-strings-informational?style=flat&color=555555)
![Source](https://img.shields.io/badge/Source-crackmes.one-informational?style=flat&color=8A2BE2)

---

## Overview

A beginner-level crackme compiled from C++ using GCC for Linux x86-64. The binary reads a password from stdin and prints either `Right password` or `Wrong password`. No anti-debug tricks, no obfuscation, no dynamically generated keys — the password is a static string baked directly into the binary.

---

## Static Analysis with `strings`

The first step is running `strings` on the binary to dump all readable ASCII sequences embedded in the executable:

```bash
strings c++crackme
```

Among the expected C++ runtime symbols, two strings immediately stand out as candidates:

```
---------------------
@!#-3~&,$;7?/.:%42+`
---------------------
```

These delimiters visually isolate the candidate string from the rest of the output. The author's own hint confirms the approach:

> *"Stored in plain text, does not contain any letters uppercase, or lowercase"*

The string `@!#-3~&,$;7?/.:%42+`` contains only special characters and digits — consistent with that hint — making it the obvious password candidate.

---

## Verification

Running the binary and submitting the extracted string confirms it:

```bash
$ ./c++crackme
Console crackme written with C++, made by sftmlg on crackmes.one!
Enter the password: @!#-3~&,$;7?/.:%42+`
Right password
```

---

## Password

```
@!#-3~&,$;7?/.:%42+`
```

---

## Key Takeaway

When a binary stores its secret in plaintext with no encoding or transformation, `strings` alone is sufficient — no disassembler or debugger required. The framing delimiters (`-----`) in the binary's rodata section made the target string trivial to spot visually in the output.

---

## Lessons Learned

- `strings` is always the first reconnaissance step on an unknown binary — it costs nothing and frequently yields immediate results on naive implementations.
- Hardcoded secrets in the `.rodata` section are fully visible without any dynamic execution or disassembly.
- Visual isolation of a secret (e.g. surrounding delimiters) does not add any security — it actually makes the target easier to identify in the output.
- The author's own hint ("stored in plain text, no letters") was enough to narrow the candidate from the `strings` dump without even running the binary.

---

## Mitigation

These points apply to real-world software where secrets must be validated client-side:

- **Never hardcode secrets in plaintext.** Any string literal in source code ends up in the binary's read-only data segment and is trivially recoverable with `strings`.
- **Use a cryptographic hash for comparison.** Store a hash of the expected value (e.g. SHA-256) and compare against a hash of the user input at runtime. This prevents direct extraction of the secret, though it still leaves the program vulnerable to hash cracking if a weak or short secret is used.
- **Add a server-side validation step.** Move the authoritative check off the client entirely. A crackme is inherently a closed system, but real applications should never trust client-side validation alone.
- **Apply binary hardening.** Stripping symbols (`strip`), enabling PIE, and using obfuscation passes (e.g. LLVM obfuscator) raises the effort required to reverse the binary, though none of these are a substitute for sound secret management.
