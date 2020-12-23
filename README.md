# Worse
Wilco's programmeertaal in Morse.  

## Worse is een turing complete programmeertaal omdat:
- In de taal Worse is conditional branching mogelijk omdat het if statements waarin functies of andere acties binnen kunnen worden uitgevoerd.
- While loops zijn geimplementeerd in Worse en kan oneindig loopen totdat de recursion limit is bereikt of wanneer er een stack-overflow is.
- Er is geen limiet voor het grootte van het geheugen. Variabellen kunnen oneindig vaak aangemaakt zolang de hardware het ondersteund en er unieke series aan karakters bestaan voor variabelnamen.
- Worse heeft de mogelijkheid om waardes te printen en teruggeven bij de main functie. Het ingeven van input voor de programma's kan worden gedaan door het in de code die uitgevoerd wordt te typen.
- Het halting probleem is lastig om op te lossen. In Worse is het verplicht om voor elke functie een waarde te hebben dat wordt teruggegeven. Dat zou kunnen betekenen dat alle functies bedoeld zijn om op een gegeven moment een waarde terug te geven en niet oneindig loopen.


## Code is geschreven in functionele stijl.
De lexer, parser and runner zijn pure functies dat geen shared state, mutable data, of bijwerkingen hebben. 


## De taal ondersteund:
De taal Worse ondersteund Loops.
Het voorbeeld hieronder print '$' 10 keer door middel van een while loop.
```
 ..--.. -- .- .. -. -.--. -.--.- -. -...- .---- ----- -.-.-. .-- .... .. .-.. . -.--. -. ---... -...- ----- -.--.- -. -...- -. -....- .---- -.-.-. .--. .-. .. -. - -.--. ...-- -.... -.--.- -.-.-. -.-.-. ... --- ... -...- .---- -.-.-. -.-.-.
```

