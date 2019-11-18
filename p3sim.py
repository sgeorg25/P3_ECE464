from __future__ import print_function
import os
import copy
import math
import time

# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Reading in the Circuit gate-level netlist file:
def netRead(netName):
    # Opening the netlist file:
    netFile = open(netName, "r")

    # temporary variables
    inputs = []  # array of the input wires
    outputs = []  # array of the output wires
    gates = []  # array of the gate list
    inputBits = 0  # the number of inputs needed in this given circuit
    filpflops = [] #list of flip flops

    # main variable to hold the circuit netlist, this is a dictionary in Python, where:
    # key = wire name; value = a list of attributes of the wire
    circuit = {}

    # Fast processing
    completed_queue = []
    leftovers_queue = []

    # Reading in the netlist file line by line
    for line in netFile:

        # NOT Reading any empty lines
        if (line == "\n"):
            continue

        # Removing spaces and newlines
        line = line.replace(" ", "")
        line = line.replace("\n", "")
        line = line.upper()

        # NOT Reading any comments
        if (line[0] == "#"):
            continue

        # @ Here it should just be in one of these formats:
        # INPUT(x)
        # OUTPUT(y)
        # z=LOGIC(a,b,c,...)

        # Read a INPUT wire and add to circuit:
        if (line[0:5] == "INPUT"):
            # Removing everything but the line variable name
            line = line.replace("INPUT", "")
            line = line.replace("(", "")
            line = line.replace(")", "")

            # Format the variable name to wire_*VAR_NAME*
            line = "wire_" + line

            # Error detection: line being made already exists
            if line in circuit:
                msg = "NETLIST ERROR: INPUT LINE \"" + line + "\" ALREADY EXISTS PREVIOUSLY IN NETLIST"
                print(msg + "\n")
                return msg

            completed_queue.append(line)

            # Appending to the inputs array and update the inputBits
            inputs.append(line)

            # add this wire as an entry to the circuit dictionary
            circuit[line] = ["INPUT", line, False, '']

            inputBits += 1
            continue

        # Read an OUTPUT wire and add to the output array list
        # Note that the same wire should also appear somewhere else as a GATE output
        if line[0:6] == "OUTPUT":
            # Removing everything but the numbers
            line = line.replace("OUTPUT", "")
            line = line.replace("(", "")
            line = line.replace(")", "")

            # Appending to the output array
            outputs.append("wire_" + line)
            continue

        # Read a gate output wire, and add to the circuit dictionary
        lineSpliced = line.split("=")  # splicing the line at the equals sign to get the gate output wire
        gateOut = "wire_" + lineSpliced[0]

        # Error detection: line being made already exists
        if gateOut in circuit:
            msg = "NETLIST ERROR: GATE OUTPUT LINE \"" + gateOut + "\" ALREADY EXISTS PREVIOUSLY IN NETLIST"
            print(msg + "\n")
            return msg

        lineSpliced = lineSpliced[1].split("(")  # splicing the line again at the "("  to get the gate logic
        logic = lineSpliced[0].upper()

        lineSpliced[1] = lineSpliced[1].replace(")", "")
        terms = lineSpliced[1].split(",")  # Splicing the the line again at each comma to the get the gate terminals
        # Turning each term into an integer before putting it into the circuit dictionary
        terms = ["wire_" + x for x in terms]

        # add the gate output wire to the circuit dictionary with the dest as the key
        if logic == "DFF":
            circuit[gateOut] = [logic, terms, True, 'U']   
            filpflops.append(gateOut)
            completed_queue.append(gateOut)
        else:
            circuit[gateOut] = [logic, terms, False, '']
            # following check if all terms have been discovered
            temp_to_check_terms_available = len(terms)
            for t in terms:
                if t in completed_queue:
                    temp_to_check_terms_available -= 1

            if temp_to_check_terms_available == 0:  # if 0 all terms have been discovered already
                # Appending the dest name to the gate list
                gates.append(gateOut)
                completed_queue.append(gateOut)
            else:
                leftovers_queue.append(gateOut)

    # Finish up the ordering
    while len(leftovers_queue):
        currgate = leftovers_queue[0]
        terms = circuit[currgate][1]
        temp_to_check_terms_available = len(terms)
        for t in terms:
            if t in completed_queue:
                temp_to_check_terms_available -= 1
        if temp_to_check_terms_available == 0:
            gates.append(currgate)
            completed_queue.append(currgate)
            del leftovers_queue[0]
        else:
            leftovers_queue.append(currgate)
            del leftovers_queue[0]

    # now after each wire is built into the circuit dictionary,
    # add a few more non-wire items: input width, input array, output array, gate list
    # for convenience

    circuit["INPUT_WIDTH"] = ["input width:", inputBits]
    circuit["INPUTS"] = ["Input list", inputs]
    circuit["OUTPUTS"] = ["Output list", outputs]
    circuit["GATES"] = ["Gate list", gates] 
    circuit["FFs"] = ["Flip Flop list", filpflops]

    # print("\n bookkeeping items in circuit: \n")
    # print(circuit["INPUT_WIDTH"])
    # print(circuit["INPUTS"])
    # print(circuit["OUTPUTS"])
    # print(circuit["GATES"])
    # print(circuit["FFs"])
    return circuit



# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: calculates the output value for each logic gate
def gateCalc(circuit, node):
    terminals = []

    # terminal will contain all the input wires of this logic gate (node)
    for gate in list(circuit[node][1]):
        
        if gate in ['0','1','U']:
            terminals.append(gate)
        else:
            terminals.append(circuit[gate][3])
    
    # print(terminals)
    # terminals = list(circuit[node][1])  
    # If the node is an Inverter gate output, solve and return the output
    if circuit[node][0] == "NOT":
        if terminals[0] == '0':
            circuit[node][3] = '1'
        elif terminals[0] == '1':
            circuit[node][3] = '0'
        elif terminals[0] == "U":
            circuit[node][3] = "U"
        else:  # Should not be able to come here
            return -1
        return circuit
    elif circuit[node][0] == "BUFF":
        circuit[node][3] = terminals[0]
        return circuit
    
    # If the node is an AND gate output, solve and return the output
    elif circuit[node][0] == "AND":
        # Initialize the output to 1
        circuit[node][3] = '1'
        # Initialize also a flag that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 0 at any input terminal, AND output is 0. If there is an unknown terminal, mark the flag
        # Otherwise, keep it at 1
        for term in terminals:  
            if term == '0':
                circuit[node][3] = '0'
                break
            if term == "U":
                unknownTerm = True

        if unknownTerm:
            if circuit[node][3] == '1':
                circuit[node][3] = "U"
        return circuit

    # If the node is a NAND gate output, solve and return the output
    elif circuit[node][0] == "NAND":
        # Initialize the output to 0
        circuit[node][3] = '0'
        # Initialize also a variable that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 0 terminal, NAND changes the output to 1. If there is an unknown terminal, it
        # changes to "U" Otherwise, keep it at 0
        for term in terminals:
            if term == '0':
                circuit[node][3] = '1'
                break
            if term == "U":
                unknownTerm = True
                break

        if unknownTerm:
            if circuit[node][3] == '0':
                circuit[node][3] = "U"
        return circuit

    # If the node is an OR gate output, solve and return the output
    elif circuit[node][0] == "OR":
        # Initialize the output to 0
        circuit[node][3] = '0'
        # Initialize also a variable that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 1 terminal, OR changes the output to 1. Otherwise, keep it at 0
        for term in terminals:
            if term == '1':
                circuit[node][3] = '1'
                break
            if term == "U":
                unknownTerm = True

        if unknownTerm:
            if circuit[node][3] == '0':
                circuit[node][3] = "U"
        return circuit

    # If the node is an NOR gate output, solve and return the output
    if circuit[node][0] == "NOR":
        # Initialize the output to 1
        circuit[node][3] = '1'
        # Initialize also a variable that detects a U to false
        unknownTerm = False  # This will become True if at least one unknown terminal is found

        # if there is a 1 terminal, NOR changes the output to 0. Otherwise, keep it at 1
        for term in terminals:
            if term == '1':
                circuit[node][3] = '0'
                break
            if term == "U":
                unknownTerm = True
        if unknownTerm:
            if circuit[node][3] == '1':
                circuit[node][3] = "U"
        return circuit

    # If the node is an XOR gate output, solve and return the output
    if circuit[node][0] == "XOR":
        # Initialize a variable to zero, to count how many 1's in the terms
        count = 0

        # if there are an odd number of terminals, XOR outputs 1. Otherwise, it should output 0
        for term in terminals:
            if term == '1':
                count += 1  # For each 1 bit, add one count
            if term == "U":
                circuit[node][3] = "U"
                return circuit

        # check how many 1's we counted
        if count % 2 == 1:  # if more than one 1, we know it's going to be 0.
            circuit[node][3] = '1'
        else:  # Otherwise, the output is equal to how many 1's there are
            circuit[node][3] = '0'
        return circuit

    # If the node is an XNOR gate output, solve and return the output
    elif circuit[node][0] == "XNOR":
        # Initialize a variable to zero, to count how many 1's in the terms
        count = 0

        # if there is a single 1 terminal, XNOR outputs 0. Otherwise, it outputs 1
        for term in terminals:
            if term == '1':
                count += 1  # For each 1 bit, add one count
            if term == "U":
                circuit[node][3] = "U"
                return circuit

        # check how many 1's we counted
        if count % 2 == 1:  # if more than one 1, we know it's going to be 0.
            circuit[node][3] = '0'
        else:  # Otherwise, the output is equal to how many 1's there are
            circuit[node][3] = '1'
        return circuit

    # Error detection... should not be able to get at this point
    return circuit[node][0]


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Updating the circuit dictionary with the input line, and also resetting the gates and output lines
def inputRead(circuit, line):
    if len(line) < circuit["INPUT_WIDTH"][1]:
        return -1 #not enough bits

    # Getting the proper number of bits:
    line = line[(len(line) - circuit["INPUT_WIDTH"][1]):(len(line))]

    # Since the for loop will start at the most significant bit, we start at input width N
    i = circuit["INPUT_WIDTH"][1] - 1
    inputs = list(circuit["INPUTS"][1])
    for bitVal in line:
        bitVal = bitVal.upper() # in the case user input lower-case u
        circuit[inputs[i]][3] = bitVal # put the bit value as the line value
        circuit[inputs[i]][2] = True  # and make it so that this line is accessed

        # In case the input has an invalid character (i.e. not "0", "1" or "U"), return an error flag
        if bitVal != "0" and bitVal != "1" and bitVal != "U":
            return -2
        i -= 1 # continuing the increments

    return circuit


# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: the actual simulation #
def basic_sim(circuit, cycle):
    # Creating a queue, using a list, containing all of the gates in the circuit
    
    while(cycle != 0):
        for key in circuit["GATES"][1]:
            circuit[key][2] = False
        queue = list(circuit["GATES"][1])
        while True:
            # If there's no more things in queue, done
            if len(queue) == 0:
                break

            # Remove the first element of the queue and assign it to a variable for us to use
            curr = queue[0]
            queue.remove(curr)

            if circuit[curr][2]:
                continue

            # initialize a flag, used to check if every terminal has been accessed
            term_has_value = True

            # Check if the terminals have been accessed
            for term in circuit[curr][1]:
                if term in ["0", "1", "U"]:  # ['1', '0', 'U']:
                    continue
                elif not circuit[term][2]:
                    term_has_value = False
                    break

            if term_has_value:
                circuit[curr][2] = True
                circuit = gateCalc(circuit, curr)

                # ERROR Detection if LOGIC does not exist
                if isinstance(circuit, str):
                    print("LOGIC NOT DETECTED: " + circuit)
                    return circuit
            else:
                # If the terminals have not been accessed yet, append the current node at the end of the queue
                queue.append(curr)
        for ffs in list(circuit["FFs"][1]):
            #The above does not write to FF's. So this will write to ffs at the end of the cycle
            circuit[ffs][3] = circuit[circuit[ffs][1][0]][3] 
        cycle -= 1
    #find the output and return it
    output = ""
    for y in circuit["OUTPUTS"][1]:
        if circuit[y][3] == '':
            output += "X"  #This is used to show that output has not reached the end. Should never hit this
        else:
            output = str(circuit[y][3]) + output
    return output

