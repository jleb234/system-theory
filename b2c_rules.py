import pandas as pd

RULES = []

descriptions = [
    """Если объекты s1 и t1, s2 и t2 связаны отношением «материализоваться в», 
    а также объекты s1 и s2 связаны отношением «предшествовать»,
    то объекты t1 и t2 тоже связаны отношением «предшествовать»."""
]

codes = [
    """MATCH (s1)-[m1 {name: 'материализоваться в'}]->(t1)
MATCH (s1)-[p {name: 'предшествовать'}]->(s2)
MATCH (s2)-[m2 {name: 'материализоваться в'}]->(t2)
MERGE (t1)-[:SEMANTIC {name: 'предшествовать'}]->(t2)"""
]

data = pd.DataFrame()
data['Описание'] = descriptions
data['Код правила'] = codes

def trigger_rules(client):
    for rule in RULES:
        client.query(rule)
