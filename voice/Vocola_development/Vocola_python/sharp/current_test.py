import re
import copy



# ---------------------------------------------------------------------------
# Unparsing of data structures (for debugging and generating error messages)

def unparse_statements(statements):
    result = ""
    for statement in statements: 
        type = statement["TYPE"]
        if type == "context" or type == "include" or type == "set": 
            result += unparse_directive (statement)
        elif type == "definition": 
            result += unparse_definition (statement)
        elif type == "function": 
            result += unparse_function_definition (statement)
        elif type == "command": 
            result +=  "C" + statement["NAME"] + ":  "
            result += unparse_command (statement, True) + ";\n"
    return result + "\n"

def unparse_directive(statement):
    type = statement["TYPE"]
    if type == "set": 
        return "$set '" + statement["KEY"] + "' to '" + statement["TEXT"] + "'\n"
    elif type == "context":   # bug fix <<<>>>
        return "|".join(statement["STRINGS"]) + ":\n"
    else: 
        return statement["TYPE"] + ":  '" + statement["TEXT"] + "'\n"

def unparse_definition(statement):
    return "<" + statement["NAME"] + "> := " + unparse_menu (statement["MENU"], True) + ";\n"

def unparse_function_definition(statement):
    result = statement["NAME"] + "(" + ",".join(statement["FORMALS"])
    result += ") := " + unparse_actions (statement["ACTIONS"])
    return result + ";\n"

def unparse_command(command, show_actions):
    result = unparse_terms (show_actions, command["TERMS"])
    if command.has_key("ACTIONS") and show_actions: 
        result += " = " + unparse_actions (command["ACTIONS"])
    return result

def unparse_terms(show_actions, terms):
    result = unparse_term(terms[0], show_actions)
    for term in terms[1:]: 
        result += " " + unparse_term(term, show_actions)
    return result

def unparse_term(term, show_actions):
    result = ""
    if term.get("OPTIONAL"): result +=  "["
    
    if   term["TYPE"] == "word":      result += term["TEXT"]
    elif term["TYPE"] == "variable":  result += "<" + term["TEXT"] + ">"
    elif term["TYPE"] == "dictation": result += "<_anything>"
    elif term["TYPE"] == "menu":      
        result += unparse_menu (term, show_actions)
    elif term["TYPE"] == "range": 
        result += str(term["FROM"]) + ".." + str(term["TO"])
    
    if term.get("OPTIONAL"): result +=  "]"
    return result

def unparse_menu(menu, show_actions):
    commands = menu["COMMANDS"]
    result = "(" + unparse_command(commands[0], show_actions)
    for command in commands[1:]: 
        result += " | " + unparse_command(command, show_actions)
    return result + ")"

def unparse_actions(actions):
    if len(actions) == 0: return ""  # bug fix <<<>>>
    result  = unparse_action(actions[0])
    for action in actions[1:]: 
        result += " " + unparse_action(action)
    return result

def unparse_action(action):
    if   action["TYPE"] == "word":      return unparse_word(action)
    elif action["TYPE"] == "reference": return "$" + action["TEXT"]
    elif action["TYPE"] == "formalref": return "$" + action["TEXT"]
    elif action["TYPE"] == "call": 
        result = action["TEXT"] + "("
        arguments = action["ARGUMENTS"]
        if len(arguments) > 0:
            result += unparse_argument(arguments[0])
            for argument in arguments[1:]: 
                result += ", " + unparse_argument(argument)
        return result + ")"
    else:
        return "<UNKNOWN ACTION>"  # should never happen...

def unparse_word(action):
    word = action["TEXT"] 
    word = word.replace("'","''")

    return "'" + word + "'" 

def unparse_argument(argument):
    return unparse_actions(argument)

##########

def Main():
    term = new Node()
    term["TEXT"] = "a 'word'!"

    print unparse_word(term)

    reference = {}
    reference["TYPE"] = "reference"
    reference["TEXT"] = "42"

    arguments = [[reference]]

    test_actions = []
          {"TYPE":"word", "TEXT":"a 'word'!"},
                {"TYPE":"reference", "TEXT":"42"},
                {"TYPE":"formalref", "TEXT":"xyzzy"},
                {"TYPE":"call", "TEXT":"foo", "ARGUMENTS":[]},
                {"TYPE":"call", "TEXT":"bar", "ARGUMENTS":arguments},

    print unparse_actions(test_actions)
    print unparse_actions(test_actions)

    test_terms = []
{"TYPE":"word", "TEXT":"Fred", "OPTIONAL":False},
              {"TYPE":"word", "TEXT":"can't", "OPTIONAL":True},
              {"TYPE":"variable", "TEXT":"list", "OPTIONAL":True},
              {"TYPE":"dictation"},
              {"TYPE":"range", "FROM":"1", "TO":"10"},

    print unparse_terms(False, test_terms)

test_command = {"TYPE":"command", "NAME":"1", "TERMS":test_terms,  # <<<>>>
                "ACTIONS":test_actions}  

print unparse_statements([test_command])

more_terms = test_terms + [{"TYPE":"menu", "COMMANDS":[test_command]}]

print unparse_terms(False, more_terms)
print unparse_terms(True, more_terms)

test_menu = {"TYPE":"menu", "COMMANDS":[test_command, test_command]}

test_commands = [test_command,
                 {"TYPE":"command", "NAME":"2", "TERMS":more_terms,  # <<<>>>
                  "ACTIONS":test_actions},
                 {"TYPE":"set", "KEY":"key", "TEXT":"value"},
                 {"TYPE":"include", "TEXT":"file.vch"},
                 {"TYPE":"definition", "NAME":"list", "MENU":test_menu},
                 {"TYPE":"function", "NAME":"foo", "FORMALS":["x", "y"],
                  "ACTIONS": test_actions},
                 {"TYPE":"context", "STRINGS":["hello", "there are"]}
                 ]

print unparse_statements(test_commands)

    return 0
