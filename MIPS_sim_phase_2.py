
###############  	Done By CS18B018,  CS18B012,  CS18B024    #####################


# R20 is $v0
# R21 is $a0
# R22 is $ra

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

# fetching registers

def check_s_or_t(a):
	b = a
	a = a.replace(" ","")
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
	elif a == "$v0":
		return 20
	elif a == "$a0":
		return 21
	elif a == "$ra":
		return 22

def la(b):
	return data_elements[b+":"]

def jump(a):
	label = a+":"
	return labels[label]


# Storing instructions

ins_3comp = ["add","sub","bne","beq","slt"]
ins_3comp_imm = ["addi","slti","sll"]
ins_2comp = ["lw","sw","move"]
ins_2comp_imm = ["li","la"]
ins_1comp = ["j","jr"]


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

labels = {}		# Dictionary for storing labels after main:

while find < len(s):
	if s[find][0][-1] == ":":
		if len(s[find]) is 1:
			if find > p:
				labels[s[find][0]] = find
			find=find+1
		else:
			temp_list = []
			for find1 in range(1,len(s[find])):
				temp_list.append(s[find][find1])

			u=len(s[find])
			for find2 in range(1,u):
				s[find].pop()
	
			s.insert(find+1,temp_list)
			if find > p:
				labels[s[find][0]] = find
			find = find + 1
	else:
		find = find + 1

ip = p + 1	#ip is something like Program Counter
count = 0

insf_insd = []	# Instruction Fetch Buffer/Latch
insd_ex = []	# Instruction Decode Buffer/Latch
ex_mem = []		# Execute Buffer/Latch
mem_wb = []		# Memory Buffer/Latch

# Temporary lists that will be updated after each cycle
temp_insf_insd = []	
temp_insd_ex = []
temp_ex_mem = []
temp_mem_wb = []

# These are something like access variables to simulate pipelining
ins_fetch = 1
ins_decode = 0
execute = 0
memory_stage = 0
writeback = 0
 

jr = 0
cycles = 0		# variable to store Number of cycles
ins_count = 0	# variable to store Number of instructions
stalls = 0		# variable to store Number of stalls

# Variables for storing stall detection
stall_detected = 0	
stall_detected_control = 0
stall_detected_decode = 1
stall_detected_control_2 = 0
stall_detected_control_3 = 0
release_stall_control = 0
release_stall_detected = 0

# Pipelining the instructions given below main: 
# ip is instruction pointer which is the index of the list containing all the instructions 

