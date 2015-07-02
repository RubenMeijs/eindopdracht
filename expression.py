import math
import sys
import itertools

def tokenize(string):
    #split a string into mathematical tokens
    #returns a list of numbers, operators, parantheses and commas
    #output will not contain spaces
    
    splitchars = list("+-*/(),")

    # surround any splitchar by spaces
    tokenstring = []
    for c in string:
        if c in splitchars:
            tokenstring.append(' %s ' % c)
        else:
            tokenstring.append(c)
    tokenstring = ''.join(tokenstring)
    #split on spaces - this gives us our tokens
    tokens = tokenstring.split() 
    
    
    ans = []
    for t in tokens:
        if len(ans) > 0 and t == ans[-1] == '*':
            ans[-1] = '**'
        else:
            ans.append(t)
    
    
    
            
    return ans
# check if a string represents a numeric value
def isnumber(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

# check if a string represents an integer value        
def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

class Expression():
    """A mathematical expression, represented as an expression tree
    
    Any concrete subclass of Expression should have these methods:
     - __str__(): return a string representation of the Expression.
     - __eq__(other): tree-equality, check if other represents the same expression tree.
    """

    # operator overloading:
    # this allows us to perform 'arithmetic' with expressions, and obtain another expression
    def __add__(self, other):
        return AddNode(self, other)
    
    def __sub__(self,other):
        return SubNode(self,other)
        
    def __mul__(self,other):
        return MulNode(self,other)
    
    def __truediv__(self,other):
        return DivNode(self,other)
    
    def __pow__(self,other):
        return PowNode(self,other)
    
    def __neg__(self):
        return NegNode(self)
    
    

    # basic Shunting-yard algorithm
    def fromString(self, string):
        
        # split into tokens
        tokens = tokenize(string)
        
        # stack used by the Shunting-Yard algorithm
        stack = []
       
        # output of the algorithm: a list representing the formula in RPN
        # this will contain Constant's and '+'s
        output = []
        
        # list of operators

        oplist = ['+','-', '*', '/','**']
        funclist = ['sin', 'cos','exp']
        funcuitvoer  = { 'sin' : SinNode, 'cos' : CosNode , 'exp': ExpNode}
        # order_op={'+':AddNode.order}
        
        # for i in oplist:
        #     order_op[t] = t.order
        # print(precendence)
        #order_op index 0 is order, index 1 is associativity (0=left, 1=right)
        order_op = {'+':[1,0],'-':[1,0], '*':[2,0], '/':[2,0],'**':[3,1],  '~':[5,1]}
        
        i = 0 
        
        while i< len(tokens):
            # print(tokens[i])
            if isnumber(tokens[i]):
                # numbers go directly to the output
                if isint(tokens[i]):
                    output.append(Constant(int(tokens[i])))
                else:
                    output.append(Constant(float(tokens[i])))
                    
            elif tokens[i] in funclist:
                """ Binnen haakjes moet gezien owrden als de invoer van een functie"""
                stack.append(tokens[i])
                
                    
            elif tokens[i] in oplist:
                
                # print(tokens[i], 'output[-1]=', output[-1])
                
                if tokens[i] == '-' and (
                    tokens[i-1] in oplist + ['('] or len(output)==0):  
                    stack.append('~')    
                     
                else:  
                    while True:
                        if len(stack) == 0 or stack[-1] not in oplist+['~']:
                            break
                        
                        elif stack[-1] == '~':
                            output.append(stack.pop())
                        
                        # Shunting Yard algoritme
                        elif (order_op[tokens[i]][1]==0 and order_op[tokens[i]][0] <= order_op[stack[-1]][0]
                            ) or (order_op[tokens[i]][1]==1 and order_op[tokens[i]][0]<order_op[stack[-1]][0]):
                            
                            output.append(stack.pop())
                        else:
                            break
                        
                    stack.append(tokens[i])
                   
            
                
                
            elif tokens[i] == '(':
                # left parantheses go to the stack
                stack.append(tokens[i])
                
            elif tokens[i] == ')':
                # right paranthesis: pop everything upto the last left paranthesis to the output
                while not stack[-1] == '(':
                    output.append(stack.pop())
                
                # pop the left paranthesis from the stack (but not to the output)
                stack.pop()
                if len(stack)> 0 and stack[-1] in funclist:
                    output.append(stack.pop())
                
            else:
                output.append(Variable(tokens[i]))
            
            i += 1
        
        # pop any tokens still on the stack to the output
        while len(stack) > 0:
            output.append(stack.pop())    
        # output is the variable we use to store the RPN representation of an expression
        self.output =output
        # convert RPN to an actual expression tree
        for t in output:
            if t in oplist :
                # let eval and operator overloading take care of figuring out what to do
                y = stack.pop()
                x = stack.pop()
                stack.append(eval('x %s y' % t))
            elif t in funclist:
                x = stack.pop()
                Node = funcuitvoer[t]
                stack.append(Node(x))
            elif t =='~':
                y = stack.pop()
                stack.append(NegNode(y))
            # elif t in neglist and stack[-1] in oplist:
                    
            else:
                
                # a constant, push it to the stack
                stack.append(t)
            
                
        # the resulting expression tree is what's left on the stack
        return stack[0]



# Storing constant values  
class Constant(Expression):
    """Represents a constant value"""
    def __init__(self, value):
        self.value = value
        self.precendence =10
        self.op_symbol = "COnstant"
    
    # Overload of equality sign   
    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return False
    
    # Overload of tostring   
    def __str__(self):
        return str(self.value)
        
    # allow conversion to int
    def __int__(self):
        return int(self.value)
    
    # allow conversion to float   
    def __float__(self):
        return float(self.value)
    
    # if evaluation is called, the constant is returned   
    def evaluate(self,variabelen={}):
        return self
    
    # returns the value without casting a specific type    
    def constantvalue(self):
        return self.value
    
    def numIntegrate(self,variabele,interval):
        return (self.value *(interval[1] -interval[0]))
    
    # waarde teruggeven bij differentiatie
    # Als leaf is aangeroepen, dan moet de afgeleide van een niet binary worden
    # bepaald. Dan moet direct de afgeleide worden gegeven
    def dif(self,leaf=True):
        if leaf:
            return Constant(0)
        else:
            return self    
            
            
        
        
#hier defineren we de variabelen        
class Variable(Expression):
    
    #initialisatie
    def __init__(self,teken):
        self.teken = teken
        self.precendence = 6
    
    #overloaden van de tostring functie
    def __str__(self):
        return str(self.teken)
    
    #overlaoden van de equals functie
    def __eq__(self,other):
        if isinstance(other, Variable):
            return self.teken == other.teken
        else:
            return False
            
    #evaluate geeft een constante waarde als x is gesubsitueerd, anders de (ongesubstitueerde) variabele zelf      
    def evaluate(self,variabelen ={}):
        if self.teken in variabelen:
            return Constant(variabelen[self.teken])
        else:
            return self
    
    # waarde teruggeven bij differentiatie
    # Als leaf is aangeroepen, dan moet de afgeleide van een niet binary worden
    # bepaald. Dan moet direct de afgeleide worden gegeven
    def dif(self, leaf=True):
        if leaf:
            return Constant(1)
        else:
            return self
            
class NegNode(Expression):
    
    def __init__(self, expressie):
        self.expressie = expressie
        self.op_symbol = '~'
        self.precendence = 2
      


    def __str__(self):
        if self.expressie.precendence < self.precendence:
            return "- (%s)" % (self.expressie)
        else:
            return "- %s" % (self.expressie)

    def evaluate(self,variabelen={}):
        getal = self.expressie.evaluate(variabelen)
        if isinstance(getal,Constant):
            return Constant(eval("%s %s %s" % (Constant(-1),'*',getal)))
        else:
            return self
    
       
        
        # #bepaal de waarden van lhs en de rhs, neem daarin de ingevulde variable waarden mee
        # getal1 = self.expressie.evaluate(variabelen)
        # print(getal1)

        # #Als een van de twee géén constante is, dan is 1 van de twee ofwel een variabele, ofwel
        # #een compound expressie met een variabele er in. Dit kan dan niet als getal geevalueerd worden
        # if not isinstance(getal1,Constant):
        #     return UnairyNode(getal1,self.op_symbol)
        
        # #Wel twee constanten? Voer de operatie uit en maak een nieuwe constante aan
        # else:

        #     return Constant(eval('%s %s' % (self.op_symbol, getal1.constantvalue())))
            

class FunctionNode(Expression):
    
    def __init__(self, invoer ,functie):
        self.functie = functie
        self.invoer = invoer
        self.operatie = self.operatie
        # self.invoer = self.invoer
        # print(type(self.invoer), type(self.functie))
    
    def __str__(self):
        # return  "%s ($s)", self.op_symbol
        return "%s (%s)" % (self.functie,self.invoer)
    
    def evaluate(self,variabelen={}):
        self.invoer = self.invoer.evaluate(variabelen)
        if not isinstance(self.invoer, Constant):
            # return self (self.invoer)
            """dit grapje met er ene variabele vn maken werkt, maar eigenlijk zou je gewoon een sinnode terug willen"""
            return self
            # return Variable(self.functie + '(' + str(self.invoer) + ')')
        else:
            return Constant(self.operatie(self.invoer))
        

class SinNode(FunctionNode):
    
    def __init__(self, invoer):
        self.operatie =  math.sin
        self.precendence = 10
        self.invoer =invoer
        super(SinNode,self).__init__(invoer, 'sin')
    
    def dif(self,leaf=False):
        return CosNode(self.invoer)*self.invoer.dif().evaluate()



class CosNode(FunctionNode):
    
    def __init__(self, invoer):
        self.operatie =  math.cos
        self.precendence = 10
        super(CosNode,self).__init__(invoer, 'cos')

    def dif(self,leaf=False):
        return Constant(-1)*SinNode(self.invoer)*self.invoer.dif().evaluate()    


class ExpNode(FunctionNode):
    
    def __init__(self, invoer):
        self.operatie =  math.exp
        self.precendence = 10
        super(ExpNode,self).__init__(invoer, 'exp')

    def dif(self,leaf=False):
        return ExpNode(self.invoer)*self.invoer.dif().evaluate()   
    


    
    
       
class BinaryNode(Expression):
    
    #A node in the expression tree representing a binary operator.
    # order_op = {'+':[1,True],'-':[1,False], '*':[2,True], '/':[2,False],'**':[3,False],'~':[4,False]}
    """ We moeten een standaard precendence en associatief mee geven """
    #initialisatie van BinaryNode
    """BinaryNode moet ook een precendence krijgen omdat er niet altijd een precendence wordt mee gegeven, niet echt duidelijk wat de default waarde moet zijn. Bij 0 werkt het niet goed..."""
    """ 1 werkt echter ook niet goed met haakjes weg werken. Hier even over nadenken hoe het precies zit. We moeten wss 
     de precendence van alle objecten na lopen en er over nadenken wat de volgorde moet zijn"""
    def __init__(self, lhs, rhs, op_symbol,precendence,associatief):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
        self.precendence = precendence
        self.associatief = associatief
        
        # print(self.precendence , "precendence", op_symbol, self.associatief)
        
    
    #overloarden bij een gelijk teken
    def __eq__(self, other):
        if type(self) == type(other):
            return self.lhs == other.lhs and self.rhs == other.rhs
        else:
            return False
   
    #overloaden van de tostring functie
    def __str__(self):
        uitvoer = ""
        
        zijde = 0 #administreer of we de linker of rechter zijde bekijken (0 = lhs)
        #ga beide kanten langs en ga na of deze kant haakjes nodig heeft
        
        for side in [self.lhs, self.rhs]:
            
           
            # is het een binarynode? bepaal de operatie orde een laag naar beneden en de huidige operatieorde
            # bepaal ook of de huidige operatie associatief is
            if True:
                # print(side,"zijde")
                order_lower = side.precendence
                order_this = self.precendence
                this_ass =  self.associatief
                
                
                #indien ofwel orde 1 laag dieper minder groot is dan de huidige, dan zijn haakjes nodig
                #haakjes zijn ook nodig als de huidige operatie niet associatief is 
                if order_lower < order_this or (not this_ass and order_lower == order_this and zijde ==1):
                    
                    uitvoer = uitvoer + "(%s)" % (str(side))
                    
                else:
                    uitvoer = uitvoer + str(side)
            
            # als de huidige zijde de lhs is, dan moet het operatiesymbool worden toegevoegd    
            if zijde == 0:
                uitvoer = uitvoer + " %s " % (self.op_symbol)
            
            # een optellen om de rhs aan te duiden
            zijde = zijde + 1
            
        return uitvoer

    #Evaluatie functie
    def evaluate(self, variabelen={}):
        
        #bepaal de waarden van lhs en de rhs, neem daarin de ingevulde variable waarden mee
        getal1 = self.lhs.evaluate(variabelen)
        getal2 = self.rhs.evaluate(variabelen)
        this_symbol = self.op_symbol
        this_order = self.precendence

        #Controleren op en verwijderen van nullen in verschillende vormen, en 
        #gevallen iets * 1 -> iets
        welke = 1

        for getal in [getal1, getal2]:
           #print("getal1",getal1,"getal2",getal2,"getal",getal)
            #Verwijderen van nullen
            if getal == Constant(0):
                if this_order==1:
                    return eval("getal" + str(welke%2 + 1))
                elif this_symbol == '*':
                    return Constant(0)
                elif this_symbol == '/':
                    if welke == 1:
                        return Constant(0)
                elif this_symbol == '**':
                    if welke == 1:
                        return Constant(0)
                    else:
                        return Constant(1)
            
            #verwijderen van enen
            elif getal == Constant(1):
                if this_symbol == '*':
                    print(getal)
                    print(eval("getal" + str(welke%2 + 1)))
                    return eval("getal" + str(welke%2 + 1))
                elif this_symbol == '/':
                    if welke == 2:
                        return getal1
                elif this_symbol == '**':
                    if welke == 1:
                        return Constant(1)
                    else:
                        return getal1
            
            #volgende zijde
            welke = welke + 1

        #Als een van de twee géén constante is, dan is 1 van de twee ofwel een variabele, ofwel
        #een compound expressie met een variabele er in. Dit kan dan niet als getal geevalueerd worden
        if not isinstance(getal1,Constant):
            return BinaryNode(getal1,getal2,this_symbol,self.precendence,self.associatief)
        elif not isinstance(getal2,Constant):
            return BinaryNode(getal1,getal2,this_symbol,self.precendence,self.associatief)
            
        #Wel twee constanten? Voer de operatie uit en maak een nieuwe constante aan
        else:
            return Constant(eval('%s %s %s' % (getal1.constantvalue(), self.op_symbol, getal2.constantvalue())))
        
        #Differentiatie
    def dif(self, leaf=False):
        
        order_this = self.precendence
        
        #Kettingregel
        if (self.op_symbol == '**' and not (isinstance(self.lhs,Constant) or isinstance(self.lhs,Variable))):
            macht = BinaryNode(self.lhs,Constant(self.rhs.constantvalue() - 1),'**',self.precendence,self.associatief)
            product = BinaryNode(self.rhs,macht,'*', self.precendence,self.associatief)
            left = self.lhs.dif()
            toreturn = BinaryNode(product,left,'*', self.precendence,self.associatief)
            
        #Productregel
        elif (self.op_symbol == '*' and not (isinstance(self.lhs,Constant) or isinstance(self.rhs,Constant))):
            afgeleide1 = self.lhs.dif(True)
            afgeleide2 = self.rhs.dif(True)
            product1 = BinaryNode(afgeleide1,self.rhs,'*', self.precendence,self.associatief)
            product2 = BinaryNode(self.lhs,afgeleide2,'*', self.precendence,self.associatief)
            toreturn = BinaryNode(product1,product2,'+', self.precendence,self.associatief)
            
        #Geen kettingregel of productregel
        else:
            left = self.lhs.dif(False)
            right = self.rhs.dif(False)
            order_this = self.precendence
            toreturn = False   

        #print(self)

        # Nu volgt het afleiden van simpele polynomiale expressies
        # Voor de lhs geldt:
        if type(toreturn) == bool:
            if isinstance(left,Constant):
                if order_this == 1:
                    left = Constant(0)
                elif order_this == 2 and isinstance(right,Constant): 
                    toreturn = Constant(0)
                #elif right is variabele of binarynode, dan niet veranderen    
                elif order_this == 3:
                    #we staan geen 2^x toe op dit moment, dus is het een getal
                    toreturn = Constant(0) 
            elif isinstance(left,Variable):
                if order_this == 1 or order_this == 2:
                    #we staan nog geen productregel toe, dus rechts is een constante
                    left = Constant(1)
                else: #orderthis == 3
                    macht = BinaryNode(left,Constant(right.constantvalue() - 1),'**', self.precendence,self.associatief)
                    toreturn = BinaryNode(right,macht,'*', self.precendence,self.associatief)

        # Voor de rhs geldt:
        if type(toreturn) == bool:
            if isinstance(right,Constant):
                if order_this == 1:
                    right = Constant(0)
                #elif order_this == 3 of 2: dit is al gereturned of hoeft niet veranderd
            elif isinstance(right,Variable):
                if order_this == 1 or order_this == 2:
                    right = Constant(1)
                #else: #orderthis == 3 machtfunctie zijn nog niet toegestaan
        
        # Indien de toreturn niet al is gedefinieed
        if type(toreturn) == bool:
            toreturn = BinaryNode(left,right,self.op_symbol, self.precendence,self.associatief)
        # Eindresultaat teruggeven
        return toreturn
        
        
        
        

    
    #Numerieke integratie
    def numIntegrate(self,variables,intervals):
        if isinstance(variables,str):
            steps_per_unit = 1000
            steps1 = (intervals[1]-intervals[0])*steps_per_unit
            begin1 = intervals[0]
            eind1 = intervals[1]
            ans = 0
            
            for i in range(0,steps1):
                x = [begin1+(i*(eind1-begin1))/steps1, begin1+((i+1)*(eind1-begin1))/steps1]
                for xpunt in x:
                    f = self.evaluate({variables[0]:xpunt})
                    ans += (1/2)*eval('%s' % f)/steps_per_unit
        
        elif len(variables)==2:
            steps_per_unit = 100
            
            steps1 = (intervals[0][1]-intervals[0][0])*steps_per_unit
            begin1 = intervals[0][0]
            eind1 = intervals[0][1]
            
            steps2 = (intervals[1][1]-intervals[1][0])*steps_per_unit
            begin2 = intervals[1][0]
            eind2 = intervals[1][1]
            
            ans = 0
            for i in range(0,steps1):
                for j in range(0,steps2):
                    x = [begin1+(i*(eind1-begin1))/steps1, begin1+((i+1)*(eind1-begin1))/steps1]
                    y = [begin2+(j*(eind2-begin2))/steps2, begin2+((j+1)*(eind2-begin2))/steps2]
                    for xpunt in x:
                        for ypunt in y:
                            f = self.evaluate({variables[0]:xpunt,variables[1]:ypunt})
                            ans += (1/4)*eval('%s' % f)/(steps_per_unit**2)
        
        elif len(variables)==3:
            steps_per_unit = 10
            
            steps1 = (intervals[0][1]-intervals[0][0])*steps_per_unit
            begin1 = intervals[0][0]
            eind1 = intervals[0][1]
            
            steps2 = (intervals[1][1]-intervals[1][0])*steps_per_unit
            begin2 = intervals[1][0]
            eind2 = intervals[1][1]
            
            steps3 = (intervals[2][1]-intervals[2][0])*steps_per_unit
            begin3 = intervals[2][0]
            eind3 = intervals[2][1]
            
            ans = 0
            for i in range(0,steps1):
                for j in range(0,steps2):
                    for k in range(0,steps3):
                        x = [begin1+(i*(eind1-begin1))/steps1, begin1+((i+1)*(eind1-begin1))/steps1]
                        y = [begin2+(j*(eind2-begin2))/steps2, begin2+((j+1)*(eind2-begin2))/steps2]
                        z = [begin3+(k*(eind3-begin3))/steps3, begin3+((k+1)*(eind3-begin3))/steps3]
                        for xpunt in x:
                            for ypunt in y:
                                for zpunt in z:
                                    f = self.evaluate({variables[0]:xpunt,variables[1]:ypunt,variables[2]:zpunt})
                                    ans += (1/8)*eval('%s' % f)/(steps_per_unit**3)
        
        return round(ans,3)
    
    #Nulpunt vinden op gespecificeerd interval
    def findRoot(self,expression,variable,interval):
        if expression.evaluate({variable:interval[0]}).constantvalue()<expression.evaluate({variable:interval[1]}).constantvalue():
            a = interval[0]
            b = interval[1]
        else:
            a = interval[1]
            b = interval[0]
        
        m = (a+b)/2
        delta = 0.0001
        
        if abs(b-a)<=delta:
            return m
        
        if expression.evaluate({variable:m}).constantvalue()<=0:
            newinterval = [m,b]
            return self.findRoot(expression,variable,newinterval)
        else:
            newinterval = [a,m]
            return self.findRoot(expression,variable,newinterval)
    
    #Numeriek vergelijkingen oplossen
    def numSolver(self,left,right,variable,interval):
        epsilon = 0.01
        solutions = []
        nulexpression = BinaryNode(left, right, '-')
        i = interval[0]
        while i+epsilon<=interval[1]:
            if (nulexpression.evaluate({variable:i}).constantvalue()<=0 and nulexpression.evaluate({variable:i+epsilon}).constantvalue()>=0) or (nulexpression.evaluate({variable:i}).constantvalue()>=0 and nulexpression.evaluate({variable:i+epsilon}).constantvalue()<=0):
                nul = self.findRoot(nulexpression,variable,[i,i+epsilon])
                solutions.append(nul)
            i += epsilon
        return solutions


#overloaden van operaties        
class AddNode(BinaryNode):
    """Represents the addition operator"""
    
    def __init__(self, lhs, rhs):
        self.precendence = 1
        self.associatief = True
        super(AddNode, self).__init__(lhs, rhs, '+',self.precendence,self.associatief)

class SubNode(BinaryNode):
    """Represents the subtraction operator"""

    def __init__(self, lhs, rhs):
        self.precendence = 1
        self.associatief = False
        super(SubNode, self).__init__(lhs, rhs , '-',self.precendence,self.associatief)
        

class DivNode(BinaryNode):
    """Represents the division operator"""

    def __init__(self, lhs, rhs):
        self.precendence = 2
        self.associatief = False
        super(DivNode, self).__init__(lhs, rhs , '/',self.precendence,self.associatief)

class MulNode(BinaryNode):
    """Represents the multiplication operator"""

    def __init__(self, lhs, rhs):
        self.precendence = 2
        self.associatief = True
        super(MulNode, self).__init__(lhs, rhs , '*',self.precendence,self.associatief)

class PowNode(BinaryNode):
    """Represents the power operator"""

    def __init__(self, lhs, rhs):
        self.precendence = 3
        self.associatief = False
        super(PowNode, self).__init__(lhs, rhs , '**',self.precendence,self.associatief)