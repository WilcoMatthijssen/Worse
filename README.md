# Worse
An interpreter for the programming language Worse.  


## How to program in Worse:
Worse is a language that can be written in the morse language.
Worse supports whitespace but doesnt need it.
For ease of use the following explanation of how to program in Worse wil not be in morse and include whitespace.

### main
Worse is a programming language that works with functions and doesn't have global variables.
Therefore when running Worse it runs a function which is called ```main``` or in morse ```-- .- .. -.```. 
This main function does not allow parameters and if defined will not be used.

```
?main()
    print(72, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100);
;

 ..--.. -- .- .. -. -.--. -.--.- 
 / / / / .--. .-. .. -. - -.--. --... ..--- --..-- / .---- ----- .---- --..-- / .---- ----- ---.. --..-- / .---- ----- ---.. --..-- / .---- .---- .---- --..-- / ...-- ..--- --..-- / .---- .---- ----. --..-- / .---- .---- .---- --..-- / .---- .---- ....- --..-- / .---- ----- ---.. --..-- / .---- ----- ----- -.--.- -.-.-. 
 -.-.-.

```

To define a function you need to start with a ```?``` or in morse with ```..--..``` to show you're defining a function.
After that you give it a name. The name needs to start with a letter and can be followed with letters or numbers. 
The name also can't be a ```while```, ```if```, and ```print``` because these are used for other things, 
although your name can contain those three as for example ```loopprint```. 

When you gave your program a name you can start with defining parameters which you can do with an open bracket.
After this you can type all your parameters with the same rules as your function name separated by commas and closed by a closing bracket.
If you dont have any parameters to define you can leave the brackets empty just as shown for the main function.

Now you can start by coding the functionality of your function. 
Worse has four actions you can use for that which are variable assignment, if statements, while statements, and print.

### Value
All the following actions make use of values so this is a short description of what a value is in Worse.
```pr```

### Variable assignment
```
?main()
    sos = 10 + 10 + 10 - 30 + 1;
;
 ..--.. -- .- .. -. -.--. -.--.- 
 / / / / ... --- ... / -...- / .---- ----- / .-.-. / .---- ----- / .-.-. / .---- ----- / -....- / ...-- ----- / .-.-. / .---- -.-.-. 
 -.-.-.

```

### If statement
```
?main()
    sos = 10;
    if(sos == 10)
        sos = 1;
    ;
;
..--.. -- .- .. -. -.--. -.--.- 
... --- ... -...- .---- ----- -.-.-. 
.. ..-. -.--. ... --- ... -...- -...- .---- ----- -.--.- 
... --- ... -...- .---- -.-.-. 
-.-.-. 
-.-.-.

```

### While statement
```
?main()
    sos = 10;
    while(sos != 0)
        sos = sos - 1;
    ;
;
..--.. -- .- .. -. -.--. -.--.- 
... --- ... -...- .---- ----- -.-.-. 
.-- .... .. .-.. . -.--. ... --- ... -.-.-- -...- ----- -.--.- 
... --- ... -...- ... --- ... -....- .---- -.-.-. 
-.-.-. 
-.-.-.
```

### Print
```
?main()
    print(72, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100);
    sos = 1;
;
..--.. -- .- .. -. -.--. -.--.- 
.--. .-. .. -. - -.--. --... ..--- --..-- .---- ----- .---- --..-- .---- ----- ---.. --..-- .---- ----- ---.. --..-- .---- .---- .---- --..-- ...-- ..--- --..-- .---- .---- ----. --..-- .---- .---- .---- --..-- .---- .---- ....- --..-- .---- ----- ---.. --..-- .---- ----- ----- -.--.- -.-.-. 
... --- ... -...- .---- -.-.-. 
-.-.-.
```


### odd & even functions
```
?odd(n)
    sos = 0;
    if(n != 0)
        sos = even(n-1);
    ;
;

?even(n)
    sos = 1;
    if(n != 0)
        sos = odd(n-1);
    ;
;

?main()
    sos = even(100);
;
```

```
 ..--.. --- -.. -.. -.--. -. -.--.- ... --- ... -...- ----- -.-.-. .. ..-. -.--. -. / -.-.-- -...- / ----- -.--.- ... --- ... -...- . ...- . -. -.--. -. -....- .---- -.--.- -.-.-. -.-.-. -.-.-. 
 ..--.. . ...- . -. -.--. -. -.--.- ... --- ... -...- .---- -.-.-. .. ..-. -.--. -. / -.-.-- -...- / ----- -.--.- ... --- ... -...- --- -.. -.. -.--. -. -....- .---- -.--.- -.-.-. -.-.-. -.-.-. 
 ..--.. -- .- .. -. -.--. -.--.- ... --- ... -...- . ...- . -. -.--. .---- ----- ----- -.--.- -.-.-. -.-.-.
```

result is 1 i.e. True


## Criteria beargumentatie

- **De code is goed becommentariëerd.**  
Elke functie heeft een docstring.

- **Er is een duidelijke README.**  
De README die u nu leest.

- **De code is geschreven in functionele programmeerstijl.**  
De lexer, parser and runner zijn pure functies dat geen shared state, mutable data, of bijwerkingen hebben.
Het GUI gedeelte in alleen niet zo functioneel. 
Het probleem hiermee is dat het wel mogelijk is door elke functie een gui object mee geef wat de gehele interpreter vervuil door telkens 1 argument mee te geven die in 2 functies gebruikt wordt. 
Het alternatief was de ingebouwde print te gebruiken wat in de achtergrond hetzelfde zou doen als de gui.


- **De gekozen of ontworpen programmeertaal is Turingcompleet.**  
    Dit is een voorbeeld van een Truth machine wat werkt in de programmeertaal Worse (vervang <INPUT> met uw eigen input):
    ``` 
    ..--.. -- .- .. -. -.--. -.--.- .. -. .--. ..- - -...- <INPUT> -.-.-. .. ..-. -.--. .. -. .--. ..- - -...- -...- .---- -.--.- ... --- ... -...- .---- -.-.-. -.-.-. .. ..-. -.--. .. -. .--. ..- - -.-.-- -...- .---- -.--.- ... --- ... -...- ----- -.-.-. -.-.-. -.-.-.
  ```

- **Deze taal moet minstens of loops of goto-statments, of lambda-calculus ondersteunen.**  
    De taal heel while loops en zien er als volgt uit:
    <INSERT VOORBEELD>

- **De taal mag géén Python, Brainfuck, C++ , of Assembler zijn.**  
    Worse is mijn eigen verzonnen taal en het is geen van die drie.

- **Het gebruik van minstens 3 hogere-orde functies.**  
    Hogere orde functies worden gebruikt. De functies die worden gebruikt zijn reduce en map in de volgende stukken.
    <INSERT VOORBEELD>

- **De code moet minstens één zelf-geschreven decorator (met -syntax) bevatten en gebruiken**  
    Er is een decorator gebruikt in de runner voor het zien welke functie gerunned wordt en hoe ver het op de stack is.
    <INSERT VOORBEELD>

- **• Alle functions moeten type-annotated zijn.**  
    Alle functies maken gebruik van type-hinting.

- **• De code moet classes bevatten.**  
    Er zijn classes gemaakt voor de tokens en alle verschillende soorten nodes.
    <INSERT VOORBEELD>

- **Object-printing functions voor elke class.** 
    Elke class die ik gemaakt voor de lexer, parser en runner is te printen.
