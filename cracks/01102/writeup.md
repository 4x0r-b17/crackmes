# ezloom — Really Easy

![Platform](https://img.shields.io/badge/Platform-Linux%20x86--64-informational?style=flat&logo=linux&logoColor=white&color=222222)
![Language](https://img.shields.io/badge/Language-C%2FC%2B%2B-informational?style=flat&logo=c&logoColor=white&color=00599C)
![Difficulty](https://img.shields.io/badge/Difficulty-1.0%20%2F%205.0-brightgreen?style=flat)
![Tools](https://img.shields.io/badge/Tools-file%20%7C%20strings-informational?style=flat&color=555555)
![Source](https://img.shields.io/badge/Source-crackmes.one-informational?style=flat&color=8A2BE2)

---

## Overview

A beginner-level crackme distributed as a file named `simp-password` with no extension. The binary reads a password from stdin via `scanf` and compares it against a hardcoded string using `strcmp`. No obfuscation, no encoding, no anti-debug measures — the password sits in plaintext in the `.rodata` section.

---

## Reconnaissance — Identifying the File

The file is delivered without an extension. The first step before any analysis is identifying what it actually is:

```bash
$ cat simp-password
```

The raw output immediately reveals ELF magic bytes and recognizable shared library references (`libc.so.6`, `ld-linux-x86-64.so.2`), confirming this is a Linux ELF executable despite the misleading filename. The symbol table also leaks the original source filename: `simp_password.c`.

Renaming and marking it executable makes it runnable:

```bash
$ chmod +x simp-password
```

---

## Static Analysis with `strings`

Running `strings` on the binary dumps all readable sequences:

```bash
$ strings simp-password
```

Two things stand out immediately. First, the input format string:

```
%41s
```

This tells us `scanf` reads at most 41 characters — the password is at most 41 characters long. Second, the password itself appears visually isolated by delimiters in the `.rodata` section:

```
--------------
iloveicecream
--------------
```

The success and failure messages confirm which string is which:

```
I love ice cream too!
Wrong try again.
```

The imported symbols also confirm the comparison mechanism — `strcmp` is listed in the dynamic symbol table, meaning the password check is a straightforward string equality test with no hashing or transformation.

---

## Verification

```bash
$ ./simp-password
Enter password: iloveicecream
I love ice cream too!
```

---

## Password

```
iloveicecream
```

---

## Key Takeaway

When a binary has no extension, `cat` or `file` should be the first move to identify its true type before any further analysis. Once identified as an ELF, the approach is identical to any other plaintext crackme — `strings` recovers the secret immediately. The presence of `strcmp` in the imports is a reliable signal that the comparison is done on the raw input with no prior transformation.

---

## Lessons Learned

- File extensions are meaningless on Linux — the ELF magic bytes (`\x7fELF`) determine execution, not the name. Always use `file` or inspect the header before assuming a file type.
- `strcmp` in the dynamic symbol table is a strong indicator that the password is stored and compared as a plaintext string, making `strings` the most efficient first tool.
- The `scanf` format string (`%41s`) leaks the maximum expected input length, which is useful context when no other hints are available.
- Delimiter patterns around strings in `.rodata` (like `------`) are a recurring author convention to visually mark secrets — they provide zero security but make the target easier to spot.
- The original source filename (`simp_password.c`) was left in the symbol table, confirming this is an unstripped debug build with no hardening applied.

---

## Mitigation

- **Strip binaries before distribution.** Unstripped binaries retain symbol names, source filenames, and section metadata that significantly aid reverse engineering. Use `strip --strip-all` to remove this information.
- **Never use `strcmp` for secret validation.** `strcmp` short-circuits on the first mismatched byte, making it vulnerable to timing attacks in addition to static analysis. Use a constant-time comparison function for any security-sensitive check.
- **Do not store secrets in plaintext in `.rodata`.** Any hardcoded string literal is permanently embedded in the binary and recoverable without execution. Apply at minimum a simple transformation (XOR, hash) to obscure the value at rest, accepting that client-side validation is always bypassable with sufficient effort.
- **Move validation server-side.** Client-side password checks are fundamentally untrustworthy. For real applications, the authoritative comparison should happen on a server the user does not control.
- **Apply binary hardening.** Enable PIE (`-fPIE -pie`), stack canaries (`-fstack-protector-strong`), and consider stripping the binary to raise the baseline effort required for static analysis.