while True:  

	if (ip < len(s)-1 and s[ip]==["",""]):  # Skipping if any new lines are present in my assembly file
		continue 
	else:
		cycles = cycles + 1	# Incrementing cycles

	###############################  WRITEBACK STAGE ######################################	

	# This stage writesback the value from memory latch to the respective register
	# and activates or deactivates other stages in pipeline depending on stalls detected

		if writeback == 1:

			# print("Writeback")

			if mem_wb != []:
				if mem_wb[0] == "$v0":
					if int(mem_wb[1]) == 1:
						out_file = open("output.txt","w")
				if mem_wb[0] == "syscall":
					index = check_s_or_t(mem_wb[1])
					out_file.write(str(reg[index])+" ")
				else:
					index = check_s_or_t(mem_wb[0])
					reg[index] = mem_wb[1]
			
			if mem_wb != [] and mem_wb[0] == "$ra":
				try:
					out_file.close()
				except IOError:
					pass
				break
			else:
				if release_stall_control == 1:
					execute = 1
					writeback = 0
					release_stall_control = 0
				elif stall_detected == 1:
					execute = 1
					writeback = 0
					stall_detected = 0
					release_stall_detected = 1
				elif stall_detected_control_3 == 1:
					memory_stage = 0
					execute = 0
					ins_decode = 1
					writeback = 0
					stall_detected_control_3 = 0
				else:
					memory_stage = 1
					writeback = 0


	############################  MEMORY STAGE ############################################

	# This stage reads from or writes into the memory and gets the address from execute latch.
	# If anything has to be written back then it is put in memory latch.
	# and activates or deactivates other stages in pipeline depending on stalls detected

		if memory_stage == 1:

			# print("Memory")

			if ex_mem == []:
				temp_mem_wb = ex_mem 
			elif (ex_mem[0] in ins_3comp) or (ex_mem[0] in ins_3comp_imm):
					temp_mem_wb = [ex_mem[1],ex_mem[2]]

			elif ex_mem[0] == "lw":
				mem_access = memory_dictionary[ex_mem[2]]
				temp_mem_wb = [ex_mem[1],mem_access]

			elif ex_mem[0] == "sw":
				if mem_wb == []:
					memory_dictionary[ex_mem[3]] = int(ex_mem[2])
					temp_mem_wb = []
				else:
					op1 = ex_mem[2]
					if mem_wb[0] == ex_mem[1]:
						op1 = mem_wb[1]
					memory_dictionary[ex_mem[3]] = int(op1)
					temp_mem_wb = []

			elif ex_mem[0] == "move":
				if mem_wb ==  []:
					temp_mem_wb = [ex_mem[1],ex_mem[2]]
				else:
					op1 = ex_mem[2]
					if mem_wb[0] == ex_mem[3]:
						op1 = mem_wb[1]
					temp_mem_wb = [ex_mem[1],op1]

			elif ex_mem[0] == "li": 
				temp_mem_wb = [ex_mem[1],ex_mem[2]]

			elif ex_mem[0] == "la":
				temp_mem_wb = [ex_mem[1],ex_mem[2]]

			elif ex_mem[0] == "syscall":
				temp_mem_wb = ex_mem

			elif ex_mem[0] == "jr":
				temp_mem_wb = [ex_mem[1],ip]
				jr = 1

			if jr == 1:
				writeback = 1
				execute = 0
				memory_stage = 0
				jr = 0
			else:
				if release_stall_control == 1:
					ins_decode = 1
					writeback = 1
					memory_stage = 0
				elif stall_detected_control_2 == 1:
					writeback = 1
					execute = 0
					ins_decode = 1
					memory_stage = 0 
				else:
					writeback = 1
					execute = 1
					memory_stage = 0

    ################################  EXECUTE STAGE  ##########################################

    # This stage does the arithmetic and logical operations based on which instruction it is and puts it in execute latch.
    # It gets to know which instruction from Instruction decode latch 
    # and activates or deactivates other stages in pipeline depending on stalls detected
			
		if execute == 1:

			# print("Execute")

			if insd_ex[0] == "bne":
				if(insd_ex[2] == "false"):
					ins_fetch = 1
					temp_ex_mem = []
				else:
					temp_ex_mem = []
				stall_detected_decode = 1

			elif insd_ex[0] == "beq":
				if(insd_ex[2] == "false"):
					ins_fetch = 1
					temp_ex_mem = []
				else:
					temp_ex_mem = []
				stall_detected_decode = 1

			elif insd_ex[0] == 'add':
				if ex_mem == [] or ex_mem[0] == "sw":
					sum = int(insd_ex[4]) + int(insd_ex[5])
					temp_ex_mem = [insd_ex[0],insd_ex[1],sum]
				else:
					op1 = insd_ex[4]
					op2 = insd_ex[5]
					if release_stall_detected == 1:
						op1 = reg[int(insd_ex[6])]
						op2 = reg[int(insd_ex[7])]
					if mem_wb != []:
						if mem_wb[0] ==  insd_ex[2]:
							op1 = mem_wb[1]
						if mem_wb[0] == insd_ex[3]:
							op2 = mem_wb[1]
					if release_stall_detected == 0 and (ex_mem[1] == insd_ex[2] or ex_mem[1] == insd_ex[3]):
						if ex_mem[0] == "lw":
							stalls = stalls + 1
							stall_detected = 1
						else:
							if ex_mem[1] == insd_ex[2]:
								op1 = ex_mem[2]
								if ex_mem[0] == "move" and mem_wb != [] and ex_mem[3] == mem_wb[0]:
									op1 = mem_wb[1]
							if ex_mem[1] == insd_ex[3]:
								op2 = ex_mem[2]
								if ex_mem[0] == "move" and mem_wb != [] and ex_mem[3] == mem_wb[0]:
									op2 = mem_wb[1]
					release_stall_detected = 0
					
					if stall_detected == 1:
						temp_ex_mem = ex_mem
					else:
						sum = int(op1) + int(op2)
						temp_ex_mem = [insd_ex[0],insd_ex[1],sum]

			elif insd_ex[0] == 'sub':
				if ex_mem == [] or ex_mem[0] == "sw":
					diff = int(insd_ex[4]) - int(insd_ex[5])
					temp_ex_mem = [insd_ex[0],insd_ex[1],diff]
				else:
					op1 = insd_ex[4]
					op2 = insd_ex[5]
					if release_stall_detected == 1:
						op1 = reg[int(insd_ex[6])]
						op2 = reg[int(insd_ex[7])]
					if mem_wb != []:
						if mem_wb[0] ==  insd_ex[2]:
							op1 = mem_wb[1]
						if mem_wb[0] == insd_ex[3]:
							op2 = mem_wb[1]
					if release_stall_detected == 0 and (ex_mem[1] == insd_ex[2] or ex_mem[1] == insd_ex[3]):
						if ex_mem[0] == "lw":
							stalls = stalls + 1
							stall_detected = 1
						else:
							if ex_mem[1] == insd_ex[2]:
								op1 = ex_mem[2]
								if ex_mem[0] == "move" and mem_wb != [] and ex_mem[3] == mem_wb[0]:
									op1 = mem_wb[1]
							if ex_mem[1] == insd_ex[3]:
								op2 = ex_mem[2]
								if ex_mem[0] == "move" and mem_wb != [] and ex_mem[3] == mem_wb[0]:
									op2 = mem_wb[1]
					release_stall_detected = 0
					
					if stall_detected == 1:
						temp_ex_mem = ex_mem
					else:
						diff = int(op1) - int(op2)
						temp_ex_mem = [insd_ex[0],insd_ex[1],diff]

			elif insd_ex[0] == 'slt':
				if ex_mem == [] or ex_mem[0] == "sw":
					if int(insd_ex[4]) < int(insd_ex[5]):
						temp_ex_mem = [insd_ex[0],insd_ex[1],1]
					else:
						temp_ex_mem = [insd_ex[0],insd_ex[1],0]
				else:
					op1 = insd_ex[4]
					op2 = insd_ex[5]
					if release_stall_detected == 1:
						op1 = reg[int(insd_ex[6])]
						op2 = reg[int(insd_ex[7])]
					if mem_wb != []:
						if mem_wb[0] ==  insd_ex[2]:
							op1 = mem_wb[1]
						if mem_wb[0] == insd_ex[3]:
							op2 = mem_wb[1]
					if  release_stall_detected == 0 and (ex_mem[1] == insd_ex[2] or ex_mem[1] == insd_ex[3]):
						if ex_mem[0] == "lw":
							stalls = stalls + 1
							stall_detected = 1
						else:
							if ex_mem[1] == insd_ex[2]:
								op1 = ex_mem[2]
								if ex_mem[0] == "move" and mem_wb != [] and ex_mem[3] == mem_wb[0]:
									op1 = mem_wb[1]
							if ex_mem[1] == insd_ex[3]:
								op2 = ex_mem[2]
								if ex_mem[0] == "move" and mem_wb != [] and ex_mem[3] == mem_wb[0]:
									op2 = mem_wb[1]		
					release_stall_detected = 0

					if stall_detected == 1:
						temp_ex_mem = ex_mem
					else:
						if int(op1) < int(op2):
							check = 1
						else:
							check = 0
						temp_ex_mem = [insd_ex[0],insd_ex[1],check]

			elif insd_ex[0] == 'addi':
				if ex_mem == [] or ex_mem[0] == "sw":
					sum = int(insd_ex[3]) + int(insd_ex[4])
					temp_ex_mem = [insd_ex[0],insd_ex[1],sum]
				else:
					op1 = insd_ex[3]
					op2 = insd_ex[4]
					if mem_wb != []:
						if mem_wb[0] ==  insd_ex[2]:
							op1 = mem_wb[1]
					if ex_mem[1] == insd_ex[2]:
						if ex_mem[0] == "lw":
							stalls = stalls + 1
							stall_detected = 1
						else:
							op1 = ex_mem[2]
							if ex_mem[0] == "move" and mem_wb != [] and ex_mem[3] == mem_wb[0]:
								op1 = mem_wb[1]
					
					if stall_detected == 1:
						temp_ex_mem = ex_mem
					else:
						sum = int(op1) + int(op2)
						temp_ex_mem = [insd_ex[0],insd_ex[1],sum]

			elif insd_ex[0] == 'slti':
				if ex_mem == [] or ex_mem[0] == "sw":
					if int(insd_ex[3]) < int(insd_ex[4]):
						temp_ex_mem = [insd_ex[0],insd_ex[1],1]
					else:
						temp_ex_mem = [insd_ex[0],insd_ex[1],0]
				else:
					op1 = insd_ex[3]
					op2 = insd_ex[4]
					if mem_wb != []:
						if mem_wb[0] ==  insd_ex[2]:
							op1 = mem_wb[1]
					if ex_mem[1] == insd_ex[2]:
						if ex_mem[0] == "lw":
							stalls = stalls + 1
							stall_detected = 1
						else:
							op1 = ex_mem[2]
							if ex_mem[0] == "move" and mem_wb != [] and ex_mem[3] == mem_wb[0]:
								op1 = mem_wb[1]

					if stall_detected == 1:
						temp_ex_mem = ex_mem
					else:
						if int(op1) < int(op2):
							check = 1
						else:
							check = 0
						temp_ex_mem = [insd_ex[0],insd_ex[1],check]

			elif insd_ex[0] == 'sll':
				if ex_mem == [] or ex_mem[0] == "sw":
					after_shift = int(insd_ex[3]) << int(insd_ex[4])
					temp_ex_mem = [insd_ex[0],insd_ex[1],after_shift]
				else:
					op1 = insd_ex[3]
					shift = insd_ex[4]
					if mem_wb != []:
						if mem_wb[0] ==  insd_ex[2]:
							op1 = mem_wb[1]
					if ex_mem[1] == insd_ex[2]:
						if ex_mem[0] == "lw":
							stalls = stalls + 1
							stall_detected = 1
						else:
							op1 = ex_mem[2]
							if ex_mem[0] == "move" and mem_wb != [] and ex_mem[3] == mem_wb[0]:
								op1 = mem_wb[1]
					
					if stall_detected == 1:
						temp_ex_mem = ex_mem
					else:
						after_shift = int(op1) << int(shift)
						temp_ex_mem = [insd_ex[0],insd_ex[1],after_shift]

			elif insd_ex[0] == "lw":
				if ex_mem == [] or ex_mem[0] == "sw":
					mem_address = int(insd_ex[3]) + int(insd_ex[4])
					temp_ex_mem = [insd_ex[0],insd_ex[1],mem_address]
				else:
					op1 = insd_ex[3]
					offset = insd_ex[4]
					if mem_wb != []:
						if mem_wb[0] == insd_ex[2]:
							op1 = mem_wb[1]
					if ex_mem[1] == insd_ex[2]:
						if ex_mem[0] == "lw":
							stalls = stalls + 1
							stall_detected = 1

						else:
							op1 = ex_mem[2]
							if ex_mem[0] == "move" and mem_wb != [] and ex_mem[3] == mem_wb[0]:
								op1 = mem_wb[1]

					if stall_detected == 1:
						temp_ex_mem = ex_mem
					else:
						mem_address = int(op1) + int(offset)
						temp_ex_mem = [insd_ex[0],insd_ex[1],mem_address]

			elif insd_ex[0] == "sw":
				if ex_mem == []:
					mem_address = int(insd_ex[4]) + int(insd_ex[5])
					temp_ex_mem = [insd_ex[0],insd_ex[1],insd_ex[3],mem_address]
				else:
					op2 = insd_ex[4]
					offset = insd_ex[5]
					if mem_wb != []:
						if mem_wb[0] == insd_ex[2]:
							op2 = mem_wb[1]
					if ex_mem[1] == insd_ex[2]:
						if ex_mem[0] == "lw":
							stalls = stalls + 1
							stall_detected = 1

						else:
							op2 = ex_mem[2]
							if ex_mem[0] == "move" and mem_wb != [] and ex_mem[3] == mem_wb[0]:
								op2 = mem_wb[1]

					if stall_detected == 1:
						temp_ex_mem = ex_mem
					else:
						mem_address = int(op2) + int(offset)
						temp_ex_mem = [insd_ex[0],insd_ex[1],insd_ex[3],mem_address]

			elif insd_ex[0] == "li" or insd_ex[0] == "syscall":
				temp_ex_mem = insd_ex 			

			elif insd_ex[0] == "la":
				temp_ex_mem = [insd_ex[0],insd_ex[1],la(insd_ex[2])]

			elif insd_ex[0] == "move":
				op1 = insd_ex[2]
				if mem_wb != []:
					if mem_wb[0] == insd_ex[3]:
						op1 = mem_wb[1]

				temp_ex_mem = [insd_ex[0],insd_ex[1],op1,insd_ex[3]]

			elif insd_ex[0] == "j":
				ins_fetch = 1
				temp_ex_mem = []


			elif insd_ex[0] == "jr":
				temp_ex_mem = insd_ex
				jr = 1

			if jr == 1:
				ins_decode = 0
				memory_stage = 1
				execute = 0
				jr = 0
			else:
				if stall_detected == 0:
					memory_stage = 1
					execute = 0
				else:
					memory_stage = 0
					execute = 1
				if stall_detected_control == 0 and stall_detected == 0:
					ins_decode = 1
				else:
					ins_decode = 0

			if stall_detected_control == 1:
				release_stall_control = 1
			stall_detected_control = 0


	#############################  INSTRUTION DECODE/ REGISTER FETCH STAGE  ##################################

	# This stage decodes the instruction and fetches registers based on the instruction fetch latch and puts it in instruction decode latch
	# and activates or deactivates other stages in pipeline depending on stalls detected

		if ins_decode == 1:

			# print("Instruction Decoded  "+insf_insd[0])

			if insf_insd[0] in ins_3comp:

				if insf_insd[0] == "bne":

					if stall_detected_decode == 1:
						stalls = stalls + 1
						stall_detected_control_2 = 1
						stall_detected_decode = 0
						temp_insd_ex = insd_ex
					else:
						index1 = check_s_or_t(insf_insd[1])
						index2 = check_s_or_t(insf_insd[2])
						operand1 = reg[index1]
						operand2 = reg[index2]

						if stall_detected_control_2 == 1:
							if ex_mem != []:
								if ex_mem[0] == "lw":
									stalls = stalls + 1
									stall_detected_control_3 = 1
								elif insf_insd[1] == ex_mem[1]:
									operand1 = ex_mem[2]
								elif insf_insd[2] == ex_mem[1]:
									operand2 = ex_mem[2] 

							stall_detected_control_2 = 0

						if stall_detected_control_3 == 0:
							if int(operand2) != int(operand1):
								temp_insd_ex = [insf_insd[0],insf_insd[3],"false"]
								stalls = stalls + 1
								stall_detected_control = 1
								ip = jump(insf_insd[3]) + 1


							else:
								temp_insd_ex = [insf_insd[0],insf_insd[3],"true"]


				elif insf_insd[0] == "beq":

					if stall_detected_decode == 1:
						stalls = stalls + 1
						stall_detected_control_2 = 1
						stall_detected_decode = 0
						temp_insd_ex = insd_ex
					else:
						index1 = check_s_or_t(insf_insd[1])
						index2 = check_s_or_t(insf_insd[2])
						operand1 = reg[index1]
						operand2 = reg[index2]

						if stall_detected_control_2 == 1:
							if ex_mem != []:
								if ex_mem[0] == "lw":
									stalls = stalls + 1
									stall_detected_control_3 = 1
								elif insf_insd[1] == ex_mem[1]:
									operand1 = ex_mem[2]
								elif insf_insd[2] == ex_mem[1]:
									operand2 = ex_mem[2] 

							stall_detected_control_2 = 0

						if stall_detected_control_3 == 0:
							if int(operand2) == int(operand1):
								temp_insd_ex = [insf_insd[0],insf_insd[3],"false"]
								stalls = stalls + 1
								stall_detected_control = 1
								ip = jump(insf_insd[3]) + 1
							else:
								temp_insd_ex = [insf_insd[0],insf_insd[3],"true"]
					 
				else:
					index2 = check_s_or_t(insf_insd[2])
					index3 = check_s_or_t(insf_insd[3])
					operand1 = reg[index2]
					operand2 = reg[index3]
					temp_insd_ex = [insf_insd[0],insf_insd[1],insf_insd[2],insf_insd[3],operand1,operand2,index2,index3]

			elif insf_insd[0] in ins_3comp_imm:

				index = check_s_or_t(insf_insd[2])
				operand1 = reg[index]
				temp_insd_ex = [insf_insd[0],insf_insd[1],insf_insd[2],operand1,int(insf_insd[3])]

			elif insf_insd[0] in ins_2comp:

				if insf_insd[0] == "lw":
					b = insf_insd[2]
					c = insf_insd[2]
					c = c.replace(" ","")
					index = check_s_or_t(b[0:-1])
					operand1 = reg[index] 
					b = b.split('(')[0]
					offset = int(b)
					temp_insd_ex = [insf_insd[0],insf_insd[1],c[-4:-1],operand1,offset]
				elif insf_insd[0] == "sw":
					b = insf_insd[2]
					c = insf_insd[2]
					c = c.replace(" ","")
					index = check_s_or_t(b[0:-1])
					index1 = check_s_or_t(insf_insd[1])
					operand2 = reg[index]
					operand1 = reg[index1] 
					b = b.split('(')[0]
					offset = int(b)
					temp_insd_ex = [insf_insd[0],insf_insd[1],c[-4:-1],operand1,operand2,offset]
				else:
					index = check_s_or_t(insf_insd[2])
					operand = reg[index]
					temp_insd_ex = [insf_insd[0],insf_insd[1],operand,insf_insd[2]]


			elif insf_insd[0] in ins_2comp_imm:

				temp_insd_ex = insf_insd

			elif insf_insd[0] in ins_1comp:

				if insf_insd[0] == "j":

					stalls = stalls + 1
					stall_detected_control = 1
					ip = jump(insf_insd[1]) + 1

					temp_insd_ex = insf_insd

				elif insf_insd[0] == "jr":

					temp_insd_ex = insf_insd
					jr = 1

			elif insf_insd[0] == "syscall":

				temp_insd_ex = [insf_insd[0], "$a0"]
			

			if jr == 1:
				ins_fetch = 0
				execute = 1
				ins_decode = 0
				jr = 0
			elif stall_detected_control == 1:
				ins_fetch = 0
				execute = 1
				ins_decode = 0
			elif stall_detected_control_2 == 1 or stall_detected_control_3 == 1:
				ins_fetch = 0
				ins_decode = 0
			else:
				ins_fetch = 1
				execute = 1
				ins_decode = 0

	###########################  INSTRUCTION FETCH STAGE ######################################

	# This stage fetches the instruction and puts it in the instruction fetch latch
	# and activates or deactivates other stages in pipeline depending on stalls detected

		if ins_fetch == 1:

			if len(s[ip]) == 1 and s[ip][0][-1] == ':':
				ip = ip + 1
			temp_insf_insd = s[ip]
			# print("Instruction Fetched")
			ip = ip+1
			ins_count = ins_count + 1
			ins_decode = 1
			ins_fetch = 0


		# updating all the latches

		insf_insd = temp_insf_insd
		insd_ex = temp_insd_ex
		ex_mem = temp_ex_mem
		mem_wb = temp_mem_wb



print("")
print("#####   REGISTERS   #####")
print("")

for i in range(len(reg)):
	print ("\t"+"R"+str(i)+"  = "+str(reg[i]))

print("")
print("#####   MEMORY   #####")
print("")
print(memory_dictionary)
print("")
print("No of stalls = ",stalls)
print("No of cycles = ",cycles)
print("No of instructions executed = ",ins_count)
print("IPC = ",(ins_count/cycles))



