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
        acceptable_sources = [i[0] for i in self.constraints]
        acceptable_targets = [i[1] for i in self.constraints]
        if type(self.source).__name__ not in acceptable_sources:
            raise RuntimeError("You can not use {} class as a source for this type of relation".format(
                type(self.source).__name__))
        if type(self.target).__name__ not in acceptable_targets:
            raise RuntimeError("You can not use {} class as a target for this type of relation".format(
                type(self.target).__name__))

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
    # rel_type = RelationType.OPTIONAL
    rel_name = "предшествовать"
    constraints = [("ScenarioStep", "ScenarioStep", "OPTIONAL")]

    # def __repr__(self):
    #     return "Шаг сценария «%s» предшествует шагу «%s»" % (self.source.name, self.target.name)


class Include(RelationItem):
    rel_name = "включать в себя"
    constraints = [("Scenario", "ScenarioStep", "REQUIRED"), ("Block", "Element", "REQUIRED")]

    # def __repr__(self):
    #     return "Сценарий «%s» включает в себя шаг «%s»" % (self.source.name, self.target.name)



