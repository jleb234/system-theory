class NodeItem:
    labels = ['B2C']
    subquery = None

    def db_create_node(self, connection):
        connection.query(f"CREATE ({self.subquery})")

    def db_merge_node(self, connection):
        connection.query(f"MERGE ({self.subquery})")

    def get_node_id(self, connection):
        result = connection.query(f"MATCH (n{self.subquery}) RETURN ID(n) AS node_id")
        return result[0]['node_id']


class User(NodeItem):
    class_name = "Пользователь"
    class_description = "Класс пользователей (сегмент пользователей, поведение которых внутри сервиса " \
                        "может различаться, так как различаются потребности, которые они закрывают с помощью сервиса)"
    labels = NodeItem.labels + ['User']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


class Reason(NodeItem):
    class_name = "Причина"
    class_description = "класс причин использования сервиса, или состояний, в котором находится пользователь " \
                        "и которое побуждает его воспользоваться сервисом"
    labels = NodeItem.labels + ['Reason']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


class Step(NodeItem):
    class_name = "Шаг сценария"
    class_description = "Шаг сценария использования сервиса без привязки к конкретной реализации " \
                        "данного шага внутри сервиса"
    labels = NodeItem.labels + ['Step']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


class Action(NodeItem):
    class_name = "Действие"
    class_description = "Техническое действие (может быть действием пользователя или «реакцией» сервиса), " \
                        "в набор которых материализуется шаг сценария"
    labels = NodeItem.labels + ['Action']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


class ViewAction(Action):
    class_name = "Просмотр"
    class_description = "Просмотр или появление в поле видимости какого-либо интерфейсного элемента"
    labels = Action.labels + ['View']


class ClickAction(Action):
    class_name = "Нажатие"
    class_description = "Нажатие (например, на кнопку или баннер)"
    labels = Action.labels + ['Click']


class Interface(NodeItem):
    class_name = "Элемент интерфейса"
    class_description = "Элемент пользовательского интерфейса, с которым пользователь осуществляет взаимодействие"
    labels = NodeItem.labels + ['Interface']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


class ButtonInterface(Interface):
    class_name = "Кнопка"
    class_description = "Кнопка"
    labels = Action.labels + ['Button']


class ScreenInterface(Interface):
    class_name = "Экран"
    class_description = "Экран"
    labels = Action.labels + ['Screen']


class Event(NodeItem):
    class_name = "Событие"
    class_description = "Событие (лог), которое вызывается в момент совершения действия для каждого уникального " \
                        "пользователя и в соответствии с которыми впоследствии можно осуществлять анализ поведения " \
                        "пользователя"
    labels = NodeItem.labels + ['Event']

    def __init__(self, name: str, user_label: str, codename: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.codename = codename
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}', codename: '{self.codename}'}}"