from ply import lex
from ply import yacc

from pddl.structs.pddl_factory import PDDLFactory
from pddl.structs import PDDLDomain
from pddl.structs import PDDLProblem

from collections import defaultdict


tokens = (
    'NAME',
    'VARIABLE',
    'NUMBER',
    'LPAREN',
    'RPAREN',
    'HYPHEN',
    'EQUALS',
    'DEFINE_KEY',
    'DOMAIN_KEY',
    'REQUIREMENTS_KEY',
    'STRIPS_KEY',
    'EQUALITY_KEY',
    'TYPING_KEY',
    'FLUENTS_KEY',
    'CONSTANTS_KEY',
    'CONDITIONAL_EFFECTS_KEY',
    'ADL_KEY',
    'TYPES_KEY',
    'PREDICATES_KEY',
    'FUNCTIONS_KEY',
    'ACTION_KEY',
    'DURATIVE_ACTION_KEY',
    'ACTION_COSTS_KEY',
    'PARAMETERS_KEY',
    'PRECONDITION_KEY',
    'CONDITION_KEY',
    'DURATION_KEY',
    'EFFECT_KEY',
    'AND_KEY',
    'OR_KEY',
    'NOT_KEY',
    'WHEN_KEY',
    'FORALL_KEY',
    'PROBLEM_KEY',
    'OBJECTS_KEY',
    'INIT_KEY',
    'GOAL_KEY',
    'DURATIVE_ACTIONS_KEY',
    'NEGATIVE_PRECONDITIONS_KEY',
    'DISJ_PRECONDITIONS_KEY',
    'ASSIGN_KEY',
    'INCREASE_KEY',
    'DECREASE_KEY',
    'LEQ_KEY',
    'GEQ_KEY',
    'PLUS_KEY',
    'MINUS_KEY',
    'METRIC_KEY',
    'MINIMIZE_KEY',
    'MAXIMIZE_KEY',
    'NUMBER_KEY',
)


t_LPAREN = r'\('
t_RPAREN = r'\)'
t_HYPHEN = r'\-'
t_EQUALS = r'='

t_ignore = ' \t'

reserved = {
    'define'                    : 'DEFINE_KEY',
    'domain'                    : 'DOMAIN_KEY',
    ':requirements'             : 'REQUIREMENTS_KEY',
    ':strips'                   : 'STRIPS_KEY',
    ':adl'                      : 'ADL_KEY',
    ':equality'                 : 'EQUALITY_KEY',
    ':typing'                   : 'TYPING_KEY',
    ':fluents'                  : 'FLUENTS_KEY',
    ':constants'                : 'CONSTANTS_KEY',
    ':types'                    : 'TYPES_KEY',
    ':durative-actions'         : 'DURATIVE_ACTIONS_KEY',
    ':negative-preconditions'   : 'NEGATIVE_PRECONDITIONS_KEY',
    ':disjunctive-preconditions': 'DISJ_PRECONDITIONS_KEY',
    ':conditional-effects'      : 'CONDITIONAL_EFFECTS_KEY',
    ':functions'                : 'FUNCTIONS_KEY',
    ':predicates'               : 'PREDICATES_KEY',
    ':action'                   : 'ACTION_KEY',
    ':durative-action'          : 'DURATIVE_ACTION_KEY',
    ':action-costs'             : 'ACTION_COSTS_KEY',
    ':parameters'               : 'PARAMETERS_KEY',
    ':precondition'             : 'PRECONDITION_KEY',
    ':condition'                : 'CONDITION_KEY',
    ':duration'                 : 'DURATION_KEY',
    ':effect'                   : 'EFFECT_KEY',
    ':metric'                   : 'METRIC_KEY',
    'and'                       : 'AND_KEY',
    'or'                        : 'OR_KEY',
    'not'                       : 'NOT_KEY',
    'when'                      : 'WHEN_KEY',
    'forall'                    : 'FORALL_KEY',
    'problem'                   : 'PROBLEM_KEY',
    ':domain'                   : 'DOMAIN_KEY',
    ':objects'                  : 'OBJECTS_KEY',
    ':init'                     : 'INIT_KEY',
    ':goal'                     : 'GOAL_KEY',
    'assign'                    : 'ASSIGN_KEY',
    'increase'                  : 'INCREASE_KEY',
    'decrease'                  : 'DECREASE_KEY',
    '<='                        : 'LEQ_KEY',
    '>='                        : 'GEQ_KEY',
    '+'                         : 'PLUS_KEY',
    '-'                         : 'MINUS_KEY',
    'minimize'                  : 'MINIMIZE_KEY',
    'maximize'                  : 'MAXIMIZE_KEY',
    'number'                    : 'NUMBER_KEY',
}


