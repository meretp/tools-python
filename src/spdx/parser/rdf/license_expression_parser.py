# Copyright (c) 2023 spdx contributors
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from rdflib import Graph, RDF
from license_expression import LicenseExpression, get_spdx_licensing
from rdflib.term import Node
from spdx.parser.error import SPDXParsingError

from spdx.rdfschema.namespace import SPDX_NAMESPACE, LICENSE_NAMESPACE


def parse_license_expression(license_expression_node: Node, graph: Graph, doc_namespace: str) -> LicenseExpression:
    spdx_licensing = get_spdx_licensing()
    expression = ""
    if license_expression_node.startswith(LICENSE_NAMESPACE):
        expression = license_expression_node.removeprefix(LICENSE_NAMESPACE)
        return spdx_licensing.parse(expression)
    if license_expression_node.startswith(doc_namespace):
        expression = license_expression_node.fragment
        return spdx_licensing.parse(expression)

    node_type = graph.value(license_expression_node, RDF.type)
    if node_type == SPDX_NAMESPACE.ConjunctiveLicenseSet:
        members = dict()
        for index, (_, _, member_node) in enumerate(
            graph.triples((license_expression_node, SPDX_NAMESPACE.member, None))):
            members[index] = parse_license_expression(member_node, graph, doc_namespace)
        if len(members) > 2:
            raise SPDXParsingError([f"A ConjunctiveLicenseSet can only have two members."])
        expression = f"{members[0]} AND {members[1]}"
    if node_type == SPDX_NAMESPACE.DisjunctiveLicenseSet:
        members = dict()
        for index, (_, _, member_node) in enumerate(
            graph.triples((license_expression_node, SPDX_NAMESPACE.member, None))):
            members[index] = parse_license_expression(member_node, graph, doc_namespace)
        if len(members) > 2:
            raise SPDXParsingError([f"A DisjunctiveLicenseSet can only have two members."])
        expression = f"{members[0]} OR {members[1]}"
    if node_type == SPDX_NAMESPACE.WithExceptionOperator:
        members = dict()
        members[0] = parse_license_expression(graph.value(license_expression_node, SPDX_NAMESPACE.member), graph,
                                              doc_namespace)
        members[1] = parse_license_exception(graph.value(license_expression_node, SPDX_NAMESPACE.licenseException),
                                             graph)
        expression = f"{members[0]} WITH {members[1]}"
    if node_type == SPDX_NAMESPACE.ExtractedLicensingInfo:
        pass

    return spdx_licensing.parse(expression)


def parse_license_exception(exception_node: Node, graph: Graph) -> str:
    if exception_node.startswith(LICENSE_NAMESPACE):
        exception = exception_node.removeprefix(LICENSE_NAMESPACE)
    else:
        exception = graph.value(exception_node, SPDX_NAMESPACE.licenseExceptionId).toPython()
    return exception
