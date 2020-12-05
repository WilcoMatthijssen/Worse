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