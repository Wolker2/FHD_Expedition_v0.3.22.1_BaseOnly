/* Reconstructed x86 source for FHDExpeditionNative.dll.
 * cdecl exports; engine callback uses Delphi EAX=self, EDX=item ABI.
 * All original instructions are visible; no bytecode blobs or .incbin.
 * Game layout: galaxy probe list +0x69c; probe id +8, planet +0x64, slot +0x68.
 */
.intel_syntax noprefix
.section .text
.global FHDExpeditionNativeInit
.global DeployProbe
.global RecoverProbe
.global RecoverIdleProbe
.global FindProbeById

FHDExpeditionNativeInit:
.L_10001000:
    push   esi
.L_10001001:
    mov    ecx,DWORD PTR [esp+0x8]
.L_10001005:
    xor    eax,eax
.L_10001007:
    test   ecx,ecx
.L_10001009:
    je     .L_10001048
.L_1000100b:
    mov    edx,DWORD PTR [ecx+0x3c]
.L_1000100e:
    test   edx,edx
.L_10001010:
    je     .L_10001048
.L_10001012:
    mov    edx,DWORD PTR [edx+0x4]
.L_10001015:
    test   edx,edx
.L_10001017:
    je     .L_10001048
.L_10001019:
    mov    esi,DWORD PTR [ecx+0x28]
.L_1000101c:
    mov    edx,DWORD PTR [edx+esi*4]
.L_1000101f:
    mov    DWORD PTR [GalaxyPointer],edx
.L_10001025:
    test   edx,edx
.L_10001027:
    je     .L_10001048
.L_10001029:
    mov    ecx,DWORD PTR [ecx+0x150]
.L_1000102f:
    mov    ecx,DWORD PTR [ecx]
.L_10001031:
    test   ecx,ecx
.L_10001033:
    je     .L_10001048
.L_10001035:
    mov    ecx,DWORD PTR [ecx-0x4]
.L_10001038:
    test   ecx,ecx
.L_1000103a:
    je     .L_10001048
.L_1000103c:
    add    ecx,0x20
.L_1000103f:
    mov    DWORD PTR [ProbeAddFunction],ecx
.L_10001045:
    xor    eax,eax
.L_10001047:
    inc    eax
.L_10001048:
    pop    esi
.L_10001049:
    ret

DeployProbe:
.L_1000104a:
    push   ebp
.L_1000104b:
    push   ebx
.L_1000104c:
    push   edi
.L_1000104d:
    push   esi
.L_1000104e:
    push   eax
.L_1000104f:
    mov    edi,DWORD PTR [esp+0x1c]
.L_10001053:
    mov    ebx,DWORD PTR [esp+0x18]
.L_10001057:
    mov    eax,[GalaxyPointer]
.L_1000105c:
    mov    esi,DWORD PTR [ProbeAddFunction]
.L_10001062:
    movd   xmm0,DWORD PTR [esp+0x20]
.L_10001068:
    movd   xmm1,ebx
.L_1000106c:
    punpckldq xmm1,xmm0
.L_10001070:
    movd   xmm0,esi
.L_10001074:
    movd   xmm2,eax
.L_10001078:
    punpckldq xmm2,xmm0
.L_1000107c:
    punpcklqdq xmm2,xmm1
.L_10001080:
    pxor   xmm0,xmm0
.L_10001084:
    pcmpeqd xmm0,xmm2
.L_10001088:
    test   edi,edi
.L_1000108a:
    sets   dl
.L_1000108d:
    movmskps ecx,xmm0
.L_10001090:
    test   ecx,ecx
.L_10001092:
    setne  dh
.L_10001095:
    xor    ecx,ecx
.L_10001097:
    or     dh,dl
.L_10001099:
    jne    .L_100010f0
.L_1000109b:
    movsx  edx,BYTE PTR [ebx+0x138]
.L_100010a2:
    cmp    edx,edi
.L_100010a4:
    jle    .L_100010f0
.L_100010a6:
    mov    eax,DWORD PTR [eax+0x69c]
.L_100010ac:
    test   eax,eax
.L_100010ae:
    je     .L_100010f0
.L_100010b0:
    mov    DWORD PTR [esp],esi
.L_100010b3:
    mov    ecx,DWORD PTR [eax+0x8]
.L_100010b6:
    test   ecx,ecx
.L_100010b8:
    jle    .L_100010da
.L_100010ba:
    mov    ebp,DWORD PTR [eax+0x4]
.L_100010bd:
    xor    edi,edi
.L_100010bf:
    mov    edx,DWORD PTR [ebp+edi*4+0x0]
.L_100010c3:
    test   edx,edx
