import math

# split a string into mathematical tokens
# returns a list of numbers, operators, parantheses and commas
# output will not contain spaces


def tokenize(string):
    splitchars = list("+-*/(),%")
    
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
    
    
    #special casing for **:
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
    """A mathematical expression, represented as an expression tree"""
    
    """
    Any concrete subclass of Expression should have these methods:
     - __str__(): return a string representation of the Expression.
     - __eq__(other): tree-equality, check if other represents the same expression tree.
    """
   
    # TODO: when adding new methods that should be supported by all subclasses, add them to this list
    
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
    
    def __mod__(self,other):
        return ModNode(self,other)
    # Done: other overloads, such as __sub__, __mul__, etc.
    
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
        oplist = ['+','-', '*', '/','**','%']
        #order_op index 0 is order, index 1 is associativity (0=left, 1=right)
        order_op = {'+':[1,0],'-':[1,0], '*':[2,0], '/':[2,0],'**':[3,1], '%':[4,1]}
        for token in tokens:
            
            if isnumber(token):
                # numbers go directly to the output
                if isint(token):
                    output.append(Constant(int(token)))
                else:
                    output.append(Constant(float(token)))
                    
            #brain fart komma's worden natuurlijk niet gebruikt om decimalen aan te geven xD        
            # elif token == ',':
                
            #     while stack[-1] != '(' or len(stack)==0:
            #         output.append(stack.pop())
                
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
                
            # TODO: do we need more kinds of tokens?
            
            else:
                output.append(Variable(token))
                
                # volgens mij (ruben) kan valueError weg als we ook variabelen toelaten
                #else:
                #     # unknown token
                #     raise ValueError('Unknown token: %s' % token)
                            
        # pop any tokens still on the stack to the output
        while len(stack) > 0:
            output.append(stack.pop())
        
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
    
    
class Constant(Expression):
    """Represents a constant value"""
    def __init__(self, value):
        self.value = value
    
    #waarom hebben we deze functie nodig?    
    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return False
        
    def __str__(self):
        return str(self.value)
        
    # allow conversion to numerical values
    def __int__(self):
        return int(self.value)
        
    def __float__(self):
        return float(self.value)
        
    def evaluate(self,variabelen):
        return self.value
    
    def numIntegrate(self,variabele,interval):
        return (self.value *(interval[1] -interval[0]))
        
        
class Variable(Expression):
    #hier defineren we de variabelen
    def __init__(self,teken):
        self.teken = teken
    
    def __str__(self):
        return str(self.teken)
    
    
    # waarom hebben we een equal functie nodig?
    def __eq__(self,other):
        if isinstance(other, Variable):
            return self.teken == other.teken
        else:
            return False
            
    def evaluate(self,variabelen):
        if self.teken in variabelen:
            return variabelen[self.teken]
        else:
            return str(self.teken)


        
class BinaryNode(Expression):
    """A node in the expression tree representing a binary operator."""
    # ik heb nog steeds niet echt een idee wat BinaryNode doet
    # wat is bijvoorbeeld dat lhs en rhs? waar haalt hij die informatie vandaan

    order_op = {'+':[1,True],'-':[1,False], '*':[2,True], '/':[2,False],'**':[3,False]}

    
    def __init__(self, lhs, rhs, op_symbol):  #waar roep je deze init aan, waar komen de gegevens vandaag? wat is dit uberhaupt?
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
    
    # TODO: what other properties could you need? Precedence, associativity, identity, etc.
            
    def __eq__(self, other):
        if type(self) == type(other):
            return self.lhs == other.lhs and self.rhs == other.rhs
        else:
            return False
    
        #ik moet opnieuw de order of operation opstellen, dat moet sneller kunnen
        
    def __str__(self):
        uitvoer = ""
        
        zijde = 0
        for side in [self.lhs, self.rhs]:
            if isinstance(side, BinaryNode):
                order_lower = self.order_op[side.op_symbol][0]
                order_this = self.order_op[self.op_symbol][0]
                lower_ass = self.order_op[self.op_symbol][1]
                
                if order_lower < order_this or (not lower_ass and order_lower <= order_this and zijde == 1):
                    uitvoer = uitvoer + "(%s)" % (str(side))
                else:
                    uitvoer = uitvoer + str(side)
            else:
                uitvoer = uitvoer + str(side)
                
            if side is self.lhs:
                uitvoer = uitvoer + " %s " % (self.op_symbol)
            
            zijde = zijde + 1
            
        return uitvoer

        # TODO: do we always need parantheses?
    
    def evaluate(self,variabelen={}):

        
        getal1 = self.lhs.evaluate(variabelen)
        getal2 = self.rhs.evaluate(variabelen)
        
        if type(getal1) ==  str:
            return getal1 + self.op_symbol +str(getal2)
        elif type(getal2) == str:
            return str(getal1) + self.op_symbol + getal2
        else:
            return Constant(eval('%s %s %s' % (getal1, self.op_symbol, getal2)))

   
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

class ModNode(BinaryNode):
    """Represents the modulo operator"""
    def __init__(self, lhs, rhs):
        super(ModNode, self).__init__(lhs, rhs , '%')

# TODO: add more subclasses of Expression to represent operators, variables, functions, etc.


