;*******************************************************************************
;   L. Westlund & A. Valenzuela
;   Texas Instruments Inc.
;   December 2008
;   Built with Code Composer Essentials 3.2.2.1.4
;*******************************************************************************
 .cdecls C,LIST,  "msp430x22x4.h"

            ;Functions
            .def	TI_getRandomIntegerFromVLO
            .def	TI_getRandomIntegerFromADC
            
            .text                  			; Program reset
        
DEVICE_TYPE .set 2                          ; 2xx devices with a Timer_A3
;DEVICE_TYPE .set 3                         ; 2xx devices with a Timer_A2

 .if DEVICE_TYPE = 3                        ; For Timer_A2 devices
TACCTLX .set TACCTL0
TACCRX .set TACCR0
 .else
TACCTLX .set TACCTL2
TACCRX .set TACCR2
 .endif

;-------------------------------------------------------------------------------
TI_getRandomIntegerFromADC
;           returns: r12
;-------------------------------------------------------------------------------
            mov.w   #16,       r15          ; loop counter
            mov.w   #INCH_10,  &ADC10CTL1
            mov.w   #SREF_1 + ADC10SHT_1 + REFON + ADC10ON, &ADC10CTL0
adcloop     bis.w   #ENC + ADC10SC, &ADC10CTL0
sampling    bit.w   #ADC10BUSY, &ADC10CTL1
            jnz     sampling
            bit.w   #0x01,     &ADC10MEM
            rrc.w   r12
            dec.w   r15
            jnz     adcloop
            ret
;-------------------------------------------------------------------------------
TI_getRandomIntegerFromVLO
;           returns: r12
;-------------------------------------------------------------------------------
            push.w  r11                     ; r11 preserved
            bic.b   #0x02,     &BCSCTL1     ; Clear RSELx bit
            bic.b   #0xE0,     &DCOCTL      ; clear DCOx bits
            bis.b   #LFXT1S_2, &BCSCTL3     ; ACLK = VLO
            mov.w   #CM_1 + CCIS_1 + CAP,   &TACCTLX ; CAP, ACLK
            mov.w   #TASSEL_2 + MC_2, &TACTL; SMCLK, cont-mode, don't clear
            mov.w   #16,       r15          ; loop counter = 16
            clr.w   r12                     ; return value cleared
            clr.w   r13                     ; ACLK divider randomness
mainLoop    mov.w   #5,        r14          ; sub loop counter
            clr.w   r11                     ; majority vote holder
capture     bit.w   #CCIFG,    &TACCTLX       ; test for capture
            jz      capture
            bic.w   #CCIFG,    &TACCTLX       ; capture occured, clear flag
            bit.w   #0x01,     &TACCRX        ; test LSB of captured time
            jz      zero                    ; of LSB is zero, jump
            inc.w   r11                     ; if not, add  one to R11 to count 1s
zero                            
            dec.w   r14                     ; decrement majority vote counter
            jnz     capture                 ; if 3 bits aren't counted for, loop
            rra.w   r12                     ; make space for the new bit
            cmp.w   #0x03, r11              ; see if there are 2 or more 1s
            jge     one
            bic.w   #0x8000, r12            ; if not, clear the new bit in r12
            jmp     done
one         bis.w   #0x8000, r12            ; if so, set the new bit in r12
done
            ;-------------------            ; xor the ACLK divider section of the BCSCTL1
            mov.w   r12,       r13
            swpb    r13
            rra.w   r13
            rra.w   r13
            rra.w   r13
            and.w   #0x30,     r13
            xor.b   r13,       &BCSCTL1
            ;-------------------            ; add to the RSEL/DIVA bits to change DCO speed
            mov.b   &BCSCTL1,  r13
            add.b   #0x15,     r13
            bis.b   #XT2OFF,   r13          ; ensure XT2 stays off
            bic.b   #XTS+0x02, r13          ; ensure LFXT1 stays in LF mode
                                            ; clear RSEL bit to ensure lower max speed
            mov.b   r13,       &BCSCTL1
            ;-------------------            ; modify DCO Mod bits
            mov.b   &DCOCTL,   r13
            add.b   &0x15,     r13
            bic.b   #0xE0,     r13
            mov.b   r13,       &DCOCTL
            ;-------------------
            dec.w   r15
            jnz     mainLoop
            pop.w   r11               ; TEST
            ret
            
            .end
