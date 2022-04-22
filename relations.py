from enum import Enum
from nodes import *


# class RelationType(Enum):
#     REQUIRED = 'REQUIRED'
#     OPTIONAL = 'OPTIONAL'
#     GENERATED = 'GENERATED'


class RelationItem:
    # rel_type = RelationType.REQUIRED
    rel_name = None
    constraints = []

    def __init__(self, source: NodeItem, target: NodeItem):
        self.source = source
        self.target = target
        self.check_acceptable()

    def check_acceptable(self):
        """Хотя бы один из вариантов source-target-branch из наборов ограничений должен быть валидным.
        Поскольку все наследники имеют в labels метку предка, именно по этой метке определяется валидность."""
        results = [(src in self.source.labels) and (trg in self.target.labels) for src, trg, brn in self.constraints]
        if not any(results):
            raise RuntimeError("You can not use {}-{} source-target combination relation of type {}".format(
                type(self.source).__name__, type(self.target).__name__, type(self).__name__))

    def db_create_relation(self, connection):
        source_id = self.source.get_node_id(connection)
        target_id = self.target.get_node_id(connection)
        rel_type = None
        for i in self.constraints:
            if type(self.source).__name__ == i[0] and type(self.target).__name__ == i[1]:
                rel_type = i[2]
        query = f"MATCH (source), (target) " \
                f"WHERE ID(source) = {source_id} AND ID(target) = {target_id} " \
                f"CREATE (source)-[:{rel_type} {{name: '{self.rel_name}'}}]->(target)"
        connection.query(query)


class Preceede(RelationItem):
    rel_name = "предшествовать"
    constraints = [("ScenarioStep", "ScenarioStep", "OPTIONAL")]


class Include(RelationItem):
    rel_name = "включать в себя"
    constraints = [("Scenario", "ScenarioStep", "REQUIRED"), ("Block", "Element", "REQUIRED")]




