from lxml import etree
from pyqtgraph import Qt, QtGui
from pyqtetreemodel import EtreeModel

import sys

""" make the test window"""
base, form = Qt.uic.loadUiType("test.ui")


class TestWin(base, form):

    def __init__(self, model, parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)

        self._model = model

        self.uiTree.setModel(self._model)
        self.exportButton.clicked.connect(self.export)
        self.importButton.clicked.connect(self.parse)

    def export(self):
        text = etree.tostring(self._model.getXMLRoot(), pretty_print=True)
        self.textEdit.setPlainText(text.decode('utf8'))

    def parse(self):
        text = self.textEdit.toPlainText()
        root = etree.fromstring(text)
        self._model.setXMLRoot(root)


""" Make some simple XML with etree"""
root = etree.Element('xmlRoot', {'attrib1': 'foo'})
child1 = etree.SubElement(root, 'Child1')
etree.SubElement(child1, 'SubChild1')
etree.SubElement(root, 'Child2')

"""initialize the EtreeModel with the root element of our xml"""
m = EtreeModel(root, parent=None)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle("cleanlooks")

    wnd = TestWin(m)            # make the test window
    wnd.show()                  # show it

    sys.exit(app.exec_())

