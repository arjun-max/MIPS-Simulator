.data
array:
.word 11, 10, 9, 1, 7, 6, 4, 5, 3, 2, 1
.text
.globl main
main:

la $s6,array

li $s1,0
li $s2,0
li $s3,11
li $s4,9
li $t8,1

Loop1: sll $t1,$s1,2
Loop2: sll $t2,$s2,2

add $t2, $t2, $s6

lw $t0,0($t2)
lw $t3,4($t2)

slt $t9,$t3,$t0

bne $t9,$t8,Exit
sw $t3,0($t2)
sw $t0,4($t2)

Exit:
slt $s8,$s2,$s4

bne $s8,$t8,Exit1
addi $s2,$s2,1

j Loop2

Exit1:
li $s2,0

slt $s7,$s1,$s3

bne $s7,$t8,Exit2
addi $s1,$s1,1
j Loop1

Exit2:
li $s1,0
li $v0,1

Loop3: sll $t4,$s1,2
add $t4,$t4,$s6
slt $t7,$s1,$s3
bne $t7,$t8,Exit3
lw $t5,0($t4)
move $a0,$t5
addi $s1,$s1,1
syscall
j Loop3

Exit3:

jr $ra
