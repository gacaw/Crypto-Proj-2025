class Prng:
    def __init__(self, key1, key2, key3, seed): # keys of size 64, seed of size 64 
        self.__key1 = key1
        self.__key2 = key2
        self.__key3 = key3
        self.__val = seed

        self.tripleDES = TripleDES(key1, key2, key3)
        

    def getNext(self):
        rand_val = self.tripleDES.encrypt(self.__val)            
        self.__val = rand_val
        return rand_val

    def nextInt(self):
        randStr = self.getNext()
        return int(randStr, 2)

class DES:
    # Initial Permutation Table
    IP = [
        58, 50, 42, 34, 26, 18, 10, 2,
        60, 52, 44, 36, 28, 20, 12, 4,
        62, 54, 46, 38, 30, 22, 14, 6,
        64, 56, 48, 40, 32, 24, 16, 8,
        57, 49, 41, 33, 25, 17, 9, 1,
        59, 51, 43, 35, 27, 19, 11, 3,
        61, 53, 45, 37, 29, 21, 13, 5,
        63, 55, 47, 39, 31, 23, 15, 7
    ]

    # Final Permutation Table (Inverse of Initial Permutation)
    FP = [
        40, 8, 48, 16, 56, 24, 64, 32,
        39, 7, 47, 15, 55, 23, 63, 31,
        38, 6, 46, 14, 54, 22, 62, 30,
        37, 5, 45, 13, 53, 21, 61, 29,
        36, 4, 44, 12, 52, 20, 60, 28,
        35, 3, 43, 11, 51, 19, 59, 27,
        34, 2, 42, 10, 50, 18, 58, 26,
        33, 1, 41, 9, 49, 17, 57, 25
    ]

    # Expansion Permutation Table
    E = [
        32, 1, 2, 3, 4, 5,
        4, 5, 6, 7, 8, 9,
        8, 9, 10, 11, 12, 13,
        12, 13, 14, 15, 16, 17,
        16, 17, 18, 19, 20, 21,
        20, 21, 22, 23, 24, 25,
        24, 25, 26, 27, 28, 29,
        28, 29, 30, 31, 32, 1
    ]

    # S-boxes (Substitution boxes)
    S_BOX = [
        # S1
        [
            [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
            [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
            [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
            [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
        ],
        # S2
        [
            [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
            [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
            [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
            [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
        ],
        # S3
        [
            [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
            [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
            [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
            [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
        ],
        # S4
        [
            [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
            [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
            [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
            [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
        ],
        # S5
        [
            [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
            [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
            [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
            [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
        ],
        # S6
        [
            [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
            [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
            [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
            [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
        ],
        # S7
        [
            [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
            [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
            [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
            [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
        ],
        # S8
        [
            [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
            [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
            [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
            [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
        ]
    ]

    # Permutation Table
    P = [
        16, 7, 20, 21,
        29, 12, 28, 17,
        1, 15, 23, 26,
        5, 18, 31, 10,
        2, 8, 24, 14,
        32, 27, 3, 9,
        19, 13, 30, 6,
        22, 11, 4, 25
    ]

    # Permuted Choice 1 Table (PC-1)
    PC1 = [
        57, 49, 41, 33, 25, 17, 9,
        1, 58, 50, 42, 34, 26, 18,
        10, 2, 59, 51, 43, 35, 27,
        19, 11, 3, 60, 52, 44, 36,
        63, 55, 47, 39, 31, 23, 15,
        7, 62, 54, 46, 38, 30, 22,
        14, 6, 61, 53, 45, 37, 29,
        21, 13, 5, 28, 20, 12, 4
    ]

    # Permuted Choice 2 Table (PC-2)
    PC2 = [
        14, 17, 11, 24, 1, 5,
        3, 28, 15, 6, 21, 10,
        23, 19, 12, 4, 26, 8,
        16, 7, 27, 20, 13, 2,
        41, 52, 31, 37, 47, 55,
        30, 40, 51, 45, 33, 48,
        44, 49, 39, 56, 34, 53,
        46, 42, 50, 36, 29, 32
    ]

    # Number of left shifts per round
    SHIFT = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

    def __init__(self, key):
        """Initialize with a 64-bit binary string key"""
        if len(key) != 64 or not all(c in '01' for c in key):
            raise ValueError("Key must be a 64-bit binary string")
        
        self.key = key
        self.subkeys = self.generate_subkeys()

    def generate_subkeys(self):
        """Generate 16 subkeys from the 64-bit binary key"""
        # Convert binary string to list of integers
        key_bits = [int(bit) for bit in self.key]
        
        # Apply PC-1 permutation (64 bits to 56 bits)
        key_pc1 = [key_bits[x-1] for x in self.PC1]
        
        # Split into left and right halves (28 bits each)
        left = key_pc1[:28]
        right = key_pc1[28:]
        
        subkeys = []
        for i in range(16):
            # Perform left shifts
            shift = self.SHIFT[i]
            left = left[shift:] + left[:shift]
            right = right[shift:] + right[:shift]
            
            # Combine and apply PC-2 permutation (56 bits to 48 bits)
            combined = left + right
            subkey = [combined[x-1] for x in self.PC2]
            subkeys.append(subkey)
        
        return subkeys

    def _process_block(self, block_bits, subkeys, encrypt=True):
        """Process a single 64-bit block"""
        if len(block_bits) != 64:
            raise ValueError("Block must be 64 bits")
        
        # Convert binary string to list of integers
        block = [int(bit) for bit in block_bits]
        
        # Initial Permutation
        block = [block[x-1] for x in self.IP]
        
        # Split into left and right halves (32 bits each)
        left = block[:32]
        right = block[32:]
        
        # 16 Feistel rounds
        for i in range(16):
            if not encrypt:
                i = 15 - i  # Reverse order for decryption
            
            # Feistel function
            expanded = [right[x-1] for x in self.E]  # Expansion to 48 bits
            xored = [e ^ subkeys[i][j] for j, e in enumerate(expanded)]
            
            # S-box substitution (48 bits to 32 bits)
            substituted = []
            for j in range(8):
                bits = xored[j*6:(j+1)*6]
                row = bits[0] * 2 + bits[-1]
                col = bits[1]*8 + bits[2]*4 + bits[3]*2 + bits[4]
                val = self.S_BOX[j][row][col]
                substituted.extend([int(b) for b in f"{val:04b}"])
            
            # Permutation
            permuted = [substituted[x-1] for x in self.P]
            
            # XOR with left half
            new_right = [l ^ p for l, p in zip(left, permuted)]
            left = right
            right = new_right
        
        # Final swap and combine
        combined = right + left
        
        # Final Permutation
        result = [combined[x-1] for x in self.FP]
        
        # Return as binary string
        return ''.join(str(bit) for bit in result)
    
    def encrypt_block(self, block_bits):
        """Encrypt a 64-bit block (binary string)"""
        return self._process_block(block_bits, self.subkeys, encrypt=True)

    def decrypt_block(self, block_bits):
        """Decrypt a 64-bit block (binary string)"""
        return self._process_block(block_bits, self.subkeys, encrypt=False)

    def encrypt(self, message_bits):
        """Encrypt a binary string of any length"""
        # Pad to multiple of 64 bits
        pad_len = (64 - (len(message_bits) % 64)) % 64
        padded = message_bits + '0' * pad_len
        
        # Process each block
        ciphertext = ''
        for i in range(0, len(padded), 64):
            block = padded[i:i+64]
            ciphertext += self.encrypt_block(block)
        
        return ciphertext

    def decrypt(self, ciphertext_bits):
        """Decrypt a binary string (must be multiple of 64 bits)"""
        if len(ciphertext_bits) % 64 != 0:
            raise ValueError("Ciphertext must be multiple of 64 bits")
        
        # Process each block
        plaintext = ''
        for i in range(0, len(ciphertext_bits), 64):
            block = ciphertext_bits[i:i+64]
            plaintext += self.decrypt_block(block)
        
        # Return without padding (caller must know original length)
        return plaintext
    
class TripleDES:
    def __init__(self, key1, key2, key3):
        """
        Initialize Triple DES with three 8-byte keys.
        For 2-key 3DES, set key3 = key1.
        """
        if any(len(k) != 64 for k in [key1, key2, key3]):
            raise ValueError("All keys must be 64-bit binary strings")
        
        self.des1 = DES(key1)
        self.des2 = DES(key2)
        self.des3 = DES(key3)
    
    def encrypt(self, message_bits):
        """Encrypt using EDE (Encrypt-Decrypt-Encrypt)"""
        temp = self.des1.encrypt(message_bits)
        temp = self.des2.decrypt(temp)
        return self.des3.encrypt(temp)
    
    def decrypt(self, ciphertext_bits):
        """Decrypt using DED (Decrypt-Encrypt-Decrypt)"""
        temp = self.des3.decrypt(ciphertext_bits)
        temp = self.des2.encrypt(temp)
        return self.des1.decrypt(temp)

def messageToBinary(message): 
    return ''.join(format(ord(char), '08b') for char in message) 

# this requires your message to be exactly a multiple of 8 bits long 
def binaryToMessage(message): 
    byteStrings = []
    for i in range(0, len(message), 8):
        byteStrings.append(message[i:i+8])
    return ''.join(chr(int(val, 2)) for val in byteStrings)

# Example Usage
if __name__ == "__main__":
    key = "0001001100110100010101110111100110011011101111001101111111110001"
    message = "Hello World!"
    binary_msg = messageToBinary(message)
    print(f"Original message: {message}")
    print(f"Original message (binary): {binary_msg}")
    
    des = DES(key)

    # Encrypt
    encrypted = des.encrypt(binary_msg)
    print(f"Encrypted (first 64 bits): {encrypted[:64]}")
    
    # Decrypt the ciphertext
    decrypted_bits = des.decrypt(encrypted)
    decrypted_msg = binaryToMessage(decrypted_bits)
    print(f"Decrypted message: {decrypted_msg}\n")
    
    # Create keys (must be 64-bit binary strings)
    key1 = "0101010101010101010101010101010101010101010101010101010101010101"
    key2 = "1010101010101010101010101010101010101010101010101010101010101010"
    key3 = "1100110011001100110011001100110011001100110011001100110011001100"

    # Initialize TripleDES
    tdes = TripleDES(key1, key2, key3)

    # Encrypt a message
    message = "Secure banking transaction"
    binary_msg = messageToBinary(message)
    encrypted = tdes.encrypt(binary_msg)

    # Decrypt
    decrypted_bits = tdes.decrypt(encrypted)
    decrypted_msg = binaryToMessage(decrypted_bits)

    print(f"Original: {message}")
    print(f"Encrypted: {encrypted[:64]}...")  # Show first 64 bits
    print(f"Decrypted: {decrypted_msg}")
    exit()


    # Use 3 different keys (for 3-key 3DES)
    key1 = b'key1____'
    key2 = b'key2____'
    key3 = b'key3____'
    
    # For 2-key 3DES: key3 = key1
    # key3 = key1
    
    tdes = TripleDES(key1, key2, key3)
    
    # Encrypt
    message = "Secure banking transaction"
    print("\nOriginal Message:", message)
    ciphertext = tdes.encrypt(message)
    print("Triple DES Encrypted:", ciphertext.hex())
    
    # Decrypt
    decrypted = tdes.decrypt(ciphertext)
    print("Triple DES Decrypted:", decrypted.decode())
    