def t_KEYWORD(t):
    r':?[a-zA-z_][a-zA-Z_0-9\-]*'
    t.type = reserved.get(t.value, 'NAME')
    return t




t_NUMBER = r'[0-9]+'

def t_NAME(t):
    r'[a-zA-z_][a-zA-Z_0-9\-]*'
    return t


def t_VARIABLE(t):
    r'\?[a-zA-z_][a-zA-Z_0-9\-]*'
    return t



def t_newline(t):
    r'\n+'
    t.lineno += len(t.value)


def t_error(t):
    print("Error: illegal character '{0}'".format(t.value[0]))
    t.lexer.skip(1)


# build the lexer
lex.lex()











def p_pddl(p):
    """structs : domain
            | problem
            | operator_def
            | literal
            | constants_lst
            | variables_lst"""
    p[0] = p[1]




def p_problem(p):
    """problem : LPAREN DEFINE_KEY problem_def domain_def member_dict RPAREN"""
    # name, domain, objects, init, goal, metric=None, minimize=True
    name    = p[3]
    domain  = p[4]
    members = p[5]
    objects = members['objects']
    init    = members['init']
    goal    = members['goal']
    metric  = members['objective_metric'] if 'objective_metric' in members else None

    dummy_domain = PDDLFactory.DOMAIN(domain)

    p[0] = PDDLFactory.PROBLEM(name, dummy_domain, objects, init, goal, metric, minimize=True)


def p_domain_def(p):
    """domain_def : LPAREN DOMAIN_KEY NAME RPAREN"""
    p[0] = p[3]


def p_problem_def(p):
    """problem_def : LPAREN PROBLEM_KEY NAME RPAREN"""
    p[0] = p[3]


def p_objects_def(p):
    """objects_def : LPAREN OBJECTS_KEY typed_constants_lst RPAREN
                   | LPAREN OBJECTS_KEY RPAREN"""
    if len(p) == 4:
        p[0] = {'objects' : []}
    elif len(p) == 5:
        p[0] = {'objects' : p[3]}


def p_init_def(p):
    """init_def : LPAREN INIT_KEY LPAREN AND_KEY ground_predicates_lst RPAREN RPAREN
                | LPAREN INIT_KEY ground_predicates_lst RPAREN
                | LPAREN INIT_KEY RPAREN"""
    if len(p) == 4:
        p[0] = {'init' : []}
    elif len(p) == 5:
        p[0] = {'init' : p[3]}
    elif len(p) == 8:
        p[0] = {'init' : p[5]}


def p_goal_def(p):
    """goal_def : LPAREN GOAL_KEY LPAREN AND_KEY literals_lst RPAREN RPAREN
                | LPAREN GOAL_KEY literal RPAREN
                | LPAREN GOAL_KEY RPAREN"""
    if len(p) == 4:
        p[0] = {'goal' : []}
    elif len(p) == 5:
        p[0] = {'goal' : [p[3]]}
    elif len(p) == 8:
        p[0] = {'goal' : p[5]}


