
from pyphp.interpreter import PHPInterpreter

def php_main():
    import sys
    if len(sys.argv) == 2:
        php = PHPInterpreter(code=open(sys.argv[1]).read())
    else:
        php = PHPInterpreter(interactive=True)
    php.run()

if __name__ == "__main__":
    php_main()
