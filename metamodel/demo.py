from dotenv import load_dotenv
import neo4j_db_connector as nc
import os

from nodes import Scenario, AppStep, UserStep, BranchType
from relations import Preceede, Include

if __name__ == '__main__':
    load_dotenv()
    conn = nc.Neo4jConnection(uri=os.getenv("URI"), user=os.getenv("USERNAME"), pwd=os.getenv("PASSWORD"))

    sc = Scenario(name='Быстрый выбор фильма')
    sc.db_merge_node(conn)
    print(type(sc).__name__)



    step1 = AppStep("Отображение страницы фильма", BranchType.main)
    step1.db_merge_node(conn)
    step2 = UserStep("Клик по кнопке `смотреть`", BranchType.main)
    step2.db_merge_node(conn)

    rel1 = Include(sc, step1)
    rel1.db_create_relation(conn)
    rel2 = Preceede(step1, step2)
    rel2.db_create_relation(conn)

    print(rel1)
    print(rel2)
