from dotenv import load_dotenv
import neo4j_db_connector as nc
import os
import streamlit as st


def get_linked_entities(node_name):
    query = f"MATCH ({{name: '{node_name}'}})-[r]-(a) " \
            f"RETURN a.name AS node_name, a.nodeType AS node_labels, ID(a) AS node_id, a.description AS node_desc, " \
            f"r.name AS rel_name, TYPE(r) AS rel_type, startNode(r).name AS start_node"
    print(query)
    return conn.query(query)


load_dotenv()
conn = nc.Neo4jConnection(uri=os.getenv("URI"), user=os.getenv("USERNAME"), pwd=os.getenv("PASSWORD"))

st.header('Создание онтологии проекта')

scenario = conn.query("MATCH (a:Base) RETURN a.name AS name, ID(a) AS id")[0]

# количество добавляемых сценариев в начале равно 0
st.session_state['scenario_count'] = 0

# увеличиваем счетчик количества добавляемых сценариев
scenario_name = st.text_input("")
if st.button(f"Добавить {scenario['name'].lower()}", key=scenario['id']):
    st.session_state['scenario_count'] += 1

if st.session_state['scenario_count'] > 0:
    # получаем связанные сущности
    linked_entities = get_linked_entities(scenario['name'])

    # создаём возможность добавления сущностей
    for linked in linked_entities:
        # счётчик состояний для связанного узла
        state_name = f'{linked["node_id"]}_count'
        st.session_state[state_name] = 0

        name_main = st.text_input(linked["node_name"])

        # further_linked_entities = get_linked_entities(linked["node_name"])
        # for further_linked in further_linked_entities:
        #     if further_linked["rel_type"] == "GENERIC":
        #         if further_linked["rel_name"] == "быть видом" and further_linked["start_node"] != linked["node_name"]:

        st.button("Добавить", key=linked["node_id"])