def p_ground_predicates_lst(p):
    """ground_predicates_lst : ground_predicate ground_predicates_lst
                             | ground_predicate"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_ground_predicate(p):
    """ground_predicate : LPAREN NAME constants_lst RPAREN
                        | LPAREN NAME RPAREN
                        | LPAREN EQUALS simple_predicate NUMBER RPAREN"""
    if len(p) == 4:
        p[0] = PDDLFactory.LITERAL(p[2])
    elif len(p) == 5:
        p[0] = PDDLFactory.LITERAL(p[2], p[3])
    elif len(p) == 6:
        p[0] = PDDLFactory.LITERAL(p[2], [p[3]] + [p[4]])



def p_metric_objective(p):
    """metric_obj : LPAREN METRIC_KEY metric_minmax simple_predicate RPAREN"""
    p[0] = {'objective_metric' : p[4],
            'objective_metric_minmax' : p[3]}


def p_metric_minmax(p):
    """metric_minmax : MINIMIZE_KEY
                     | MAXIMIZE_KEY"""
    p[0] = p[1]

def p_domain(p):
    """domain : LPAREN DEFINE_KEY domain_def member_dict RPAREN"""
    name    = p[3]
    members = p[4]
    types   = members['types']
    reqs    = members['requirements']
    consts  = members['constants']
    functs  = members['functions']
    preds   = members['predicates']
    ops     = members['operators']
    p[0] = PDDLDomain(name, reqs, types, consts, functs, preds, ops)


def p_member_dict(p):
    """member_dict : member member_dict
                   | member"""
    mods = defaultdict(lambda : [])
    if len(p) == 2:
        mods.update(p[1] if p[1] else {})
    elif len(p) == 3:
        mods.update(p[1])
        mods.update(p[2])
    p[0] = mods


def p_member(p):
    """member : types_def
                  | constants_def
                  | require_def
                  | predicates_def
                  | operators_def
                  | functions_def

                  | objects_def
                  | init_def
                  | goal_def
                  | metric_obj"""
    p[0] = p[1]


def p_functions_def(p):
    """functions_def : LPAREN FUNCTIONS_KEY function_def_lst RPAREN
                     | LPAREN FUNCTIONS_KEY RPAREN"""
    if len(p) == 5:
        p[0] = {'functions' : p[3]}
    elif len(p) == 4:
        p[0] = {'functions' : []}

def p_function_def_lst(p):
    """function_def_lst : function_def function_def_lst
                        | function_def"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]



def p_function_def(p):
    """function_def : LPAREN NAME typed_variables_lst RPAREN
                    | LPAREN NAME typed_variables_lst RPAREN HYPHEN NUMBER_KEY
                    | LPAREN NAME RPAREN
                    | LPAREN NAME RPAREN HYPHEN NUMBER_KEY"""
    if len(p) == 4:
        p[0] = PDDLFactory.LITERAL(p[2])
    elif len(p) == 5:
        p[0] = PDDLFactory.LITERAL(p[2], p[3])
    elif len(p) == 6:
        p[0] = PDDLFactory.LITERAL(p[2])
    elif len(p) == 7:
        p[0] = PDDLFactory.LITERAL(p[2], p[3])


def p_require_def(p):
    """require_def : LPAREN REQUIREMENTS_KEY require_key_lst RPAREN"""
    p[0] = {'requirements' : p[3]}


def p_require_key_lst(p):
    """require_key_lst : require_key require_key_lst
                       | require_key"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_require_key(p):
    """require_key : STRIPS_KEY
                   | EQUALITY_KEY
                   | TYPING_KEY
                   | DURATIVE_ACTIONS_KEY
                   | NEGATIVE_PRECONDITIONS_KEY
                   | DISJ_PRECONDITIONS_KEY
                   | CONDITIONAL_EFFECTS_KEY
                   | ACTION_COSTS_KEY
                   | ADL_KEY
                   | FLUENTS_KEY"""
    p[0] = str(p[1])


def p_types_def(p):
    """types_def : LPAREN TYPES_KEY typed_constants_lst RPAREN
                 | LPAREN TYPES_KEY RPAREN"""
    if len(p) == 5:
        p[0] = {'types' : p[3]}
    elif len(p) == 4:
        p[0] = {'types' : []}


def p_constants_def(p):
    """constants_def : LPAREN CONSTANTS_KEY typed_constants_lst RPAREN
                     | LPAREN CONSTANTS_KEY RPAREN"""
    if len(p) == 5:
        p[0] = {'constants' : p[3]}
    elif len(p) == 4:
        p[0] = {'constants' : []}

def p_predicates_def(p):
    """predicates_def : LPAREN PREDICATES_KEY predicate_def_lst RPAREN
                     | LPAREN PREDICATES_KEY RPAREN"""
    if len(p) == 5:
        p[0] = {'predicates' : p[3]}
    elif len(p) == 4:
        p[0] = {'predicates' : []}


def p_operators_def_dict(p):
    """operators_def : operator_def_lst"""
    p[0] = {'operators' : p[1]}


def p_operator_def_lst(p):
    """operator_def_lst : operator_def operator_def_lst
                        | operator_def"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_operator_def(p):
    """operator_def : strips_action_def"""
    p[0] = p[1]


