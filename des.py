# basically just transcribed from my HW 1 (which was in C): 

import math 

def messageToBinary(message): 
    return ''.join(format(ord(char), '08b') for char in message) 

# this requires your message to be exactly a multiple of 8 bits long 
def binaryToMessage(message): 
    byteStrings = []
    for i in range(0, len(message), 8):
        byteStrings.append(message[i:i+8])
    return ''.join(chr(int(val, 2)) for val in byteStrings)
    

def DES(mode, input, argKey):
    S0 = [[1,0,3,2], [3,2,1,0], [0,2,1,3], [3,1,3,2]]
    #print(S0)
    S1 = [[0,1,2,3], [2,0,1,3], [3,0,1,0], [2,1,0,3]]
    
    inputSize = len(input)
    pTextSize = inputSize 
    while(pTextSize % 8 != 0): 
        pTextSize += 1 
    
    pText = []
    for i in range(pTextSize):
        pText.append('0')
    for i in range(pTextSize):
        if(i < inputSize): 
            pText[i] = int(input[i])
        else:
            pText[i] = 0 
            
    #print(pText) 
    
    # ----------- line 88 
    
    key = [0,0,0,0,0,0,0,0,0,0] 
    for i in range(10): 
        key[i] = int(argKey[i])
        
    #print(key)
    
    p10 = [3,5,2,7,4,10,1,9,8,6]
    p8 = [6,3,7,4,8,5,10,9]
    initPerm = [2,6,3,1,4,8,5,7] 
    invPerm = [4,1,3,5,7,2,8,6] 
    
    permKey = [0,0,0,0,0,0,0,0,0,0] 
    for i in range(10): 
        permKey[i] = key[p10[i]-1]
    #print(permKey)
    
    lKey = [0,0,0,0,0]
    rKey = [0,0,0,0,0] 
    for i in range(5):
        lKey[i] = permKey[i] 
    for i in range(5,10):
        rKey[i-5] = permKey[i] 
        
    lKeyStart = lKey[0] 
    rKeyStart = rKey[0] 
    for i in range(4): 
        lKey[i] = lKey[i+1]
        rKey[i] = rKey[i+1] 
    lKey[4] = lKeyStart
    rKey[4] = rKeyStart
    
    combinedKey = [0,0,0,0,0,0,0,0,0,0] 
    for i in range(5): 
        combinedKey[i] = lKey[i] 
    for i in range(5,10): 
        combinedKey[i] = rKey[i-5] 
    
    K1 = [0,0,0,0,0,0,0,0] 
    
    for i in range(8): 
        K1[i] = combinedKey[p8[i]-1] 
    
    lKeyStart = lKey[0] 
    rKeyStart = rKey[0] 
    
    for i in range(4): 
        lKey[i] = lKey[i+1]
        rKey[i] = rKey[i+1] 
    lKey[4] = lKeyStart 
    rKey[4] = rKeyStart 
    
    lKeyStart = lKey[0] 
    rKeyStart = rKey[0] 
    for i in range(4): 
        lKey[i] = lKey[i+1] 
        rKey[i] = rKey[i+1] 
    lKey[4] = lKeyStart 
    rKey[4] = rKeyStart 
    
    for i in range(5): 
        combinedKey[i] = lKey[i] 
    for i in range(5, 10): 
        combinedKey[i] = rKey[i-5] 
        
    K2 = [0,0,0,0,0,0,0,0] 
    
    for i in range(8): 
        K2[i] = combinedKey[p8[i]-1] 
    
    
    # key creation done 
    
    if(mode == 1): 
        tempK = [0,0,0,0,0,0,0,0] 
        for i in range(8): 
            tempK[i] = K1[i] 
        for i in range(8):
            K1[i] = K2[i] 
        for i in range(8): 
            K2[i] = tempK[i] 
    
    blocks = [] # this part might not work 
    numBlocks = int(math.ceil(pTextSize/8.0))
        
    for i in range(int(math.ceil(pTextSize/8.0))): 
        blocks.append([])
        for k in range(8): 
            blocks[i].append(pText[8*i+k]) 
    
    #print(blocks)
    
    
    for i in range(numBlocks): 
        block = [0,0,0,0,0,0,0,0] 
        for k in range(8): 
            block[k] = blocks[i][k] 
            
        initialPerm = [0,0,0,0,0,0,0,0] 
        for k in range(8):
            initialPerm[k] = block[initPerm[k]-1] 
    
        
        lText = [0,0,0,0]
        rText = [0,0,0,0]
        
        for k in range(4): 
            lText[k] = initialPerm[k]
        for k in range(4,8): 
            rText[k-4] = initialPerm[k] 
        
        expandedRHS = [0,0,0,0,0,0,0,0] 
        expandedRHS[0] = rText[3] 
        expandedRHS[1] = rText[0]
        expandedRHS[2] = rText[1]
        expandedRHS[3] = rText[2]
        expandedRHS[4] = rText[1]
        expandedRHS[5] = rText[2]
        expandedRHS[6] = rText[3]
        expandedRHS[7] = rText[0]
    
        XOR1 = [0,0,0,0,0,0,0,0] 
        for k in range(8): 
            if(expandedRHS[k] == K1[k]): 
                XOR1[k] = 0
            else: 
                XOR1[k] = 1 
        
        lXOR1 = [0,0,0,0] 
        rXOR1 = [0,0,0,0] 
        
        for k in range(4): 
            lXOR1[k] = XOR1[k] 
        for k in range(4,8): 
            rXOR1[k-4] = XOR1[k] 
        
        lColAdd1 = 0 
        lRowAdd1 = 0 
        
        if(lXOR1[1] == 1): 
            lColAdd1 += 2 
        if(lXOR1[2] == 1): 
            lColAdd1 += 1
        if(lXOR1[0] == 1): 
            lRowAdd1 += 2 
        if(lXOR1[3] == 1): 
            lRowAdd1 += 1 
            
        lVal1 = S0[lRowAdd1][lColAdd1] 
        lS01 = [0,0] 
        if(lVal1 == 0): 
            lS01[0] = 0 
            lS01[1] = 0 
        if(lVal1 == 1): 
            lS01[0] = 0 
            lS01[1] = 1
        if(lVal1 == 2): 
            lS01[0] = 1
            lS01[1] = 0 
        if(lVal1 == 3): 
            lS01[0] = 1 
            lS01[1] = 1 
        
        rColAdd1 = 0 
        rRowAdd1 = 0 
        
        if(rXOR1[1] == 1): 
            rColAdd1 += 2 
        if(rXOR1[2] == 1): 
            rColAdd1 += 1
        if(rXOR1[0] == 1): 
            rRowAdd1 += 2 
        if(rXOR1[3] == 1): 
            rRowAdd1 += 1 
        
        rVal1 = S1[rRowAdd1][rColAdd1]
        rS01 = [0,0] 
        if(rVal1 == 0):
            rS01[0] = 0
            rS01[1] = 0
        if(rVal1 == 1):
            rS01[0] = 0
            rS01[1] = 1
        if(rVal1 == 2):
            rS01[0] = 1
            rS01[1] = 0 
        if(rVal1 == 3): 
            rS01[0] = 1
            rS01[1] = 1
            
        # up to line 522 from the original C code 
        
        combinedLHSRHS = [0,0,0,0] 
        for k in range(2): 
            combinedLHSRHS[k] = lS01[k] 
        for k in range(2,4): 
            combinedLHSRHS[k] = rS01[k-2] 
        
        perm4_1 = [0,0,0,0] 
        perm4_1[0] = combinedLHSRHS[1] 
        perm4_1[1] = combinedLHSRHS[3] 
        perm4_1[2] = combinedLHSRHS[2] 
        perm4_1[3] = combinedLHSRHS[0] 
        
        
        XORend1 = [0,0,0,0] 
        for k in range(4): 
            if(perm4_1[k] == lText[k]): 
                XORend1[k] = 0 
            else: 
                XORend1[k] = 1 
                
        
        expandedRHS2 = [0,0,0,0,0,0,0,0] 
        expandedRHS2[0] = XORend1[3]
        expandedRHS2[1] = XORend1[0]
        expandedRHS2[2] = XORend1[1]
        expandedRHS2[3] = XORend1[2]
        expandedRHS2[4] = XORend1[1]
        expandedRHS2[5] = XORend1[2]
        expandedRHS2[6] = XORend1[3]
        expandedRHS2[7] = XORend1[0] 
        
        XOR2 = [0,0,0,0,0,0,0,0] 
        for k in range(8): 
            if(expandedRHS2[k] == K2[k]): 
                XOR2[k] = 0 
            else: 
                XOR2[k] = 1 
                
        
        lXOR2 = [0,0,0,0] 
        rXOR2 = [0,0,0,0] 
        
        for k in range(4): 
            lXOR2[k] = XOR2[k] 
        for k in range(4,8):
            rXOR2[k-4] = XOR2[k] 
            
        lColAdd2 = 0 
        lRowAdd2 = 0 
        
        if(lXOR2[1] == 1): 
            lColAdd2 += 2 
        if(lXOR2[2] == 1): 
            lColAdd2 += 1 
        if(lXOR2[0] == 1): 
            lRowAdd2 += 2 
        if(lXOR2[3] == 1): 
            lRowAdd2 += 1 
            
        lVal2 = S0[lRowAdd2][lColAdd2] 
        lS02 = [0,0] 
        if(lVal2 == 0):
            lS02[0] = 0 
            lS02[1] = 0 
        if(lVal2 == 1): 
            lS02[0] = 0
            lS02[1] = 1 
        if(lVal2 == 2): 
            lS02[0] = 1
            lS02[1] = 0
        if(lVal2 == 3): 
            lS02[0] = 1 
            lS02[1] = 1 
            
        rColAdd2 = 0 
        rRowAdd2 = 0 
        
        if(rXOR2[1] == 1): 
            rColAdd2 += 2 
        if(rXOR2[2] == 1): 
            rColAdd2 += 1 
        if(rXOR2[0] == 1): 
            rRowAdd2 += 2
        if(rXOR2[3] == 1): 
            rRowAdd2 += 1
            
        # line 727 in the original C code 
        
        rVal2 = S1[rRowAdd2][rColAdd2] 
        rS02 = [0,0] 
        if(rVal2 == 0):
            rS02[0] = 0
            rS02[1] = 0
        if(rVal2 == 1): 
            rS02[0] = 0
            rS02[1] = 1
        if(rVal2 == 2): 
            rS02[0] = 1
            rS02[1] = 0 
        if(rVal2 == 3): 
            rS02[0] = 1
            rS02[1] = 1 
            
            
        
        combinedLHSRHS2 = [0,0,0,0] 
        for k in range(2):
            combinedLHSRHS2[k] = lS02[k]
        for k in range(2,4): 
            combinedLHSRHS2[k] = rS02[k-2] 
        
        perm4_2 = [0,0,0,0] 
        perm4_2[0] = combinedLHSRHS2[1]
        perm4_2[1] = combinedLHSRHS2[3]
        perm4_2[2] = combinedLHSRHS2[2]
        perm4_2[3] = combinedLHSRHS2[0] 
        
        
        XORend2 = [0,0,0,0] 
        for k in range(4): 
            if(perm4_2[k] == rText[k]):
                XORend2[k] = 0 
            else: 
                XORend2[k] = 1
            
            
        combinedEnd = [0,0,0,0,0,0,0,0] 
        for k in range(4): 
            combinedEnd[k] = XORend2[k] 
        for k in range(4,8): 
            combinedEnd[k] = XORend1[k-4] 
        
        
        endPerm = [0,0,0,0,0,0,0,0] 
        for k in range(8): 
            endPerm[k] = combinedEnd[invPerm[k]-1] 
        
        for k in range(8): 
            pText[8*i + k] = endPerm[k] 
    
    
    # line 860 
    
    
    #print(pText)
    
    for i in range(len(pText)): 
        if(pText[i] == 0):
            pText[i] = '0'
        else: 
            pText[i] = '1'
    
    return "".join(pText)     
        
        
        
        
def tripleDES(mode, message, key1, key2, key3): 
    ans1 = DES(mode, message, key1) 
    ans2 = DES(mode, ans1, key2)
    return DES(mode, ans2, key3) 
    
    
        

#print(DES(0,"00011101111010101010111011011","1100011110"))    


# 00011101111010101010111011011 <-- input 
# 00011101111010101010111011011000 <-- encrypted and then decrypted again, so it seems to work 

# 00011011011101111010011000100011
# 00011011011101111010011000100011 

#print(tripleDES(0,"00011101111010101010111011011","1101011110", "1100011010", "1000011110"))
#print(tripleDES(1,"10111001100101010110010011010000","1000011110", "1100011010", "1101011110"))


# 10111001100101010110010011010000 <-- ctext 

# 00011101111010101010111011011    <-- original 
# 00011101111010101010111011011000
# 00011101111010101010111011011000 


#print(messageToBinary("hello world"))
#print(binaryToMessage("0110100001100101011011000110110001101111001000000111011101101111011100100110110001100100"))