def fault_sim(circuit, activeFaults, inputCircuit,goodOutput,faultFile):
    toOutput = []
    for x in activeFaults:
        output = ''
        circuit = copy.deepcopy(inputCircuit)
        
        xSplit = x[0].split("-SA-")
        

        # Get the value to which the node is stuck at
        value = xSplit[1]

        currentFault = "wire_" + xSplit[0]

        if "-IN-" not in currentFault:
            circuit[currentFault][3] = value
            circuit[currentFault][2] = True

        else:
            currentFault = currentFault.split("-IN-")
            circuit[currentFault[0]][1].remove("wire_"+currentFault[1])
            circuit[currentFault[0]][1].append(value)

        basic_sim(circuit)

    return activeFaults

# -------------------------------------------------------------------------------------------------------------------- #
# FUNCTION: Main Function
def main():
    # Used for file access
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in

    print("Sequential Simulator:")

    # Select circuit benchmark file, default is circuit.bench
    while True:
        cktFile = os.path.join(script_dir, "circuit.bench")   
        userInput = input("\n Read circuit benchmark file: use circuit.bench?" + " Enter to accept or type filename: ")
        if userInput == "":
            break
        else:
            cktFile = os.path.join(script_dir, userInput)
            if not os.path.isfile(cktFile):
                print("File does not exist. \n")
            else:
                break
    circuit = netRead(cktFile)
    #select TV
    while True:
        seed = input("What is your TV value in integer: ")
        if seed.isdigit():
            width = circuit["INPUT_WIDTH"][1]
            seed = int(seed)
            if(seed < 0):
                TV = bin(seed & 0b1*width)[2:]
                break
            else:
                TV = bin(seed)[2:].zfill(width)
                TV = TV[:width]#only take the msb values
                break
    print("Your TV is : " + str(TV))

    #Select cycle count
    while True:
        cycle = 5
        userInput = input("How many cycles, press enter to run 5 times: ")
        if userInput == "":
            break
        else:
            if userInput.isdigit():
                if(int(userInput) > 0):
                    cycle = int(userInput)
                    break
                else:
                    print("Enter a value greater than 0")
                
    #Select the fault
    while True:
        first_input = circuit["INPUTS"][1][0]
        currFault = first_input[5:]+"-SA-0"
        userInput = input("Enter the fault you want to simulate. Press enter to use " + currFault + ": ")
        if userInput == "":
            break
        else:
            if "SA" in userInput: #not really doing much of a check 
                currFault = userInput
                break
    
    print("\n")
    #When reading in input, puts the MSB bit in the last input and LSB to the first input
    circuit = inputRead(circuit, TV)
    newCircuit = copy.deepcopy(circuit) #make a copy

    #look for good output
    output = basic_sim(circuit, cycle)
    print("Good output is: " + output)
    for ff in circuit["FFs"][1]:
        print("Value of " + ff + " Flip Flop is " + circuit[ff][3])
    circuit = copy.deepcopy(newCircuit)
    
    print("\n")
    #implement the fault into the circuit
    xSplit = currFault.split("-SA-")
    valueOfFault = xSplit[1]

    currWire = "wire_" + xSplit[0]
    if "-IN-" not in currWire:
        circuit[currWire][3] = valueOfFault
        circuit[currWire][2] = True
    else:
        currWire = currWire.split("-IN-")
        circuit[currWire[0]][1].remove("wire_"+currWire[1])
        circuit[currWire[0]][1].append(valueOfFault)

    output = basic_sim(circuit, cycle)
    print("Output of " + currFault + " is " + output)
    for ff in circuit["FFs"][1]:
        print("Value of " + ff + " Flip Flop is " + circuit[ff][3])


if __name__ == "__main__":
    main()
