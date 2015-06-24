# eindopdracht

Repo voor de eindopdracht van het vak wisb256

Opdrachten

gelukt:

- Overload van de aritmetische operatoren (+, -, *, /, **) zodat we kunnen ‘rekenen’ met Expressions.
- Het vertalen van een Expression naar een string, waarbij er niet meer haakjes worden gebruikt dan
nodig (zoals in opdracht G van de midterm).
- Het vertalen van een string naar een Expression met behulp van het Shunting-yard algoritme.
- In plaats van constanten moet je ook variabelen (zoals ‘x’ of ‘a’) in je expressie-boom ondersteunen.
- Het berekenen van de numerieke waarde van een expressie. Hierbij worden de numerieke waarden van 
variabelen aangeleverd met een dictionary.
-  gedeeltelijke evaluatie

To do:

- negatie (oftewel 3+-2 en 3*-2 etc.) : 
Het probleem is op het moment met aftrekken, hij ziet dat stack niet leeg is en dan verwacht hij dat het een negatief is maar dat is hij ook niet en dan gebeurt er maar niks waardoor de rest van de operatoren niet op de goede plekken komen te staan
Ik weet het niet zeker maar volgens mij maakt hij van ~ een variabelen maar dat is niet helemaal duidelijk, het probleem lijkt te zijn dat hij negatief maken pas na andere operaties doet. dus 2*-4+10 wordt in rpn [2 10 4 + ~ *] 
- Overload van de gelijkheidsoperator om te checken of twee expressiebomen dezelfde berekening voorstellen.
-  evaluate aanpassen zodat oa 1+x+18 =  19+x wordt, begin van simplify dus
- functies
    - sin, cos, tan en hun inverse
    - log
    - exp
    - polynomen
- differentieren
    - functies
    - polynomen
    - rekenregels
- numeriek integreren
- onbekende functies
- integreren
    - standaard functies integraal meegeven oid
- verdere toevoegingen verzinnen, wellicht: 
- abc formule? Solver? graden en radialen invoeren
- constantes zoals pi, i etc.