.L_100010c5:
    je     .L_100010d5
.L_100010c7:
    cmp    DWORD PTR [edx+0x64],ebx
.L_100010ca:
    jne    .L_100010d5
.L_100010cc:
    mov    esi,DWORD PTR [esp+0x1c]
.L_100010d0:
    cmp    DWORD PTR [edx+0x68],esi
.L_100010d3:
    je     .L_100010fa
.L_100010d5:
    inc    edi
.L_100010d6:
    cmp    ecx,edi
.L_100010d8:
    jne    .L_100010bf
.L_100010da:
    mov    edx,DWORD PTR [esp+0x20]
.L_100010de:
    mov    DWORD PTR [edx+0x64],ebx
.L_100010e1:
    mov    ecx,DWORD PTR [esp+0x1c]
.L_100010e5:
    mov    DWORD PTR [edx+0x68],ecx
.L_100010e8:
    mov    esi,DWORD PTR [esp]
.L_100010eb:
    call   esi
.L_100010ed:
    xor    ecx,ecx
.L_100010ef:
    inc    ecx
.L_100010f0:
    mov    eax,ecx
.L_100010f2:
    add    esp,0x4
.L_100010f5:
    pop    esi
.L_100010f6:
    pop    edi
.L_100010f7:
    pop    ebx
.L_100010f8:
    pop    ebp
.L_100010f9:
    ret
.L_100010fa:
    xor    ecx,ecx
.L_100010fc:
    jmp    .L_100010f0

RecoverProbe:
.L_100010fe:
    push   ebp
.L_100010ff:
    push   ebx
.L_10001100:
    push   edi
.L_10001101:
    push   esi
.L_10001102:
    mov    ecx,DWORD PTR [esp+0x14]
.L_10001106:
    mov    edx,DWORD PTR [GalaxyPointer]
.L_1000110c:
    test   edx,edx
.L_1000110e:
    sete   bl
.L_10001111:
    test   ecx,ecx
.L_10001113:
    sete   bh
.L_10001116:
    xor    eax,eax
.L_10001118:
    or     bh,bl
.L_1000111a:
    jne    .L_10001174
.L_1000111c:
    mov    edx,DWORD PTR [edx+0x69c]
.L_10001122:
    test   edx,edx
.L_10001124:
    je     .L_10001174
.L_10001126:
    mov    esi,DWORD PTR [edx+0x4]
.L_10001129:
    mov    edi,DWORD PTR [edx+0x8]
.L_1000112c:
    test   esi,esi
.L_1000112e:
    sete   bl
.L_10001131:
    test   edi,edi
.L_10001133:
    setle  bh
.L_10001136:
    or     bh,bl
.L_10001138:
    jne    .L_10001174
.L_1000113a:
    xor    eax,eax
.L_1000113c:
    cmp    DWORD PTR [esi+eax*4],ecx
.L_1000113f:
    je     .L_1000114a
.L_10001141:
    inc    eax
.L_10001142:
    cmp    edi,eax
.L_10001144:
    jne    .L_1000113c
.L_10001146:
    xor    eax,eax
.L_10001148:
    jmp    .L_10001174
.L_1000114a:
    lea    ebx,[edi-0x1]
.L_1000114d:
    cmp    eax,ebx
.L_1000114f:
    jge    .L_1000115e
.L_10001151:
    inc    eax
.L_10001152:
    mov    ebp,DWORD PTR [esi+eax*4]
.L_10001155:
    mov    DWORD PTR [esi+eax*4-0x4],ebp
.L_10001159:
    inc    eax
.L_1000115a:
    cmp    edi,eax
.L_1000115c:
    jne    .L_10001152
.L_1000115e:
    xor    eax,eax
.L_10001160:
    mov    DWORD PTR [esi+edi*4-0x4],eax
.L_10001164:
    mov    DWORD PTR [edx+0x8],ebx
.L_10001167:
    mov    DWORD PTR [ecx+0x64],eax
.L_1000116a:
    mov    DWORD PTR [ecx+0x68],0xffffffff
.L_10001171:
    xor    eax,eax
.L_10001173:
    inc    eax
.L_10001174:
    pop    esi
.L_10001175:
    pop    edi
.L_10001176:
    pop    ebx
.L_10001177:
    pop    ebp
.L_10001178:
    ret

RecoverIdleProbe:
.L_10001179:
    mov    ecx,DWORD PTR [GalaxyPointer]
.L_1000117f:
    xor    eax,eax
.L_10001181:
    test   ecx,ecx
.L_10001183:
    je     .L_100011e9
.L_10001185:
    push   ebp
.L_10001186:
    push   ebx
.L_10001187:
    push   edi
