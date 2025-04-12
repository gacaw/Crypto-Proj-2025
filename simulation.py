# bank transaction simulator: 

import random
import math

import ecc
import hmac

class Bank:
    
    def __init__(self, money):
        self.money = money 
        self.__private_key = -1
        self.__public_key = -1
        
    def getMoney(self):
        return self.money 
    
    def addMoney(self, newMoney): 
        self.money += newMoney 
        
    def subMoney(self, newMoney): 
        self.money -= newMoney 
        
    def setKeys(self, private, public): 
        self.__private_key = private 
        self.__public_key = public 
        
    def getPublic(self):
        return self.__public_key
    

def sessionKeyGen(bank): 
    # using a smaller stackoverflow curve since the standard ones are way too large for this code to handle 
    curve = ecc.EllipticCurve(a=int(0xfffffffffffffffffffffffffffffffefffffffffffffffc), b=int(0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1), p=int(0xfffffffffffffffffffffffffffffffeffffffffffffffff))
                                          
    

    # define a generator 
    #xVal = 192779291135662930711103080
    #yVal = math.sqrt(xVal**3 + curve.a * xVal + curve.b) % curve.p
    G = (int(0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012), int(0x07192b95ffc8da78631011ed6b24cdd573f977a11e794811))  
    
        
    print("G:", G)
    
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
    print("Private Key:", private_key)
    print("Public Key:", public_key)
    
    client_private_key = random.randint(1, privateKeySize) 
    client_public_key = curve.scalar_multiplication(client_private_key, G)
    
    print("Private Key:", client_private_key)
    print("Public Key:", client_public_key) 
    
    clientID = random.randint(1, privateKeySize) 
    sessionKey = random.randint(1, privateKeySize) 
    
    # we don't actually have a separate server set up so the rest of this is really just a simulation, but you get the gist: 
    
    # conversion of plaintext to a point on the curve: 
    pText = "hello"
    pText = pText.encode('utf-8') 
    #print(hmac.sha1(pText))
    hash_x = int(hmac.sha1(pText), 16) % curve.p 
    print(hash_x)    
    
    y_sqr = (hash_x**3 + curve.a * hash_x + curve.b) % curve.p 
    y = math.sqrt(y_sqr)
    #print(y)
    while(not(curve.is_on_curve(hash_x, y))):
        hash_x += 1
        y_sqr = (hash_x**3 + curve.a * hash_x + curve.b) % curve.p 
        y = math.sqrt(y_sqr)
    
    print("Original pText:", (hash_x, y))
    
    # ctext is of the form {kG,Pm +kPb}
    
    k = random.randint(1, 10000) # not really sure how large this should be. This should be fine though 
    
    cText0, cText1 = (curve.scalar_multiplication(k, G), curve.point_addition((hash_x, y), curve.scalar_multiplication(k, public_key))) # this SHOULD work 
    
    print(cText0, cText1) 
    
    nBkG0, nBkG1 = curve.scalar_multiplication(private_key, cText0) #* -1 
    nBkG1 *= -1
    print(nBkG0, nBkG1)
    #print(type(nBkG0), type(cText1[0]))
    pTextPoint = curve.point_addition(cText1, (nBkG0, nBkG1)) 
    print(pTextPoint) 
    
    # We're getting stuck here because the numbers get too big and become floats. 
    # I've tried all sorts of smaller elliptic curves, but I can't find one that works. 
    # So the best bet might be to figure out an alternative way to take the modular multiplicative inverse of a really really big number. 
    

    

if __name__ == "__main__": 
    # for some reason something is printing even before main(). Idk what's going on there. It's probably fine. 
    
    bank = Bank(100) 
    
    sessionKeyGen(bank)
    
    #print(bank.getPublic())