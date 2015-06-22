from expression import *

exp = Expression()

#b=a.fromString("(5+((1+s)*4))-3")
#b=a.fromString("(5+((1+2)+4))-3") werkt
#b=a.fromString("(5-((1+2)+4))-3")
#b=a.fromString("((1/2)-(3/4))/(5*6)") werkt
#b=a.fromString("12 * 13") werkt
#s = Variable('s')

a = Constant(1)
b = Constant(2)
x = Variable('x')
z = Variable('z')
y = Variable('y')
c = y**x**y**x - (y - a) - (y - b) + ((x * a)/b) - a * (a-b) + z
#c = a**x**a**x - (a - a) - (a - b) + ((x * a)/b) - a * (a-b)

print(c)

print(c.evaluate({'x':3,'y':1}))

