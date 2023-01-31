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
import os
from datetime import datetime
from typing import Tuple

import pytest
from rdflib import Graph, RDF, URIRef
from rdflib.term import Node

from spdx.model.version import Version

from spdx.model.actor import Actor, ActorType

from spdx.parser.rdf.creation_info_parser import parse_creation_info, parse_namespace_and_spdx_id
from spdx.rdfschema.namespace import SPDX_NAMESPACE


def test_parse_creation_info():
    graph = Graph().parse(os.path.join(os.path.dirname(__file__), "data/file_to_test_rdf_parser.rdf.xml"))

    creation_info, _ = parse_creation_info(graph)
    assert creation_info.spdx_id == "SPDXRef-DOCUMENT"
    assert creation_info.spdx_version == "SPDX-2.3"
    assert creation_info.name == "documentName"
    assert creation_info.document_namespace == "https://some.namespace"
    assert creation_info.creators == [Actor(ActorType.PERSON, "creatorName", "some@mail.com")]
    assert creation_info.created == datetime(2022, 12, 1, 0, 0)
    assert creation_info.creator_comment == "creatorComment"
    assert creation_info.data_license == "CC0-1.0"
    assert creation_info.license_list_version == Version(3, 19)
    assert creation_info.document_comment == "documentComment"


def test_parse_namespace_and_spdx_id():
    graph = Graph().add((URIRef("docNamespace#spdxID"), RDF.type, SPDX_NAMESPACE.SpdxDocument))

    namespace, spdx_id, _ = parse_namespace_and_spdx_id(graph)

    assert namespace == "docNamespace"
    assert spdx_id == "spdxID"


@pytest.mark.parametrize("triple", [(URIRef("docNamespace"), RDF.type, SPDX_NAMESPACE.SpdxDocument),
                                    (URIRef(""), RDF.type, URIRef(""))])
def test_parse_namespace_and_spdx_id_with_system_exit(triple: Tuple[Node, Node, Node]):
    graph = Graph().add(triple)

    with pytest.raises(SystemExit):
        parse_namespace_and_spdx_id(graph)