## Bevat
- **Classes met inheritance:**
    De base class is [Node](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/classes.py#L51) en hieruit erven 3 andere nodes.  
    [ValueNode](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/classes.py#L65) <-- hieruit erven alle dingen die een waarde kunnen geven.
    - [IntNode](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/classes.py#L91)
    - [VariableNode](https://github.com/WilcoMatthijssen/Worse/blob/ed61ed0e1f1c11b80373c7095be2ffff5b9bf5b9/parse.py#L46)
    - [FuncExeNode](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/classes.py#L104)
    - [OperationNode](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/classes.py#L118)
    
    [ActionNode](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/classes.py#L134) <-- hieruit erven alle acties.
    - [AssignNode](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/classes.py#L147)
    - [PrintNode](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/classes.py#L161)
    - [IfWhileNode](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/classes.py#L174)
    
    [FuncDefNode](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/classes.py#L190)

- **Object-printing voor elke class:**
    Ja
   
- **Decorator:**
    De decorator zorgt er voor dat elk meegegeven parameter door de deepcopy functie gaat en 
    wordt gebruikt voor alle functies die ik geschreven heb voor deze opdracht 
    (de lijst hieronder laat niet alle toepassingen zien van de decorator).
    ```python
    def deepcopy_decorator(func):
        def inner(*args):
            return func(*list(map(lambda element: deepcopy(element), args)))
        return inner
    ```
    - [Definitie](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/classes.py#L6)
    - [Toepassing_1](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/lexer.py#L15)
    - [Toepassing_2](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/parse.py#L21)
    - [Toepassing_3](https://github.com/WilcoMatthijssen/Worse/blob/8f14f09f352043cd21461fff1d3e2852ccde279f/runner.py#L17)

    
- **Type-annotatie:**
    - Haskell-stijl in comments: [ja]
    - Python-stijl in functiedefinities: [ja]
    
- **Toepassing hogere-orde functies:**
    - [map lexer.py#L60](https://github.com/WilcoMatthijssen/Worse/blob/421dd189005befe794a1057b85a71c3605335830/lexer.py#L60)
    - [map lexer.py#L64](https://github.com/WilcoMatthijssen/Worse/blob/421dd189005befe794a1057b85a71c3605335830/lexer.py#L64)
    - [map lexer.py#L137](https://github.com/WilcoMatthijssen/Worse/blob/421dd189005befe794a1057b85a71c3605335830/lexer.py#L137)
    - [map lexer.py#L141](https://github.com/WilcoMatthijssen/Worse/blob/421dd189005befe794a1057b85a71c3605335830/lexer.py#L141)
    - [reduce lexer.py#L143](https://github.com/WilcoMatthijssen/Worse/blob/421dd189005befe794a1057b85a71c3605335830/lexer.py#L143)
    - [get_op_func runner.py#L29](https://github.com/WilcoMatthijssen/Worse/blob/8216fbb60fdd6e5e581a3dbcbf15f8c06fb77264/runner.py#L29)
    - [map runner.py#L61](https://github.com/WilcoMatthijssen/Worse/blob/8216fbb60fdd6e5e581a3dbcbf15f8c06fb77264/runner.py#L61)
    - [reduce runner.py#L76](https://github.com/WilcoMatthijssen/Worse/blob/8216fbb60fdd6e5e581a3dbcbf15f8c06fb77264/runner.py#L76)
    - [map runner.py#L90](https://github.com/WilcoMatthijssen/Worse/blob/8216fbb60fdd6e5e581a3dbcbf15f8c06fb77264/runner.py#L90)
    - [reduce runner.py#L91](https://github.com/WilcoMatthijssen/Worse/blob/8216fbb60fdd6e5e581a3dbcbf15f8c06fb77264/runner.py#L91)
    - [reduce runner.py#L105](https://github.com/WilcoMatthijssen/Worse/blob/8216fbb60fdd6e5e581a3dbcbf15f8c06fb77264/runner.py#L105)

    

## Interpreter-functionaliteit Must-have:
- **Functies:**
    Meer per file
    
    _Voorbeeld van de main functie wat een andere functie aanroept en het resultaat hiervan zelf teruggeeft:_
    ```
   ..--.. ..-. ..- -. -.-. .---- -.--. -.--.- ... --- ... -...- ..--- -.-.-. -.-.-. ..--.. -- .- .. -. -.--. -.--.- ... --- ... -...- ..-. ..- -. -.-. .---- -.--. -.--.- -.-.-. -.-.-. 
    ```
    
    
- **Functie-parameters kunnen worden meegegeven worden door:**
    In de code de functie te gebruiken en parameters in te geven in de haken.
    
    _Voorbeeld van een functie dat wordt aangeroepen en 2 parameters die worden meegegeven:_
    ```
   ..--.. ..-. ..- -. -.-. .---- -.--. -. --..-- .- -.. -.. -.--.- ... --- ... -...- -. .-.-. .- -.. -.. -.-.-. -.-.-. ..--.. -- .- .. -. -.--. -.--.- ... --- ... -...- ..-. ..- -. -.-. .---- -.--. .---- ----- --..-- .---- ----- -.--.- -.-.-. -.-.-. 
    ```
    
- **Functies kunnen andere functies aanroepen:**
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

- **Functie resultaat wordt op de volgende manier weergegeven:**
    - Printen
    - Return waarde
    
    _Voorbeeld van printen "Hello world" en 1 teruggeven als resultaat van de main functie:_
    ```
     ..--.. -- .- .. -. -.--. -.--.- .--. .-. .. -. - -.--. --... ..--- --..-- .---- ----- .---- --..-- .---- ----- ---.. --..-- .---- ----- ---.. --..-- .---- .---- .---- --..-- ...-- ..--- --..-- .---- .---- ----. --..-- .---- .---- .---- --..-- .---- .---- ....- --..-- .---- ----- ---.. --..-- .---- ----- ----- -.--.- -.-.-. ... --- ... -...- .---- -.-.-. -.-.-.
    ```
    _Output van voorbeeld:_
    ```
    Process starting with function: main
    Hello world
    Process finished with 1
    ```
    
