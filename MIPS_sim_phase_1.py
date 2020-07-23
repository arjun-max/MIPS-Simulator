
###############  	Done By CS18B018,  CS18B012,  CS18B024    #####################


# R20 is $v0
# R21 is $a0

import re
import os

input_file = open("bubble_sort.asm","r")	# file in which our assembly code is written 

i = 0
p = 0
e = 4294967295	# upper bound of 32 bit number
f = -(2**31)	# lower bound of 32 bit number
s = []			# List for storing all the instructions from the assembly file

reg = [0]*32		# 32 Registers 
memory = [0]*1024	# 4kb Memory  
mem_count = 0		# Stores number of elements in memory

data_elements = {} 			# Stores multiple elements under .data
memory_dictionary = {}		# Stores elements of memory in dictionary
							# In this dictionary address is stored in 'key' and value of memory is stored in 'value'

for ij in range(0,4096,4):
	memory_dictionary[ij] = 0  

# Checking if register is $s or $t

def check_s_or_t(a):
	b = a
	if b.replace("-","").isdigit() or b.replace(".","").isdigit():
		return int(a)
	elif a[-2] == 's':
		if int(a[-1]) >=0 and int(a[-1]) <= 9:
			return int(a[-1])
		else:
			return -1
	elif a[-2] == 't':
		if int(a[-1]) >=0 and int(a[-1]) <= 9:
			return (int(a[-1]) + 10)
		else:
			return -1

# Checking if value in register is more than 32 bits

def check_register_overflow():
	g = -1
	while(g < 32):
		g = g + 1
		flag = 0
		if(reg[g] > f and reg[g] < e):
			flag+= 0
		else:
			print("register value $s"+str(g)+" has exceeded")
			return 1
		return flag

# Functions for carrying out different assembly language instructions

def li(a,b):
	l = check_s_or_t(a)
	if check_register_overflow()==0:
		reg[l] = int(b)

def add(a,b,c):
	l = check_s_or_t(a)
	h = check_s_or_t(b)
	k = check_s_or_t(c)
	if check_register_overflow()==0:
		reg[l] = reg[h] + reg[k]

def sub(a,b,c):
	l = check_s_or_t(a)
	h = check_s_or_t(b)
	k = check_s_or_t(c)
	if check_register_overflow()==0:
		reg[l] = reg[h] - reg[k]

def bne(a,b,c):
	l = check_s_or_t(a)
	h = check_s_or_t(b)

	if reg[l] != reg[h]:
		
		bne_j = jump(c)
		
		return bne_j
	else:	
		return -1

def beq(a,b,c):
	l = check_s_or_t(a)
	h = check_s_or_t(b)
	if reg[l]==reg[h]:
		beq_j=jump(c)
		return beq_j
	else:
		return -1

def addi(a,b,c):
	l = check_s_or_t(a)
	h = check_s_or_t(b)
	k = int(c)
	if check_register_overflow()==0:
		reg[l] = reg[h] + k

def slt(a,b,c):
	l = check_s_or_t(a)
	h = check_s_or_t(b)
	k = check_s_or_t(c)
	if reg[h] < reg[k]:
		reg[l] = 1
	else:
		reg[l] = 0

def slti(a,b,c):
	l = check_s_or_t(a)
	h = check_s_or_t(b)
	k = int(c)

	if reg[h] < k:
		reg[l] = 1
	else:
		reg[l] = 0

def sll(a,b,c):
	l = check_s_or_t(a)
	h = check_s_or_t(b)
	k = int(c)

	reg[l] = reg[h] << k

def la(a,b):
	l = check_s_or_t(a)
	if(check_register_overflow() == 0):
		reg[l] = data_elements[b+":"]

def lw(a,b):
	l = check_s_or_t(a)
	k = check_s_or_t(b[0:-1])
	b = b.split('(')[0]
	h = int(b)
	if(check_register_overflow() == 0):
		reg[l] = memory_dictionary[reg[k] + h]
	return 1

def sw(a,b):
	l = check_s_or_t(a)
	k = check_s_or_t(b[0:-1])
	b = b.split('(')[0]
	h = int(b)
	if check_register_overflow()==0:
		memory_dictionary[reg[k] + h] = reg[l]

def jump(a):
	label = a+":"
	flag = False
	for n_ip in range(p+1,len(s)):
		if(s[n_ip][0]) == label:
			flag = True
			break
		else:
			continue
	if(flag):
		return n_ip
	else:
		return -1