def p_predicate_def_lst(p):
    """predicate_def_lst : predicate_def predicate_def_lst
                         | predicate_def"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_strips_action_def(p):
    """strips_action_def : LPAREN ACTION_KEY NAME parameters_def action_def_body RPAREN"""
    parameters = p[4]
    precond, effects = p[5]
    if len(effects) == 1 and effects[0].name == 'and':
        effects = tuple(effects[0].args)
    p[0] = PDDLFactory.STRIPS_OP(p[3], parameters, precond, effects)



def p_predicate_def(p):
    """predicate_def : LPAREN NAME typed_variables_lst RPAREN
                     | LPAREN NAME RPAREN"""
    if len(p) == 4:
        p[0] = PDDLFactory.PREDICATE(p[2])
    elif len(p) == 5:
        p[0] = PDDLFactory.PREDICATE(p[2], types=p[3])



def p_parameters_def(p):
    """parameters_def : PARAMETERS_KEY LPAREN typed_variables_lst RPAREN
                      | PARAMETERS_KEY LPAREN RPAREN"""
    if len(p) == 4:
        p[0] = []
    elif len(p) == 5:
        p[0] = p[3]




def p_duration_def(p):
    """duration_def : DURATION_KEY LPAREN EQUALS VARIABLE NUMBER RPAREN"""
    p[0] = int(p[5])


def p_durative_condition_def(p):
    """durative_condition_def : CONDITION_KEY LPAREN AND_KEY durative_condition_literals_lst RPAREN
                              | CONDITION_KEY durative_condition_literal"""
    if len(p) == 3:
        p[0] = [p[2]]
    elif len(p) == 6:
        p[0] = p[4]


def p_durative_condition_literals_lst(p):
    """durative_condition_literals_lst : durative_condition_literal durative_condition_literals_lst
                              | durative_condition_literal"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_durative_condition_literal(p):
    """durative_condition_literal : LPAREN NAME NAME literal RPAREN"""
    # A condition literal is among the following: at start, over all, at end
    p[0] = PDDLFactory.LITERAL(name='{} {}'.format(p[2], p[3]), args=[p[4]])



def p_action_def_body(p):
    """action_def_body : precond_def effects_def"""
    p[0] = (p[1], p[2])


def p_precond_def(p):
    """precond_def : PRECONDITION_KEY LPAREN AND_KEY literals_lst RPAREN
                    | PRECONDITION_KEY LPAREN RPAREN
                    | PRECONDITION_KEY LPAREN AND_KEY RPAREN
                    | PRECONDITION_KEY literal"""
    if len(p) == 3:
        p[0] = [p[2]]
    elif len(p) == 4:
        p[0] = []
    elif len(p) == 5:
        p[0] = []
    elif len(p) == 6:
        p[0] = p[4]


def p_effects_def(p):
    """effects_def : EFFECT_KEY LPAREN AND_KEY effects_lst RPAREN
                    | EFFECT_KEY LPAREN RPAREN
                    | EFFECT_KEY LPAREN AND_KEY RPAREN
                    | EFFECT_KEY effect"""
    if len(p) == 3:
        p[0] = [p[2]]
    elif len(p) == 4:
        p[0] = []
    elif len(p) == 5:
        p[0] = []
    if len(p) == 6:
        p[0] = p[4]



def p_effects_lst(p):
    """effects_lst : effect effects_lst
                   | effect"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_effect(p):
    """effect : literal"""
    if len(p) == 2:
        p[0] = p[1]


def p_literals_lst(p):
    """literals_lst : literal literals_lst
                    | literal"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_literal(p):
    """literal : LPAREN NOT_KEY predicate RPAREN
               | predicate"""
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 5:
        pred = p[3]
        pred.is_negative = True
        p[0] = pred


def p_when(p):
    """when : LPAREN NAME literals_lst RPAREN
            | literal
    """

    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 5:
        p[0] = PDDLFactory.LITERAL(p[2], p[3])

def p_simple_predicate(p):
    """simple_predicate : LPAREN NAME variables_lst RPAREN
                        | LPAREN NAME RPAREN"""
    if len(p) == 4:
        p[0] = PDDLFactory.LITERAL(name=p[2])
    elif len(p) == 5:
        p[0] = PDDLFactory.LITERAL(name=p[2], args=p[3])

