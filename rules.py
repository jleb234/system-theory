RULES = []

# если шаг сценария 1 предшествует шагу сценария 2, а сценарий Х включает в себя шаг сценария 1,
# то сценарий Х включает в себя также и шаг 2
STEPS_RULE = "MATCH(step1:ScenarioStep)-[{name: 'предшествовать'}]->(step2:ScenarioStep), " \
             "(sc:Scenario)-[r {name: 'включать в себя'}]->(step1) " \
             "MERGE(sc)-[:GENERATED {name: 'включать в себя'}]->(step2)"
RULES.append(STEPS_RULE)

# если шаг сценария осуществляется на экране Х и предполагает взаимодействие с Y,
# то Y располагается на экране Х
LOCATION_RULE = "MATCH(step:ScenarioStep)-[{name: 'осуществляться на'}]->(screen:Screen), " \
                "(step)-[{name: 'предполагать взаимодействие с'}]->(el) " \
                "MERGE(el)-[:GENERATED {name: 'располагаться на'}]->(screen)"
RULES.append(LOCATION_RULE)


def trigger_rules(client):
    for rule in RULES:
        client.execute(rule)