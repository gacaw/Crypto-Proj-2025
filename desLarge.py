 # basically just transcribed from my HW 1 (which was in C): 

import math 


class Prng:
    def __init__(self, key1, key2, key3, seed): # keys of size 64, seed of size 64 
        self.__key1 = key1
        self.__key2 = key2
        self.__key3 = key3
        self.__val = seed
        

    def getNext(self):
        rand_val = tripleDES(0, self.__val, self.__key1, self.__key2, self.__key3)            
        self.__val = rand_val
        return rand_val

    def nextInt(self):
        randStr = self.getNext()
        return int(randStr, 2)

def messageToBinary(message): 
    return ''.join(format(ord(char), '08b') for char in message) 

# this requires your message to be exactly a multiple of 8 bits long 
def binaryToMessage(message): 
    byteStrings = []
    for i in range(0, len(message), 8):
        byteStrings.append(message[i:i+8])
    return ''.join(chr(int(val, 2)) for val in byteStrings)
    

# 64 bit block size
# 64 bit key 
# 48 bit subkeys 
# 16x4 S-Boxes 
# 32 element P-Boxes 
def DES(mode, inputVal, argKey):
    S0 = [
    [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
    [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
    [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
    [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
]
    #print(S0)
    S1 = [
    [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
    [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
    [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
    [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
]
    
    inputSize = len(inputVal)
    pTextSize = inputSize 
    while(pTextSize % 64 != 0): 
        pTextSize += 1 
    
    pText = []
    for i in range(pTextSize):
        pText.append('0')
    for i in range(pTextSize):
        if(i < inputSize): 
            pText[i] = int(inputVal[i])
        else:
            pText[i] = 0 
            
    #print(pText) 
    
    # ----------- line 88 
    
    key = [0 for i in range(64)] 
    for i in range(64): 
        key[i] = int(argKey[i])
        
    #print(key)
    
    # 64 bit key 
    p10 = [57,49,41,33,25,17,9,1,58,50,42,34,26,18,10,2,59,51,43,35,27,19,11,3,60,52,44,36,63,55,47,39,31,23,15,7,62,54,46,38,30,22,14,6,61,53,45,37,29,21,13,5,28,20,12,4] 
    # 48 bit subkeys
    p8 = [14,17,11,24,1,5,3,28,15,6,21,10,23,19,12,4,26,8,16,7,27,20,13,2,41,52,31,37,47,55,30,40,51,45,33,48,44,49,39,56,34,53,46,42,50,36,29,32]  
    initPerm = [58,50,42,34,26,18,10,2,60,52,44,36,28,20,12,4,62,54,46,38,30,22,14,6,64,56,48,40,32,24,16,8,57,49,41,33,25,17,9,1,59,51,43,35,27,19,11,3,61,53,45,37,29,21,13,5,63,55,47,39,31,23,15,7] 
    invPerm = [40,8,48,16,56,24,64,32,39,7,47,15,55,23,63,31,38,6,46,14,54,22,62,30,37,5,45,13,53,21,61,29,36,4,44,12,52,20,60,28,35,3,43,11,51,19,59,27,34,2,42,10,50,18,58,26,33,1,41,9,49,17,57,25] 
    eBox = [32,1,2,3,4,5,4,5,6,7,8,9,8,9,10,11,12,13,12,13,14,15,16,17,16,17,18,19,20,21,20,21,22,23,24,25,24,25,26,27,28,29,28,29,30,31,32,1]
    
    
    permKey = [0 for i in range(56)] 
    for i in range(56): 
        #print(i)
        permKey[i] = key[p10[i]-1]
    #print(permKey)
    
    lKey = [0 for i in range(28)]
    rKey = [0 for i in range(28)] 
    for i in range(28):
        lKey[i] = permKey[i] 
    for i in range(28,56):
        rKey[i-28] = permKey[i] 
        
    lKeyStart = lKey[0] 
    rKeyStart = rKey[0] 
    for i in range(27): 
        lKey[i] = lKey[i+1]
        rKey[i] = rKey[i+1] 
    lKey[27] = lKeyStart
    rKey[27] = rKeyStart
    
    combinedKey = [0 for i in range(56)] 
    for i in range(28): 
        combinedKey[i] = lKey[i] 
    for i in range(28,56): 
        combinedKey[i] = rKey[i-28] 
    
    K1 = [0 for i in range(48)] 
    
    for i in range(48): 
        K1[i] = combinedKey[p8[i]-1] 
    
    lKeyStart = lKey[0] 
    rKeyStart = rKey[0] 
    
    for i in range(27): 
        lKey[i] = lKey[i+1]
        rKey[i] = rKey[i+1] 
    lKey[27] = lKeyStart 
    rKey[27] = rKeyStart 
    
    lKeyStart = lKey[0] 
    rKeyStart = rKey[0] 
    for i in range(27): 
        lKey[i] = lKey[i+1] 
        rKey[i] = rKey[i+1] 
    lKey[27] = lKeyStart 
    rKey[27] = rKeyStart 
    
    for i in range(28): 
        combinedKey[i] = lKey[i] 
    for i in range(28, 56): 
        combinedKey[i] = rKey[i-28] 
        
    K2 = [0 for i in range(48)] 
    
    for i in range(48): 
        K2[i] = combinedKey[p8[i]-1] 
    
    
    # key creation done 
    
    if(mode == 1): 
        tempK = [0 for i in range(48)] 
        for i in range(48): 
            tempK[i] = K1[i] 
        for i in range(48):
            K1[i] = K2[i] 
        for i in range(48): 
            K2[i] = tempK[i] 
    
    blocks = [] # this part might not work 
    numBlocks = int(math.ceil(pTextSize/64.0))
        
    for i in range(int(math.ceil(pTextSize/64.0))): 
        blocks.append([])
        for k in range(64): 
            blocks[i].append(pText[64*i+k]) 
    
    #print(blocks)
    
    
    for i in range(numBlocks): 
        block = [0 for k in range(64)] 
        for k in range(64): 
            block[k] = blocks[i][k] 
            
        #print(block)
        
        #print(len(initPerm))
        initialPerm = [0 for k in range(64)] 
        for k in range(64):
            #print(k)
            #print(initPerm[k])
            initialPerm[k] = block[initPerm[k]-1] 
    
        
        lText = [0 for k in range(32)]
        rText = [0 for k in range(32)]
        
        for k in range(32): 
            lText[k] = initialPerm[k]
        for k in range(32,64): 
            rText[k-32] = initialPerm[k] 
        
        expandedRHS = [0 for k in range(48)] 
        for k in range(48): 
            expandedRHS[k] = rText[eBox[k]-1] 
        
    
        XOR1 = [0 for k in range(48)] 
        for k in range(48): 
            if(expandedRHS[k] == K1[k]): 
                XOR1[k] = 0
            else: 
                XOR1[k] = 1 
        
        lXOR1 = [0 for k in range(24)] 
        rXOR1 = [0 for k in range(24)] 
        
        
        # ---------------------------------
        binVals = []
        for k in range(8): 
            if(k < 4):
                side = 1 # left
            else:
                side = 0 # right 
            
            sXOR1 = XOR1[k:k+6] 
            
            sColAdd = 0 
            sRowAdd = 0 
            address = "".join([str(k) for k in sXOR1]) 
            #print(address)
            #int(bin, 2) 
            rowStr = address[0] + address[-1] 
            colStr = address[1:-1]
            #print(rowStr, colStr)
            sColAdd = int(colStr, 2)
            sRowAdd = int(rowStr, 2)
            #print(sRowAdd, sColAdd)
            
            val1 = S0[sRowAdd][sColAdd] 
            S01 = [0,0,0,0] 
            S01 = [0 if char == '0' else 1 for char in str(bin(val1))[2:]]
            while(len(S01) < 4):
                S01.insert(0,0)
            binVals.append(S01)
            #print(val1, S01, str(bin(val1)))
                
        
        # ---------------------------------
        
        combinedLHSRHS = [] 
        for entry in binVals: 
            combinedLHSRHS += entry
        #print(len(combinedLHSRHS))
        
        # up to line 522 from the original C code 
        
        perm4_1 = [0 for k in range(32)]
        P = [16,7,20,21,29,12,28,17,1,15,23,26,5,18,31,10,2,8,24,14,32,27,3,9,19,13,30,6,22,11,4,25] 
        for k in range(32): 
            perm4_1[k] = combinedLHSRHS[P[k]-1] 
        
        # -----------------------------
        XORend1 = [0 for k in range(32)] 
        for k in range(32): 
            if(perm4_1[k] == lText[k]): 
                XORend1[k] = 0 
            else: 
                XORend1[k] = 1 
                
        
        expandedRHS2 = [0 for k in range(48)] 
        for k in range(48): 
            expandedRHS2[k] = XORend1[eBox[k]-1] 
        
        XOR2 = [0 for k in range(48)] 
        for k in range(48): 
            if(expandedRHS2[k] == K2[k]): 
                XOR2[k] = 0 
            else: 
                XOR2[k] = 1 
                
        
        lXOR2 = [0 for k in range(24)] 
        rXOR2 = [0 for k in range(24)] 
        # -------------------- 
        binVals = []
        for k in range(8): 
            if(k < 4):
                side = 1 # left
            else:
                side = 0 # right 
            
            sXOR1 = XOR2[k:k+6] 
            
            sColAdd = 0 
            sRowAdd = 0 
            address = "".join([str(k) for k in sXOR1]) 
            #print(address)
            #int(bin, 2) 
            rowStr = address[0] + address[-1] 
            colStr = address[1:-1]
            #print(rowStr, colStr)
            sColAdd = int(colStr, 2)
            sRowAdd = int(rowStr, 2)
            #print(sRowAdd, sColAdd)
            
            val1 = S0[sRowAdd][sColAdd] 
            S01 = [0,0,0,0] 
            S01 = [0 if char == '0' else 1 for char in str(bin(val1))[2:]]
            while(len(S01) < 4):
                S01.insert(0,0)
            binVals.append(S01)
            #print(val1, S01, str(bin(val1)))

            
        combinedLHSRHS = [] 
        for entry in binVals: 
            combinedLHSRHS += entry
        #print(len(combinedLHSRHS))

        
        
        
        perm4_2 = [0 for k in range(32)] 
        for k in range(32): 
            perm4_2[k] = combinedLHSRHS[P[k]-1]
        
        
        XORend2 = [0 for k in range(32)] 
        for k in range(32): 
            if(perm4_2[k] == rText[k]):
                XORend2[k] = 0 
            else: 
                XORend2[k] = 1
            
            
        combinedEnd = [0 for k in range(64)] 
        for k in range(32): 
            combinedEnd[k] = XORend2[k] 
        for k in range(32,64): 
            combinedEnd[k] = XORend1[k-32] 
        
        
        endPerm = [0 for k in range(64)] 
        for k in range(64): 
            endPerm[k] = combinedEnd[invPerm[k]-1] 
        
        for k in range(64): 
            pText[64*i + k] = endPerm[k] 
    
    
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
    
    
        
tempKey = "".join(["0" for i in range(64)])
#print(DES(0,"00011101111010101010111011011","1100011110"))    
#print(DES(0,"00011101111010101010111011011",tempKey))    
#1100101011100001110011111110110111000110111011010010010101000010
#print(DES(1,"1100101011100001110011111110110111000110111011010010010101000010",tempKey))   
#0001110111101010101011101101100000000000000000000000000000000000 
#00011101111010101010111011011

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