from expression import *

exp = Expression()

#b=a.fromString("(5+((1+s)*4))-3")
#b=a.fromString("(5+((1+2)+4))-3") werkt
#b=a.fromString("(5-((1+2)+4))-3")
#b=a.fromString("((1/2)-(3/4))/(5*6)") werkt
#b=a.fromString("12 * 13") werkt
#s = Variable('s')

n = Constant(0)
a = Constant(1)
b = Constant(2)
c = Constant(3)
d = Constant(4)
x = Variable('x')
z = Variable('z')
y = Variable('y')

#e = c * (a + x ** b) ** b * (n + b * x ** a) + c * b * x ** a + n 
#e = (a + x**b) ** c + c * x ** b + d * d
#e = b * b * b * b ** b
#e = c * x ** d + a * x ** c + b * x ** b + d * x ** a
#e = a**x**a**x - (a - a) - (a - b) + ((x * a)/b) - a * (a-b)

f = (b*x+a)*(x+a)+c*x**d -((a-x**d)**d)*x
#f = (x + a) * (x**b) + 
print(f.dif())
print(f.dif().evaluate())

#print(e.evaluate())

#print(c.evaluate({'x':3,'y':1}))

