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
from datetime import datetime

from rdflib import Graph, Literal, RDFS, URIRef

from spdx.datetime_conversions import datetime_to_iso_string
from spdx.writer.rdf.creation_info_writer import add_creation_info_to_graph
from spdx.writer.rdf.writer_utils import spdx_namespace
from tests.spdx.fixtures import creation_info_fixture


def test_add_creation_info_to_graph():
    graph = Graph()
    creation_info = creation_info_fixture()

    add_creation_info_to_graph(creation_info, graph)

    assert (None, None, spdx_namespace().SpdxDocument) in graph
    assert (URIRef(f"{creation_info.document_namespace}#{creation_info.spdx_id}"), None, None) in graph
    assert (None, spdx_namespace().creationInfo, None) in graph
    assert (None, spdx_namespace().name, Literal("documentName")) in graph
    assert (None, spdx_namespace().specVersion, Literal("SPDX-2.3")) in graph

    assert (None, None, spdx_namespace().CreationInfo) in graph
    assert (None, spdx_namespace().created, Literal(datetime_to_iso_string(datetime(2022, 12, 1)))) in graph
    assert (None, RDFS.comment, Literal("creatorComment")) in graph
    assert (None, spdx_namespace().licenseListVersion, Literal("3.19")) in graph
    assert (None, spdx_namespace().creator, Literal("Person: creatorName (some@mail.com)")) in graph