import math
import sys
import itertools
import copy


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
    #A mathematical expression, represented as an expression tree
    
    #Any concrete subclass of Expression should have these methods:
    # - __str__(): return a string representation of the Expression.
    # - __eq__(other): tree-equality, check if other represents the same expression tree.

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
        funclist = ['sin', 'cos','exp','log','tan']
        funcuitvoer  = { 'sin' : SinNode, 'cos' : CosNode , 'exp': ExpNode, 'log': LogNode, 'tan': TanNode}

        # order_op index 0 is order, index 1 is associativity (0=left, 1=right)
        Nodes = [AddNode,SubNode,DivNode,MulNode,PowNode,NegNode]
        
        
        #hier wordt een lijst gemaakt met de precedence en associativiteit
        order_op = {}
        for node in Nodes:
            if node == NegNode:
                a = node(0)
                order_op[a.op_symbol]=[a.precedence,a.associativiteit]
            else:
                a = node(0,0)
                order_op[a.op_symbol]=[a.precedence,a.associativiteit]
        
        
        # het getal i geeft aan om welke token het gaat
        i = 0 
        
        while i< len(tokens):
            
            # als de huidige token een getal is wordt deze direct naar de output gestuurd
            if isnumber(tokens[i]):
                if isint(tokens[i]):
                    output.append(Constant(int(tokens[i])))
                else:
                    output.append(Constant(float(tokens[i])))
                    
            # als de token in de lijst met functies staat dan wordt deze naar de stack gestuurd        
            
            elif tokens[i] in funclist:
                stack.append(tokens[i])
                
            # als de token een operator is moeten verschillende dingen worden gecontroleerd
            
            elif tokens[i] in oplist:
                if tokens[i] == '-' and (
                    tokens[i-1] in oplist + ['('] or len(output)==0):  
                    # we hebben gecontroleerd of het minnetje wat we tegen komen een negate is, 
                    # als dit het geval is sturen we negate naar de stack
                    stack.append('~')    
                else:  
                    # als de operator geen negate is dan wordt hier bepaald in welke volgorde de operatoren naar de output moeten
                    while True:
                        #als er niks in de stack zit dan moet de operator sowieso naar de stack
                        if len(stack) == 0 or stack[-1] not in oplist+['~']:
                            break
                        
                        # Shunting Yard algoritme, met de regels van de volgorde van operaties wordt bepaald
                        # wanneer operatoren van de stack naar de output moeten
                        elif (order_op[tokens[i]][1]==0 and order_op[tokens[i]][0] <= order_op[stack[-1]][0]
                            ) or (order_op[tokens[i]][1]==1 and order_op[tokens[i]][0]<order_op[stack[-1]][0]):
                            
                            output.append(stack.pop())
                        else:
                            break
                    # de huidige token wordt altijd naar de stack gestuurd
                    stack.append(tokens[i])
                   

            elif tokens[i] == '(':
                # linker haakjes gaan naar de stack
                stack.append(tokens[i])
                
            elif tokens[i] == ')':
                # rechter haakje: pop alles van de stack naar de outpu totdat we een linkerhaakje tegen komen
                while not stack[-1] == '(':
                    output.append(stack.pop())
                
                # pop the left paranthesis from the stack (but not to the output)
                stack.pop()
                if len(stack)> 0 and stack[-1] in funclist:
                    output.append(stack.pop())
            
            #als de token geen getal, operator, haakje of functie is is het een variabele
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
                # functies zijn UnaryNodes en werken maar op 1 getal
                x = stack.pop()
                Node = funcuitvoer[t]
                stack.append(Node(x))
            elif t =='~':
                # negnodes werken op 1 getal en worden hier uitgevoerd
                y = stack.pop()
                stack.append(NegNode(y))
                    
            else:
                # a constant, push it to the stack
                stack.append(t)
            
                
        # the resulting expression tree is what's left on the stack
        return stack[0]


# Storing constant values  
class Constant(Expression):
    #Represents a constant value
    def __init__(self, value):
        self.value = value
        self.precedence =10

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
    # Als leaf True is, dan moet onmiddelijk de afgeleide worden teruggegeven
    # Als leaf false is, dan geeft hij de waarde terug en wordt hoger 
    # in de boom bepaald wat er mee moet gebeuren
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
        self.precedence = 10
    
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
    
    #initialisatie van de negnode. De inwendige invoer wordt meegegeven, het teken en de precedence
    def __init__(self, invoer):
        self.invoer = invoer
        self.op_symbol = '~'
        self.precedence = 3
        self.associativiteit = 1
    #printen. Indien de precedence van de invoer lager is, dan zijn er haakjes nodig
    def __str__(self):
        if self.invoer.precedence < self.precedence:
            return "- (%s)" % (self.invoer)
        else:
            return "- %s" % (self.invoer)

    #Evaluatie. Wanneer de invoer een constante is, maak dan een nieuwe constante aan
    #Wanneer de invoer iets anders is, dan moet er een nieuwe 
    def evaluate(self,variabelen={}):
        getal = self.invoer.evaluate(variabelen)
        if isinstance(getal,Constant):
            return Constant(-getal.value)
                #eval("%s %s %s" % (Constant(-1),'*',getal)))
        else:
            return NegNode(self.invoer.evaluate())
    
    #Differentiatie betekent dat differentiatie van expression node moet worden teruggegeven
    def dif(self,leaf=False):
        return NegNode(self.invoer.dif())
    

