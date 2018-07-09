import csv
import datetime
import sys
import sqlite3
import random

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
    def __init__(self, conn, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.conn = conn
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
        c = self.conn.cursor()
        c.execute("SELECT * FROM software")
        for i in c.fetchall():
            software = Software(i[0], i[1], i[2])
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
            c = self.conn.cursor()
            c.execute("SELECT * FROM software WHERE year = :year", {'year': self.year})
            for i in c.fetchall():
                software = Software(i[0], i[1], i[2])
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
        c = self.conn.cursor()
        c.execute("SELECT * FROM software WHERE year = :year", {'year': self.year})
        if c.fetchone() is not None:
            return True

    def populate(self, software):
        self.addSoftware(software)
        self.resultsCounter += 1
        self.resultsNumber.setText("Results ( " + str(self.resultsCounter) + " )")
        c = self.conn.cursor()
        c.execute("INSERT INTO software VALUES (:team, :description, :year)",
                  {'team': software.team, 'description': software.description, 'year': software.year})
        self.conn.commit()

    def refreshList(self):
        self.resultsList.clear()
        c = self.conn.cursor()
        if self.searchedAYear:
            # for line in csvReader:
            #     if int(line[2]) == self.year:
            #         software = Software(line[0], line[1], line[2])
            #         self.addSoftware(software)
            c.execute("SELECT * FROM software WHERE year = :year", {'year': self.year})
        else:
            c.execute("SELECT * FROM software")
        for i in c.fetchall():
            software = Software(i[0], i[1], i[2])
            self.addSoftware(software)
            self.resultsCounter += 1
            self.resultsNumber.setText("Results ( " + str(self.resultsCounter) + " )")

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
            c = self.conn.cursor()
            c.execute("UPDATE software SET description = :description WHERE team = :team AND year = :year",
                      {'team': self.addEditTeam.text(), 'description': self.addEditDescription.toPlainText(),
                       'year': int(self.addEditYear.text())})
            self.conn.commit()
            self.refreshList()
        self.resultsList.setStyleSheet("outline: 0")
        self.stackedWidget.setCurrentIndex(2)
        self.resetAddEditPage()

    def goToResults(self):
        self.stackedWidget.setCurrentIndex(2)
        self.resetAddEditPage()


def main():
    conn = sqlite3.connect('software.db')
    # c.execute("""CREATE TABLE software (
    #             team text,
    #             description text,
    #             year integer
    #             )""")
    # c.execute("INSERT INTO software VALUES ('Rainer', 'Lim', 10)")
    # software = Software("John", "Doe", 11)
    # c.execute("INSERT INTO software VALUES (:team, :description, :year)",
    #           {'team': software.team, 'description': software.description, 'year': software.year})
    # conn.commit()
    # c.execute("SELECT * FROM software WHERE description=:description",
    #           {'description': 'Doe'})
    # print(c.fetchone())
    # conn.commit()
    # conn.close()

    # conn.execute('''
    # CREATE TABLE SOFTWARE
    # (ID INT PRIMARY KEY NOT NULL,
    # TEAM TEXT NOT NULL,
    # DESCRIPTION TEXT NOT NULL,
    # YEAR INT NOT NULL);
    # ''')
    # print("Table created")
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui(conn)
    ui.show()
    sys.exit(app.exec_())
    # conn.close()
    # c = conn.cursor()
    # c.execute("SELECT * FROM software WHERE year=:year", {'year': 2008})
    # print(c.fetchall())
    # conn.commit()
    # conn.close()
    # cursor = conn.execute("SELECT * FROM SOFTWARE WHERE ID=1 LIMIT 1")
    # for row in cursor:
    #     print("ID = ", row[0])
    #     print("TEAM = ", row[1])
    #     print("DESCRIPTION = ", row[2])
    #     print("YEAR = ", row[3])


if __name__ == '__main__':
    main()
