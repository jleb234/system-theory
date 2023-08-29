import pandas as pd


def create_rules(user_label, task_label):
    rules = []

    rules.append((
        """Если объекты s1 и a1, s2 и a2 (классов Step и Action соответственно) 
связаны отношением «материализоваться в»,
а также объекты s1 и s2 связаны отношением «предшествовать»,
то объекты a1 и a2 тоже связаны отношением «предшествовать».""",
        """MATCH (s1:Step)-[{name: 'материализоваться в'}]->(a1:Action) 
MATCH (s1:Step)-[{name: 'предшествовать'}]->(s2:Step) 
MATCH (s2:Step)-[{name: 'материализоваться в'}]->(a2:Action) 
MERGE (a1)-[:SEMANTIC {name: 'предшествовать'}]->(a2)"""
    ))

    return pd.DataFrame(rules, columns=['desc', 'code'])
