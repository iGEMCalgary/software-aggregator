import sys
import images_rc

from PyQt5 import QtCore, QtGui, QtWidgets


class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ClickableLabel, self).__init__(parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        self.clicked.emit()


class DynamicLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super(DynamicLineEdit, self).__init__(parent)
        self.setStyleSheet("color: rgb(255, 255, 255)")
        self.timer = QtCore.QTimer()
        self.suggestions = ["Enter a team", "Enter a description", "Enter a year"]
        self.index = 0
        self.timer.timeout.connect(self.setupSuggestions)
        self.timer.start(1000)

    def focusInEvent(self, event):
        super(DynamicLineEdit, self).focusInEvent(event)
        self.clear()
        self.timer.stop()

    def setupSuggestions(self):
        if self.index > 2:
            self.index = 0
        self.setText(self.suggestions[self.index])
        self.index += 1


class SoftwareWidget(QtWidgets.QWidget):
    def __init__(self, font, parent=None):
        super(SoftwareWidget, self).__init__(parent)
        self.setStyleSheet('''
        QLabel {
            background: transparent;
            color: rgb(255, 255, 255);
        }
        ''')
        self.vBoxLayout = QtWidgets.QVBoxLayout()
        font.setPointSize(10)
        font.setBold(True)
        self.team = QtWidgets.QLabel()
        self.team.setFont(font)
        font.setBold(False)
        self.description = QtWidgets.QLabel()
        self.description.setFont(font)
        self.description.setWordWrap(True)
        self.description.setAlignment(QtCore.Qt.AlignJustify)
        self.description.setStyleSheet("padding-right: 20px")
        self.year = QtWidgets.QLabel()
        self.year.setFont(font)
        self.vBoxLayout.addWidget(self.team)
        self.vBoxLayout.addWidget(self.description)
        self.vBoxLayout.addWidget(self.year)
        self.setLayout(self.vBoxLayout)

    def setTeam(self, text):
        self.team.setText(text)

    def setDescription(self, text):
        self.description.setText(text)

    def setYear(self, text):
        self.year.setText(text)


class View(object):
    def setupUi(self, window):
        self.font = self.loadFont()
        window.setObjectName("window")
        window.resize(1200, 800)
        window.setStyleSheet('''
        QWidget {
            background: rgb(4, 15, 15);
        }
        QLabel {
            color: rgb(255, 255, 255);
        }
        QLineEdit {
            background: rgb(4, 15, 15);
            color: rgb(255, 255, 255);
            border: none;
        }
        Line {
            background-color: rgb(255, 255, 255);
        }
        QListWidget {
            background: rgb(4, 15, 15);
            color: rgb(255, 255, 255);
            border: none;
            outline: 0;
        }
        QListWidget::item:hover {
            background: rgb(16, 61, 61);
        }
        QListWidget::item:selected {
            background: rgb(87, 115, 122);
        }
        ''')
        self.mainLayout = QtWidgets.QGridLayout(window)
        self.mainLayout.setObjectName("homeLayout")
        self.stackedWidget = QtWidgets.QStackedWidget(window)
        # self.stackedWidget.setLineWidth(1)
        self.stackedWidget.setObjectName("stackedWidget")
        self.homePage = QtWidgets.QWidget()
        self.homePage.setObjectName("homePage")
        self.homeLayout = QtWidgets.QVBoxLayout(self.homePage)
        self.homeLayout.setObjectName("homeLayout")
        # Home Page
        self.viewAllButton = ClickableLabel(self.homePage)
        self.homeQuitButton = ClickableLabel(self.homePage)
        self.intro = QtWidgets.QLabel(self.homePage)
        self.searchQuestion = QtWidgets.QLabel(self.homePage)
        self.searchLine = DynamicLineEdit(self.homePage)
        self.hLine = QtWidgets.QFrame(self.homePage)
        self.setupHomeHeader()
        self.setupHomeBody()
        self.setupHomeFooter()
        self.stackedWidget.addWidget(self.homePage)
        # Scrape Page
        # Input Default Content
        self.mainLayout.addWidget(self.stackedWidget)
        self.retranslateView(window)
        self.stackedWidget.setCurrentIndex(0)

    def loadFont(self):
        fontDb = QtGui.QFontDatabase()
        fontId = fontDb.addApplicationFont('fonts/Raleway-Light.ttf')
        fontFam = fontDb.applicationFontFamilies(fontId)
        return QtGui.QFont(fontFam[0])

    def setupHomeHeader(self):
        hLayout = QtWidgets.QHBoxLayout()
        self.viewAllButton.setObjectName("viewAllButton")
        spacer = QtWidgets.QSpacerItem(20, 200, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.homeQuitButton.setObjectName("homeQuitButton")
        hLayout.addWidget(self.viewAllButton, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        hLayout.addItem(spacer)
        hLayout.addWidget(self.homeQuitButton, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.homeLayout.addLayout(hLayout)

    def setupHomeBody(self):
        font = self.font
        font.setPointSize(60)
        self.intro.setFont(font)
        self.intro.setObjectName("title")
        self.homeLayout.addWidget(self.intro, 0, QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        font.setPointSize(24)
        self.searchQuestion.setFont(font)
        self.searchQuestion.setObjectName("searchQuestion")
        self.homeLayout.addWidget(self.searchQuestion, 0, QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        hLayout = QtWidgets.QHBoxLayout()
        leftSpacer = QtWidgets.QSpacerItem(360, 20, QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Fixed)
        vLayout = QtWidgets.QVBoxLayout()
        self.searchLine.setFont(font)
        self.searchLine.setObjectName("searchLine")
        self.hLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.hLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.hLine.setObjectName("hLine")
        vLayout.addWidget(self.searchLine)
        vLayout.addWidget(self.hLine)
        rightSpacer = QtWidgets.QSpacerItem(360, 20, QtWidgets.QSizePolicy.Minimum,
                                            QtWidgets.QSizePolicy.Fixed)
        hLayout.addItem(leftSpacer)
        hLayout.addLayout(vLayout)
        hLayout.addItem(rightSpacer)
        self.homeLayout.addLayout(hLayout)

    def setupHomeFooter(self):
        hLayout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(20, 200, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        hLayout.addItem(spacer)
        self.homeLayout.addLayout(hLayout)

    def retranslateView(self, window):
        translate = QtCore.QCoreApplication.translate
        window.setWindowTitle(translate("window", "Sara"))
        self.viewAllButton.setText(translate(
            "window", "<html><head/><body><p><img src=\":/Image_2/BookIcon.png\" height=\"30\"/></p></body></html>"))
        self.homeQuitButton.setText(translate(
            "window", "<html><head/><body><p><img src=\":/Image_1/CloseIcon.png\" height=\"30\"/></p></body></html>"))
        self.intro.setText(translate("window", "Hi, I\'m Sara"))
        self.searchQuestion.setText(translate("Form", "What are you looking for ?"))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    view = View()
    view.setupUi(window)
    window.show()
    sys.exit(app.exec_())
