import graphviz as gv
from IPython.display import Image, display

# oval
PRIMITIVE = "primitive"
# ovals to oval
COMPOSITE = "composite"
# double oval
MULTIVALUED = "multivalued"
# dashed oval
DERIVED = "derived"

# no arrow
MANY_TO_MANY = "none"
# solid arrow
ONE_TO_MANY = "normal"
# open arrow
ONE_TO_ONE = "vee"


class Element():
    """
    Represents an element in a database table.
    """

    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        pass


class Attribute(Element):
    """
    Represents an attribute in a database table.
    Attributes:
        name (str): Name of the attribute.
        display_name (str): Name of the attribute to be displayed. Becomes underlined if pk is True.
        type (str): Type of the attribute. Default is PRIMITIVE. Other options are COMPOSITE, MULTIVALUED, or DERIVED.
        composite_attrs (list[Element]): List of composite attributes in the attribute.
        pk (bool): Primary Key? True if the attribute is a primary key.
    """

    def __init__(self, name: str, type: str = PRIMITIVE, composite_attrs: list[Element] = None, pk: bool = False) -> None:
        self.name = name
        self.display_name = name
        self.type = type
        self.composite_attrs = composite_attrs
        self.pk = pk
        if self.pk:
            self.display_name = "".join([char + '\u0332' for char in name])

    def __str__(self) -> str:
        return self.name


class Entity(Element):
    """
    Represents an entity in a database table.
    Attributes:
        name (str): Name of the entity.
        attributes (list[Attribute]): List of attributes on the entity.
        weak (bool): Weak entity? Set to true to make this a weak entity.
    """

    def __init__(self, name: str, attributes: list[Attribute], weak: bool = False) -> None:
        self.name = name
        self.attributes = attributes
        self.weak = weak

    def __str__(self) -> str:
        return self.name


class Relationship(Element):
    """
    Represents a relationship between two entities in a database.
    Attributes:
        name (str): Name of the relationship.
        entities (list[Entity]): List of entities in the relationship.
        arrows (list[str]): List of arrows for the relationship. Options are MANY_TO_MANY, ONE_TO_MANY, or ONE_TO_ONE.
        attributes (list[Attribute]): List of attributes in the relationship.
        type (str): Type of the relationship. Default is default. Other option is ISA which makes a triangle shape.
        weak (bool): Weak relationship? Set to true to make this a weak relationship.
    """

    def __init__(self, name: str, entities: list[Entity], arrows: list[str], attributes: list[Attribute] = None, type: str = "default", weak: bool = False) -> None:
        self.name = name
        self.type = type
        self.attributes = attributes
        self.entities = entities
        self.arrows = arrows
        self.weak = weak

    def __str__(self) -> str:
        return self.name


class ERDiagram():
    """
    Represents an entity-relationship diagram.
    Attributes:
        title (str): Title of the diagram.
        entities (list[Entity]): List of entities in the diagram.
        relationships (list[Relationship]): List of relationships in the diagram.

    Functions:
        draw(): Draws the entity-relationship diagram and displays it in a notebook.
    """

    def __init__(self, title: str, entities: list[Entity], relationships: list[Relationship]) -> None:
        self.title = title.replace(" ", "_")
        self.entities = entities
        self.relationships = relationships

    def draw_attr(self, dot, attribute: Attribute, parent: Element) -> None:
        # Composite Attribute - ovals to oval
        if attribute.type == COMPOSITE:
            dot.node(f"{parent.name}{attribute.name}",
                     attribute.display_name, shape="ellipse")
            for composite_attr in attribute.composite_attrs:
                dot.node(f"{parent.name}{composite_attr.name}",
                         composite_attr.display_name, shape="ellipse")
                dot.edge(f"{parent.name}{attribute.name}",
                         f"{parent.name}{composite_attr.name}", arrowhead="none")
            dot.edge(
                parent.name, f"{parent.name}{attribute.name}", arrowhead="none")
        # Multivalue Attribute - Double oval
        elif attribute.type == MULTIVALUED:
            dot.node(f"{parent.name}{attribute.name}",
                     attribute.display_name, shape="ellipse", peripheries="2")
            dot.edge(
                parent.name, f"{parent.name}{attribute.name}", arrowhead="none")
        # Derived Attribute - Dashed oval
        elif attribute.type == DERIVED:
            dot.node(f"{parent.name}{attribute.name}",
                     attribute.display_name, shape="ellipse", style="dashed")
            dot.edge(
                parent.name, f"{parent.name}{attribute.name}", arrowhead="none")
        # Primitive Attribute - Oval
        else:
            dot.node(f"{parent.name}{attribute.name}",
                     attribute.display_name, shape="ellipse")
            dot.edge(
                parent.name, f"{parent.name}{attribute.name}", arrowhead="none")

    def draw(self) -> None:
        """
        Draws the entity-relationship diagram.
        """
        dot = gv.Digraph(comment=self.title)

        for relationship in self.relationships:
            if relationship.type == "ISA":
                if relationship.weak:
                    dot.node(relationship.name,
                             relationship.name, shape="triangle", peripheries="2")
                else:
                    dot.node(relationship.name,
                             relationship.name, shape="triangle")
            else:
                if relationship.weak:
                    dot.node(relationship.name,
                             relationship.name, shape="diamond", peripheries="2")
                else:
                    dot.node(relationship.name,
                             relationship.name, shape="diamond")

            if relationship.attributes is not None:
                for attribute in relationship.attributes:
                    self.draw_attr(dot, attribute, relationship)

            for i in range(len(relationship.entities)):
                dot.edge(relationship.name, relationship.entities[i].name,
                         arrowhead=relationship.arrows[i])

        for entity in self.entities:
            if entity.weak:
                dot.node(entity.name, entity.name,
                         shape="box", peripheries="2")
            else:
                dot.node(entity.name, entity.name, shape="box")
            for attribute in entity.attributes:
                self.draw_attr(dot, attribute, entity)

        dot.render(self.title, format="png", cleanup=True)
        display(Image(self.title + ".png"))
