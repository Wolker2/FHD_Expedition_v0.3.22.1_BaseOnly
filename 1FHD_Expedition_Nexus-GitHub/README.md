# FHD_Expedition 0.3.22.1 — source for Nexus Mods review

**Verified on 28 October 2026: all 11 runtime files rebuild from editable source with exactly the supplied SHA-256 hashes, including the native DLL and both SCR files.**

**Original-code finding:** the supplied intro SCR6 contains four opening braces and five closing braces in its dialog-event source. This lexical imbalance is preserved and recorded; byte-identical reconstruction does not establish that the original intro works in the game. No hidden gameplay fixes were introduced.

The module credits **Prolog_D**, declares version **0.3.22.1**, conflicts with **EvoFreeInflation,EvoNoInflation**, and installs at `Mods/FHD_MODS/FHD_Expedition`.

## Contents

| Path | Purpose |
| --- | --- |
| `source/CFG/*.json`, `source/CFG/Rus/Lang.json` | Complete editable DAT trees, configuration and embedded runtime code |
| `source/script/*.rson` | Reconstructed source/definitions for both controllers |
| `source/script/*.layout.json` | Explicit typed serialization order for SCR8 and legacy SCR6 |
| `source/native/expedition_native.S` | Complete readable x86 source of the DLL, including its DOS stub |
| `source/native/link.ld`, `pe_profile.json` | Native layout and named deterministic PE32 metadata |
| `source/DATA/UI/*.json` | Lossless sources for all four GI images |
| `source/ModuleInfo.txt` | UTF-8 metadata, rebuilt in its original CP1251 encoding |
| `scripts/` | Source codecs, assembler/PE builder, complete build and resource audit |
| `tests/` | Source-only rebuilding, source edits and native behavior fixture |
| `original-file-sha256.json` | Reference hashes of all 11 runtime files |
| `build-verification.json` | Completed results, environment and original-code findings |
| `.github/workflows/build.yml` | Automated source-build/check workflow |

Three screenshots, the historical `VALIDATION_MainPreserveFix.json`, the link-time `.lib` import library, and original runtime binaries are excluded from this compact review package. The import library is unnecessary for the supplied source build and is not a game-runtime input.

## Build and verify

Requirements: Python 3.10+ and GNU binutils (`as`, `ld`, `objcopy`, `objdump`, `nm`). Behavioral native tests additionally require `qemu-i386` from `qemu-user`. No pip packages, Windows tools, game executable or original DLL/SCR/DAT/GI files are required.

```sh
python3 scripts/build.py --strict-original
python3 -m unittest discover -s tests -v
```

Verified with Python 3.12.14, zlib 1.3.2, GNU binutils 2.42 and QEMU i386 8.2.2. The optional environment variable `FHD_QEMU_I386` can select an emulator executable already installed outside PATH. The GitHub workflow installs its dependencies automatically; hosted execution was not performed during preparation.

Outputs: `dist/FHD_Expedition_FROM_SOURCE.zip` and `dist/build-report.json`. The ZIP contains three DATs, two SCRs, four GIs, the DLL and ModuleInfo. All six local CacheData references resolve to output files. For intentional source changes, omit `--strict-original`; changed hashes are reported.

Five Python tests passed. They include a complete isolated build without any precompiled runtime input, edits to both SCR formats and embedded DAT code, all original hashes, and native execution with 40 mock-engine checks.

## Native DLL source and behavior

The original 3,072-byte PE32 DLL was reconstructed as editable GNU x86 assembly. Its entire 574-byte native code section is assembled from visible instructions; no `.incbin`, encoded code blob, original DLL or extracted machine-code file is a build input. The PE builder generates the DOS header, export table, relocations, section table and padding from named metadata and assembled symbols. Its output is byte-identical to the original DLL.

The native module has no Windows API import table. It operates on the game's supplied structures and calls a recovered engine callback using Delphi's register ABI. The exported cdecl interface is:

| Export | Behavior |
| --- | --- |
| `FHDExpeditionNativeInit(context)` | Resolves the galaxy and list-add callback from the supplied runtime context |
| `DeployProbe(planet, slot, probe)` | Checks required pointers/slot and duplicate destination, assigns a probe and invokes the engine list-add callback |
| `RecoverProbe(probe)` | Removes a known probe from the list, compacts it and clears assignment |
| `RecoverIdleProbe()` | Removes and returns the first unassigned probe |
| `FindProbeById(id)` | Finds a probe by its positive ID |

`tests/native_fixture.S` links the same assembly into a standalone 32-bit Linux executable. QEMU runs 40 checks against mock game structures: initialization, callback ABI, deployment, duplicate/bounds rejection, lookup, list compaction, assignment clearing and idle recovery. This does not replace testing against the real game and its engine layout.

## Script recovery and original-source findings

The complete `FHD_Expedition.scr` is version 8, 1,118 bytes. The complete intro is version 6, 1,949 bytes. Both were parsed without an unconsumed remainder, including legacy fields, variables, object bindings, state/dialog definitions and all stored code.

The RSON scenes are reconstructed views; visual positions were regenerated. Their typed sidecars contain field references, structural constants and explicit legacy values. The Python serializer is the authoritative verified path and reproduces the original SCRs. It does not implement the general RScript graph compiler. Adding/removing objects requires corresponding sidecar changes. All original runtime statements are visible in RSON fields or configuration JSON.

The supplied SRHD-XenoModKit 0.10.4 reported zero issues for the main scene. Its intro-scene compatibility lint reported three issues: the original extra closing brace and two display-answer expressions using `'restart~'+CT(...)` that its RScript-specific message rule does not accept. Those two tool-specific findings are not presented as proven game failures. The original expressions remain intact for exact reproduction. RScript opening/recompilation and in-game CodeEC compilation were not executed.

The embedded source ends its intro dialog event with `...AddDialogOverride('FHDExpeditionIntroDialog',1000000,0);}}}}}`. The report explicitly records the 4/5 brace counts. Resolving this original-code issue would be a separate mod change, with different output bytes.

## Configuration, graphics and provenance

DAT JSON retains all strings, record ordering, sorting metadata, seeds and compression parameters. GI JSON retains header fields, layer bounds, RGB565 color samples, transparency samples and RLE packets. No original runtime blob is hidden in these sources.

The previously supplied [SpaceRangersHD_decomp](https://github.com/pakompom/SpaceRangersHD_decomp) loader and expression/buffer code informed SCR6/SCR8 handling. RSON structure and GI conventions were checked using supplied examples and [SRHD-XenoModKit](https://github.com/Xenomorphchyma/SRHD-XenoModKit). The independent DAT codec follows conventions studied in Sergei Osminin's MIT-licensed [rangers-utils](https://github.com/murgesku/rangers-utils). Native instructions and PE metadata were reconstructed from the supplied DLL. Existing authorship and licensing are not changed.

Input archive SHA-256: `b5053e0de70e6bee5ae393cafd10ded2fd11bafeb4d6d7895f5c1c3bf55bed8c`. All 16 files were extracted successfully; the source build reproduces the 11 relevant runtime files.

Byte identity confirms preservation of the supplied mod. Real-game execution, gameplay correctness, antivirus verdicts and Nexus moderation approval were not performed or claimed.
