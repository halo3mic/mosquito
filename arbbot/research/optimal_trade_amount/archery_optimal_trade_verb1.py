
# o is MTA
# i is mUSD

Bo = 133.96 * 10**3  # Balance of asset o
Bi = 5.9 * 10**6  # Balance of asset i
Wo = 0.05  # Weight of asset o
Wi = 0.95  # Weight of asset i
SPio1 = (Bi*Wo)/(Bo*Wi) # Current spot price (asset i over asset o)
SPio2 = 2.32 # Target spot price (asset i over asset o)
Ai = Bi * ((SPio2 / SPio1)**(Wo/(Wo+Wi))-1)

Ao = lambda x: Bo * (1-(Bi/(Bi+x))**(Wi/Wo))

print(Ai)
print(Ao(Ai))