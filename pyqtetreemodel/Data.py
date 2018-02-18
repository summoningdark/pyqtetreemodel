import pyqtgraph as pg
from lxml import etree


class Node(object):
    def __init__(self, parent=None):
        super(Node, self).__init__()

        self._children = []
        self._parent = parent

        if parent is not None:
            parent.addChild(self)

    @property
    def children(self):
        return self._children

    def parent(self):
        return self._parent

    def setParent(self, parent):
        self._parent = parent

    def addChild(self, child):
        self._children.append(child)
        child._parent = self

    def insertChild(self, position, child):

        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):

        if position < 0 or position > len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None

        return True

    def child(self, row):
        if 0 <= row < len(self._children):
            return self._children[row]
        return None

    def childCount(self):
        return len(self._children)

    def columnCount(self):
        return 2

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def data(self, column, role):
        return None

    def setData(self, column, value):
        return False

    def flags(self, column):
        if column < self.columnCount():
            return pg.QtCore.Qt.ItemIsEnabled | pg.QtCore.Qt.ItemIsSelectable | pg.QtCore.Qt.ItemIsEditable
        return pg.QtCore.Qt.NoItemFlags

    def resource(self):
        """
        returns the resource to use for the icon
        :return:
        """
        return None


class ElementNode(Node):
    def __init__(self, element, parent=None):
        super(ElementNode, self).__init__(parent=parent)
        if not isinstance(element, etree._Element):
            raise TypeError('must provide an lxml.etree.element')
        self._element = element

        # create attribute nodes
        for key in self._element.attrib:
            AttributeNode(key, parent=self)
        # create text node
        TextNode(parent=self)
        # create all child nodes
        for child in self._element:
            ElementNode(child, parent=self)

    @property
    def element(self):
        return self._element

    @property
    def numAttributes(self):
        return len(self.element.attrib)

    @property
    def elementChildren(self):
        return list(self.children[self.numAttributes+1:])

    def elementRow(self):
        """
        returns the position of self's etree element in the etree element of self's parent
        :return:
        """
        return self._parent.element.index(self._element)

    def data(self, column, role):
        if role == pg.QtCore.Qt.DisplayRole:
            if column == 0:
                return self.element.tag

    def setData(self, column, value):
        if column == 0:
            self.element.tag = value
            return True
        return False

    def addAttribute(self, key, value):
        if key in self.element.attrib:
            key += '_new'
        self.element.attrib[key] = value
        self.insertChild(self.numAttributes - 1, AttributeNode(key, parent=None))

    def removeAttribute(self, key):
        if key in self.element.attrib:
            node = self.attributeNodeByKey(key)
            if node is not None:
                position = self._children.index(node)
                self.removeChild(position)
            del self.element.attrib[key]

    def addChildElement(self, element=None):
        """
        adds a new child element to the etree and creates a node for it
        :param element: etree.Element
        :return: the new node
        """
        if not isinstance(element, etree._Element):
            element = etree.Element('NewElement')
        self.element.append(element)                    # add the element to the etree
        return ElementNode(element, parent=self)        # create a node for it

    def removeChildElement(self, position):
        """
        removes the child element at position
        :param position:
        :return:
        """
        # remove from etree
        child = self.children[position]                 # get child node
        if isinstance(child, ElementNode):              # can only remove ElementNodes
            i = self._element.index(child.element)      # get index of child element
            del(self._element[i])                       # remove etree element
        # remove child node
        self.removeChild(position)

    def attributeNodeByKey(self, key):
        node = None
        for child in self._children:
            if isinstance(child, AttributeNode):
                if child.key == key:
                    node = child
        return node


class AttributeNode(Node):
    def __init__(self, key, parent=None):
        super(AttributeNode, self).__init__(parent=parent)
        self._key = key

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, new):
        self._parent.element.attrib[new] = self.value           # make a new entry in the element attributes
        del(self._parent.element.attrib[self._key])
        self._key = new

    @property
    def value(self):
        if self._parent is not None:
            return self._parent.element.attrib[self._key]
        return None

    @value.setter
    def value(self, new):
        self._parent.element.attrib[self._key] = new

    def addChild(self, child):
        return False

    def insertChild(self, position, child):
        return False

    def removeChild(self, position):
        return False

    def data(self, column, role):
        if role == pg.QtCore.Qt.DisplayRole:
            if column == 0:
                return self.key
            elif column == 1:
                return self.value

    def setData(self, column, value):
        if column == 0:
            self.key = value
            return True
        elif column == 1:
            self.value = value
            return True
        return False

    def flags(self, column):
        if 0 <= column < self.columnCount():
            return pg.QtCore.Qt.ItemIsEnabled | pg.QtCore.Qt.ItemIsSelectable | pg.QtCore.Qt.ItemIsEditable
        return pg.QtCore.Qt.NoItemFlags


class TextNode(Node):
    def __init__(self, parent=None):
        super(TextNode, self).__init__(parent=parent)

    @property
    def text(self):
        if self._parent is not None:
            return self._parent.element.text
        return None

    def addChild(self, child):
        return False

    def insertChild(self, position, child):
        return False

    def removeChild(self, position):
        return False

    def flags(self, column):
        if 0 < column < self.columnCount():
            return pg.QtCore.Qt.ItemIsEnabled | pg.QtCore.Qt.ItemIsSelectable | pg.QtCore.Qt.ItemIsEditable
        return pg.QtCore.Qt.ItemIsEnabled

    def data(self, column, role):
        if role == pg.QtCore.Qt.DisplayRole:
            if column == 0:
                return 'Text:'
            elif column == 1:
                return self.text

    def setData(self, column, value):
        if column == 1:
            self._parent.element.text = value
