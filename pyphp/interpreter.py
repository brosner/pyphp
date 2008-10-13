
import sys

try:
    import ply
except ImportError:
    print "error: you need ply"
    raise SystemExit
else:
    import ply.lex as lex
    import ply.yacc as yacc

class Interpreter(object):
    def __init__(self, code="", interactive=False):
        self.code = code
        self.interactive = interactive
        
        self.vars = {}
        self.constants = {}
        self.functions = {}
        
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self)
    
    def run(self):
        if not self.interactive:
            yacc.parse(self.code)
        else:
            print self.banner
            while 1:
                try:
                    s = raw_input("php >> ")
                except EOFError:
                    break
                if not s:
                    continue
                yacc.parse(s)
            print

class PHPInterpreter(Interpreter):
    
    def __init__(self, *args, **kwargs):
        super(PHPInterpreter, self).__init__(*args, **kwargs)
        if self.interactive:
            self.lexer.begin("php")
        def test_func():
            return "hey this is pretty cool.\n"
        self.functions["test_func"] = test_func
    
    def _get_banner(self):
        return "pyPHP 0.1"
    banner = property(_get_banner)
    
    states = (
        ("php", "exclusive"),
    )
    
    tokens = (
        "ECHO",
        "DOLLAR",
        "SEMI",
        "LABEL",
        "SINGLE_QUOTE",
        "DOUBLE_QUOTE",
        "INT",
        "RPARA",
        "LPARA",
        "COMMA",
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
    )
    
    precedence = (
        ("left", "PLUS", "MINUS"),
        ("left", "TIMES", "DIVIDE"),
    )
    
    t_php_ignore = " \t"
    
    def t_php(self, t):
        r"<\?php"
        t.lexer.begin("php")
    def t_php_CLOSE_TAG(self, t):
        r"\?>"
        t.lexer.begin("INITIAL")
    
    def t_php_NEWLINE(self, t):
        r"\n+"
        t.lexer.lineno += t.value.count("\n")
    
    t_php_DOLLAR = r"\$"
    t_php_SEMI = r";"
    t_php_SINGLE_QUOTE = r"'"
    t_php_DOUBLE_QUOTE = r'"'
    t_php_LPARA = r"\("
    t_php_RPARA = r"\)"
    t_php_COMMA = r","
    t_php_PLUS = r"\+"
    t_php_MINUS = r"-"
    t_php_TIMES = r"\*"
    t_php_DIVIDE = r"/"
    t_php_ECHO = r"echo"
    
    def t_php_INT(self, t):
        r"\d+"
        try:
            t.value = int(t.value)
        except ValueError:
            t.value = 0
        return t
    
    reserved_map = {
        "echo": "ECHO"
    }
    
    def t_php_LABEL(self, t):
        r"[A-Za-z_][\w_]*"
        t.type = self.reserved_map.get(t.value, "LABEL")
        return t
    
    def p_statement_list(self, p):
        """statement_list : statement_list statement
                          | statement"""
        pass
    
    def p_statement_expr(self, p):
        """statement : expr SEMI"""
        if self.interactive:
            sys.stdout.write(str(p[1]) + "\n")
    
    def p_statement_echo(self, p):
        """statement : ECHO expr SEMI"""
        sys.stdout.write(str(p[2]))
    
    def p_expr_int(self, p):
        """expr : INT
                | function_call"""
        p[0] = p[1]
    def p_expr_variable(self, p):
        """expr : DOLLAR LABEL"""
        p[0] = self.vars.get(p[2], "")
    def p_expr_single_quote(self, p):
        """expr : SINGLE_QUOTE SINGLE_QUOTE"""
        if len(p) == 3:
            p[0] = ""
    def p_expr_double_quote(self, p):
        """expr : DOUBLE_QUOTE DOUBLE_QUOTE"""
        if len(p) == 3:
            p[0] = ""
    def p_expr_binop(self, p):
        """expr : expr PLUS expr
                | expr MINUS expr
                | expr TIMES expr
                | expr DIVIDE expr"""
        if p[2] == "+":
            p[0] = p[1] + p[3]
        elif p[2] == "-":
            p[0] = p[1] - p[3]
        elif p[2] == "*":
            p[0] = p[1] * p[3]
        elif p[2] == "/":
            p[0] = p[1] / p[3]
    
    def p_function_call(self, p):
        """function_call : LABEL function_params"""
        try:
            p[0] = self.functions[p[1]](*p[2])
        except KeyError: # undefined function
            print "Undefined function: %s" % p[1]
        except TypeError, e: # bad parameters
            print e
    def p_function_params(self, p):
        """function_params : LPARA RPARA
                           | LPARA function_argument_list RPARA"""
        if len(p) == 3:
            p[0] = []
        else:
            p[0] = p[2]
    def p_function_argument_list(self, p):
        """function_argument_list : function_argument_list COMMA expr
                                  | expr"""
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]
    
    def t_php_error(self, t):
        print "illegal character in PHP state: %s" % repr(t.value[0])
        t.lexer.skip(1)
    
    def t_error(self, t):
        print "illegal character in INITIAL state: %s" % repr(t.value[0])
        t.lexer.skip(1)
    
    def p_error(self, p):
        print "Syntax error on line %d." % p.lineno
