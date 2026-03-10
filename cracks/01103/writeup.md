# svidnet — ZEXOR-v1 (Linux Version)

![Platform](https://img.shields.io/badge/Platform-Linux%20x86--64-informational?style=flat&logo=linux&logoColor=white&color=222222)
![Language](https://img.shields.io/badge/Language-C%2FC%2B%2B-informational?style=flat&logo=c&logoColor=white&color=00599C)
![Difficulty](https://img.shields.io/badge/Difficulty-1.0%20%2F%205.0-brightgreen?style=flat)
![Tools](https://img.shields.io/badge/Tools-Ghidra-informational?style=flat&color=555555)
![Source](https://img.shields.io/badge/Source-crackmes.one-informational?style=flat&color=8A2BE2)

---

## Overview

ZEXOR-v1 is a GTK3-based GUI license checker for Linux Wayland. Unlike the previous crackmes in this series, the binary is not a simple stdin/stdout program — it presents a graphical input field and validates the entered license key against a hardcoded string. Two solution paths exist: extracting the valid key, or patching the binary to bypass the check entirely. Both are covered here.

---

## Setup

The binary requires GTK3 to run. Mark it executable and install the dependency if needed:

```bash
$ chmod +x ZEXORv1_wayland

# Debian/Ubuntu
$ sudo apt install pkg-config libgtk-3-dev
```

---

## Solution 1 — Key Extraction via Disassembly

Since `strings` may not isolate the key cleanly among GTK's symbol noise, the reliable approach is opening the binary in a disassembler (Ghidra was used here) and locating the validation function.

### Finding the Validation Logic

Ghidra identifies a function named `valid(char const*)` at `0x00101319`. Its decompiled pseudocode is straightforward:

```c
bool valid(char *param_1)
{
  int iVar1;

  iVar1 = strcmp(param_1, "AEXORRBSHA36325S33");
  return iVar1 == 0;
}
```

The function takes the user input as `param_1` and compares it directly against a hardcoded string via `strcmp`. There is no hashing, encoding, or transformation of any kind.

### Tracing the Reference in Assembly

The relevant assembly confirms the hardcoded string reference:

```asm
00101325  MOV  RDX, qword ptr [s_AEXORRBSHA36325S33_00102008]  ; = "AEXORRBSHA36325S33"
0010132c  MOV  RAX, qword ptr [RBP + local_10]                 ; user input
00101330  MOV  RSI, RDX                                         ; second arg to strcmp
00101333  MOV  RDI, RAX                                         ; first arg to strcmp
00101336  CALL strcmp
0010133b  TEST EAX, EAX
0010133d  SETZ AL                                               ; AL = 1 if equal
```

The string `AEXORRBSHA36325S33` is stored at address `0x00102008` in the `.rodata` section and loaded directly into the `strcmp` call with no intermediate processing. The call site `btn_clicked:0x00101382` shows this function is invoked when the GUI button is clicked.

---

## Solution 2 — Binary Patch (Bypass)

Rather than entering the correct key, the check can be patched so `valid()` always returns true regardless of input.

The return value is determined by these two instructions:

```asm
0010133b  TEST EAX, EAX   ; sets ZF if strcmp returned 0 (match)
0010133d  SETZ AL         ; AL = 1 only if ZF set (i.e. strings were equal)
```

Replacing `SETZ AL` (`0F 94 C0`) with `MOV AL, 1` (`B0 01`) forces the function to always return `true`, making the license check unconditionally pass. Alternatively, patching the `TEST EAX, EAX` to `XOR EAX, EAX` before `SETZ` achieves the same result by always setting the zero flag.

---

## Valid License Key

```
AEXORRBSHA36325S33
```

---

## Key Takeaway

Moving from a CLI binary to a GUI application does not meaningfully raise the bar for static analysis. The validation logic is identical in structure — a `strcmp` against a hardcoded string — and is just as visible in a disassembler. The added complexity of GTK event handling (`btn_clicked`) only affects where to look, not how hard it is to find. Binary patching is a viable alternative whenever the goal is bypass rather than key recovery.

---

## Lessons Learned

- GUI wrappers do not add security. The underlying validation logic is exposed in exactly the same way as a CLI binary — the entry point is just a button callback instead of a `main` loop.
- Locating the validation function is straightforward when the binary is unstripped: Ghidra resolves the mangled C++ symbol `_Z5validPKc` directly to `valid(char const*)`, making the target function trivial to find by name.
- `strcmp` is always a high-value target during reverse engineering. Its presence in the import table signals a plaintext string comparison, and tracing its call sites leads directly to the secret.
- The `SETZ` instruction after `TEST EAX, EAX` is the canonical pattern for converting a `strcmp` result into a boolean. Recognizing this pattern immediately reveals both the key location and the patch point.
- Binary patching is a faster path to bypass than key extraction when the goal is simply gaining access — useful to understand as a concept even when key recovery is the primary objective.

---

## Mitigation

- **Strip debug symbols.** The mangled function name `_Z5validPKc` resolves cleanly to `valid(char const*)` in Ghidra. Stripping the binary removes these symbols and forces the analyst to identify functions by behavior rather than name.
- **Avoid `strcmp` for license validation.** `strcmp` is a standard library call visible in the import table and trivially traceable. A custom comparison routine inlined at compile time (`-O2` with no external call) is harder to locate, though not impossible.
- **Do not store license keys in `.rodata`.** Any string literal in source ends up in the read-only data section as a direct reference. At minimum, obfuscate the key at rest — store it XOR-encoded and decode at runtime — so it does not appear as a recognizable string in the binary.
- **Implement integrity checks.** To resist patching, add a self-integrity check (e.g. a checksum over the `.text` section at startup) that detects if the binary has been modified. This raises the cost of a patch bypass significantly.
- **Move license validation off the client.** Any check that runs entirely on the user's machine can be bypassed with sufficient effort. Authoritative license validation should involve a server-side component that the user cannot patch or bypass locally.
