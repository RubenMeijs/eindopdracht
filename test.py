from expression import *

a = Expression()


b=a.fromString("x**2-5*x+4")
c=a.fromString("0")
#b=a.fromString("(5+((1+2)+4))-3") werkt
#b=a.fromString("(5-((1+2)+4))-3")
#b=a.fromString("((1/2)-(3/4))/(5*6)") werkt
#b=a.fromString("12 * 13") werkt
d=b.numSolver(b,c,'x',[-4,5])

print(d)