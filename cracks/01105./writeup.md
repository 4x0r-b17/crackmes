# BitFriends — nasm crack

![Platform](https://img.shields.io/badge/Platform-Linux%20x86--64-informational?style=flat&logo=linux&logoColor=white&color=222222)
![Language](https://img.shields.io/badge/Language-NASM%20Assembly-informational?style=flat&color=6E4C13)
![Difficulty](https://img.shields.io/badge/Difficulty-1.0%20%2F%205.0-brightgreen?style=flat)
![Tools](https://img.shields.io/badge/Tools-strings-informational?style=flat&color=555555)
![Source](https://img.shields.io/badge/Source-crackmes.one-informational?style=flat&color=8A2BE2)

---

## Overview

A beginner-level crackme written directly in NASM — x86-64 assembly — with no C runtime or standard library involved. The binary reads a password from stdin and branches to either a `correct_func` routine or a failure path. Despite being written at the assembly level, the password is stored as a plaintext data label in the `.data` section, making it immediately recoverable with `strings`.

---

## Static Analysis with `strings`

```bash
$ strings nasm_crack
```

The output is notably cleaner than a C/C++ binary — no mangled symbols, no libc imports, no C++ runtime noise. What remains is almost entirely meaningful:

```
Enter your password: 
Correct!
Wrong!
supersecret
write.asm
msg1
len1
correct
lenc
wrong
lenw
passwd
input
correct_func
```

Several things are immediately apparent. The source filename `write.asm` confirms this is a raw assembly binary with no higher-level language involved. The labeled symbols expose the program's internal structure directly: `passwd` and `input` are the data labels for the stored password and the user input buffer respectively, and `correct_func` is the success branch. The password `supersecret` appears as a plaintext string between the response messages and the symbol names, sitting in the `.data` section exactly as defined in the source.

---

## Verification

```bash
$ ./nasm_crack
Enter your password: supersecret
Correct!
```

---

## Password

```
supersecret
```

---

## Key Takeaway

Writing a binary in raw assembly does not make it harder to reverse than a compiled C program when secrets are stored as plaintext data labels. In fact, the absence of a C runtime and standard library makes the `strings` output significantly cleaner and easier to read — there is no symbol noise to filter through. The internal label names (`passwd`, `input`, `correct_func`) survived into the binary's symbol table and describe the program's logic more clearly than most decompiled C pseudocode would.

---

## Lessons Learned

- Assembly-level authorship provides no inherent security advantage over compiled C when secrets are stored as named data labels in `.data`. The abstraction level of the source language is irrelevant once the binary is on disk.
- Unstripped assembly binaries can be more readable than unstripped C binaries — without C runtime overhead, every symbol in the output is directly authored and semantically meaningful.
- Label names in NASM (`passwd`, `input`, `correct_func`) map directly to symbol table entries and survive into the final ELF unless explicitly stripped, effectively documenting the program's logic for anyone running `strings` or opening the binary in a disassembler.
- The `.data` section in a NASM binary is the direct equivalent of a string literal in C source — anything defined there as a `db` directive appears verbatim in the binary and is trivially recoverable.

---

## Mitigation

- **Strip the binary.** Label names like `passwd`, `input`, and `correct_func` are left in the symbol table and describe the program's internal logic in plain English. A stripped binary removes these entries and forces the analyst to infer function purpose from behavior rather than names. In NASM, compile with `strip --strip-all` after linking.
- **Do not define secrets as named data labels.** A `passwd db "supersecret", 0` declaration in the `.data` section is identical in effect to a string literal in C — it lands in the binary verbatim. At minimum, store the password as a sequence of XOR-encoded bytes and decode at runtime.
- **Implement the comparison in a way that resists static extraction.** Rather than comparing raw input against a stored string, derive a hash of the input at runtime and compare against a stored hash value. This prevents direct recovery of the secret from the binary while keeping the validation logic self-contained.
- **Strip symbol and section metadata.** The source filename `write.asm` and all internal label names were recoverable from the binary. Beyond `strip`, consider using `objcopy --strip-debug` and avoid meaningful label names in security-sensitive code paths.
