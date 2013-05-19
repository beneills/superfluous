Superfluous
===========

A utility to add superfluous comments to C code.

Status
---------

It works just fine, but would ideally:

* detect more code constructs to add more comments

* parse the code properly, rather than treating lines atomically

* handle more languages, so it could **self-superfluous-comment it's own source**

Usage
---------

    superfluous.py [-h] infile [outfile]

Example
-------------

We turn this:

    #include <stdio.h>

    int main()
    {
        int i;
   	for (i = 0; i < 10; i++)
   	{
	    printf ("Hello World\n");
	}
	return 0;
    }

Into:
    
    $ ./superfluous.py hello.c

    // include stdio.h
    #include <stdio.h>

    int main()
    {
        // declare, but do not initialize i
        int i;
        // loop, starting with i = 0,
        //       do i++ each time,
        //       while i < 10
        for (i = 0; i < 10; i++)
        {
            // print the string: "Hello World\n"
            printf ("Hello  World\n");
        }
        // return 0
        return 0;
    }
