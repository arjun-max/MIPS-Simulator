
###############  	Done By CS18B018,  CS18B012,  CS18B024    #####################


# R20 is $v0
# R21 is $a0
# R22 is $ra

import re
import os
import math

input_file = open("updated_bubble_sort.asm","r")	# file in which our assembly code is written 
cache_file = open("cache_details.txt","r")

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

def decimal_to_binary(a):
	b = ''
	for i in range(32):
		rem = a%2
		a = int(a/2)
		b = b+str(rem)
	return b[::-1]

def binary_to_decimal(a):
	i = len(a) - 1
	sum = 0
	while i >= 0:
		sum = sum + (2**i)*(int(a[len(a)-i-1]))
		i = i - 1
	return sum

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


#################  CACHE   ####################

######### Reading Cache details from file ###########

c = []

line = cache_file.readline()

while line:
	x = re.split("\n",line)
	c.append(x)	
	line = cache_file.readline()
cache_file.close()

for l in range(len(c)):
	c[l] = ' '.join(c[l]).split()

while [] in c:
	c.remove([])

L1_cache_size = int(c[1][3])
L1_block_size = int(c[2][3])
L1_associativity = (c[3][2])
L1_cache_latency = int(c[4][6])

L2_cache_size = int(c[6][3])
L2_block_size = int(c[7][3])
L2_associativity = (c[8][2])
L2_cache_latency = int(c[9][6])

main_mem_latency = int(c[10][5])

L1_cache_accesses = 0
L1_misses = 0
L2_cache_accesses = 0
L2_misses = 0

############  Building cache   ##############

L1_cache = []
L2_cache = []

L1_no_blocks = int((L1_cache_size)/(L1_block_size))
L1_block_words = int((L1_block_size)/4)

if L1_associativity == "fully":
	L1_no_sets = 0
else:
	L1_associativity = int(L1_associativity)
	L1_no_sets = int(L1_no_blocks/(L1_associativity))

if L1_no_sets == 0:
	L1_cache = [[[['','']for j in range(L1_block_words)]for i in range(L1_no_blocks)]]
else:
	L1_cache = [[[['',''] for k in range(L1_block_words)] for j in range(L1_associativity)] for i in range(L1_no_sets)]


L2_no_blocks = int((L2_cache_size)/(L2_block_size))
L2_block_words = int((L2_block_size)/4)

if L2_associativity == "fully":
	L2_no_sets = 0
else:
	L2_associativity = int(L2_associativity)
	L2_no_sets = int(L2_no_blocks/(L2_associativity))

if L2_no_sets == 0:
	L2_cache = [[[['','']for j in range(L2_block_words)]for i in range(L2_no_blocks)]]
else:
	L2_cache = [[[['',''] for k in range(L2_block_words)] for j in range(L2_associativity)] for i in range(L2_no_sets)]

###################################################################

def print_L1_cache():	# Code for printing contents of L1 cache

	offset_bits = math.ceil(math.log(L1_block_size,2))

	if L1_no_sets != 0:
		index_bits = math.ceil(math.log(L1_no_sets,2))

	print("Contents of L1 CACHE")

	for sets in range(len(L1_cache)):
		for blocks in range(len(L1_cache[sets])):
			for offsets in range(len(L1_cache[sets][blocks])):
				if L1_cache[sets][blocks][offsets][0] != '':

					tag = L1_cache[sets][blocks][offsets][0]
					value = L1_cache[sets][blocks][offsets][1]

					offset = decimal_to_binary(int(offsets*4))
					offset = offset[(32-offset_bits):33]

					if L1_no_sets != 0:
						index = decimal_to_binary(sets)
						index = index[(32-index_bits):(33)]
					else:
						index = ''

					decimal_addr = binary_to_decimal(tag + index + offset)

					print(decimal_addr,": ",value)
		if L1_no_sets == 0:
			break
		else:
			continue


def print_L2_cache():	# Code for printing contents of L2 cache

	offset_bits = math.ceil(math.log(L2_block_size,2))

	if L2_no_sets != 0:
		index_bits = math.ceil(math.log(L2_no_sets,2))

	print("Contents of L2 CACHE")

	for sets in range(len(L2_cache)):
		for blocks in range(len(L2_cache[sets])):
			for offsets in range(len(L2_cache[sets][blocks])):
				if L2_cache[sets][blocks][offsets][0] != '':

					tag = L2_cache[sets][blocks][offsets][0]
					value = L2_cache[sets][blocks][offsets][1]

					offset = decimal_to_binary(int(offsets*4))
					offset = offset[(32-offset_bits):33]

					if L2_no_sets != 0:
						index = decimal_to_binary(sets)
						index = index[(32-index_bits):(33)]
					else:
						index = ''

					decimal_addr = binary_to_decimal(tag + index + offset)

					print(decimal_addr,": ",value)
		if L2_no_sets == 0:
			break
		else:
			continue



