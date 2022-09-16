from rdflib import Graph

from namespaces import template_uri, reference_uri, class_uri, term_type_uri, rr_constant_uri
from util import parse_template, make_string_setter


def get_subject_map(g: Graph, node):
    response = {}

    template = g.value(node, template_uri)
    if template:
        response["template"] = template

    elif not response:
        reference = g.value(node, reference_uri)
        if reference:
            response["reference"] = reference

    elif not response:
        constant = g.value(node, rr_constant_uri)
        if constant:
            response["constant"] = str(constant)

    ## ToDo a subject can have several classes
    class_nodes = list(g.objects(node, class_uri))
    if class_nodes:
        response["class_nodes"] = class_nodes[0]

    term_type = g.value(node, term_type_uri)
    if term_type:
        response["term_type"] = term_type

    return response


def get_subject_setter(subject, references, subject_value):
    if "template" in subject:
        return get_subject_template_setter(subject, references, subject_value)
    elif "reference" in subject:
        return f'        bind(uri(str(?{references[str(subject["reference"])]})) as {subject_value})\n'
    elif "constant" in subject:
        # subject is constant so can just be added in construct
        return ""


def get_subject_references(subject):
    if "template" in subject:
        return [str(element["value"]) for element in parse_template(subject["template"]) if element["reference"]]
    elif "reference" in subject:
        return [str(subject["reference"])]
    elif "constant" in subject:
        return []


def get_subject_template_setter(subject, references, subject_value):
    is_blank_node = "term_type" in subject and str(subject["term_type"]) == "http://www.w3.org/ns/r2rml#BlankNode"

    return make_string_setter({"template": parse_template(subject["template"])}, subject_value[1:], references,
                              not is_blank_node)
