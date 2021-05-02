from .datasets import *
from .parser import PDDLParser
from .structs import PDDLFactory, PDDLProblem, PDDLDomain, StripsOperator




def set_default_planner(planner):
    PDDLProblem.planner = planner


