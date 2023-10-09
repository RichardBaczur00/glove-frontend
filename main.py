import sys

from PyQt5.QtWidgets import QApplication

from views.index import IndexPage


if __name__ == '__main__':
    app = QApplication(sys.argv)
    index = IndexPage()
    index.show()
    sys.exit(app.exec_())
    