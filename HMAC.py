class Hmac:
    def __init__(self):
        self.block_size = 64  # SHA-1 block size

    # left rotate a 32-bit integer n by b bits 
    def left_rotate(self, n, b):
        """Left rotate a 32-bit integer n by b bits"""
        return ((n << b) | (n >> (32 - b))) & 0xFFFFFFFF
    
    def sha1(self, data):
        """
        SHA-1 hash function implementation
        Args:
            data: Input bytes to hash
        Returns:
            Hexadecimal string of the hash
        """
        
        # hash constants 
        h0 = 0x67452301
        h1 = 0xEFCDAB89
        h2 = 0x98BADCFE
        h3 = 0x10325476
        h4 = 0xC3D2E1F0
    
        original_byte_len = len(data)
        original_bit_len = original_byte_len * 8
    
        # append the bit '1' to the message. Not sure why this is a thing, but it genuinely doesn't work without it so whatever 
        data += b'\x80' # this does bit-literal string conversion 
    
        # pad with zeros until message length is congruent to 448 mod 512
        data += b'\x00' * ((56 - (len(data) % 64)) % 64)
    
        # append the original message length as a 64-bit big-endian integer
        data += original_bit_len.to_bytes(8, 'big') # they go out of their way to hide the fact that this is necessary, but it again doesn't spit out the right hash without it  
    
        # process the message in 512-bit chunks
        for i in range(0, len(data), 64):
            chunk = data[i:i+64]
    
            # break chunk into 16 32-bit big-endian words 
            w = [int.from_bytes(chunk[j:j+4], 'big') for j in range(0, 64, 4)]
    
            # extend the 16 32-bit words into 80 32-bit words
            for j in range(16, 80):
                w.append(self.left_rotate(w[j-3] ^ w[j-8] ^ w[j-14] ^ w[j-16], 1))
    
            a = h0
            b = h1
            c = h2 
            d = h3 
            e = h4
            
            for j in range(80):
                if 0 <= j <= 19:
                    f = (b & c) | ((~b) & d)
                    k = 0x5A827999
                elif 20 <= j <= 39:
                    f = b ^ c ^ d
                    k = 0x6ED9EBA1
                elif 40 <= j <= 59:
                    f = (b & c) | (b & d) | (c & d)
                    k = 0x8F1BBCDC
                elif 60 <= j <= 79:
                    f = b ^ c ^ d
                    k = 0xCA62C1D6
    
                temp = (self.left_rotate(a, 5) + f + e + k + w[j]) & 0xFFFFFFFF
                e = d
                d = c
                c = self.left_rotate(b, 30)
                b = a
                a = temp
    
            # update hash values
            # last part truncates down to 32 bits 
            h0 = (h0 + a) & 0xFFFFFFFF # last part truncates down to 32 bits 
            h1 = (h1 + b) & 0xFFFFFFFF
            h2 = (h2 + c) & 0xFFFFFFFF
            h3 = (h3 + d) & 0xFFFFFFFF
            h4 = (h4 + e) & 0xFFFFFFFF
    
        # convert back to a normal string 
        answer = ""
        answer += str(hex(h0))[2:] # converts to hex, discards the '0x' part, and converts to a string 
        answer += str(hex(h1))[2:]
        answer += str(hex(h2))[2:]
        answer += str(hex(h3))[2:]
        answer += str(hex(h4))[2:]
        return answer 
    
    def hmac(self, key: bytes, message: bytes, hash_function):
        """
        HMAC implementation using SHA-1
        Args:
            key: Secret key (bytes)
            message: Message to authenticate (bytes)
        Returns:
            HMAC as hexadecimal string
        """
        # Key processing
        if len(key) > self.block_size:
            key = hash_function(key)
        if len(key) < self.block_size:
            key = key.ljust(self.block_size, b'\x00')
        
        # Create pads
        opad = bytes([b ^ 0x5C for b in key])
        ipad = bytes([b ^ 0x36 for b in key])

        # Inner and outer hash
        inner_hash = hash_function(ipad + message).encode('utf-8')
        return hash_function(opad + inner_hash).encode('utf-8')
        
# Test cases
if __name__ == "__main__":
    hmac = Hmac()
    
    # Test HMAC-SHA1
    key = b"my key"
    message = b"hello world"
    print(f"HMAC-SHA1: {hmac.hmac(key, message, hmac.sha1)}")
    
    # Test SHA-1 against known values
    test_vectors = [
        (b"", "da39a3ee5e6b4b0d3255bfef95601890afd80709"),
        (b"hello world", "2aae6c35c94fcfb415dbe95f408b9ce91ee846ed"),
        (b"The quick brown fox jumps over the lazy dog", "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"),
        (b"Bank transaction 12345", "4dfb1fa62578bf395194330577088586b030667e")
    ]
    
    print("\nSHA-1 Test Vectors:")
    for data, expected in test_vectors:
        result = hmac.sha1(data)
        print(f"Input: {data}")
        print(f"Expected: {expected}")
        print(f"Result:   {result}")
        print(f"Status:   {'PASS' if result == expected else 'FAIL'}\n")