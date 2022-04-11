from dotenv import load_dotenv
import neo4j_db_connector as nc
import os
import streamlit as st
import graphviz as graphviz
import pandas as pd


def get_linked_entities(node_name, rel_type=""):
    """Получает информацию о связанных узлах"""
    query = f"MATCH ({{name: '{node_name}'}})-[r {rel_type}]-(a) " \
            f"RETURN a.name AS node_name, a.nodeType AS nodeType, ID(a) AS node_id, labels(a) AS node_labels, " \
            f"a.description AS node_desc, a.propertyName AS property_name, " \
            f"r.name AS rel_name, TYPE(r) AS rel_type, startNode(r).name AS start_node"
    # print(query)
    entities = conn.query(query)
    entities_df = pd.DataFrame.from_records(
        entities,
        columns=[
            'node_name', 'nodeType', 'node_id', 'node_labels', 'node_desc', 'property_name',
            'rel_name', 'rel_type', 'start_node'])
    entities_df = entities_df[entities_df['rel_type'] != 'GENERATED']
    # сортировка – для того, чтобы поля ввода генерировались последовательно (сначала для обязательных элементов)
    entities_df['rel_type'] = pd.Categorical(entities_df['rel_type'], ["REQUIRED", "OPTIONAL"])

    # убираем дубликаты связанных отношением "иметь вид" узлов, т.к. в интерфейсе для всех них предусмотрено одно поле
    types_df = entities_df[entities_df['rel_name'] == 'иметь вид']
    types_df = types_df[types_df['start_node'] != types_df['node_name']]
    types_df = types_df.drop_duplicates(subset=['start_node'])
    no_types_df = entities_df[entities_df['rel_name'] != 'иметь вид']
    entities_df = pd.concat([no_types_df, types_df])

    return entities_df.sort_values("rel_type")
    # TODO в идеале это класс


def get_options(node_id, rel_type='иметь значение'):
    """Получает список значений свойств"""
    query = f"MATCH (a)-[{{name: '{rel_type}'}}]->(b) " \
            f"WHERE ID(a) = {node_id} " \
            f"RETURN b.name AS name"
    # print(query)
    properties = conn.query(query)
    return [pr["name"] for pr in properties]


def get_labels(p_entity):
    labels = p_entity['nodeType'] + p_entity['node_labels']
    labels.remove('Meta')
    return labels


def add_entity(p_entity, p_properties, p_previous, f_iteration=False):
    labels = get_labels(p_entity)
    if f_iteration:
        query = f"CREATE (:{':'.join(labels)} {p_properties})"
    else:
        prev_labels = get_labels(p_previous)
        query = f"MERGCE (a)-[:{p_entity['rel_type']} {{name: '{p_entity['rel_name']}'}}]" \
                f"->(:{':'.join(labels)} {p_properties}) " \
                f"WHERE ID(a) = {p_previous['node_id']}"
    print(query)


