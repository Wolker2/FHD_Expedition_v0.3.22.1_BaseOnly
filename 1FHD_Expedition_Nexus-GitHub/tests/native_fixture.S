/* Standalone 32-bit Linux fixture for the five original DLL exports.
 * The same assembly code is linked into this test executable. Mock data
 * models only the memory layouts read/written by the DLL; no game is used.
 * Exit 0 = PASS, otherwise the failed check's number.
 */
.intel_syntax noprefix
.section .text
.global _start
.extern FHDExpeditionNativeInit, DeployProbe, RecoverProbe, RecoverIdleProbe, FindProbeById
.extern GalaxyPointer, ProbeAddFunction

.macro check expected, number
    cmp eax, \expected
    je 1f
    mov ebx, \number
    jmp failed
1:
.endm

.macro check_mem address, expected, number
    cmp DWORD PTR [\address], \expected
    je 1f
    mov ebx, \number
    jmp failed
1:
.endm

.macro deploy planet, slot, probe
    push OFFSET \probe
    push \slot
    push OFFSET \planet
    call DeployProbe
    add esp, 12
.endm

_start:
    push 0
    call FHDExpeditionNativeInit
    add esp, 4
    check 0, 1
    mov DWORD PTR [Context+0x3c], OFFSET ParameterList
    mov DWORD PTR [Context+0x28], 0
    mov DWORD PTR [Context+0x150], OFFSET CallbackArray
    push OFFSET Context
    call FHDExpeditionNativeInit
    add esp, 4
    check 1, 2
    check_mem GalaxyPointer, "OFFSET Galaxy", 3
    check_mem ProbeAddFunction, "OFFSET MockAdd", 4
    mov DWORD PTR [ProbeA+8], 100
    mov DWORD PTR [ProbeB+8], 101
    mov DWORD PTR [ProbeC+8], 102

    deploy Planet, 0, ProbeA
    check 1, 5
    check_mem ProbeList+8, 1, 6
    check_mem ProbeItems, "OFFSET ProbeA", 7
    check_mem ProbeA+0x64, "OFFSET Planet", 8
    check_mem ProbeA+0x68, 0, 9
    check_mem LastAddSelf, "OFFSET ProbeList", 10
    check_mem LastAddItem, "OFFSET ProbeA", 11

    /* Duplicate destination/slot, negative slot, out-of-range slot. */
    deploy Planet, 0, ProbeB
    check 0, 12
    deploy Planet, -1, ProbeB
    check 0, 13
    deploy Planet, 2, ProbeB
    check 0, 14
    check_mem ProbeList+8, 1, 15
    push 0
    push 1
    push OFFSET Planet
    call DeployProbe
    add esp, 12
    check 0, 16
    deploy Planet, 1, ProbeB
    check 1, 17
    check_mem ProbeList+8, 2, 18
    check_mem ProbeItems+4, "OFFSET ProbeB", 19

    push 101
    call FindProbeById
    add esp, 4
    check "OFFSET ProbeB", 20
    push 0
    call FindProbeById
    add esp, 4
    check 0, 21
    push 999
    call FindProbeById
    add esp, 4
    check 0, 22

    push OFFSET ProbeC
    call RecoverProbe
    add esp, 4
    check 0, 23
    push OFFSET ProbeA
    call RecoverProbe
    add esp, 4
    check 1, 24
    check_mem ProbeList+8, 1, 25
    check_mem ProbeItems, "OFFSET ProbeB", 26
    check_mem ProbeItems+4, 0, 27
    check_mem ProbeA+0x64, 0, 28
    check_mem ProbeA+0x68, -1, 29
    push 0
    call RecoverProbe
    add esp, 4
    check 0, 30

    call RecoverIdleProbe
    check 0, 31
    mov DWORD PTR [ProbeB+0x64], 0
    call RecoverIdleProbe
    check "OFFSET ProbeB", 32
    check_mem ProbeList+8, 0, 33
    check_mem ProbeItems, 0, 34
    check_mem ProbeB+0x68, -1, 35
    call RecoverIdleProbe
    check 0, 36

    /* Null list is rejected by the exports without dereferencing it. */
    mov DWORD PTR [Galaxy+0x69c], 0
    deploy Planet, 0, ProbeA
    check 0, 37
    push OFFSET ProbeA
    call RecoverProbe
    add esp, 4
    check 0, 38
    push 100
    call FindProbeById
    add esp, 4
    check 0, 39
    call RecoverIdleProbe
    check 0, 40
    xor ebx, ebx
failed:
    mov eax, 1
    int 0x80

/* Delphi register ABI expected by DeployProbe: EAX=list, EDX=probe. */
MockAdd:
    push ebx
    mov DWORD PTR [LastAddSelf], eax
    mov DWORD PTR [LastAddItem], edx
    mov ecx, DWORD PTR [eax+8]
    mov ebx, DWORD PTR [eax+4]
    mov DWORD PTR [ebx+ecx*4], edx
    inc DWORD PTR [eax+8]
    mov eax, ecx
    pop ebx
    ret

.section .data
.balign 4
Galaxy:
    .zero 0x69c
    .long ProbeList
ProbeList:
    .long 0
    .long ProbeItems
    .long 0
ProbeItems: .zero 32
Planet:
    .zero 0x138
    .byte 2
.balign 4
ProbeA: .zero 0x6c
ProbeB: .zero 0x6c
ProbeC: .zero 0x6c
Context: .zero 0x154
ParameterList: .long 0, ParameterArray
ParameterArray: .long Galaxy
CallbackArray: .long CallbackObject
CallbackPrefix: .long MockAdd-32
CallbackObject: .long 0
LastAddSelf: .long 0
LastAddItem: .long 0
.section .note.GNU-stack,"",@progbits