def p_predicate(p):
    """predicate : simple_predicate
                 | LPAREN AND_KEY literals_lst RPAREN
                 | LPAREN OR_KEY literals_lst RPAREN
                 | LPAREN EQUALS VARIABLE VARIABLE RPAREN
                 | LPAREN EQUALS VARIABLE constant RPAREN
                 | LPAREN EQUALS constant VARIABLE RPAREN
                 | LPAREN WHEN_KEY when when RPAREN
                 | LPAREN NAME RPAREN
                 | LPAREN FORALL_KEY LPAREN typed_variables_lst RPAREN literal RPAREN
                 | NUMBER
                 | numeric_op"""

    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = PDDLFactory.LITERAL(p[2])
    elif len(p) == 5:
        p[0] = PDDLFactory.LITERAL(p[2], p[3])
    elif len(p) == 6:
        p[0] = PDDLFactory.LITERAL(p[2], [p[3], p[4]])
    elif len(p) == 8:
        pred_wrapper = PDDLFactory.LITERAL(name=' '.join([str(v) for v in p[4]])) # TODO fix
        p[0] = PDDLFactory.LITERAL(name=p[2], args=[pred_wrapper] + [p[6]])


def p_numeric_op(p):
    """numeric_op : LPAREN numberic_op_name simple_predicate simple_predicate RPAREN
                  | LPAREN numberic_op_name simple_predicate NUMBER RPAREN"""

    p[0] = PDDLFactory.LITERAL(name=p[2], args=[p[3], p[4]])


def p_numberic_op_name(p):
    """numberic_op_name : ASSIGN_KEY
                        | INCREASE_KEY
                        | DECREASE_KEY
                        | LEQ_KEY
                        | GEQ_KEY
                        | PLUS_KEY
                        | MINUS_KEY
                        | EQUALS"""
    p[0] = str(p[1])


def p_typed_constants_lst(p):
    """typed_constants_lst : constants_lst HYPHEN type typed_constants_lst
                           | constants_lst HYPHEN type
                           | constants_lst"""
    if len(p) == 2:
        p[0] = [PDDLFactory.TERM(value, None) for value in p[1]]
    if len(p) == 4:
        p[0] = [PDDLFactory.TERM(value, p[3]) for value in p[1]]
    elif len(p) == 5:
        p[0] = [PDDLFactory.TERM(value, p[3]) for value in p[1]] + p[4]


def p_typed_variables_lst(p):
    """typed_variables_lst : variables_lst HYPHEN type typed_variables_lst
                           | variables_lst HYPHEN type
                           | variables_lst"""
    if len(p) == 2:
        p[0] = [PDDLFactory.TERM(name, 'object') for name in p[1]]
    elif len(p) == 4:
        p[0] = [PDDLFactory.TERM(name, p[3]) for name in p[1]]
    elif len(p) == 5:
        p[0] = [PDDLFactory.TERM(name, p[3]) for name in p[1]] + p[4]


def p_constants_lst(p):
    """constants_lst : constant constants_lst
                     | constant"""
    if len(p) == 2:
        p[0] = [PDDLFactory.TERM(p[1])]
    elif len(p) == 3:
        p[0] = [PDDLFactory.TERM(p[1])] + p[2]


def p_variables_lst(p):
    """variables_lst : VARIABLE variables_lst
                     | VARIABLE
                     | NAME variables_lst
                     | NAME"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]




def p_type(p):
    """type : NAME"""
    p[0] = p[1]


def p_constant(p):
    """constant : NAME"""
    p[0] = p[1]


def p_error(p):
    print("Error: syntax error when parsing '{}'".format(p))


# build parser
yacc.yacc()


class PDDLParser(object):

    @classmethod
    def parse_string(cls, data):
        parsed = yacc.parse(str(data))
        return parsed

    @classmethod
    def parse_file(cls, filename):
        data = cls.read_input(filename)
        parsed = PDDLParser.parse_string(data)
        return parsed


    @classmethod
    def read_input(cls, filename):
        with open(filename, 'r') as file:
            data = ''
            for line in file:
                line = line.rstrip().lower()
                line = cls.__strip_comments(line)
                data += '\n' + line
        return data

    @classmethod
    def __strip_comments(cls, line):
        pos = line.find(';')
        if pos != -1:
            line = line[:pos]
        return line

