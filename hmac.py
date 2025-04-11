# left rotate a 32-bit integer n by b bits 
def left_rotate(n, b):
    return ((n << b) | (n >> (32 - b))) & 0xFFFFFFFF

def sha1(data):
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
    while (len(data) * 8) % 512 != 448:
        data += b'\x00'

    # append the original message length as a 64-bit big-endian integer
    data += original_bit_len.to_bytes(8, 'big') # they go out of their way to hide the fact that this is necessary, but it again doesn't spit out the right hash without it  

    # process the message in 512-bit chunks
    for i in range(0, len(data), 64):
        chunk = data[i:i+64]
        #print(chunk) 

        # break chunk into 16 32-bit big-endian words 
        w = [int.from_bytes(chunk[j:j+4], 'big') for j in range(0, 64, 4)]
        #print(w)

        # extend the 16 32-bit words into 80 32-bit words
        for j in range(16, 80):
            w.append(left_rotate(w[j-3] ^ w[j-8] ^ w[j-14] ^ w[j-16], 1))

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

            temp = (left_rotate(a, 5) + f + e + k + w[j]) & 0xFFFFFFFF
            e = d
            d = c
            c = left_rotate(b, 30)
            b = a
            a = temp

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



def hmac(key: bytes, message: bytes, hash_function, block_size=64):
    if len(key) > block_size:
        key = hash_function(key)
    if len(key) < block_size:
        key = key.ljust(block_size, b'\x00')
    
    opad = bytes([b ^ 0x5C for b in key])
    ipad = bytes([b ^ 0x36 for b in key])
    inner_hash = hash_function(ipad + message).encode('utf-8')
    return hash_function(opad + inner_hash).encode('utf-8')
    
    
key = b"my key"
text = b"hello world"

print(hmac(key, text, sha1).decode("utf-8"))




