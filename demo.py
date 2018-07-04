import csv
import datetime
import sys

from PyQt5 import QtCore, QtWidgets

import view
from scraper import Parser
from software import Software
from summarizer import Summarizer


class ScrapeThread(QtCore.QThread):
    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal()
    result = QtCore.pyqtSignal(Software)

    def __init__(self, year):
        QtCore.QThread.__init__(self)
        self.year = year
        self.parser = Parser()
        self.summarizer = Summarizer()

    def __del__(self):
        self.wait()

    def getData(self):
        teamInfo = self.parser.getData(self.year, self.progress)
        teamsWithSoftware = 0
        for i in range(len(teamInfo)):
            result = self.summarizer.summarize(teamInfo[i][1])
            if result['Success'] and len(result['TopNDescription']) > 0:
                teamInfo[i][1] = result['TopNDescription']
                teamsWithSoftware += 1
            else:
                teamInfo[i][1] = 'Unable to retrieve ' + teamInfo[i][0] + ' software.'
            software = Software(teamInfo[i][0], teamInfo[i][1], self.year)
            self.result.emit(software)
            self.progress.emit(50 / len(teamInfo))

    def run(self):
        self.getData()
        self.finished.emit()


class Ui(QtWidgets.QWidget, view.View):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.viewAllButton.clicked.connect(self.viewAll)
        self.homeQuitButton.clicked.connect(self.close)
        self.searchLine.returnPressed.connect(self.startSearching)
        self.scrapeBackButton.clicked.connect(self.back)
        self.scrapeQuitButton.clicked.connect(self.close)
        self.scrapeYesButton.clicked.connect(self.startScraping)
        self.scrapeNoButton.clicked.connect(self.back)
        self.resultsBackButton.clicked.connect(self.back)
        self.resultsQuitButton.clicked.connect(self.close)
        self.resultsAddButton.clicked.connect(self.openAddPage)
        self.resultsEditButton.clicked.connect(self.openEditPage)
        self.addEditBackButton.clicked.connect(self.goToResults)
        self.addEditQuitButton.clicked.connect(self.close)
        self.searchedAYear = False
        self.addEditConfirmButton.clicked.connect(self.confirm)
        self.addEditCancelButton.clicked.connect(self.goToResults)
        self.setFocus()

    def mousePressEvent(self, event):
        focusedWidget = QtWidgets.QApplication.focusWidget()
        if isinstance(focusedWidget, view.DynamicLineEdit):
            self.searchLine.timer.start(1000)
            self.searchLine.clearFocus()
        if isinstance(focusedWidget, QtWidgets.QListWidget):
            self.resultsList.clearSelection()

    def viewAll(self):
        self.searchedAYear = False
        self.resultsCounter = 0
        self.resultsProgressBar.hide()
        self.resultsAddButton.show()
        self.resultsEditButton.show()
        self.resultsMessage.setText("All Software")
        self.resultsList.clear()
        with open('software.csv', 'r', encoding='utf-8') as csvFile:
            csvReader = csv.reader(csvFile)
            for line in csvReader:
                software = Software(line[0], line[1], line[2])
                self.addSoftware(software)
                self.resultsCounter += 1
                self.resultsNumber.setText("Results ( " + str(self.resultsCounter) + " )")
        self.resultsList.verticalScrollBar().setSliderPosition(0)
        self.stackedWidget.setCurrentIndex(2)

    def startSearching(self):
        self.searchedAYear = True
        self.resultsProgressBar.hide()
        self.resultsList.clear()
        self.year = int(self.searchLine.text())
        if not self.inDb():
            self.reset()
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.resultsCounter = 0
            self.resultsMessage.setText("Software from " + str(self.year))
            with open('software.csv', 'r', encoding='utf-8') as csvFile:
                csvReader = csv.reader(csvFile)
                for line in csvReader:
                    if int(line[2]) == self.year:
                        software = Software(line[0], line[1], line[2])
                        self.addSoftware(software)
                        self.resultsCounter += 1
                        self.resultsNumber.setText("Results ( " + str(self.resultsCounter) + " )")
            self.resultsList.verticalScrollBar().setSliderPosition(0)
            self.stackedWidget.setCurrentIndex(2)

    def back(self):
        self.stackedWidget.setCurrentIndex(0)
        self.searchLine.timer.start(1000)
        self.searchLine.clearFocus()

    def startScraping(self):
        self.resultsCounter = 0
        self.resultsMessage.setText("Let me see what I can find...")
        self.resultsProgressBar.show()
        self.resultsAddButton.hide()
        self.resultsEditButton.hide()
        self.resultsNumber.setText("Results ( " + str(self.resultsCounter) + " )")
        self.resultsList.clear()
        self.year = int(self.searchLine.text())
        self.scrapeThread = ScrapeThread(self.year)
        self.resultsProgressBar.setValue(0)
        self.scrapeThread.progress.connect(self.updateProgressBar)
        self.scrapeThread.result.connect(self.populate)
        self.scrapeThread.finished.connect(self.finish)
        self.scrapeThread.start()
        self.stackedWidget.setCurrentIndex(2)

    def updateProgressBar(self, val):
        self.resultsProgressBar.setValue(self.resultsProgressBar.value() + val)

    def inDb(self):
        with open('software.csv', 'r', encoding='utf-8') as csvFile:
            csvReader = csv.reader(csvFile)
            for line in csvReader:
                if int(line[2]) == self.year:
                    return True

    def populate(self, software):
        self.addSoftware(software)
        self.resultsCounter += 1
        self.resultsNumber.setText("Results ( " + str(self.resultsCounter) + " )")
        with open('software.csv', 'a', encoding='utf-8') as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=',', lineterminator='\n')
            csvWriter.writerow([software.team, "" + software.description + "", str(software.year)])

    def refreshList(self):
        self.resultsList.clear()
        with open('software.csv', 'r', encoding='utf-8') as csvFile:
            csvReader = csv.reader(csvFile)
            if self.searchedAYear:
                for line in csvReader:
                    if int(line[2]) == self.year:
                        software = Software(line[0], line[1], line[2])
                        self.addSoftware(software)
            else:
                for line in csvReader:
                    software = Software(line[0], line[1], line[2])
                    self.addSoftware(software)

    def reset(self):
        self.resultsProgressBar.setValue(0)

    def finish(self):
        self.resultsProgressBar.setValue(100)
        self.resultsMessage.setText("Is it me you're looking for ?")
        self.resultsProgressBar.hide()
        self.resultsAddButton.show()
        self.resultsEditButton.show()
        self.reset()

    def openAddPage(self):
        self.addEditMessage.setText("Add Software")
        self.addEditTeam.clear()
        self.addEditDescription.clear()
        now = datetime.datetime.now()
        self.addEditYear.setText(str(now.year))
        self.addEditYear.setEnabled(False)
        self.addEditYear.setStyleSheet("border: none")
        self.stackedWidget.setCurrentIndex(3)

    def openEditPage(self):
        if self.resultsList.selectedItems():
            selectedWidget = self.resultsList.itemWidget(self.resultsList.currentItem())
            self.addEditMessage.setText("Edit Team " + selectedWidget.team.text())
            self.addEditTeam.setText(selectedWidget.team.text())
            self.addEditTeam.setEnabled(False)
            self.addEditTeam.setStyleSheet("border: none")
            self.addEditDescription.setText(selectedWidget.description.text())
            self.addEditYear.setText(selectedWidget.year.text())
            self.addEditYear.setEnabled(False)
            self.addEditYear.setStyleSheet("border: none")
            self.stackedWidget.setCurrentIndex(3)

    def resetAddEditPage(self):
        self.addEditTeam.setEnabled(True)
        self.addEditTeam.setStyleSheet("border: 1px solid #ffffff")
        self.addEditYear.setEnabled(False)
        self.addEditYear.setStyleSheet("border: 1px solid #ffffff")

    def confirm(self):
        if self.addEditTeam.isEnabled():
            software = Software(self.addEditTeam.text(), self.addEditDescription.toPlainText(), self.addEditYear.text())
            self.populate(software)
        else:
            with open('software.csv', 'r', encoding='utf-8') as csvFile:
                csvReader = csv.reader(csvFile)
                lines = list(csvReader)
                for line in lines:
                    if self.addEditTeam.text() in line and self.addEditYear.text() in line:
                        line[1] = self.addEditDescription.toPlainText()
                        break
                with open('software.csv', 'w', encoding='utf-8') as csvFile:
                    csvWriter = csv.writer(csvFile, delimiter=',', lineterminator='\n')
                    csvWriter.writerows(lines)
            self.refreshList()
        self.resultsList.setStyleSheet("outline: 0")
        self.stackedWidget.setCurrentIndex(2)
        self.resetAddEditPage()

    def goToResults(self):
        self.stackedWidget.setCurrentIndex(2)
        self.resetAddEditPage()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