# Function for getting tag, index and offset depending on which level of cache 

def get_tag_ind_off(a,b):

	result = []
	bin_addr = decimal_to_binary(a)

	if b == 'L1':
		offset_bits = math.ceil(math.log(L1_block_size,2))

		L1_offest = bin_addr[(32-offset_bits):33]

		if L1_no_sets == 0:
			index_bits = 0
			L1_index = ''
		else:
			index_bits = math.ceil(math.log(L1_no_sets,2))
			L1_index = bin_addr[(32-index_bits-offset_bits):(32-offset_bits)]

		if index_bits == 0:
			L1_tag = bin_addr[0:32-offset_bits]
			L1_index_decimal = 0
		else:
			L1_tag = bin_addr[0:32-index_bits-offset_bits]
			L1_index_decimal = binary_to_decimal(L1_index)

		L1_offset_decimal =	int(binary_to_decimal(L1_offest)/4)

		result = [L1_tag,L1_index_decimal,L1_offset_decimal]

	elif b == 'L2':
		offset_bits = math.ceil(math.log(L2_block_size,2))

		L2_offest = bin_addr[(32-offset_bits):33]

		if L2_no_sets == 0:
			index_bits = 0
			L2_index = ''
		else:
			index_bits = math.ceil(math.log(L2_no_sets,2))
			L2_index = bin_addr[(32-index_bits-offset_bits):(32-offset_bits)]

		if index_bits == 0:
			L2_tag = bin_addr[0:32-offset_bits]
			L2_index_decimal = 0
		else:
			L2_tag = bin_addr[0:32-index_bits-offset_bits]
			L2_index_decimal = binary_to_decimal(L2_index)

		L2_offset_decimal =	int(binary_to_decimal(L2_offest)/4)

		result = [L2_tag,L2_index_decimal,L2_offset_decimal]

	return result

###############################################################################

def insert_L1_cache(a,value):	  # Function for inserting a word into L1 cache
	addre = []
	latency = L1_cache_latency
	L1_flag = False
	addre = get_tag_ind_off(a,'L1')
	for blocks in range(len(L1_cache[addre[1]])):
		if L1_cache[addre[1]][blocks][addre[2]][0] == '':
			L1_flag = True
			L1_cache[addre[1]][blocks][addre[2]][0] = addre[0]
			L1_cache[addre[1]][blocks][addre[2]][1] = value
			L1_cache[addre[1]].insert(0,L1_cache[addre[1]].pop(blocks))
			break
		
	if L1_flag == False:
		if L1_no_sets == 0:
			tag = L1_cache[addre[1]][L1_no_blocks-1][addre[2]][0]
			val = L1_cache[addre[1]][L1_no_blocks-1][addre[2]][1]
		else:
			tag = L1_cache[addre[1]][L1_associativity-1][addre[2]][0]
			val = L1_cache[addre[1]][L1_associativity-1][addre[2]][1]


		L1_cache[addre[1]][blocks][addre[2]][0] = addre[0]
		L1_cache[addre[1]][blocks][addre[2]][1] = value

		L1_cache[addre[1]].insert(0,L1_cache[addre[1]].pop(blocks))

		offset = decimal_to_binary(int(addre[2]*4))
		offset_bits = math.ceil(math.log(L1_block_size,2))
		offset = offset[(32-offset_bits):33]

		if L1_no_sets == 0:
			index = ''
		else:
			index = decimal_to_binary(addre[1])
			index_bits = math.ceil(math.log(L1_no_sets,2))
			index = index[(32-index_bits):(33)]


		address_L1 = binary_to_decimal(tag + index + offset)

		latency = latency + insert_L2_cache(address_L1,val)

	return latency


def insert_L2_cache(a,val):    # Function for inserting a word into L2 cache 

	addre = []
	addre = get_tag_ind_off(a,'L2')

	tag = (addre[0])
	ind = (addre[1])
	off = (addre[2])
	latency = L2_cache_latency
	L2_flag = False

	for blocks in range(len(L2_cache[ind])):
		if L2_cache[ind][blocks][off][0] == '' or L2_cache[ind][blocks][off][0] == tag:
			L2_flag = True
			L2_cache[ind][blocks][off][0] = tag
			L2_cache[ind][blocks][off][1] = val

			L2_cache[ind].insert(0,L2_cache[ind].pop(blocks))
			break

	if L2_flag == False:
		if L2_no_sets == 0:
			tag_new = L2_cache[ind][L2_no_blocks-1][off][0]
			val_new = L2_cache[ind][L2_no_blocks-1][off][1]
		else:
			tag_new = L2_cache[ind][L2_associativity-1][off][0]
			val_new = L2_cache[ind][L2_associativity-1][off][1]

		L2_cache[ind][blocks][off][0] = tag
		L2_cache[ind][blocks][off][1] = val

		L2_cache[ind].insert(0,L2_cache[ind].pop(blocks))

		latency = latency + insert_main_memory(tag_new,ind,off,val_new)

	return latency