def move(a,b):
	if(a == '$a0'):
		l = check_s_or_t(b)
		reg[21] = reg[l]
	else:
		l = check_s_or_t(a)
		h = check_s_or_t(b)
		reg[l]  = reg[h]

# Code for Reading assembly file

line = input_file.readline()

while line:
	x = re.split(",| |\n",line)
	s.append(x)	
	line = input_file.readline()
input_file.close()


while s[i][0]!=".text":
	i=i+1

if s[0][0] == '.data':
	if s[1][0][0] != "." and s[1][0][-1] == ":":
		y=2
		while y<i:
			data_elements[s[y-1][0]]=mem_count
			if s[y][0] == ".word" or ".asciiz":
				for k in range(1 ,len(s[y])):
					if s[y][k] != '' :
						if int(s[y][k]) > f  and  int(s[y][k]) < e :
							memory_dictionary[mem_count] = int(s[y][k])
							mem_count = mem_count + 4
						
			y+=2

while s[p][0]!="main:":
	p=p+1

for l in range(len(s)):
	s[l] = ' '.join(s[l]).split()

while [] in s:
	s.remove([])

find = 0

# Separating the lists which have label: and some other instruction on the same line as two or more instructions

while find < len(s):
	if s[find][0][-1] == ":":
		if len(s[find]) is 1:
			find=find+1
		else:
			temp_list = []
			for find1 in range(1,len(s[find])):
				temp_list.append(s[find][find1])

			u=len(s[find])
			for find2 in range(1,u):
				s[find].pop()
	
			s.insert(find+1,temp_list)
			find = find + 1
	else:
		find = find + 1

ip = p
count = 0

# Executing the instructions given below main: 
# ip is instruction pointer which is the index of the list containing all the instructions 
# ip goes till length of s

while ip<len(s)-1 :
	ip = ip + 1
	if (s[ip]==["",""]):  # Skipping if any new lines are present in my assembly file
		continue 
	else:
		if s[ip][0] == 'add':
			add(s[ip][1],s[ip][2],s[ip][3])
		elif s[ip][0] == 'sub':
		    sub(s[ip][1],s[ip][2],s[ip][3])
		elif s[ip][0] == 'bne':
		 	bne_j = bne(s[ip][1],s[ip][2],s[ip][3])
		 	if bne_j == -1:
		 		continue
		 	else:
		 		ip = bne_j 
		 		continue
		elif s[ip][0] == 'beq':
		    beq_=beq(s[ip][1],s[ip][2],s[ip][3])
		    if beq_== -1:
		    	continue
		    else:
		    	ip = beq_
		elif s[ip][0] == 'li':
			if s[ip][1] == '$v0' and s[ip][2] == '1' or s[ip][2] == '4':
				reg[20] = int(s[ip][2])
				out_file = open("output.txt","w")
			else:
				li(s[ip][1],s[ip][2])
		elif s[ip][0] == 'addi':
		    addi(s[ip][1],s[ip][2],s[ip][3])
		elif s[ip][0] == 'lw':
		    lw(s[ip][1],s[ip][2])
		elif s[ip][0] == 'la':
			la(s[ip][1],s[ip][2])
		elif s[ip][0] == 'sw':
		    sw(s[ip][1],s[ip][2])  
		elif s[ip][0] == 'j':
		    jump_ = jump(s[ip][1])
		    if jump_== -1:
		    	print("Invalid")
		    	break
		    else:
		    	ip = jump_
		    	continue  
		elif s[ip][0] == 'slti':
		    slti(s[ip][1],s[ip][2],s[ip][3])
		elif s[ip][0] == 'slt':
		    slt(s[ip][1],s[ip][2],s[ip][3])
		elif s[ip][0] == 'sll':
		    sll(s[ip][1],s[ip][2],s[ip][3])
		elif s[ip][0] == 'move':
			move(s[ip][1],s[ip][2])
		elif s[ip][0] == 'syscall':
			count = count + 1
			out_file.write(str(reg[21])+" ")
			if(count == 1):
				os.startfile("output.txt")
		elif s[ip][0] == 'jr':
			if(count > 0):
				out_file.close()
			break

# Printing Registers and Memory

print("")

print("#####   REGISTERS   #####")
print("")

for i in range(len(reg)):
	print ("\t"+"R"+str(i)+"  = "+str(reg[i]))

print("")
print("#####   MEMORY   #####")
print("")
print(memory_dictionary)
