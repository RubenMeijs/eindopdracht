import math
import sys

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
        funclist = ['sin']
        order_op={'+':AddNode.order}
        
        # for i in oplist:
        #     order_op[t] = t.order
        # print(precendence)
        #order_op index 0 is order, index 1 is associativity (0=left, 1=right)
        order_op = {'+':[1,0],'-':[1,0], '*':[2,0], '/':[2,0],'**':[3,1],  '~':[2,0]}
        
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
                output.append(tokens[i+1])
                output.append(tokens[i])
                i += 1
                    
            elif tokens[i] in oplist:
                
                # print(tokens[i], 'output[-1]=', output[-1])
                
                if tokens[i] == '-' and (
                    tokens[i-1] in oplist + ['('] or len(output)==0):  
                    stack.append('~')    
                        
                    # # print(True, '-',len(output))
                    # #hier controleer ik of het minnetje niet de eerste invoer is, want dan weten we zeker dat het een negatie is
                    # if len(stack)>0:
                    #     if tokens[i-1] in oplist:
                    #         stack.append('~')
                    #     elif tokens[i-1] == '(':
                    #         stack.append('~')
                    #         ### negatief unairy
                    #     #anders is het dus gewoon een normale invoer en moet je dus gewoon ene minnetje appenden
                    #     # om een of andere reden moet ik hier wel de stack poppen maar waarom weet ik niet meer...
                    #     else:
                    #         stack.append(tokens[i])
                    # elif len(output) ==0:
                    #     stack.append('~')
                    # else:
                    #     stack.append(tokens[i])
                # pop operators from the stack to the output until the top is no longer an operator
                else:    
                    while True:
                        
                        if len(stack) == 0 or stack[-1] not in oplist:
                            break
                        
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

            else:
                output.append(Variable(tokens[i]))
            
            i += 1
        
        # pop any tokens still on the stack to the output
        while len(stack) > 0:
            output.append(stack.pop())
        
        # output is the variable we use to store the RPN representation of an expression
        # convert RPN to an actual expression tree
        for t in output:
            if t in oplist :
                # let eval and operator overloading take care of figuring out what to do
                y = stack.pop()
                x = stack.pop()
                stack.append(eval('x %s y' % t))
            elif t in funclist:
                x = stack.pop()
                stack.append('%s(x)' %t) 
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
        
        
#hier defineren we de variabelen        
class Variable(Expression):
    
    #initialisatie
    def __init__(self,teken):
        self.teken = teken
    
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
            
class NegNode(Expression):
    
    def __init__(self, expressie):
        self.expressie = expressie

    def __str__(self):
        rstring = str(self.expressie)
        return "- %s" % (rstring)

    def evaluate(self,variabelen={}):
        print(self.expressie,type(self.expressie))
        return eval("%s %s %s" % (Constant(-1),'*',self.expressie.evaluate(variabelen)))
            
        
        
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
    
    def __init__(self, invoer,functie):
        self.functie = functie
        self.invoer = invoer
    
    def __str__(self):
        return "%s ( %s)" % (self.functie,self.invoer)

class SinNode(FunctionNode):
    
    def __init__(self, invoer):
        super(SinNode,self).__init__(self,invoer,math.sin)

    

       
class BinaryNode(Expression):
    
    #A node in the expression tree representing a binary operator.
    order_op = {'+':[1,True],'-':[1,False], '*':[2,True], '/':[2,False],'**':[3,False],'~':[2,True]}

    #initialisatie van BinaryNode
    def __init__(self, lhs, rhs, op_symbol):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
        
        
    
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
            if isinstance(side, BinaryNode): 
                order_lower = self.order_op[side.op_symbol][0]
                order_this = self.order_op[self.op_symbol][0]
                this_ass = self.order_op[self.op_symbol][1]
                
                #indien ofwel orde 1 laag dieper minder groot is dan de huidige, dan zijn haakjes nodig
                #haakjes zijn ook nodig als de huidige operatie niet associatief is 
                if order_lower < order_this or (not this_ass and order_lower <= order_this and zijde == 1):
                    uitvoer = uitvoer + "(%s)" % (str(side))
                else:
                    uitvoer = uitvoer + str(side)
            
            # elif isinstance(side, NegNode):
            #     order_lower = self.order_op[side.op_symbol][0]
            #     order_this = 2
            #     this_ass = True
                
            #     if order_lower < order_this or (not this_ass and order_lower <= order_this and zijde == 1):
            #         uitvoer = uitvoer + "(%s)" % (str(side))
            #     else:
            #         uitvoer = uitvoer + str(side)
                
            
            # geen binarynode? Dan kan tostring worden aangeroepen
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

        #Als een van de twee géén constante is, dan is 1 van de twee ofwel een variabele, ofwel
        #een compound expressie met een variabele er in. Dit kan dan niet als getal geevalueerd worden
        if not isinstance(getal1,Constant):
            return BinaryNode(getal1,getal2,self.op_symbol)
        elif not isinstance(getal2,Constant):
            return BinaryNode(getal1,getal2,self.op_symbol)
            
        #Wel twee constanten? Voer de operatie uit en maak een nieuwe constante aan
        else:
            # print('%s %s %s' % (getal1.constantvalue(), self.op_symbol, getal2.constantvalue()))
            ans = Constant(eval('%s %s %s' % (getal1.constantvalue(), self.op_symbol, getal2.constantvalue())))
            
            return ans
        
    
    
        
        
        

    
    #Numerieke integratie
    def numIntegrate(self,variabele,interval):
        steps_per_unit = 1000
        steps = (interval[1]-interval[0])*steps_per_unit
        begin = interval[0]
        eind = interval[1]
        ans = 0
        
        for i in range(1,steps):
            xa = begin+ (i*(eind -begin))/steps
            xb = begin+ ((i+1)*(eind -begin))/steps
            fa = self.evaluate({variabele: xa })
            fb = self.evaluate({variabele: xb})
            
            Fx = eval('%s %s %s' % (fa,'+',fb))
            
            ans += (1/2)*Fx/steps_per_unit
            
        return round(ans,3)

#overloaden van operaties        
class AddNode(BinaryNode):
    """Represents the addition operator"""
    order = [1, True]


    def __init__(self, lhs, rhs):
        super(AddNode, self).__init__(lhs, rhs, '+')

class SubNode(BinaryNode):
    """Represents the subtraction operator"""
    
    order = [1, False]

    def __init__(self, lhs, rhs):
        super(SubNode, self).__init__(lhs, rhs , '-')
        

class DivNode(BinaryNode):
    """Represents the division operator"""
    order = [2, False]
    

    def __init__(self, lhs, rhs):
        super(DivNode, self).__init__(lhs, rhs , '/')

class MulNode(BinaryNode):
    """Represents the multiplication operator"""
    order = [2, True]

    def __init__(self, lhs, rhs):
        super(MulNode, self).__init__(lhs, rhs , '*')

class PowNode(BinaryNode):
    """Represents the power operator"""
    order = [3, False]

    def __init__(self, lhs, rhs):
        super(PowNode, self).__init__(lhs, rhs , '**')
        


        


        

     