def insert_main_memory(tag,ind,off,val):	# Function for writing in main memory

	latency = main_mem_latency

	offset = decimal_to_binary(off*4)
	offset_bits = math.ceil(math.log(L2_block_size,2))
	offset = offset[(32-offset_bits):33]

	if L2_no_sets == 0:
		index = ''
	else:
		index = decimal_to_binary(ind)
		index_bits = math.ceil(math.log(L2_no_sets,2))
		index = index[(32-index_bits):(33)]

	addr = tag + index + offset

	addr_decimal = binary_to_decimal(addr)

	memory_dictionary[addr_decimal] = val

	return latency


#################	CACHE Controller #####################

def cache_controller(addr,ins,value):

	global L1_cache_accesses
	global L1_misses
	global L2_cache_accesses
	global L2_misses

	result = []
	addre = []
	latency = 0
	L1_flag = False 
	L2_flag = False
	

############	checking if address requested is in L1 Cache  ###########	

	addre = get_tag_ind_off(addr,'L1')

	L1_cache_accesses = L1_cache_accesses + 1

	for blocks in range(len(L1_cache[addre[1]])):
		if L1_cache[addre[1]][blocks][addre[2]][0] == addre[0]:
			L1_flag = True
			if ins == "lw":
				pass
			elif ins == "sw":
				L1_cache[addre[1]][blocks][addre[2]][1] = value

			result = [L1_cache[addre[1]][blocks][addre[2]][1],L1_cache_latency]

			L1_cache[addre[1]].insert(0,L1_cache[addre[1]].pop(blocks))  # maintaining LRU property

			return result

#############	checking if address requested is in L2 cache ################

	if L1_flag == False:
		L1_misses = L1_misses + 1
		L2_cache_accesses = L2_cache_accesses + 1
		addre = get_tag_ind_off(addr,'L2')

		for blocks in range(len(L2_cache[addre[1]])):

			if L2_cache[addre[1]][blocks][addre[2]][0] == addre[0]:
				L2_flag = True

				if ins == "sw":
					L2_cache[addre[1]][blocks][addre[2]][1] = value
				
				true_value = L2_cache[addre[1]][blocks][addre[2]][1]

				############	inserting in L1 cache ###############

				L2_cache[addre[1]].insert(0,L2_cache[addre[1]].pop(blocks))	 # maintaining LRU property

				result = [true_value,(L2_cache_latency+L1_cache_latency)]

				latency = insert_L1_cache(addr,true_value)

				result[1] = result[1] + latency


				return result

################	checking if address requested is in main memory  ############

		if L2_flag == False:
			L2_misses = L2_misses + 1
			if ins == "lw":
				val = memory_dictionary[addr]
			elif ins == "sw":
				memory_dictionary[addr] = value
				val = value

			####### 	insert into L1 cache   #######

			latency = insert_L1_cache(addr,val)

			result = [val,(main_mem_latency+L2_cache_latency+L1_cache_latency+latency)]

			return result


#####################################################################	


ip = p + 1	# ip is something like Program Counter

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

result_from_cache = []
stall_detected_mem = 1

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
				if stall_detected_mem == 1:
					result_from_cache = cache_controller(int(ex_mem[2]),"lw",0)
					stall_cycles = int(result_from_cache[1])
					stalls = stalls + stall_cycles
					stall_detected_mem = 0
				if stall_cycles == 0:
					temp_mem_wb = [ex_mem[1],result_from_cache[0]]
					stall_detected_mem = 1
				else:
					stall_cycles = stall_cycles - 1

			elif ex_mem[0] == "sw":
				if mem_wb == []:
					result_from_cache = cache_controller(int(ex_mem[3]),"sw",int(ex_mem[2]))
					temp_mem_wb = []		
				else:
					op1 = ex_mem[2]
					if mem_wb[0] == ex_mem[1]:
						op1 = mem_wb[1]
					result_from_cache = cache_controller(int(ex_mem[3]),"sw",int(op1))
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
				if stall_detected_mem == 0:
					writeback = 0
					execute = 0
					ins_decode = 0
					memory_stage = 1
				elif release_stall_control == 1:
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
print_L1_cache()
print("")
print_L2_cache()
print("")
print("No of stalls = ",stalls)
print("No of cycles = ",cycles)
print("No of instructions executed = ",ins_count)
print("IPC = ",(ins_count/cycles))
print("Miss Rate L1 = ",(L1_misses/L1_cache_accesses))
print("Miss Rate L2 = ",(L2_misses/L2_cache_accesses))