# Super classen van de functies exp, sin, cos 
class FunctionNode(Expression):
    
    #Elke functie moet meekrijgen het type functie, de invoer en de operatie
    def __init__(self, invoer ,func_symbol):
        self.func_symbol = func_symbol
        self.invoer = invoer
        self.operatie = self.operatie
        self.precedence = 10

    #De printfunctie. De invoer moet altijd om haakjes worden gezet.
    def __str__(self):
        return "%s (%s)" % (self.func_symbol,self.invoer)
    
    #Eerste wordt invoer geevalueerd. Als dit geen getal oplevert dan moet 
    #dit geevalueerd worden als een getal. Als iets anders oplevert moet de ver
    #eenvoudigde invoer worden teruggegeven. 
    def evaluate(self,variabelen={}):
        evaluated = self.invoer.evaluate(variabelen)
        if not isinstance(evaluated, Constant):
            toreturn = copy.copy(self)
            toreturn.invoer = evaluated
            return self
        else:
            return self.operatie(evaluated)
        
# Een subclass van functionnode
class SinNode(FunctionNode):
    
    #De operatie is sinus met een maximale precendence
    def __init__(self, invoer):
        self.operatie =  math.sin
        super(SinNode,self).__init__(invoer, 'sin')
    
    #Geef de afgeleide terug
    def dif(self,leaf=False):
        return CosNode(self.invoer)*self.invoer.dif()

# Een subclass van functionnode
class CosNode(FunctionNode):
    
    #De operatie is cosinus met een maximale precendence
    def __init__(self, invoer):
        self.operatie =  math.cos
        super(CosNode,self).__init__(invoer, 'cos')
    
    #Geef de afgeleide terug
    def dif(self,leaf=False):
        return NegNode(SinNode(self.invoer))*self.invoer.dif()  

class TanNode(FunctionNode):

    #De operatie is exp met een maximale precendence
    def __init__(self, invoer):
        self.operatie =  math.tan
        super(TanNode,self).__init__(invoer, 'tan')
    
    #Geef de afgeleide terug
    def dif(self,leaf=False):
        return DivNode(Constant(1),PowNode(CosNode(self.invoer),Constant(2)))* self.invoer.dif()
# Een subclass van functionnode
class ExpNode(FunctionNode):
    
    #De operatie is exp met een maximale precendence
    def __init__(self, invoer):
        self.operatie =  math.exp
        super(ExpNode,self).__init__(invoer, 'exp')
    
    #Geef de afgeleide terug
    def dif(self,leaf=False):
        return ExpNode(self.invoer)*self.invoer.dif() 

# Een subclass van functionnode
class LogNode(FunctionNode):
    
    #De operatie is exp met een maximale precendence
    def __init__(self, invoer):
        self.operatie =  math.log
        super(LogNode,self).__init__(invoer, 'log')
    
    #Geef de afgeleide terug
    def dif(self,leaf=False):
        return DivNode(Constant(1),self.invoer)*self.invoer.dif()

