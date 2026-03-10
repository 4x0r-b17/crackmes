# crackmes

![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-informational?style=flat&logo=linux&logoColor=white&color=222222)
![Language](https://img.shields.io/badge/Language-C%20%7C%20C%2B%2B-informational?style=flat&logo=c&logoColor=white&color=00599C)
![Source](https://img.shields.io/badge/Source-crackmes.one-informational?style=flat&color=8A2BE2)

A personal collection of reverse engineering writeups built around crackmes — small, purpose-built binaries designed to be analyzed and defeated. The goal of each challenge is typically to recover a hidden password, bypass a license check, or understand how a protection mechanism works, using only static and dynamic analysis tools without access to source code.

Reverse engineering is the process of working backwards from a compiled binary to understand its logic and behavior. It is a foundational skill in offensive and defensive security alike — applied in vulnerability research, malware analysis, CTF competitions, and software auditing.

Challenges are sourced from [crackmes.one](https://crackmes.one).

---

## Why This Matters

Practicing on crackmes directly builds skills that transfer to real-world security work.

**Software security** — Understanding how binaries validate input, store secrets, and implement control flow is essential for identifying vulnerabilities. The same techniques used to extract a hardcoded password from a crackme apply to auditing authentication logic in production software, identifying unsafe cryptographic implementations, and finding exploitable branches in compiled code.

**Malware analysis** — Malware authors rely on many of the same techniques found in crackmes: obfuscated strings, anti-debug tricks, and patched control flow. Developing fluency with disassemblers, learning to read decompiler output, and building intuition for how compilers translate high-level constructs into assembly are all direct prerequisites for analyzing malicious binaries in the wild.

---

## Repository Structure

```
cracks/
  <difficulty><platform><id>/
    writeup.md
```

### Folder Naming

Each challenge lives in its own folder under `cracks/` named according to this pattern:

```
<difficulty[01-06]><platform[1=Linux, 2=Windows]><id[01-N]>
```

| Segment      | Values       | Description                          |
|--------------|--------------|--------------------------------------|
| `difficulty` | `01` – `06`  | Challenge difficulty rating          |
| `platform`   | `1` or `2`   | `1` = Linux, `2` = Windows           |
| `id`         | `01` – `N`   | Sequential challenge index           |

**Example:** `011001` — difficulty 01, Linux, challenge 01.

---

## Tooling

Tools used across writeups vary by challenge complexity. Common ones include:

- `strings`, `file` — initial static reconnaissance
- `Ghidra` — disassembly and decompilation
- `GDB` — dynamic analysis and debugging
- `hexedit` / `pwndbg` — binary patching
