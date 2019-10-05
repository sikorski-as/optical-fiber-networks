import re
from pprint import pprint

from pyparsing import Word, Literal, pyparsing_common, OneOrMore, alphanums, Suppress, SkipTo, LineEnd, ParserElement, \
    Forward, printables, ZeroOrMore, Group, Optional, delimitedList


def action_for(token: ParserElement):
    def wrapper(func):
        token.setParseAction(func)
        return func

    return wrapper


left_bracket = Suppress('(')
right_bracket = Suppress(')')
number = pyparsing_common.number
identifier = pyparsing_common.identifier
comma_separated_list = pyparsing_common.comma_separated_list
operator_assign = Suppress(Literal('='))
keyword_meta = Suppress(Literal('META'))
keyword_nodes = Suppress(Literal('NODES'))
keyword_links = Suppress(Literal('LINKS'))
keyword_demands = Suppress(Literal('DEMANDS'))
keyword_admissible_paths = Suppress(Literal('ADMISSIBLE_PATHS'))


node_definition = identifier + left_bracket + number + number + right_bracket
@action_for(node_definition)
def action_node_definition(string, location, tokens):
    return {'id': tokens[0], 'longitude': tokens[1], 'latitude': tokens[2]}


module_pair = number + number
@action_for(module_pair)
def action_node_definition(string, location, tokens):
    return {'module_capacity': tokens[0], 'module_cost': tokens[1]}


link_definition = identifier + left_bracket + identifier + identifier + right_bracket + number * 4 + left_bracket + ZeroOrMore(Group(module_pair)) + right_bracket
@action_for(link_definition)
def action_node_definition(string, location, tokens):
    return {
        'id': tokens[0],
        'source': tokens[1],
        'target': tokens[2],
        'pre_installed_capacity': tokens[3],
        'pre_installed_capacity_cost': tokens[4],
        'routing_cost': tokens[5],
        'setup_cost': tokens[6],
        'modules': tokens[7].asList(),
    }


demand_definition = identifier + left_bracket + identifier * 2 + right_bracket + number * 2 + (number | Literal('UNLIMITED'))
@action_for(demand_definition)
def action_demand_definition(string, location, tokens):
    return {
        'id': tokens[0],
        'source': tokens[1],
        'target': tokens[2],
        'routing_unit': tokens[3],
        'demand_value': tokens[4],
        'max_path_length': tokens[5],
    }


nodes = keyword_nodes + left_bracket + OneOrMore(node_definition) + right_bracket
@action_for(nodes)
def action_nodes(string, location, tokens):
    return {'name': 'nodes', 'value': tokens.asList()}


links = keyword_links + left_bracket + OneOrMore(link_definition) + right_bracket
@action_for(links)
def action_links(string, location, tokens):
    return {'name': 'links', 'value': tokens.asList()}


demands = keyword_demands + left_bracket + OneOrMore(demand_definition) + right_bracket
@action_for(demands)
def action_demands(string, location, tokens):
    return {'name': 'demands', 'value': tokens.asList()}


admissible_path_definition = identifier + left_bracket + OneOrMore(identifier) + right_bracket
@action_for(admissible_path_definition)
def action_admissible_path_definition (string, location, tokens):
    return {'path_id': tokens[0], 'links': tokens[1:]}


admissible_paths_for_demand = identifier + left_bracket + ZeroOrMore(admissible_path_definition) + right_bracket
@action_for(admissible_paths_for_demand)
def action_admissible_paths_for_demand(string, location, tokens):
    return {'demand_id': tokens[0], 'paths': tokens[1:]}


admissible_paths = keyword_admissible_paths + left_bracket + ZeroOrMore(admissible_paths_for_demand) + right_bracket
@action_for(admissible_paths)
def action_admissible_paths(string, location, tokens):
    return {'name': 'admissible_paths', 'value': tokens.asList()}


meta_definition = identifier + Suppress(Literal('=')) + comma_separated_list
@action_for(meta_definition)
def action_meta_definition(s, l, tokens):
    name = tokens[0]
    value = tokens[1:] if len(tokens) > 2 else tokens[1]
    return name, value


meta = keyword_meta + left_bracket + ZeroOrMore(meta_definition) + right_bracket
@action_for(meta)
def action(string, location, tokens):
    return {'name': 'meta', 'value': dict(tokens.asList())}


native_file = Optional(meta) + nodes + links + demands + admissible_paths
@action_for(native_file)
def action_nodes(string, location, tokens):
    return {section['name']: section['value'] for section in tokens}


def preprocess(code):
    without_comments = re.sub(r'[#?].*\n', '', code)
    return without_comments


def load_as_dict(filepath: str):
    with open(filepath, 'r') as f:
        code = f.read()
        preprocessed = preprocess(code)
        return native_file.parseString(preprocessed)[0]
