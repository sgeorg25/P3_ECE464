from __future__ import print_function
import os
import copy
import math
import csv



# FUNCTION: Main Function
def main():


###A
    tva1 = open("TV_A1.txt","w")
    filepath = 'TV_A.txt'
    with open(filepath) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            if cnt%2 ==0: 
                ib_string = ""
                for bit in line:
                    if bit == "1":
                        ib_string += "0"
                    elif bit == "0":
                        ib_string += "1"        
                tva1.write(ib_string + "\n")            
                line = fp.readline()
            else:
                tva1.write(line)            
                line = fp.readline()
            cnt += 1


            
            
    ###B	
    tvb1 = open("TV_B1.txt","w")
    filepath = 'TV_B.txt'
    with open(filepath) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            if cnt%2 ==0: 
                ib_string = ""
                for bit in line:
                    if bit == "1":
                        ib_string += "0"
                    elif bit == "0":
                        ib_string += "1"        
                tvb1.write(ib_string + "\n")            
                line = fp.readline()
            else:
                tvb1.write(line)            
                line = fp.readline()

            cnt += 1

###C
    tvc1 = open("TV_C1.txt","w")
    filepath = 'TV_C.txt'
    with open(filepath) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            if cnt%2 ==0: 
                ib_string = ""
                for bit in line:
                    if bit == "1":
                        ib_string += "0"
                    elif bit == "0":
                        ib_string += "1"        
                tvc1.write(ib_string + "\n")            
                line = fp.readline()
            else:
                tvc1.write(line)            
                line = fp.readline()
            cnt += 1
###D               
    tvd1 = open("TV_D1.txt","w")
    filepath = 'TV_D.txt'
    with open(filepath) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            if cnt%2 ==0: 
                ib_string = ""
                for bit in line:
                    if bit == "1":
                        ib_string += "0"
                    elif bit == "0":
                        ib_string += "1"        
                tvd1.write(ib_string + "\n")            

                line = fp.readline()
            else:
                tvd1.write(line)            
                line = fp.readline()
            cnt += 1

###E        
    tve1 = open("TV_E1.txt","w")
    filepath = 'TV_E.txt'
    with open(filepath) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            if cnt%2 ==0: 
                ib_string = ""
                for bit in line:
                    if bit == "1":
                            ib_string += "0"
                    elif bit == "0":
                            ib_string += "1"        
                tve1.write(ib_string + "\n")            
                line = fp.readline()
            else:
                tve1.write(line)            
                line = fp.readline()
            cnt += 1
    tva1.close()
    tvb1.close()
    tvc1.close()
    tvd1.close()
    tve1.close()    
    
if __name__ == "__main__":
    main()
