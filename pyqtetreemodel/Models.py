from pyqtgraph import QtCore
from lxml import etree
from .Data import ElementNode, Node


class EtreeModel(QtCore.QAbstractItemModel):
    sortRole = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1

    def __init__(self, root, parent=None):
        super(EtreeModel, self).__init__(parent)
        if not isinstance(root, etree._Element):
            raise TypeError('must provide a root lxml.etree.element')
        self._rootNode = Node()
        self._rootNode.addChild(ElementNode(root))

    def rowCount(self, parent):
        if parent.isValid():
            parentNode = parent.internalPointer()
        else:
            parentNode = self._rootNode

        return parentNode.childCount()

    def columnCount(self, parent):
        if parent.isValid():
            parentNode = parent.internalPointer()
        else:
            parentNode = self._rootNode

        return parentNode.columnCount()

    def data(self, index, role):

        if not index.isValid():
            return None

        node = index.internalPointer()

        return node.data(index.column(), role)

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        if index.isValid():

            node = index.internalPointer()

            if role == QtCore.Qt.EditRole:
                if node.setData(index.column(), value):
                    self.dataChanged.emit(index, index)
                    return True
        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return ""
            elif section == 1:
                return ""

    def flags(self, index):
        if index.isValid():
            node = index.internalPointer()
        else:
            node = self._rootNode
        return node.flags(index.column())

    def parent(self, index):

        node = self.getNode(index)
        parentNode = node.parent()

        if parentNode == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent=QtCore.QModelIndex()):

        parentNode = self.getNode(parent)

        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        success = False
        parentNode = self.getNode(parent)

        self.beginInsertRows(parent, position, position + rows - 1)

        for row in range(rows):
            childCount = parentNode.childCount()
            element = etree.Element("untitled" + str(childCount))
            childNode = ElementNode(element)
            success = parentNode.insertChild(position, childNode)

        self.endInsertRows()

        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):

        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)

        for row in range(rows):
            success = parentNode.removeChild(position)

        self.endRemoveRows()

        return success

    def addAttribute(self, index, key, value):
        """
        adds an attribute to the element at 'index'.
        :param index: QModelIndex
        :param key: string
        :param value:
        :return:
        """
        node = self.getNode(index)
        if isinstance(node, ElementNode):
            self.beginInsertRows(index, node.numAttributes, node.numAttributes)
            node.addAttribute(key, value)
            self.endInsertRows()

    def removeAttribute(self, index, key):
        """
        removes the attribute with 'key' from the element at 'index'
        :param index: QModelIndex
        :param key: string
        :param value:
        :return:
        """
        node = self.getNode(index)
        if isinstance(node, ElementNode):
            attributeNode = node.attributeNodeByKey(key)
            children = node.children
            position = children.index(attributeNode)
            self.beginRemoveRows(index, position, position)
            node.removeAttribute(key)
            self.endRemoveRows()

    def addChildElement(self, index):
        """
        adds a child element to the element referenced by index
        :param index: QModelIndex
        :return:
        """
        node = self.getNode(index)
        if isinstance(node, ElementNode):
            self.beginInsertRows(index, node.childCount(), node.childCount())
            node.addChildElement()
            self.endInsertRows()

    def addParentElement(self, index):
        """
        inserts a parent element immediately above the node referenced by index
        :param index: QModelIndex
        :return:
        """
        node = self.getNode(index)
        parentindex = self.parent(index)                        # get the parent QModelIndex
        parentnode = node.parent()                              # get the parent Node
        if parentnode is not self._rootNode:
            row = node.row()
            elementRow = node.elementRow()

            # make the necessary changes to the etree
            newElement = etree.Element('NewElement')            # make the new etree element
            newElementNode = ElementNode(newElement)            # make the new ElementNode
            parentnode.element[elementRow] = newElement         # put the new element in position
            newElement.append(node.element)                     # add the current element as a child

            # make the necessary changes to the nodes
            self.beginRemoveRows(parentindex, row, row)
            parentnode.removeChild(row)
            self.endRemoveRows()

            self.beginInsertRows(parentindex, row, row)
            parentnode.insertChild(row, newElementNode)
            newElementNode.addChild(node)
            self.endInsertRows()
        else:
            # make the necessary changes to the etree
            newElement = etree.Element('NewElement')  # make the new etree element
            newElementNode = ElementNode(newElement)  # make the new ElementNode
            newElement.append(node.element)           # add the current element as a child
            # make the necessary changes to the nodes
            self._rootNode.removeChild(0)
            self._rootNode.addChild(newElementNode)
            newElementNode.addChild(node)
            self.reset()

    def removeElement(self, index):
        """
        removes an element. all children of the removed element become children of the removed element's parent
        :param index: QModelIndex
        :return:
        """
        node = self.getNode(index)
        if isinstance(node, ElementNode):
            row = node.row()                        # position of the node in its parent
            elementrow = node.elementRow()          # position of the node's element in the parent's element
            parent = node.parent()                  # parent node
            childList = node.elementChildren        # save the list of all the element children under node
            self.deleteElement(index)               # get rid of the element
            for child in reversed(childList):       # loop through all the children in reverse order
                parent.element.insert(elementrow, child.element)
                parent.insertChild(row, child)

    def deleteElement(self, index):
        """
        deletes an element. all children are deleted as well
        :param index: QModelIndex
        :return:
        """
        node = self.getNode(index)
        if isinstance(node, ElementNode):
            parentindex = self.parent(index)        # get the parent QModelIndex
            parent = node.parent()                  # get the parent node
            if parent is not self._rootNode:        # can't delete the last node
                row = node.row()
                self.beginRemoveRows(parentindex, row, row)
                parent.removeChildElement(row)
                self.endRemoveRows()

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._rootNode

    def getXMLRoot(self):
        return self._rootNode.child(0).element

    def setXMLRoot(self, root):
        if not isinstance(root, etree._Element):
            raise TypeError('must provide a root lxml.etree.element')
        self._rootNode.removeChild(0)
        self._rootNode.addChild(ElementNode(root))
        self.reset()
