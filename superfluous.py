#!/usr/bin/env python3

#
# Superfluous
# Uncopyright, Ben Eills, 2013
#


import argparse
import re
import sys


REGEXES = { 'i' : '[^\d\W]\w*',             # identifier
            'w' : '[ \t]*'                  # whitespace
            }

class Construct:
    """
    A logical piece of C code for which we have a comment template.
    """
    def __init__(self):
        pass

    def match(self, line):
        """
        Returns comment or None.
        """
        return None


class SimpleRegexConstruct(Construct):
    """
    Covers most cases with straightforward regex group matching.
    """

    def __init__(self, pattern, description):
        """
        `pattern` -- we substitute from REGEXES using format()
                     to obtain a regex
        `description` -- a text string with format()-style keyword
                         syntax
        """
         
        self.compiled = re.compile(pattern.format(**REGEXES))
        self.description = description

    def match(self, line):
        m = self.compiled.match(line)
        if m:
            return self.description.format(**m.groupdict())
        return None

class ForLoopConstruct(Construct):
    """
    Handles complicated for loops.
    """

    compiled = re.compile('{w}for{w}\('
                         '{w}(?P<init>[^;]*?){w};'
                         '{w}(?P<cond>[^;]*?){w};'
                         '{w}(?P<action>[^;]*?){w}\)'
                         .format(**REGEXES))

    def match(self, line):
        m = self.compiled.match(line)
        if m:
            return 'loop, starting with {init},\n      do {action} each time,\n      while {cond}'.format(**m.groupdict())
        return None


class LineMatch:
    """
    A match of a particular line against a particular form.
    """

    def __init__(self, whitespace, description):
        self.whitespace = whitespace
        self.description = description

    def lines(self):
        """
        Return lines representing superfluous comment.
        """
        return ['{0}// {1}\n'.format(self.whitespace, d)
                for d in self.description.split('\n')]

class Code:
    """
    Internal representation of a C source file.
    """

    constructs = [SimpleRegexConstruct('printf{w}\({w}"(?P<str>(\\.|[^"])*)'
                                       '"{w}\){w};',
                                       'print the string: "{str}"'),
                  # Includes
                  SimpleRegexConstruct('#include{w}[<"](?P<id>[^>"]+)[>"]'
                                       , 'include {id}'),

                  # Declarations
                  SimpleRegexConstruct('int{w}(?P<id>{i}){w};', 'declare, '
                                       'but do not initialize {id}'),

                  # Returns
                  SimpleRegexConstruct('return{w};',
                                       'return without value'),

                  SimpleRegexConstruct('return{w}(?P<val>[^;]+){w};',
                                       'return {val}'),
                  # Loops
                  ForLoopConstruct()]

    def __init__(self, lines):
        """
        `lines` -- list of string lines
        We avoid complicated C parsing by making this approximation.
        """
        self.lines = lines

    def add_superfluous_comments(self):
        """
        Main method to actually add comments to instance.
        """
        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            m = self._match(line)
            if m:
                comment = m.lines()
                self.lines[i:i] = comment
                i += len(comment)
            i += 1

    def string(self):
        """
        Return string representation of code.
        """
        return ''.join(self.lines)

    def _match(self, line):
        """
        Is this line actionable?
        """
        for construct in Code.constructs:
            c = construct.match(line.lstrip(' \t'))
            if c:
                w = re.match('^{w}'.format(**REGEXES), line)
                return LineMatch(w.group(0), c)
        # Default to no match
        return None


def parse(f):
    """
    Parse file f into lines and return Code instance.
    """
    return Code(f.readlines())
    

def main():
    # Argument handling
    parser = argparse.ArgumentParser(description='A utility to add superfluous'
                                                 ' comments to C code.')
    parser.add_argument('infile', type=argparse.FileType('r'),
                        default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout)
    args = parser.parse_args()

    # Actual work
    code = parse(args.infile)
    args.infile.close()
    code.add_superfluous_comments()

    # Output to file/stdout
    args.outfile.write(code.string())
    args.outfile.close()

if __name__ == '__main__':
    main()
