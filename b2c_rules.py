RULES = []



def trigger_rules(client):
    for rule in RULES:
        client.query(rule)
