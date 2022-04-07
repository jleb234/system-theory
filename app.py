from dotenv import load_dotenv
import neo4j_db_connector as nc
import os
import streamlit as st
import graphviz as graphviz


def get_linked_entities(node_name):
    """Получает информацию о связанных узлах"""
    query = f"MATCH ({{name: '{node_name}'}})-[r]-(a) " \
            f"RETURN a.name AS node_name, a.nodeType AS node_labels, ID(a) AS node_id, " \
            f"a.description AS node_desc, a.propertyName AS property_name, " \
            f"r.name AS rel_name, TYPE(r) AS rel_type, startNode(r).name AS start_node"
    # print(query)
    return conn.query(query)


def get_options(node_id):
    """Получает список значений свойств"""
    query = f"MATCH (a)-[{{name: 'иметь значение'}}]->(b) " \
            f"WHERE ID(a) = {node_id} " \
            f"RETURN b.name AS name"
    # print(query)
    properties = conn.query(query)
    return [pr["name"] for pr in properties]


def generate_interface_section(entity, first_iteration=False, previous=None):
    # state_name = f'{entity["node_id"]}_count'
    # st.session_state[state_name] = 0

    # вывод заголовка / подзаголовка
    if first_iteration:
        st.header(entity["node_name"])
    else:
        st.subheader(entity["node_name"])

    # вывод графической информации о связи с предыдущей связанной сущностью
    if not first_iteration:
        graph = graphviz.Digraph()
        if entity["start_node"] == entity["node_name"]:
            graph.edge(entity['node_name'], previous['node_name'], label=entity['rel_name'])
        else:
            graph.edge(previous['node_name'], entity['node_name'], label=entity['rel_name'])
        st.graphviz_chart(graph)

    # текстовое поля для ввода названия новой сущности
    name = st.text_input(entity["node_name"], key=entity["node_id"])

    linked_entities = get_linked_entities(entity["node_name"])

    # ввод свойств сущностей (при наличии)
    properties = {}
    for linked_entity in linked_entities:
        if linked_entity["rel_type"] == "REQUIRED":
            if linked_entity["rel_name"] == 'иметь свойство':
                properties[linked_entity["property_name"]] = st.selectbox(
                    linked_entity["node_name"], options=get_options(linked_entity["node_id"]))
                print(properties)

    # кнопка "Добавить"
    add_option = f"Добавить {entity['node_name'].lower()}"
    button = st.checkbox(add_option, key=entity['node_id'])
    if button:
        # st.session_state[state_name] += 1
        # добавление фрагмента в онтологию

        # рекурсивный выхов функции для следуюшего узла, связанногос текущим обязательным исходящим отношением
        for linked_entity in linked_entities:
            if linked_entity["rel_name"] not in ["иметь свойство"]:
                if linked_entity["rel_type"] == "REQUIRED" and linked_entity["start_node"] == entity["node_name"]:
                    generate_interface_section(linked_entity, previous=entity)


load_dotenv()
conn = nc.Neo4jConnection(uri=os.getenv("URI"), user=os.getenv("USERNAME"), pwd=os.getenv("PASSWORD"))
# conn = nc.Neo4jConnection(uri=os.getenv("URI_CLOUD"),
#                           user=os.getenv("USERNAME_CLOUD"),
#                           pwd=os.getenv("PASSWORD_CLOUD"))

st.title('Создание онтологии проекта')
entities = conn.query("MATCH (a:Base) RETURN a.name AS node_name, ID(a) AS node_id")

for i in entities:
    generate_interface_section(i, first_iteration=True)
