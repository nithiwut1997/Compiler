
stack_LL1 = ["EOF"]

alphabet = "abcdefghijklmnopqrstuvwxyz"
alphabet = alphabet + alphabet.upper()
alphabet = set(e for e in alphabet)

terminal = set(e for e in ["+", "-", "IF", "<", "=", "PRINT", "GOTO", "STOP", "EOF"])

next_set = {
    1 : ["line", "pgm"],
    2 : ["EOF"],
    3 : ["line_num", "stmt"],
    4 : ["asgmnt"],
    5 : ["if"],
    6 : ["print"],
    7 : ["goto"],
    8 : ["stop"],
    9 : ["id", "=", "exp"],
    10 : ["term", "exp*"],
    11 : ["+", "term"],
    12 : ["-", "term"],
    13 : None,
    14 : ["id"],
    15 : ["const"],
    16 : ["IF", "cond", "line_num"],
    17 : ["term", "cond*"],
    18 : ["<", "term"],
    19 : ["=", "term"],
    20 : ["PRINT", "id"],
    21 : ["GOTO", "line_num"],
    22 : ["STOP"]
}

parsing_table = {
    "pgm" : {"line_num" : 1, "EOF" : 2},
    "line" : {"line_num" : 3},
    "asgmnt" : {"id" : 9},
    "exp*" : {"line_num" : 13, "+" : 11, "-" : 12, "EOF" : 13},
    "term" : {"id" : 14, "const" : 15},
    "if" : {"IF" : 16},
    "cond*" : {"<" : 18, "=" : 19},
    "print" : {"PRINT" : 20},
    "goto" : {"GOTO" : 21},
    "stop" : {"STOP" : 22},
    "stmt" : {"id" : 4, "IF" : 5, "PRINT" : 6, "GOTO" : 7, "STOP" : 8},
    "exp" : {"id" : 10, "const" : 10},
    "cond" : {"id" : 17, "const" : 17}
}

def get_terminal_type(token):
    if token.isdigit():
        return "num"
    elif token in alphabet:
        return "id"
    elif token in terminals:
        return token
    raise Exception("token not terminals")

def get_rule(stack_top, token):
    terminal_type = get_terminal_type(token)
    if terminal_type != "num" and terminal_type in parsing_table[stack_top]:
        return parsing_table[stack_top][terminal_type]

    elif "line_num" in parsing_table[stack_top]:
        return parsing_table[stack_top]["line_num"]

    elif("const" in parsing_table[stack_top]):
        return parsing_table[stack_top]["const"]

    raise Exception('rule not defined') 

def is_same_terminal(token, top_stack):       
    terminal_type = get_terminal_type(token)
    if terminal_type != "num":
        terminal_equal_top_stack = terminal_type == top_stack
        return terminal_equal_top_stack
    else:
        top_is_line_num_or_const = (top_stack == "line_num" or top_stack == "const")
        return top_is_line_num_or_const
    
def is_terminal(symbol):
    return not symbol in parsing_table

def tokenize(line):
    return line.strip().split()

def get_bcode(terminal_symbol, value):
    if(terminal_symbol == "line_num"): 
        return ("#line", int(value))
    elif(terminal_symbol == "id"): 
        return ("#id", ord(value) - ord('A') + 1)
    elif(terminal_symbol == "const"):
        return ("#const", int(value))
    elif(terminal_symbol == "IF"): 
        return ("#if", 0)
    elif(terminal_symbol == "GOTO"):
        return ("#goto", int(value))
    elif(terminal_symbol == "PRINT"): 
        return ("#print", 0)
    elif(terminal_symbol == "STOP"): 
        return ("#stop", 0)
    elif(terminal_symbol == "+"): 
        return ("#op", 1)
    elif(terminal_symbol == "-"): 
        return ("#op", 2)
    elif(terminal_symbol == "<"): 
        return ("#op", 3)
    elif(terminal_symbol == "="): 
        return ("#op", 4)

def generate_bcode(parsed_list):
    bcode_list = []
    for i in range(len(parsed_list)):
        if(parsed_list[i][0] not in ["GOTO","line_num"] or i == 0):
            bcode_list.append(get_bcode(parsed_list[i][0], parsed_list[i][1]))
        else:
            if(parsed_list[i][0] == 'line_num' and i != 0):
                bcode_list.append(get_bcode("GOTO", parsed_list[i][1]))
    return bcode_list

def parse(token):
    while(not is_same_terminal(token, stack_LL1[-1])):
        stack_top = stack_LL1.pop()
        if is_terminal(stack_top):
            raise Exception("top stack is terminal") 
        rule = get_rule(stack_top, token)
        if(next_set[rule] != None):
            stack_LL1.extend(next_set[rule][::-1])
    return stack_LL1.pop()
    
def convert_to_bcode(scanned_line):
    parsed_list = []
    for token in scanned_line:
        parsed_list.append((parse(token), token))
    bcode_list = generate_bcode(parsed_list)
    print('Generated bcode : ',bcode_list)
    bcode_string = ''
    for types, value in bcode_list:
        bcode_string = bcode_string + str(bcode_type[types])+ ' ' + str(value) + ' '
    return bcode_string.strip()

#------------------------------------------------------------------------------------------------------

import sys
file_name = str(sys.argv[1])
file = open(file_name, 'r')
outfile = open(file_name+'.bout','w')
for line_count,line in enumerate(file):
    if line_count == 0:
        stack_LL1.append("pgm")
    scanned_line = tokenize(line)
    print(line.strip())
    bcode_string = convert_to_bcode(scanned_line)
    print('bcode : '+bcode_string)
    outfile.write(bcode_string+'\n')
outfile.write('0\n')
file.close()
outfile.close()

