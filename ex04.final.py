"""
ex04 - Matthew Laws
"""


class Expr:
    """ This abstract class handles all expressions"""
    def bracket(self, expression, bracket_list):
        """ Returns the expression as a string.  
        If the class of the expression is listed in the bracket_list, the output is enclosed in brackets. """
        if expression.__class__ in bracket_list:
             return f"({str(expression)})"
        else:
            return str(expression)

    def make_tt(self):
        """ Creates a truth table for this expression. """
        # 1. Extract all the different Vars in the expression, ignoring duplicates.
        vars_found = list(self.all_vars(self))

        # 2. Generate the table header (the top line) that displays the Var names.
        table = self.make_tt_header(vars_found)

        # 3. Generate each line of the table.
        columns_needed = len(vars_found)    # We need 1 column for each Var in the expression.
        lines_needed = 2 ** columns_needed  # 1 Var needs 2 lines, 2 Var needs 4 lines, 3 Var needs 8 lines, etc.
        for line_number in range(lines_needed):
            table += self.make_tt_line(line_number, columns_needed, vars_found)

        return table + "\n"

    def make_tt_header(self, vars):
        """ Returns the header line of the truth table. """
        top_line = ""
        # Create a column for each Var, containing the name of the Var.
        for var in vars:
            top_line += f"{var}\t\t| "
        # Add one extra column to print out the expression.
        top_line += f"{self}\n-"
        # Optional.  Add a separator line.
        for var in vars:
            top_line += "-------+"
        top_line += "--------\n"
        return top_line

    def make_tt_line(self, line_number, columns, vars):
        """ Returns one line of the truth table. """
        env = {}  # Create a dictionary containing the values of the Vars for this line.
        line = ""
        # Starting with a blank line; add each column by putting True or False in, as appropriate.
        for column in range(columns):
            # Add a column to the line containing the Var's value for this line/column combination.
            # Column 0 alternates between true and false after every (2**0=) 1 line.
            # Column 1 alternates between true and false after every (2**1=) 2 lines.
            # Column 2 alternates between true and false after every (2**2=) 4 lines, etc.
            var_value = int(line_number / 2**column) %2 == 0 #returns an int and //2 to provide either 0(True) or 1(False). ==0 Converts the 0 or 1 into True or False.
            line += f" {var_value}\t|"
            # Add the name:value pair to the dictionary.
            var_name = vars[column]
            env[var_name] = var_value

        # Add one extra column to contain the result of the expression for the Vars on this line.
        line += f" {self.eval(env)}\n"

        return line

    def all_vars(self, expression):
        """ Recursively examines the given expression (and any expressions that it contains) and
        returns a set of all the Vars it contained there in.
        """
        vars = set()
        if expression.__class__ == Var:
            # expression is a Var (e.g. Var("x")), add it to the set.
            vars = vars | set([expression.name])
        elif issubclass(expression.__class__, BinOp):
            # expression is a BinOp.  Look for Vars in its left and right halves.
            vars = vars | self.all_vars(expression.left_expr)
            vars = vars | self.all_vars(expression.right_expr)
        else:
            # expression is a single op (e.g. Not(Var("x")).  Look for Vars in the expression it contains.
            vars = vars | self.all_vars(expression.expr)
        return vars

    def isTauto(self):
        """ Returns True if this expression always evaluates as True, otherwise False"""
        vars = list(self.all_vars(self))
        columns_needed = len(vars)
        lines_needed = 2**columns_needed
        # Loop through each combination of Var values until one is found that makes the expression false.
        for line in range(lines_needed):
            env = {}
            for column in range(columns_needed):
                var_name = vars[column]
                var_value = (int(line / 2**column) % 2 == 0)
                env[var_name] = var_value
            if not self.eval(env):
                # We only need to find 1 false value, so return immediately 1 is found.
                return False

        # None of the lines were false
        return True

    def eval(self, env):
        pass


class Var(Expr):
    """ Represents a named variable. """
    def __init__(self, name):
        self.name = name

    def eval(self, env):
        return env[self.name]

    def __str__(self):
        return self.name


class Not(Expr):
    """ Not is an expression that yields the opposite value to the expression it contains. """
    def __init__(self, expr):
        self.expr = expr

    def eval(self, env):
        return not self.expr.eval(env)

    def __str__(self):
        # Note: Not binds stronger than And, Or and Eq.
        return f"!{self.bracket(self.expr, [And, Or, Eq])}"


class BinOp(Expr):
    """ A binary operation is an expression that contains two expressions. """
    def __init__(self, left_expr, right_expr):
        self.left_expr = left_expr
        self.right_expr = right_expr

    def join(self, operand, bracket_list):
        """ Returns the two halves of a BinOp as a single string. """
        joined_expression = self.bracket(self.left_expr, bracket_list)
        joined_expression += operand
        joined_expression += self.bracket(self.right_expr, bracket_list)
        return joined_expression


class Or(BinOp):
    """ Or is an binary operation that evaluates to True if either of its component expressions are True. """
    def eval(self, env):
        return self.left_expr.eval(env) or self.right_expr.eval(env)

    def __str__(self):
        # Note: Or binds stronger than Eq.
        return self.join("|", [Eq])


class And(BinOp):
    """ And is an binary operation that evaluates to True if both of its component expressions are True. """
    def eval(self, env):
        return self.left_expr.eval(env) and self.right_expr.eval(env)

    def __str__(self):
        # Note: And binds stronger than both Eq and Or.
        return self.join("&", [Eq, Or])


class Eq(BinOp):
    """ Eq is an binary operation that evaluates to True if both of its component expressions are the same. """
    def eval(self, env):
        return self.left_expr.eval(env) == self.right_expr.eval(env)

    def __str__(self):
        return self.join("==", [])
    
    
    
    
    
#Provided test questions below:   
    
e1 = Or(Var("x"),Not(Var("x")))
e2 = Eq(Var("x"),Not(Not(Var("x"))))
e3 = Eq(Not(And(Var("x"),Var("y"))),Or(Not(Var("x")),Not(Var("y"))))
e4 = Eq(Not(And(Var("x"),Var("y"))),And(Not(Var("x")),Not(Var("y"))))
e5 = Eq(Eq(Eq(Var("p"),Var("q")),Var("r")),Eq(Var("p"),Eq(Var("q"),Var("r"))))

print(e1)
print(e2)
print(e3)
print(e4)
print(e5)

print(And(Not(Var("p")),Var("q")))
print(Not(And(Var("p"),Var("q"))))
print(Or(And(Var("p"),Var("q")),Var("r")))
print(And(Var("p"),Or(Var("q"),Var("r"))))
print(Eq(Or(Var("p"),Var("q")),Var("r")))
print(Or(Var("p"),Eq(Var("q"),Var("r"))))

print (e2.eval({"x" : True}))
print (e3.eval({"x" : True, "y" : True}))
print (e4.eval({"x" : False, "y" : True}))

print(e1.make_tt())
print(e2.make_tt())
print(e3.make_tt())
print(e4.make_tt())
print(e5.make_tt())

print (And(Var("x"),And(Var("y"),Var("z"))))
print (And(And(Var("x"),Var("y")),Var("z")))

print (e1.isTauto())
print (e2.isTauto())
print (e3.isTauto())
print (e4.isTauto())
print (e5.isTauto())