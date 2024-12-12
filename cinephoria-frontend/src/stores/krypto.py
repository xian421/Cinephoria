# Parameter
p = 191  # Primzahl
q = 167  # Primzahl
s = 599  # Startwert
l = 100  # Länge der Bitfolge

# Überprüfung der Parameter
def is_prime(num):
    """Prüft, ob eine Zahl eine Primzahl ist."""
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

assert is_prime(p), "p ist keine Primzahl"
assert is_prime(q), "q ist keine Primzahl"

n = p * q
assert s < n, "s muss kleiner als n sein"
assert s % p != 0 and s % q != 0, "s muss teilerfremd zu n sein"

# BBS-Algorithmus
x = (s**2) % n  # Initialer Zustand x_0
bitfolge = []   # Liste für die Pseudozufallsbits

for i in range(l):
    x = (x**2) % n  # x_i = x_{i-1}^2 mod n
    z = x % 2       # Letztes Bit von x_i
    bitfolge.append(z)

# Ausgabe der Bitfolge
print("Pseudozufalls-Bitfolge:")
print("".join(map(str, bitfolge)))
