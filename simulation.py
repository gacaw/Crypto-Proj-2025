# bank transaction simulator: 

import random
import math

import ecc
import hmacFile
import des 

class Alice:
    
    def __init__(self):
        self.__session_key = -1
        self.__key1 = -1
        self.__key2 = -1 
        self.__key3 = -1
        
    def setSessionKey(self, sessionKey):
        self.__session_key = sessionKey 
        self.__key1 = self.__session_key[0:len(sessionKey)//3]
        self.__key1 = des.messageToBinary(self.__key1)[0:10]
        self.__key2 = self.__session_key[len(sessionKey)//3:2*len(sessionKey)//3]
        self.__key2 = des.messageToBinary(self.__key2)[0:10]
        self.__key3 = self.__session_key[2*len(sessionKey)//3:]
        self.__key3 = des.messageToBinary(self.__key3)[0:10]
        
    def depositMoneyMessage(self, money): 
        message = "d|" + str(money) 
        message = des.messageToBinary(message) 
        return(des.tripleDES(0, message, self.__key1, self.__key2, self.__key3))
    
    def withdrawMoneyMessage(self, money): 
        message = "w|" + str(money) 
        message = des.messageToBinary(message) 
        return(des.tripleDES(0, message, self.__key1, self.__key2, self.__key3))
    
    def balanceMoneyMessage(self): 
        message = "b|" 
        message = des.messageToBinary(message) 
        return(des.tripleDES(0, message, self.__key1, self.__key2, self.__key3))
        
    def decryptBalance(self, message, key1, key2, key3): 
        return 5

class Bank:
    
    def __init__(self, money):
        self.__money = money 
        self.__private_key = -1
        self.__public_key = -1
        self.__session_key = -1
        self.__key1 = -1
        self.__key2 = -1 
        self.__key3 = -1
    
    def setSessionKey(self, sessionKey):
        self.__session_key = sessionKey 
        self.__key1 = self.__session_key[0:len(sessionKey)//3]
        self.__key1 = des.messageToBinary(self.__key1)[0:10]
        self.__key2 = self.__session_key[len(sessionKey)//3:2*len(sessionKey)//3]
        self.__key2 = des.messageToBinary(self.__key2)[0:10]
        self.__key3 = self.__session_key[2*len(sessionKey)//3:]
        self.__key3 = des.messageToBinary(self.__key3)[0:10]
        
    def getMoney(self):
        return self.__money 
    
    def addMoney(self, newMoney): 
        self.__money += newMoney 
        return -2 # marks success. Can never fail at depositing money 
        
    def subMoney(self, newMoney): 
        if(self.__money - newMoney < 0): 
            return None # marks failure due to not enough funds 
        else: 
            self.__money -= newMoney
            return -2 # marks success 
        
    def setKeys(self, private, public): 
        self.__private_key = private 
        self.__public_key = public 
        
    def getPublic(self):
        return self.__public_key
    
    def decryptMessage(self, message): 
        message = des.tripleDES(1, message, self.__key3, self.__key2, self.__key1)
        message = des.binaryToMessage(message) 
        #print("!", message)
        action = message[0] 
        #print(message[2:])
        if(action == 'd'): 
            rc = self.addMoney(int(message[2:]))
            return rc 
        elif(action == 'w'): 
            rc = self.subMoney(int(message[2:]))
            return rc 
        elif(action == 'b'): 
            return self.getMoney() 
        return -1 # marks some weird error 
    
# random string of 10-15 lowercase letters (can't be longer for some reason)
def generateSessionKey():
    str = ""
    for i in range(random.randint(10,15)):
        tempNum = random.randint(1,26) 
        str += chr(ord('`')+tempNum)
    return str

def fasterModularSqrt(y, p):
    # math.sqrt() seems to be stalling quite a bit, so this is necessary 
    # check if a has a square root modulo p with the Legendre Symbol
    if pow(y, (p - 1) // 2, p) != 1:
        return None  # No solution exists

    # Special case for p ≡ 3 (mod 4)
    if p % 4 == 3:
        return pow(y, (p + 1) // 4, p)
    
    # Tonelli–Shanks Algorithm: 
    # find q and s such that p - 1 = q * 2^s with q odd
    s = 0
    q = p - 1
    while q % 2 == 0:
        q //= 2
        s += 1

    # find a quadratic non-residue z
    z = 2
    while pow(z, (p - 1) // 2, p) == 1:
        z += 1

    m = s
    c = pow(z, q, p)
    t = pow(y, q, p)
    r = pow(y, (q + 1) // 2, p)

    # find the least i such that t^(2^i) ≡ 1 (mod p)
    while t != 0 and t != 1:
        t2i = t
        i = 0
        while t2i != 1 and i < m:
            t2i = pow(t2i, 2, p)
            i += 1
        
        b = pow(c, 2 ** (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p

    return r

def sessionKeyGen(bank, hmacFxn, shaFxn): 
    # using a smaller stackoverflow curve since the standard ones are way too large for this code to handle 
    curve = ecc.EllipticCurve(a=int(0xfffffffffffffffffffffffffffffffefffffffffffffffc), b=int(0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1), p=int(0xfffffffffffffffffffffffffffffffeffffffffffffffff))
                                    
    

    # define a generator 
    #xVal = 192779291135662930711103080
    #yVal = math.sqrt(xVal**3 + curve.a * xVal + curve.b) % curve.p
    G = (int(0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012), int(0x07192b95ffc8da78631011ed6b24cdd573f977a11e794811))  
        
    #print("G:", G)
    
    #xVal = 192779291135662930711103080
    #yVal = math.sqrt(xVal**3 + curve.a * xVal + curve.b) % curve.p
    #G = (xVal, yVal)  
    if not curve.is_on_curve(*G):
        raise ValueError("ERROR: Base point is not on the curve.")

    privateKeySize = 100000 # extend this to 1 million when submitting. This is just barely fast enough to test 

    private_key = random.randint(1, privateKeySize) 
    public_key = curve.scalar_multiplication(private_key, G)

    bank.setKeys(private_key, public_key)
    
    
    #print(f"Curve: y^2 = x^3 + {curve.a}x + {curve.b} (mod {curve.p})")
    #print("Base Point:", G)
    #print("Private Key:", private_key)
    #print("Public Key:", public_key)
    
    client_private_key = random.randint(1, privateKeySize) 
    client_public_key = curve.scalar_multiplication(client_private_key, G)
    
    #print("Private Key:", client_private_key)
    #print("Public Key:", client_public_key) 
    
    clientID = random.randint(1, privateKeySize) 
    sessionKey = random.randint(1, privateKeySize) 
    
    # we don't actually have a separate server set up so the rest of this is really just a simulation, but you get the gist: 
    
    # conversion of plaintext to a point on the curve: 
    #pText = "hello" # change to a random string representing the session key 
    pText = generateSessionKey()
    #pText = pText.encode('utf-8') 
    #print("!", pText)
    
    #shared_secret_Alice = curve.scalar_multiplication(client_private_key, public_key) 
    #shared_secret_Alice_tag = hmac.sha1(str(shared_secret_Alice[0]).encode('utf-8'))[:5]
    shared_secret_Alice = curve.scalar_multiplication(client_private_key, public_key) 
    key = str(shared_secret_Alice[0]).encode('utf-8')
    shared_secret_Alice_tag = hmacFxn(key, pText.encode('utf-8'), shaFxn).decode("utf-8")[:5]
    
    
    pTextNew = pText + "|" + shared_secret_Alice_tag
    pText = pTextNew # for some reason the terminal complained when I did this all in one line 
    
    #print("!!", pText)
    
    
    #print(hmac.sha1(pText))
    #hash_x = int(hmac.sha1(pText), 16) % curve.p 
    hash_x = int.from_bytes(pText.encode('utf-8'), 'big')
    
    #print("Original pText:", hash_x) 
    
    y_sqr = (hash_x**3 + curve.a * hash_x + curve.b) % curve.p 
    y = fasterModularSqrt(y_sqr,curve.p)
    #print(y)
    increment_counter = 0
    while(y == None or not(curve.is_on_curve(hash_x, int(y)))):
        hash_x += 1 
        increment_counter += 1 
        y_sqr = (hash_x**3 + curve.a * hash_x + curve.b) % curve.p 
        y = fasterModularSqrt(y_sqr,curve.p)
        if(y == None):
            continue
        else:
            y = int(y)
    
    #print("Original pText Point:", (hash_x, y))
    
    # ctext is of the form {kG,Pm +kPb}
    
    k = random.randint(1, 10000) # not really sure how large this should be. This should be fine though 
    
    cText0, cText1 = (curve.scalar_multiplication(k, G), curve.point_addition((hash_x, y), curve.scalar_multiplication(k, public_key))) # this SHOULD work 
    
    #print(cText0, cText1) 
    
    nBkG0, nBkG1 = curve.scalar_multiplication(private_key, cText0) #* -1 
    nBkG1 *= -1
    #print(nBkG0, nBkG1)
    #print(type(nBkG0), type(cText1[0]))
    lhs, rhs = cText1 
    lhs = int(lhs)
    rhs = int(rhs)
    pTextPoint = curve.point_addition((lhs, rhs), (nBkG0, nBkG1)) 
    #print("new point:", pTextPoint) 
    
    #symmetric_key = pTextPoint[0].decode('utf-8')
    #plaintext = bytes([c ^ symmetric_key[i % len(symmetric_key)] for i, c in enumerate(cText1)])
    
    newHashX = pTextPoint[0]
    newHashX -= increment_counter 
    byte_length = (newHashX.bit_length() + 7) // 8  # Calculate the byte length
    byte_sequence = newHashX.to_bytes(byte_length, 'big')  # Convert back to bytes
    #print(byte_sequence)
    pText = byte_sequence.decode('utf-8')

    #print(pText) # session key restored 
    
    parts = pText.split("|")
    sessionKey = parts[0]
    mac_identifier = parts[1]
    
    shared_secret_Bob = curve.scalar_multiplication(private_key, client_public_key) 
    key = str(shared_secret_Bob[0]).encode('utf-8')
    shared_secret_Bob_tag = hmacFxn(key, sessionKey.encode('utf-8'), shaFxn).decode("utf-8")[:5] 
    #hmac.sha1(str(shared_secret_Bob[0]).encode('utf-8'))[:5]
    
    #print(mac_identifier, shared_secret_Bob_tag)
    
    if(mac_identifier != shared_secret_Bob_tag):
        print("ERROR: MAC tags do not match. Cannot authenticate sender")
    
    
    # Now Bob has the Session Key and has used the MAC to authenticate Alice --------------------------------------------------------------------------------------------------------- 
    
    
    return sessionKey
    
    

if __name__ == "__main__": 
    # for some reason something is printing even before main(). Idk what's going on there. It's probably fine. 
    
    myHmac = hmacFile.Hmac() 
    
    bank = Bank(0) 
    alice = Alice()
    
    
    # Uncomment when done. This just takes some time. 
    print(type(myHmac))
    text = b"hello world"
    print(myHmac.sha1(text))
    # generates a session key five times and concatenates to make up for the weird ECC bug that only allows for a maximum of 15 char long session keys 
    """
    sessionKeyArr = []
    for i in range(5):
        sessionKey = sessionKeyGen(bank, myHmac.hmac, myHmac.sha1) # doesn't work because ECC is a nightmare and the curves need to be massive for the plaintext to point conversion to work, but also have to be small enough to not automatically become floating point numbers and lose some precision and I really don't think there is a perfect middle ground and I'm absolutely out of ideas 
        sessionKeyArr.append(sessionKey)
    sessionKey = "".join(sessionKeyArr)    
    """
     
    sessionKey = "zmfubxgxfxqvdmnrwrkmsfclmkizugxjpbjfihtsygoyuzdnugzdyngoshnpznz"
        
    alice.setSessionKey(sessionKey)
    bank.setSessionKey(sessionKey)
    
    #alice.depositMoney(5)
    
    #print(sessionKey)
    
    #print(bank.getPublic())
    
    # This part cannot be run in VSCode because VSCode for some reason does not support input() 
    # Instead use Spyder or an equivalent interface 
    while(1): 
        mode = -1
        amount = -1
        user_input = input("Enter an action (deposit <num>)(withdraw <num>)(balance): ")
        if(user_input[0:8] != "deposit " and user_input[0:9] != "withdraw " and user_input != "balance"):
            print("Please enter a valid action")
            continue 
        if(user_input[0:8] == "deposit "):
            mode = 0
            if(len(user_input) < 9):
                print("Please enter a valid action")
                continue 
            amount = int(user_input[8:])
            
            encStr = alice.depositMoneyMessage(amount) 
            rc = bank.decryptMessage(encStr) 
            if(rc == -1):
                print("An error occurred")
            elif(rc == -2): 
                print("Successfully deposited", amount) 
            else: 
                print("Balance:", rc)
            
            
            
        elif(user_input[0:9] == "withdraw "):
            mode = 1
            if(len(user_input) < 10):
                print("Please enter a valid action")
                continue 
            amount = int(user_input[9:])
            
            encStr = alice.withdrawMoneyMessage(amount) 
            rc = bank.decryptMessage(encStr) 
            if(rc == -1):
                print("An error occurred")
            elif(rc == -2): 
                print("Successfully withdrew", amount) 
            else: 
                print("You do not have sufficient funds in the bank to withdraw:", amount)
        else: 
            mode = 2  # check balance 
            
            encStr = alice.balanceMoneyMessage() 
            rc = bank.decryptMessage(encStr) 
            if(rc == -1):
                print("An error occurred")
            else: 
                print("Balance:", rc)
        #print(amount)