#De standaard node is een binarynode, hier zijn de meeste en meest uitgebreidde
# functionaliteiten te vinden
class BinaryNode(Expression):
    
    #A node in the expression tree representing a binary operator.
    def __init__(self, lhs, rhs, op_symbol,precedence,commutatief):
        self.lhs = lhs
        self.rhs = rhs
        self.op_symbol = op_symbol
        self.precedence = precedence
        self.commutatief = commutatief

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
            # bepaal ook of de huidige operatie commutatief is
            if True:
                # print(side,"zijde")
                order_lower = side.precedence
                order_this = self.precedence
                this_ass =  self.commutatief
                
                
                #indien ofwel orde 1 laag dieper minder groot is dan de huidige, dan zijn haakjes nodig
                #haakjes zijn ook nodig als de huidige operatie niet commutatief is 
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
        this_order = self.precedence 

        #Controleren op en verwijderen van nullen in verschillende vormen, en 
        #gevallen iets * 1 -> iets
        welke = 1

        for getal in [getal1, getal2]:
            #Verwijderen van nullen
            if getal == Constant(0):
                #Nullen in een + en - worden verwijderd
                if this_symbol == '+':
                    return eval("getal" + str(welke%2 + 1))
                elif this_symbol == '-':    
                    if welke == 1:
                        return NegNode(getal2)
                    else:
                        return getal1
                #bij * en / wordt het 0
                elif this_symbol == '*':
                    return Constant(0)
                elif this_symbol == '/':
                    if welke == 1:
                        return Constant(0)
                #een macht wordt 1 of 0
                elif this_symbol == '**':
                    if welke == 1:
                        return Constant(0)
                    else:
                        return Constant(1)
            
            #verwijderen van enen
            elif getal == Constant(1):
                if this_symbol == '*':
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
            return BinaryNode(getal1,getal2,this_symbol,self.precedence,self.commutatief)
        elif not isinstance(getal2,Constant):
            return BinaryNode(getal1,getal2,this_symbol,self.precedence,self.commutatief)
            
        #Wel twee constanten? Voer de operatie uit en maak een nieuwe constante aan
        else:
            return Constant(eval('%s %s %s' % (getal1.value, self.op_symbol, getal2.value)))
        
    #Differentiatie
    def dif(self, leaf=False):
        
        order_this = self.precedence
        
        #Kettingregel. De verschillende elementen worden los van elkaar aangemaakt. Dus eerst f(x) en x'
        # en dan het product
        if (self.op_symbol == '**' and not (isinstance(self.lhs,Constant) or isinstance(self.lhs,Variable))):
            macht = PowNode(self.lhs,Constant(self.rhs.value - 1))
            product = MulNode(self.rhs,macht)
            left = self.lhs.dif()
            toreturn = MulNode(product,left)
            
        #Productregel. Analoog aan kettingregel. Eerst f'(x) en g'(x). Dan f(x)g'(x) en f'(x)g(x) en dan 
        # de som
        elif (self.op_symbol == '*' and not (isinstance(self.lhs,Constant) or isinstance(self.rhs,Constant))):
            afgeleide1 = self.lhs.dif(True)
            afgeleide2 = self.rhs.dif(True)
            product1 = MulNode(afgeleide1,self.rhs)
            product2 = MulNode(self.lhs,afgeleide2)
            toreturn = AddNode(product1,product2)
            
        #Geen kettingregel of productregel
        else:
            left = self.lhs.dif(False)
            right = self.rhs.dif(False)
            order_this = self.precedence
            toreturn = False   

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
                    macht = PowNode(left,Constant(right.value -1))
                    toreturn = MulNode(right,macht)
                    
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
            toreturn = BinaryNode(left,right,self.op_symbol, self.precedence,self.commutatief)
        # Eindresultaat teruggeven
        return toreturn
        
        
    
    #Numerieke integratie
    def numIntegrate(self,variables,intervals):
        #voor 1 variabele
        if isinstance(variables,str):
            #stapgrootte vastleggen voor 1 variabele
            steps_per_unit = 1000
            steps1 = (intervals[1]-intervals[0])*steps_per_unit
            begin1 = intervals[0]
            eind1 = intervals[1]
            ans = 0
            
            #trapeziummethode toepassen op alle stapjes
            for i in range(0,steps1):
                x = [begin1+(i*(eind1-begin1))/steps1, begin1+((i+1)*(eind1-begin1))/steps1]
                for xpunt in x:
                    f = self.evaluate({variables:xpunt})
                    ans += (1/2)*eval('%s' % f)/steps_per_unit
            
            return round(ans,3)
        
        #voor 1 variabele voor het geval dat deze in een lijst staat
        elif (isinstance(variables,list) and len(variables)==1):
            #stapgrootte vastleggen voor 1 variabele
            steps_per_unit = 1000
            steps1 = (intervals[0][1]-intervals[0][0])*steps_per_unit
            begin1 = intervals[0][0]
            eind1 = intervals[0][1]
            ans = 0
            
            #trapeziummethode toepassen op alle stapjes
            for i in range(0,steps1):
                x = [begin1+(i*(eind1-begin1))/steps1, begin1+((i+1)*(eind1-begin1))/steps1]
                for xpunt in x:
                    f = self.evaluate({variables[0]:xpunt})
                    ans += (1/2)*eval('%s' % f)/steps_per_unit
            
            return round(ans,3)
        
        #voor meerdere variabelen
        else:
            #testen of er een of meerdere getallen in intervals zitten
            test = []
            for i in intervals:
                test.append(isinstance(i,list))
            if all(test)==False:
                newfunction = self
                newvariables = variables
                newintervals = intervals
                correction = 0
                number = 0
                #nieuwe functie, variabelen en intervallen maken
                for j in intervals:
                    if (isinstance(j,int) or isinstance(j,float)):
                        newfunction = newfunction.evaluate({variables[number]:j})
                        newvariables.pop(number)
                        newintervals.pop(number)
                        correction += 1
                    number += 1
                #de functie numIntegrate opnieuw runnen voor de nieuwe functie
                return newfunction.numIntegrate(newvariables,newintervals)
            
            #integratie starten voor meerdere variabelen
            else:
                #integratie voor twee variabelen
                if len(variables)==2:
                    #stapgrootte vastleggen voor 2 variabele
                    steps_per_unit = 100
                    
                    steps1 = (intervals[0][1]-intervals[0][0])*steps_per_unit
                    begin1 = intervals[0][0]
                    eind1 = intervals[0][1]
                    
                    steps2 = (intervals[1][1]-intervals[1][0])*steps_per_unit
                    begin2 = intervals[1][0]
                    eind2 = intervals[1][1]
                    
                    ans = 0
                    #trapeziummethode toepassen op alle stapjes
                    for i in range(0,steps1):
                        for j in range(0,steps2):
                            x = [begin1+(i*(eind1-begin1))/steps1, begin1+((i+1)*(eind1-begin1))/steps1]
                            y = [begin2+(j*(eind2-begin2))/steps2, begin2+((j+1)*(eind2-begin2))/steps2]
                            for xpunt in x:
                                for ypunt in y:
                                    f = self.evaluate({variables[0]:xpunt,variables[1]:ypunt})
                                    ans += (1/4)*eval('%s' % f)/(steps_per_unit**2)
                    
                    return round(ans,3)
                
                #integratie voor drie variabelen
                elif len(variables)==3:
                    #stapgrootte vastleggen voor 3 variabele
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
                    #trapeziummethode toepassen op alle stapjes
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
        
        return round(ans,3)
    
    #Nulpunt vinden op gespecificeerd interval
    def findRoot(self,expression,variable,interval):
        #zorgen dat de functie altijd stijgt bekeken van a naar b
        if expression.evaluate({variable:interval[0]}).constantvalue()<expression.evaluate({variable:interval[1]}).constantvalue():
            a = interval[0]
            b = interval[1]
        else:
            a = interval[1]
            b = interval[0]
        
        #middelpunt definieren
        m = (a+b)/2
        #definieren hoe precies het nulpunt moet worden gevonden
        delta = 0.0001
        
        #m als output geven indien het interval te klein is geworden
        if abs(b-a)<=delta:
            return m
        
        #bekijken aan welke kant van het middelpunt het nulpunt ligt
        #de functie findRoot opnieuw runnen voor een half zo groot interval
        if expression.evaluate({variable:m}).constantvalue()<=0:
            newinterval = [m,b]
            return self.findRoot(expression,variable,newinterval)
        else:
            newinterval = [a,m]
            return self.findRoot(expression,variable,newinterval)
    
    #Numeriek vergelijkingen oplossen
    def numSolver(self,left,right,variable,interval):
        #definieren hoe precies nulpunten van elkaar onderscheiden moeten worden
        epsilon = 0.01
        solutions = []
        #een kant van de vergelijking gelijk stellen aan nul
        nulexpression = SubNode(left, right)
        i = interval[0]
        #findRoot toepassen op alle intervallen die een nulpunt moeten bevatten
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
        self.precedence = 1 #meegeven van de precendence en associativiteit
        self.commutatief = True
        self.op_symbol = '+'
        self.associativiteit = 0
        super(AddNode, self).__init__(lhs, rhs,self.op_symbol,self.precedence,self.commutatief)
    
    