def generate_interface_section(
        entity,  # текущая сущность с полями в формате Series
        optional=False,  # является ли связь с предыдущей сущностью опциональной
        first_iteration=False,  # является ли это первой итерацией (используется для форматирования заголовков)
        previous=None,  # информация о предыдущей сущности в формате Series
        previous_name=None,  # информация о имени экземпляра предыдущей сущности (информация из поля ввода)
        key_name=None,  # уникальный ключ для элементов интерфейса
        section_type='general'  # тип секции; возможные значения: types (родовидовые отношения с предыдущей сущностью)
):
    # вывод заголовка / подзаголовка
    header = entity["node_name"] + ' *' if optional else entity["node_name"]
    if first_iteration:
        st.header(header)
    elif section_type == 'general':
        st.markdown(f"### {header}")
    else:
        st.markdown(f"#### {header}")

    # вывод графической информации о связи с предыдущей связанной сущностью
    if not first_iteration and not section_type == 'types':
        graph = graphviz.Digraph()
        if entity["start_node"] == previous['node_name'] or entity["start_node"] != entity["node_name"]:
            graph.edge(f"{previous['node_name']} «{previous_name}»", entity['node_name'], label=entity['rel_name'])
        else:
            graph.edge(entity['node_name'], f"{previous['node_name']} «{previous_name}»", label=entity['rel_name'])
        st.graphviz_chart(graph)

    linked_entities = get_linked_entities(entity["node_name"])

    # ввод свойств сущностей (при наличии)
    properties = {}
    has_types = False
    for _, linked_entity in linked_entities.iterrows():
        # print(linked_entity)
        if linked_entity["rel_name"] == 'иметь свойство':
            options = get_options(linked_entity["node_id"])
            input_label = linked_entity["node_name"]
            # отмечаем звездочкой необязательные поля
            input_label = input_label if linked_entity["rel_type"] == "REQUIRED" else input_label + ' *'
            if len(options) > 0:  # если есть заданные значения свойств, показываем выпадающий список
                properties[linked_entity["property_name"]] = st.selectbox(
                    input_label, options=options, help=linked_entity["node_desc"], key=key_name)
            else:  # если заданных значений свойств нет, показываем поле ввода
                properties[linked_entity["property_name"]] = st.text_input(
                    input_label, help=linked_entity["node_desc"], key=key_name)
            # print(properties)
        if linked_entity["rel_name"] == 'иметь вид' and linked_entity['start_node'] == entity["node_name"]:
            options = get_options(entity["node_id"], rel_type=linked_entity["rel_name"])
            node_type = st.selectbox("Вид", options=options, key=key_name)
            if st.checkbox("Заполнить информацию о виде", key=key_name):
                entities = conn.query(f"MATCH (a {{name: '{node_type}'}}) "
                                      f"RETURN a.name AS node_name, ID(a) AS node_id")
                entities_df = pd.DataFrame.from_records(entities, columns=['node_name', 'node_id'])
                for _, i in entities_df.iterrows():
                    pr_name = generate_interface_section(
                        i, section_type='types', key_name=previous_name + linked_entity['node_name'] + node_type)
                    print(pr_name)
            has_types = True

    # кнопка "Добавить"
    if not has_types:
        if st.button(f"Добавить {entity['node_name'].lower()}", key=key_name):
            add_entity(entity, properties, previous, first_iteration)
            # TODO добавление фрагмента в онтологию

    linked_entities_f = linked_entities[linked_entities["rel_name"] != "иметь свойство"]
    linked_entities_f = linked_entities_f[linked_entities_f["start_node"] == entity["node_name"]]
    if linked_entities_f.shape[0] > 0:
        # опция для показа связанные сущности (реализовано как чекбокс)
        if st.checkbox("Заполнить связанную информацию", key=key_name):
            # рекурсивный вызов функции для следуюшего узла, связанного с текущим обязательным исходящим отношением
            for n, linked_entity in linked_entities_f.iterrows():
                optional = True if linked_entity['rel_type'] == 'OPTIONAL' else False
                new_previous_name = properties['name'] if 'name' in properties.keys() else pr_name
                generate_interface_section(linked_entity, optional=optional, previous=entity,
                                           previous_name=new_previous_name, key_name=new_previous_name + str(n))
    if 'name' in properties.keys():
        return properties['name']
    elif len(properties.keys()) > 0:
        return properties[list(properties.keys())[0]]
    else:
        return None


load_dotenv()
conn = nc.Neo4jConnection(uri=os.getenv("URI"), user=os.getenv("USERNAME"), pwd=os.getenv("PASSWORD"))
# conn = nc.Neo4jConnection(uri=os.getenv("URI_CLOUD"),
#                           user=os.getenv("USERNAME_CLOUD"),
#                           pwd=os.getenv("PASSWORD_CLOUD"))

st.title('Создание онтологии проекта')
entities = conn.query("MATCH (a:Base) RETURN a.name AS node_name, ID(a) AS node_id, a.nodeType AS nodeType, "
                      "labels(a) AS node_labels")
entities_df = pd.DataFrame.from_records(entities, columns=['node_name', 'node_id', 'nodeType', 'node_labels'])

for _, i in entities_df.iterrows():
    generate_interface_section(i, first_iteration=True, previous_name='Base')
