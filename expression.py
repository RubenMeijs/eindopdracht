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
    
    
    sub_ans = []
    for t in tokens:
        if len(sub_ans) > 0 and t == sub_ans[-1] == '*':
           sub_ans[-1] = '**'
        else:
            sub_ans.append(t)
    
    ans = [sub_ans[0]]
    i=1
    
    
    while i<len(sub_ans):
        
        if (sub_ans[i] == '-' and sub_ans[i-1] in splitchars):
            
            if sub_ans[i-1] == '+':
                ans.pop()
                ans.append('-')
                i+=1
                
                
            elif sub_ans[i-1]  == '-':
                ans.pop()
                ans.append('+')
                i += 1
            
            elif sub_ans[i-1] == ('*' or '/'):
                ans.append( '-1')
                ans.append( '*')
                i+= 1
                
            else:
                ans.append('-' + sub_ans[i+1])
                i += 2
             
            
        else:
            ans.append(sub_ans[i])
            i+=1
            
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
        #order_op index 0 is order, index 1 is associativity (0=left, 1=right)
        order_op = {'+':[1,0],'-':[1,0], '*':[2,0], '/':[2,0],'**':[3,1], '%':[4,1]}
        for token in tokens:
            
            if isnumber(token):
                # numbers go directly to the output
                if isint(token):
                    output.append(Constant(int(token)))
                else:
                    output.append(Constant(float(token)))
                    
            elif token in oplist:
                
                # pop operators from the stack to the output until the top is no longer an operator
                while True:
                    
                    if len(stack) == 0 or stack[-1] not in oplist:
                        break
                    
                    # Shunting Yard algoritme
                    elif (order_op[token][1]==0 and order_op[token][0] <= order_op[stack[-1]][0]
                        ) or (order_op[token][1]==1 and order_op[token][0]<order_op[stack[-1]][0]):
                        
                        output.append(stack.pop())
                    else:
                        break
                    
                stack.append(token)
                
            elif token == '(':
                # left parantheses go to the stack
                stack.append(token)
                
            elif token == ')':
                # right paranthesis: pop everything upto the last left paranthesis to the output
                while not stack[-1] == '(':
                    output.append(stack.pop())
                
                # pop the left paranthesis from the stack (but not to the output)
                stack.pop()

            else:
                output.append(Variable(token))

        # pop any tokens still on the stack to the output
        while len(stack) > 0:
            output.append(stack.pop())
        
        # output is the variable we use to store the RPN representation of an expression
        self.output = output

        # convert RPN to an actual expression tree
        for t in output:
            if t in oplist:
                # let eval and operator overloading take care of figuring out what to do
                y = stack.pop()
                x = stack.pop()
                stack.append(eval('x %s y' % t))
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
    def evaluate(self,variabelen):
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
    def evaluate(self,variabelen):
        if self.teken in variabelen:
            return Constant(variabelen[self.teken])
        else:
            return self

        
class BinaryNode(Expression):
    
    #A node in the expression tree representing a binary operator.
    order_op = {'+':[1,True],'-':[1,False], '*':[2,True], '/':[2,False],'**':[3,False]}

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

            return Constant(eval('%s %s %s' % (getal1.constantvalue(), self.op_symbol, getal2.constantvalue())))

    
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
        super(AddNode, self).__init__(lhs, rhs, '+')

class SubNode(BinaryNode):
    """Represents the subtraction operator"""
    def __init__(self, lhs, rhs):
        super(SubNode, self).__init__(lhs, rhs , '-')

class DivNode(BinaryNode):
    """Represents the division operator"""
    def __init__(self, lhs, rhs):
        super(DivNode, self).__init__(lhs, rhs , '/')

class MulNode(BinaryNode):
    """Represents the multiplication operator"""
    def __init__(self, lhs, rhs):
        super(MulNode, self).__init__(lhs, rhs , '*')

class PowNode(BinaryNode):
    """Represents the power operator"""
    def __init__(self, lhs, rhs):
        super(PowNode, self).__init__(lhs, rhs , '**')