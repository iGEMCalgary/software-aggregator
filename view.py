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
        self.setStyleSheet('''
        QLineEdit {
            border: none;
            padding: 0px;
        }
        ''')
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
        }
        ''')
        self.hBoxLayout = QtWidgets.QHBoxLayout()
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
            border: 1px solid #ffffff;
            padding: 10px;
        }
        QTextEdit {
            color: rgb(255, 255, 255);
            border: 1px solid #ffffff;
            padding: 10px;
        }
        Line {
            background-color: rgb(255, 255, 255);
        }
        QListWidget {
            background: rgb(4, 15, 15);
            border: none;
            color: rgb(255, 255, 255);
            outline: 0;
        }
        QListWidget::item:hover {
            background: rgb(16, 61, 61);
        }
        QListWidget::item:selected {
            background: rgb(87, 115, 122);
        }
        QScrollBar:vertical {
            background: white;
            border: 1px solid #ffffff;
            margin: 0px 0px 0px 0px;
            width: 10px;
        }
        QScrollBar::handle:vertical {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop: 0 rgb(4, 15, 15), stop: 0.5 rgb(4, 15, 15), stop:1 rgb(4, 15, 15));
            min-height: 0px;
        }
        QScrollBar::add-line:vertical {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop: 0 rgb(4, 15, 15), stop: 0.5 rgb(4, 15, 15),  stop:1 rgb(4, 15, 15));
            height: 0px;
            subcontrol-origin: margin;
            subcontrol-position: bottom;
        }
        QScrollBar::sub-line:vertical {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop: 0  rgb(4, 15, 15), stop: 0.5 rgb(4, 15, 15),  stop:1 rgb(4, 15, 15));
            height: 0 px;
            subcontrol-origin: margin;
            subcontrol-position: top;
        }
        ''')
        self.mainLayout = QtWidgets.QGridLayout(window)
        self.mainLayout.setObjectName("homeLayout")
        self.stackedWidget = QtWidgets.QStackedWidget(window)
        self.stackedWidget.setObjectName("stackedWidget")
        # Home Page
        self.homePage = QtWidgets.QWidget()
        self.homePage.setObjectName("homePage")
        self.homeLayout = QtWidgets.QVBoxLayout(self.homePage)
        self.homeLayout.setObjectName("homeLayout")
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
        self.scrapePage = QtWidgets.QWidget()
        self.scrapePage.setObjectName("scrapePage")
        self.scrapeLayout = QtWidgets.QVBoxLayout(self.scrapePage)
        self.scrapeLayout.setObjectName("scrapeLayout")
        self.scrapeBackButton = ClickableLabel(self.scrapePage)
        self.scrapeQuitButton = ClickableLabel(self.scrapePage)
        self.scrapeMessage = QtWidgets.QLabel(self.scrapePage)
        self.scrapeQuestion = QtWidgets.QLabel(self.scrapePage)
        self.scrapeYesButton = ClickableLabel(self.scrapePage)
        self.scrapeNoButton = ClickableLabel(self.scrapePage)
        self.setupScrapeHeader()
        self.setupScrapeBody()
        self.setupScrapeFooter()
        self.stackedWidget.addWidget(self.scrapePage)
        # Results Page
        self.resultsPage = QtWidgets.QWidget()
        self.resultsPage.setObjectName("resultsPage")
        self.resultsLayout = QtWidgets.QVBoxLayout(self.resultsPage)
        self.resultsLayout.setObjectName("resultsLayout")
        self.resultsBackButton = ClickableLabel(self.resultsPage)
        self.resultsQuitButton = ClickableLabel(self.resultsPage)
        self.resultsMessage = QtWidgets.QLabel(self.resultsPage)
        self.resultsProgressBar = QtWidgets.QProgressBar(self.resultsPage)
        self.resultsNumber = QtWidgets.QLabel(self.resultsPage)
        self.resultsCounter = 0
        self.resultsList = QtWidgets.QListWidget(self.resultsPage)
        self.resultsAddButton = ClickableLabel(self.resultsPage)
        self.resultsEditButton = ClickableLabel(self.resultsPage)
        self.setupResultsHeader()
        self.setupResultsBody()
        self.setupResultsFooter()
        self.stackedWidget.addWidget(self.resultsPage)
        # Add/Edit Page
        self.addEditPage = QtWidgets.QWidget()
        self.addEditPage.setObjectName("addEditPage")
        self.addEditLayout = QtWidgets.QVBoxLayout(self.addEditPage)
        self.addEditLayout.setObjectName("addEditLayout")
        self.addEditBackButton = ClickableLabel(self.addEditPage)
        self.addEditQuitButton = ClickableLabel(self.addEditPage)
        self.addEditMessage = QtWidgets.QLabel(self.addEditPage)
        self.teamLabel = QtWidgets.QLabel(self.addEditPage)
        self.descriptionLabel = QtWidgets.QLabel(self.addEditPage)
        self.yearLabel = QtWidgets.QLabel(self.addEditPage)
        self.addEditTeam = QtWidgets.QLineEdit(self.addEditPage)
        self.addEditDescription = QtWidgets.QTextEdit(self.addEditPage)
        self.addEditYear = QtWidgets.QLineEdit(self.addEditPage)
        self.addEditConfirmButton = ClickableLabel(self.addEditPage)
        self.addEditCancelButton = ClickableLabel(self.addEditPage)
        self.setupAddEditHeader()
        self.setupAddEditBody()
        self.setupAddEditFooter()
        self.stackedWidget.addWidget(self.addEditPage)
        # Finish Initialization
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
        lSpacer = QtWidgets.QSpacerItem(340, 20, QtWidgets.QSizePolicy.Minimum,
                                        QtWidgets.QSizePolicy.Fixed)
        vLayout = QtWidgets.QVBoxLayout()
        self.searchLine.setFont(font)
        self.searchLine.setObjectName("searchLine")
        self.hLine.setStyleSheet("background-color: rgb(255, 255, 255)")
        self.hLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.hLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.hLine.setObjectName("hLine")
        vLayout.addWidget(self.searchLine)
        vLayout.addWidget(self.hLine)
        rSpacer = QtWidgets.QSpacerItem(340, 20, QtWidgets.QSizePolicy.Minimum,
                                        QtWidgets.QSizePolicy.Fixed)
        hLayout.addItem(lSpacer)
        hLayout.addLayout(vLayout)
        hLayout.addItem(rSpacer)
        self.homeLayout.addLayout(hLayout)

    def setupHomeFooter(self):
        hLayout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(20, 200, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        hLayout.addItem(spacer)
        self.homeLayout.addLayout(hLayout)

    def setupScrapeHeader(self):
        hLayout = QtWidgets.QHBoxLayout()
        self.scrapeBackButton.setObjectName("scrapeBackButton")
        spacer = QtWidgets.QSpacerItem(20, 200, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.scrapeQuitButton.setObjectName("scrapeQuitButton")
        hLayout.addWidget(self.scrapeBackButton, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        hLayout.addItem(spacer)
        hLayout.addWidget(self.scrapeQuitButton, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.scrapeLayout.addLayout(hLayout)

    def setupScrapeBody(self):
        font = self.font
        font.setPointSize(24)
        vLayout = QtWidgets.QVBoxLayout()
        self.scrapeMessage.setFont(font)
        self.scrapeMessage.setObjectName("scrapeMessage")
        self.scrapeQuestion.setFont(font)
        self.scrapeQuestion.setObjectName("scrapeQuestion")
        font.setPointSize(16)
        hLayout = QtWidgets.QHBoxLayout()
        self.scrapeYesButton.setFont(font)
        self.scrapeYesButton.setObjectName("scrapeYesButton")
        self.scrapeNoButton.setFont(font)
        self.scrapeNoButton.setObjectName("scrapeNoButton")
        hLayout.addWidget(self.scrapeYesButton, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        hLayout.addWidget(self.scrapeNoButton, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        vLayout.addWidget(self.scrapeMessage, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        vLayout.addWidget(self.scrapeQuestion, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        vLayout.addLayout(hLayout)
        self.scrapeLayout.addLayout(vLayout)

    def setupScrapeFooter(self):
        hLayout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(20, 200, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        hLayout.addItem(spacer)
        self.scrapeLayout.addLayout(hLayout)

    def setupResultsHeader(self):
        hLayout = QtWidgets.QHBoxLayout()
        self.resultsBackButton.setObjectName("resultsBackButton")
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.resultsQuitButton.setObjectName("resultsQuitButton")
        hLayout.addWidget(self.resultsBackButton, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        hLayout.addItem(spacer)
        hLayout.addWidget(self.resultsQuitButton, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.resultsLayout.addLayout(hLayout)

    def setupResultsBody(self):
        font = self.font
        font.setPointSize(24)
        self.resultsMessage.setFont(font)
        self.resultsMessage.setObjectName("resultsMessage")
        self.resultsLayout.addWidget(self.resultsMessage, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        progressBarLayout = QtWidgets.QHBoxLayout()
        progressLSpacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.resultsProgressBar.setProperty("value", 0)
        self.resultsProgressBar.setObjectName("resultsProgressBar")
        progressRSpacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        progressBarLayout.addItem(progressLSpacer)
        progressBarLayout.addWidget(self.resultsProgressBar)
        progressBarLayout.addItem(progressRSpacer)
        self.resultsLayout.addLayout(progressBarLayout)
        font.setPointSize(16)
        self.resultsNumber.setFont(font)
        self.resultsNumber.setObjectName("resultsNumber")
        self.resultsLayout.addWidget(self.resultsNumber, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        listLayout = QtWidgets.QHBoxLayout()
        listLSpacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        font.setPointSize(10)
        self.resultsList.setFont(font)
        self.resultsList.setObjectName("resultsList")
        self.resultsList.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        listRSpacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        listLayout.addItem(listLSpacer)
        listLayout.addWidget(self.resultsList)
        listLayout.addItem(listRSpacer)
        self.resultsLayout.addLayout(listLayout)
        buttonLayout = QtWidgets.QHBoxLayout()
        font.setPointSize(16)
        self.resultsAddButton.setFont(font)
        self.resultsAddButton.setObjectName("resultsAddButton")
        self.resultsAddButton.hide()
        self.resultsEditButton.setFont(font)
        self.resultsEditButton.setObjectName("resultsEditButton")
        self.resultsEditButton.hide()
        buttonLayout.addWidget(self.resultsAddButton, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        buttonLayout.addWidget(self.resultsEditButton, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.resultsLayout.addItem(
            QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))
        self.resultsLayout.addLayout(buttonLayout)

    def setupResultsFooter(self):
        hLayout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        hLayout.addItem(spacer)
        self.resultsLayout.addLayout(hLayout)

    def setupAddEditHeader(self):
        hLayout = QtWidgets.QHBoxLayout()
        self.addEditBackButton.setObjectName("addEditBackButton")
        spacer = QtWidgets.QSpacerItem(20, 100, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.addEditQuitButton.setObjectName("addEditQuitButton")
        hLayout.addWidget(self.addEditBackButton, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        hLayout.addItem(spacer)
        hLayout.addWidget(self.addEditQuitButton, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.addEditLayout.addLayout(hLayout)

    def setupAddEditBody(self):
        font = self.font
        font.setPointSize(24)
        self.addEditMessage.setFont(font)
        self.addEditMessage.setObjectName("addEditMessage")
        self.addEditLayout.addWidget(self.addEditMessage, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        northSpacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.addEditLayout.addItem(northSpacer)
        textEditLayout = QtWidgets.QGridLayout()
        textEditLSpacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        textEditLayout.addItem(textEditLSpacer, 0, 0)
        font.setPointSize(10)
        self.teamLabel.setFont(font)
        self.teamLabel.setObjectName("teamLabel")
        self.descriptionLabel.setFont(font)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.yearLabel.setFont(font)
        self.yearLabel.setObjectName("yearLabel")
        textEditLayout.addWidget(self.teamLabel, 0, 1, QtCore.Qt.AlignRight)
        textEditLayout.addItem(QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed), 1, 1)
        textEditLayout.addWidget(self.descriptionLabel, 2, 1, QtCore.Qt.AlignRight)
        textEditLayout.addItem(QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed), 3, 1)
        textEditLayout.addWidget(self.yearLabel, 4, 1, QtCore.Qt.AlignRight)
        teamLayout = QtWidgets.QHBoxLayout()
        self.addEditTeam.setFont(font)
        self.addEditTeam.setObjectName("addEditTeam")
        teamSpacer = QtWidgets.QSpacerItem(
            680, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        teamLayout.addWidget(self.addEditTeam)
        teamLayout.addItem(teamSpacer)
        self.addEditDescription.setFont(font)
        self.addEditDescription.setObjectName("addEditDescription")
        yearLayout = QtWidgets.QHBoxLayout()
        self.addEditYear.setFont(font)
        self.addEditYear.setObjectName("addEditYear")
        yearSpacer = QtWidgets.QSpacerItem(
            850, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        yearLayout.addWidget(self.addEditYear)
        yearLayout.addItem(yearSpacer)
        textEditLayout.addLayout(teamLayout, 0, 2)
        textEditLayout.addWidget(self.addEditDescription, 2, 2)
        textEditLayout.addLayout(yearLayout, 4, 2)
        textEditRSpacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        textEditLayout.addItem(textEditRSpacer, 0, 3)
        buttonLayout = QtWidgets.QHBoxLayout()
        font.setPointSize(16)
        self.addEditConfirmButton.setFont(font)
        self.addEditConfirmButton.setObjectName("addEditConfirmButton")
        self.addEditCancelButton.setFont(font)
        self.addEditCancelButton.setObjectName("addEditCancelButton")
        buttonLayout.addWidget(self.addEditConfirmButton, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        buttonLayout.addWidget(self.addEditCancelButton, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.addEditLayout.addLayout(textEditLayout)
        southSpacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.addEditLayout.addItem(southSpacer)
        self.addEditLayout.addLayout(buttonLayout)

    def setupAddEditFooter(self):
        hLayout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(20, 100, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        hLayout.addItem(spacer)
        self.addEditLayout.addLayout(hLayout)

    def retranslateView(self, window):
        _translate = QtCore.QCoreApplication.translate
        window.setWindowTitle(_translate("window", "Sara"))
        # Home Page
        self.viewAllButton.setText(_translate(
            "window", "<html><head/><body><p><img src=\":/Image_2/BookIcon.png\" height=\"30\"/></p></body></html>"))
        self.homeQuitButton.setText(_translate(
            "window", "<html><head/><body><p><img src=\":/Image_1/CloseIcon.png\" height=\"30\"/></p></body></html>"))
        self.intro.setText(_translate("window", "Hi, I\'m Sara"))
        self.searchQuestion.setText(_translate("Form", "What are you looking for ?"))
        # Scrape Page
        self.scrapeBackButton.setText(_translate(
            "window", "<html><head/><body><p><img src=\":/Image_3/BackIcon.png\" height=\"30\"/></p></body></html>"))
        self.scrapeQuitButton.setText(_translate(
            "window", "<html><head/><body><p><img src=\":/Image_1/CloseIcon.png\" height=\"30\"/></p></body></html>"))
        self.scrapeMessage.setText(_translate("window", "I don\'t think I have that year."))
        self.scrapeQuestion.setText(_translate("window", "Would you like me to search the interweb ?"))
        self.scrapeYesButton.setText(_translate("window", "Yes"))
        self.scrapeNoButton.setText(_translate("window", "No ( Return to Home Page )"))
        # Results Page
        self.resultsBackButton.setText(_translate(
            "window", "<html><head/><body><p><img src=\":/Image_3/BackIcon.png\" height=\"30\"/></p></body></html>"))
        self.resultsQuitButton.setText(_translate(
            "window", "<html><head/><body><p><img src=\":/Image_1/CloseIcon.png\" height=\"30\"/></p></body></html>"))
        self.resultsMessage.setText(_translate("window", "Let me see what I can find..."))
        self.resultsNumber.setText(_translate("window", "Results ( 0 )"))
        self.resultsAddButton.setText(_translate("window", "Add"))
        self.resultsEditButton.setText(_translate("window", "Edit"))
        # Add/Edit Page
        self.addEditBackButton.setText(_translate(
            "window", "<html><head/><body><p><img src=\":/Image_3/BackIcon.png\" height=\"30\"/></p></body></html>"))
        self.addEditQuitButton.setText(_translate(
            "window", "<html><head/><body><p><img src=\":/Image_1/CloseIcon.png\" height=\"30\"/></p></body></html>"))
        self.addEditMessage.setText(_translate("window", "New Entry"))
        self.teamLabel.setText(_translate("window", "Team    "))
        self.descriptionLabel.setText(_translate("window", "Description    "))
        self.yearLabel.setText(_translate("window", "Year    "))
        self.addEditConfirmButton.setText(_translate("window", "Save"))
        self.addEditCancelButton.setText(_translate("window", "Cancel"))

    def addSoftware(self, software):
        softwareWidget = SoftwareWidget(self.font)
        softwareWidget.setTeam(software.team)
        softwareWidget.setDescription(software.description)
        softwareWidget.setYear(str(software.year))
        softwareItem = QtWidgets.QListWidgetItem(self.resultsList)
        softwareItem.setSizeHint(softwareWidget.sizeHint())
        self.resultsList.addItem(softwareItem)
        self.resultsList.setItemWidget(softwareItem, softwareWidget)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    view = View()
    view.setupUi(window)
    window.show()
    sys.exit(app.exec_())
