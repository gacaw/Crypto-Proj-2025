class EllipticCurve:
    INFINITY = None  # Clearer than (0, 0)
    
    # define the coefficients for y^2 = x^3 + ax + b (mod p) 
    def __init__(self, a, b, p):
        self.a = a  
        self.b = b  
        self.p = p  

        # check if the curve's discriminant is valid 
        if (4 * a**3 + 27 * b**2) % p == 0:
            raise ValueError("ERROR: Invalid curve. Discriminant is zero.")
        
    def is_on_curve(self, point):
        if point == self.INFINITY:
            return True
        
        x, y = point
        return (y**2 - x**3 - self.a * x - self.b) % self.p == 0
    
    def point_addition(self, P, Q):
        if P is None:  # infinity
            return Q
        if Q is None:  # infinity
            return P

        x1, y1 = P
        x2, y2 = Q

        if x1 == x2 and y1 == -y2 % self.p:  
            return None # infinity 

        if P == Q:  # point doubling
            m = (3 * x1**2 + self.a) * (pow(2 * y1, -1, self.p)) % self.p
        else:  # point addition
            m = (y2 - y1) * (pow(x2 - x1, -1, self.p)) % self.p

        x3 = (m**2 - x1 - x2) % self.p
        y3 = (m * (x1 - x3) - y1) % self.p

        return (x3, y3)
    
    # def scalar_multiplication(self, k, P):
    #     result = None  # start at infinity 
    #     for i in range(k):
    #         result = self.point_addition(result, P)
    #     return result

    def scalar_multiplication(self, k, P):
        if k == 0:
            return self.INFINITY
            
        # Handle negative k by negating the point
        if k < 0:
            return self.scalar_multiplication(-k, (P[0], -P[1] % self.p))
            
        result = None  # start at infinity
        current = P
        
        # Double-and-add algorithm
        while k > 0:
            if k % 2 == 1:
                result = self.point_addition(result, current)
            current = self.point_addition(current, current)  # double the point
            k = k >> 1  # divide by 2
            
        return result
    
if __name__ == "__main__":
    curve = EllipticCurve(a=2, b=3, p=97)  # y² = x³ + 2x + 3 mod 97
    P = (3, 6)  # Base point
    Q = (80, 87)  # Another point on the curve

    print(f"Curve: y^2 = x^3 + {curve.a}x + {curve.b} (mod {curve.p})\n")

    # P + Q
    sum_PQ = curve.point_addition(P, Q)
    print("Point Addition:")
    print(f"P + Q = {sum_PQ}\n")  # Expected: (3, 6) + (80, 87) = (3, 91)
    assert (sum_PQ[0] == 3 and sum_PQ[1] == 91), "Incorrect Point Addition"

    # P + P
    print("Point Doubling:")
    double_P = curve.point_addition(P, P)
    print(f"2P = {double_P}\n")  # Expected: 2*(3,6) = (80, 10)
    assert (double_P[0] == 80 and double_P[1] == 10), "Incorrect Point Doubling"

    # 5 * P
    print("Scaler Multiplication:")
    scalar_mult = curve.scalar_multiplication(4, P)
    print(f"4P = {scalar_mult}\n")  # Expected: 4*(3,6) = (3, 91)
    assert (scalar_mult[0] == 3 and scalar_mult[1] == 91), "Incorrect Scaler Multiplication"

    # P + (-P) = Infinity
    print("Infinity: ")
    P_neg = (3, -6 % 97)  # -P = (3, 91)
    sum_P_negP = curve.point_addition(P, P_neg)
    print(f"P + (-P) = {sum_P_negP}\n")  # Expected: None (Infinity)
    assert (sum_P_negP == None), "Incorrect Infinity"

    print("Test is_on_curve")
    print(f"Is P on curve? {curve.is_on_curve(P)}")  # Expected: True
    assert curve.is_on_curve(P) == True
    print(f"Is (1,1) on curve? {curve.is_on_curve((1, 1))}\n")  # Expected: False
    assert curve.is_on_curve((1, 1)) == False

    # Key Generation
    # Alice
    print("Key Generation Example")
    alice_priv = 9
    alice_pub = curve.scalar_multiplication(alice_priv, P)
    assert (alice_pub[0] == 3 and alice_pub[1] == 91), "Incorrect Alice Public Key"

    # Bob
    bob_priv = 7
    bob_pub = curve.scalar_multiplication(bob_priv, P)
    assert (bob_pub[0] == 80 and bob_pub[1] == 10), "Incorrect Bob Public Key"

    shared_secret_alice = curve.scalar_multiplication(alice_priv, bob_pub)
    shared_secret_bob = curve.scalar_multiplication(bob_priv, alice_pub)

    print(f"Alice's public key: {alice_pub}")
    print(f"Bob's public key: {bob_pub}")
    print(f"Shared secret (Alice): {shared_secret_alice}")
    print(f"Shared secret (Bob): {shared_secret_bob}")
    print(f"Secrets match? {shared_secret_alice == shared_secret_bob}\n")
    assert shared_secret_alice == shared_secret_bob, "Needs to be the same"

    # Test with large scalar
    large_k = 123456789
    print("Testing with large scalar (this would be impossible with naive approach):")
    large_mult = curve.scalar_multiplication(large_k, P)
    print(f"{large_k}P = {large_mult}\n")
    assert curve.is_on_curve(large_mult), "Result should be on curve"

    # Invalid Curve
    print("Invalid Curve Case:")
    try:
        invalid_curve = EllipticCurve(a=0, b=0, p=97)  # Invalid: 4*0³ + 27*0² = 0
    except ValueError as e:
        print(f"Error: {e}")  # Expected: "Invalid curve discriminant."