.L_10001188:
    push   esi
.L_10001189:
    mov    ecx,DWORD PTR [ecx+0x69c]
.L_1000118f:
    test   ecx,ecx
.L_10001191:
    je     .L_100011e5
.L_10001193:
    mov    edx,DWORD PTR [ecx+0x4]
.L_10001196:
    mov    esi,DWORD PTR [ecx+0x8]
.L_10001199:
    test   edx,edx
.L_1000119b:
    sete   bl
.L_1000119e:
    test   esi,esi
.L_100011a0:
    setle  bh
.L_100011a3:
    or     bh,bl
.L_100011a5:
    jne    .L_100011e5
.L_100011a7:
    xor    edi,edi
.L_100011a9:
    mov    eax,DWORD PTR [edx+edi*4]
.L_100011ac:
    test   eax,eax
.L_100011ae:
    je     .L_100011b6
.L_100011b0:
    cmp    DWORD PTR [eax+0x64],0x0
.L_100011b4:
    je     .L_100011bf
.L_100011b6:
    inc    edi
.L_100011b7:
    cmp    esi,edi
.L_100011b9:
    jne    .L_100011a9
.L_100011bb:
    xor    eax,eax
.L_100011bd:
    jmp    .L_100011e5
.L_100011bf:
    lea    ebx,[esi-0x1]
.L_100011c2:
    cmp    edi,ebx
.L_100011c4:
    jge    .L_100011d3
.L_100011c6:
    inc    edi
.L_100011c7:
    mov    ebp,DWORD PTR [edx+edi*4]
.L_100011ca:
    mov    DWORD PTR [edx+edi*4-0x4],ebp
.L_100011ce:
    inc    edi
.L_100011cf:
    cmp    esi,edi
.L_100011d1:
    jne    .L_100011c7
.L_100011d3:
    mov    DWORD PTR [edx+esi*4-0x4],0x0
.L_100011db:
    mov    DWORD PTR [ecx+0x8],ebx
.L_100011de:
    mov    DWORD PTR [eax+0x68],0xffffffff
.L_100011e5:
    pop    esi
.L_100011e6:
    pop    edi
.L_100011e7:
    pop    ebx
.L_100011e8:
    pop    ebp
.L_100011e9:
    ret

FindProbeById:
.L_100011ea:
    push   ebx
.L_100011eb:
    push   edi
.L_100011ec:
    push   esi
.L_100011ed:
    mov    ecx,DWORD PTR [esp+0x10]
.L_100011f1:
    mov    edx,DWORD PTR [GalaxyPointer]
.L_100011f7:
    test   edx,edx
.L_100011f9:
    sete   bl
.L_100011fc:
    test   ecx,ecx
.L_100011fe:
    setle  bh
.L_10001201:
    xor    eax,eax
.L_10001203:
    or     bh,bl
.L_10001205:
    jne    .L_1000123a
.L_10001207:
    mov    esi,DWORD PTR [edx+0x69c]
.L_1000120d:
    test   esi,esi
.L_1000120f:
    je     .L_1000123a
.L_10001211:
    mov    edx,DWORD PTR [esi+0x4]
.L_10001214:
    mov    esi,DWORD PTR [esi+0x8]
.L_10001217:
    test   edx,edx
.L_10001219:
    sete   bl
.L_1000121c:
    test   esi,esi
.L_1000121e:
    setle  bh
.L_10001221:
    or     bh,bl
.L_10001223:
    jne    .L_1000123a
.L_10001225:
    xor    edi,edi
.L_10001227:
    mov    eax,DWORD PTR [edx+edi*4]
.L_1000122a:
    test   eax,eax
.L_1000122c:
    je     .L_10001233
.L_1000122e:
    cmp    DWORD PTR [eax+0x8],ecx
.L_10001231:
    je     .L_1000123a
.L_10001233:
    inc    edi
.L_10001234:
    cmp    esi,edi
.L_10001236:
    jne    .L_10001227
.L_10001238:
    xor    eax,eax
.L_1000123a:
    pop    esi
.L_1000123b:
    pop    edi
.L_1000123c:
    pop    ebx
.L_1000123d:
    ret

.section .data
.global GalaxyPointer, ProbeAddFunction
GalaxyPointer: .long 0
ProbeAddFunction: .long 0

.section .dosstub,"a"
.code16
    push cs
    pop ds
    mov dx, OFFSET .LDosMessage
    mov ah, 9
    int 0x21
    mov ax, 0x4c01
    int 0x21
.LDosMessage:
    .ascii "This program cannot be run in DOS mode.$"
    .balign 4, 0
.code32

.section .note.GNU-stack,"",@progbits