#onderstaande functies zijn extra maar analoog aan addnode
class SubNode(BinaryNode):
    """Represents the subtraction operator"""
    
    def __init__(self, lhs, rhs):
        self.precedence = 1
        self.commutatief = False
        self.op_symbol = '-'
        self.associativiteit = 0
        super(SubNode, self).__init__(lhs, rhs , self.op_symbol,self.precedence,self.commutatief)
        

class DivNode(BinaryNode):
    """Represents the division operator"""
    
    def __init__(self, lhs, rhs):
        self.precedence = 2
        self.commutatief = False
        self.op_symbol = '/'
        self.associativiteit = 0
        super(DivNode, self).__init__(lhs, rhs , self.op_symbol,self.precedence,self.commutatief)

class MulNode(BinaryNode):
    """Represents the multiplication operator"""

    def __init__(self, lhs, rhs):
        self.precedence = 2
        self.commutatief = True
        self.op_symbol = '*'
        self.associativiteit = 0
        super(MulNode, self).__init__(lhs, rhs ,self.op_symbol,self.precedence,self.commutatief)

class PowNode(BinaryNode):
    """Represents the power operator"""
    
    def __init__(self, lhs, rhs):
        self.precedence = 3
        self.commutatief = False
        self.op_symbol = '**'
        self.associativiteit = 1
        super(PowNode, self).__init__(lhs, rhs , self.op_symbol,self.precedence,self.commutatief)