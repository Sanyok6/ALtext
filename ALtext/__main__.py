from PyQt5 import QtCore, QtGui, QtWidgets	
from functionality import Functionality
from UI import Ui_MainWindow

if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	app.setStyle("Fusion")
	MainWindow = QtWidgets.QMainWindow()
	func = Functionality(MainWindow, sys.argv[1:])
	func.more()
	MainWindow.show()
	sys.exit(app.exec_())

