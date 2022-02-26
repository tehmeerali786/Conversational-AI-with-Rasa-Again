import json
from collections import defaultdict 
from typing import Any, Dict, List, Text 

from neo4j import GraphDatabase 
from rasa_sdk.knowledge_base.storage import KnowledgeBase 

def _dict_to_cypher(data):
    pieces = []
    for k, v in data.items():
        piece = "{}: '{}'".format(k, v)
        pieces.append(piece)

    join_piece = ", ".join(pieces)

    return "{" + join_piece + "}"


class Neo4jKnowledgeBase(KnowledgeBase):
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

        self.representation_attribute = defaultdict(lambda: "name")

        self.relation_attributes = {

            "Singer": {},
            "Album": {},
            "Song": {"singer":"SUNG_BY", "album":"INCLUDED_IN"},
        }

        super().__init__()

    def close(self):
        self._driver.close()

    async def get_attributes_of_object(self, object_type: Text) -> List[Text]:
        # transformer for query
        object_type = object_type.capitalize()

        result = self.do_get_attributes_of_object(object_type)

        return result

    def do_get_attributes_of_obect(self, object_type) -> List[Text]:
        with self._driver.session() as session:
            result = session.write_transaction(
                self._do_get_attributes_of_object, object_type
            )

        result = result + list(self.relation_attributes[object_type].keys())
        
        return result

    def _do_get_attributes_of_object(self, tx, object_type) -> List[Text]:
        query = "MATCH (o:{object_type}) RETURN o LIMIT 1".format(
            object_type=object_type
        )
        print(query)
        result = tx.run(query,)

        record = result.single()

        if record:
            return list(record[0].keys())


        return []

    async def get_represntation_attribute_of_object(self, object_type: Text) -> Text:
        """
            Returns a lambda function that takes an object and returns a string
            representation of it.
            Args:
                object_type: the object type
            Returns: lambda function
        """

        return self.representation_attribute[object_type]

    def go_get_objects(
        self,
        object_type: Text,
        attributions: Dict[Text, Text],
        relations: Dict[Text, Text],
        limit: int,
    ):
        with self._driver.session() as session:
            result = session.write_transaction(
                self._do_get_objects, object_type, attributions, relations, limit
            )

        return result

    def go_get_object(
        self,
        object_type: Text,
        object_identifier: Text,
        key_attribute: Text,
        representation_attribute: Text,

        ):

            with self._driver.session() as session:
                result = session.write_transaction(
                    self._do_get_object,
                    object_type,
                    object_identifier,
                    key_attribute,
                    representation_attribute,
                    self.relation_attributes[object_type],
                )

            return result

    @staticmethod
    def _do_get_objects(

        tx,
        object_type: Text,
        attributions: Dict[Text, Text],
        relations: Dict[Text, Text],
        limit: int,
    ):
        print("<_do_get_objects>: ", object_type, attributions, relations, limit)
        if not relations:
            # attr only, simple case
            query = "MATCH (o:{object_type} {attrs}) RETURN o LIMIT {limit}".format(
                object_type=object_type,
                attrs= _dict_to_cypher(attributions),
                limit=limit,
            )
            print(query)
            result = tx.run(query,)

            return [dict(record["o"].items()) for record in result]

        else:
            basic_query = "MATCH (o: {object_type} {attrs})".format(
                object_type=object_type,
                attrs = _dict_to_cypher(attributions),
                limit=limit,
            )
            sub_queries = []
            for k, v in relations.items():
                sub_query = "MATCH (o)-[:{}]->({{name: '{}'}})".format(k, v)
            where_clause = "WHERE EXISTS {" + sub_query  + "}"

            for sub_query in sub_queries[1:]:
                where_clause = "WHERE EXISTS {" + sub_query  + " " + where_clause + "}"