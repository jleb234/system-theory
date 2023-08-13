from dotenv import load_dotenv
import os
import types
import neo4j_db_connector as nc

import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

import b2c_relations
import b2c_nodes

load_dotenv()
conn = nc.Neo4jConnection(uri=os.getenv("NEO4J_URI"),
                          user=os.getenv("NEO4J_USERNAME"),
                          pwd=os.getenv("NEO4J_PASSWORD"))


def get_all_subclasses(ni, res: list):
    """Получение всех допустимых классов объектов"""
    for node in ni.__subclasses__():
        if isinstance(node.__init__, types.FunctionType):
            res.append(node)
        if len(node.__subclasses__()) > 0:
            get_all_subclasses(node, res)
    return res


def get_text_input_value(lbl, values):
    v = st.text_input(lbl)
    values.append(v)


def get_node_form(selected_ntype, node_types_avail, user_label):
    """Отрисовка формы для добавления объекта"""
    for node in node_types_avail:
        if node.__name__ == selected_ntype:
            attrs = [i for i in node.__init__.__code__.co_varnames if i != 'self']
            with st.form("add_node"):
                attr_values = []
                for attr in attrs:
                    if attr == 'user_label':
                        attr_values.append(user_label)
                    else:
                        get_text_input_value(attr, attr_values)

                submitted = st.form_submit_button("Создать")
                if submitted:
                    n = node(*attr_values)
                    n.db_merge_node(conn)
                    st.caption('Объект успешно создан')


def get_items_by_type(node_type, task_label, user_label):
    query = f"MATCH (a:{node_type}:{task_label}:{user_label}) RETURN a.name AS name"
    db_nodes = conn.query(query)
    # print(db_nodes)
    return [n["name"] for n in db_nodes]


def get_node_class(node_name, node_type, user_label, node_module):
    """Получение экземпляра класса Nodes на основе его названия и типа"""
    query = f'MATCH (a:{node_type} {{name: "{node_name}"}}) RETURN a'
    db_nodes = conn.query(query)
    print(db_nodes)
    nds = get_all_subclasses(node_module.NodeItem, [])
    for node in nds:
        if node.__name__ == node_type:
            attrs = [i for i in node.__init__.__code__.co_varnames if i != 'self']
            print(attrs)
            attr_values = []
            for attr in attrs:
                if attr == 'user_label':
                    attr_values.append(user_label)
                else:
                    attr_values.append(db_nodes[0]['a'][attr])
            print(attr_values)
            return node(*attr_values)


def get_relation_form(selected_rtype, rel_types_avail, task_label, user_label, node_module):
    """Отрисовка формы для добавления связи"""
    for rel in rel_types_avail:
        if rel.__name__ == selected_rtype:
            for cnstr in rel.constraints:
                main_node_type = cnstr[0]
                related_node_type = cnstr[1]
                print(main_node_type, related_node_type)
                with st.form(f"add_node_{main_node_type}_{related_node_type}"):
                    main_node_name = st.selectbox(main_node_type,
                                                  get_items_by_type(main_node_type, task_label, user_label),
                                                  key=f'n1_{main_node_type}_{related_node_type}')
                    related_node_name = st.selectbox(related_node_type,
                                                     get_items_by_type(related_node_type, task_label, user_label),
                                                     key=f'n2_{main_node_type}_{related_node_type}')
                    submitted = st.form_submit_button("Создать")
                    if submitted:
                        main_node = get_node_class(main_node_name, main_node_type, user_label, node_module)
                        related_node = get_node_class(related_node_name, related_node_type, user_label, node_module)
                        r = rel(main_node, related_node)
                        r.db_create_relation(conn)
                        st.caption('Связь успешно создана')


def get_graph(task_label, user_label):
    nodes = []
    edges = []

    query_nodes = f'MATCH (a:{task_label}:{user_label}) RETURN a'
    db_nodes = conn.query(query_nodes)
    for db_node in db_nodes:
        nodes.append(Node(id=db_node['a'].element_id, title=db_node['a']['name'],
                          label=db_node['a']['name'], size=25))

    query_rels = f'MATCH (:{task_label}:{user_label})-[r]-(:{task_label}:{user_label}) RETURN r'
    db_rels = conn.query(query_rels)
    for db_rel in db_rels:
        edges.append(Edge(source=db_rel['r'].nodes[0].element_id,
                          label=db_rel['r']['name'],
                          type="CURVE_SMOOTH",
                          target=db_rel['r'].nodes[1].element_id))

    graph_config = Config(width=750,
                          height=500,
                          directed=True,
                          physics=True,
                          hierarchical=False,
                          )

    return agraph(nodes=nodes, edges=edges, config=graph_config)


def get_task_content(task_label, user_label, title, node_module, relations_module):
    st.title(title)

    st.header('Создание объектов')
    node_types = get_all_subclasses(node_module.NodeItem, [])

    node_dict = {}
    for i in node_types:
        node_dict[i.__name__] = i.class_name
    # node_labels = [i.__name__ for i in node_types]
    selected_node_label = st.selectbox("Класс объекта", node_dict.values())
    selected_node_type = [i for i in node_dict if node_dict[i] == selected_node_label][0]
    get_node_form(selected_node_type, node_types, user_label)

    st.header('Создание связей')
    rel_types = get_all_subclasses(relations_module.RelationItem, [])
    rel_dict = {}
    for i in rel_types:
        rel_dict[i.__name__] = i.rel_name
    # rel_labels = [i.__name__ for i in rel_types]
    selected_rel_label = st.selectbox("Тип связи", rel_dict.values())
    selected_rel_type = [i for i in rel_dict if rel_dict[i] == selected_rel_label][0]
    get_relation_form(selected_rel_type, rel_types, task_label, user_label, node_module)

    st.header('Визуализация модели')
    get_graph(task_label, user_label)

    # TODO Добавить таблицу с правилами и кнопку "Запустить правила"
    # TODO Добавить редактируемые правила, если есть возможность скачивать и загружать модель
    # TODO Добавить возможность скачивания и загрузки модели
    del_btn = st.button("Удалить модель")  # TODO Добавить подтверждаение
    if del_btn:
        conn.query(f"MATCH (n:{task_label}:{user_label}) DETACH DELETE n")
        st.experimental_rerun()


if __name__ == '__main__':
    with open('pages/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    name, authentication_status, username = authenticator.login('Login', 'main')

    if st.session_state["authentication_status"]:
        tab1, tab2 = st.tabs(["B2C", "Робот"])
        with tab1:
            get_task_content('B2C', username, 'Аналитика пользовательского поведения в B2C-сервисе',
                             node_module=b2c_nodes, relations_module=b2c_relations)
        with tab2:
            st.title("Робот")

        authenticator.logout('Выйти', 'main', key='unique_key')

    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')
