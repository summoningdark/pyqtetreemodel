from pyqtgraph import QtGui, QtCore
from .Models import EtreeModel
from .Data import ElementNode, AttributeNode


class TextEditDelegate(QtGui.QStyledItemDelegate):
    pass


class XmlTreeView(QtGui.QTreeView):
    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setHeaderHidden(True)
        self._delegate = TextEditDelegate()
        self.setItemDelegate(self._delegate)
        self.customContextMenuRequested.connect(self._menu)
        self.collapsed.connect(self.resizeColumns)
        self.expanded.connect(self.resizeColumns)

    def setModel(self, QAbstractItemModel):
        if isinstance(QAbstractItemModel, EtreeModel):
            QtGui.QTreeView.setModel(self, QAbstractItemModel)

    def resizeColumns(self):
        self.resizeColumnToContents(0)

    def _menu(self, pos):
        index = self.indexAt(pos)
        if index.isValid():
            node = index.internalPointer()
            menu = QtGui.QMenu()

            removeAttribute = None
            addAttribute = None
            addChild = None
            addParent = None
            remove = None
            delete = None

            if isinstance(node, AttributeNode):
                removeAttribute = menu.addAction(self.tr('Remove Attribute'))
            elif isinstance(node, ElementNode):
                addAttribute = menu.addAction(self.tr("Add Attribute"))
                addChild = menu.addAction(self.tr("Add Child"))
                addParent = menu.addAction(self.tr("Add Parent"))
                remove = menu.addAction(self.tr("Remove"))
                delete = menu.addAction(self.tr("Delete"))

            foo = menu.exec_(self.viewport().mapToGlobal(pos))
            if foo is not None:
                if foo is removeAttribute:
                    parentIndex = self.model().parent(index)
                    self.model().removeAttribute(parentIndex, node.key)
                elif foo is addAttribute:
                    attributeName = 'NewAttribute'
                    self.model().addAttribute(index, attributeName, '')
                elif foo is addChild:
                    self.model().addChildElement(index)
                elif foo is addParent:
                    self.model().addParentElement(index)
                elif foo is remove:
                    self.model().removeElement(index)
                elif foo is delete:
                    self.model().deleteElement(index)


