class EllipticCurve:
    # note: uses None type as infinity stand-in 
    
    # define the coefficients for y^2 = x^3 + ax + b (mod p) 
    def __init__(self, a, b, p):
        self.a = a  
        self.b = b  
        self.p = p  

        # check if the curve's discriminant is valid 
        if (4 * a**3 + 27 * b**2) % p == 0:
            raise ValueError("ERROR: Invalid curve. Discriminant is zero.")

    def is_on_curve(self, x, y):
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
            m = (3 * x1**2 + self.a) * pow(2 * y1, -1, self.p) % self.p
        else:  # point addition
            m = (y2 - y1) * pow(x2 - x1, -1, self.p) % self.p

        x3 = (m**2 - x1 - x2) % self.p
        y3 = (m * (x1 - x3) - y1) % self.p

        return (x3, y3)

    def scalar_multiplication(self, k, P):
        result = None  # start at infinity 
        for i in range(k):
            result = curve.point_addition(result, P)
        return result



if __name__ == "__main__":
    
    curve = EllipticCurve(a=2, b=3, p=97)

    # define a base point / generator 
    G = (3, 6)  
    if not curve.is_on_curve(*G):
        raise ValueError("ERROR: Base point is not on the curve.")

    private_key = 10  # change this later to be the output of some other file 
    public_key = curve.scalar_multiplication(private_key, G)

    print(f"Curve: y^2 = x^3 + {curve.a}x + {curve.b} (mod {curve.p})")
    print("Base Point:", G)
    print("Private Key:", private_key)
    print("Public Key:", public_key)

    # scalar mult test
    scalar = 4
    point = curve.scalar_multiplication(scalar, G)
    print(f"{scalar} * G = {point}")
    
    scalar = 2
    point = curve.scalar_multiplication(scalar, G)
    print(f"{scalar} * G = {point}")
    
    print(f"{G} + {G} = {curve.point_addition(G, G)}")
    
    # checking by hand, it looks like this works 
    
    
    
    