from PyQt5 import QtCore, QtGui, QtWidgets	
from UI import Ui_MainWindow
from autocomplete import MyTextEdit
from startup import welcome_tab
import os

class Functionality(Ui_MainWindow):
	def __init__(self, window, args=None):
		self.setupUi(window)
		self.window = window
		self.editors, self.opened_files = [], []
		if args!=[]:self.open_file(0,args)
	def more(self):
		self.actionOpen.triggered.connect(self.open_file)
		self.actionSave.triggered.connect(self.save_file)
		self.actionNew.triggered.connect(lambda: self.new_tab("New Tab"))
		self.actFind.triggered.connect(self.findAction)
		self.actRep.triggered.connect(self.replaceAction)
		self.actionOpenDir.triggered.connect(self.open_dir)
		self.ShowFR.triggered.connect(self.showFindReplaceTool)

		self.showFindReplaceTool()
		
		self.tabWidget.tabCloseRequested.connect(self.close_tab)
		self.tabWidget.setCurrentIndex(0)	

		self.default_screen()

	def open_file(self, _="", selected_files=[]):
		try:
			if selected_files == []:
				selected_files = QtWidgets.QFileDialog.getOpenFileNames()[0]
			for f in selected_files: self.opened_files.append(f)
			for index in range(len(selected_files)):
				with open(selected_files[index]) as f:
					text = f.read()
				self.new_tab(selected_files[index].split("/")[-1],selected_files[index].split("/")[-1])
				self.editors[len(self.editors)-1].setPlainText(text)

			self.tabWidget.setCurrentIndex(len(self.opened_files)-1)
		except IndexError:
			print("error")

	def open_dir(self):
		try:
			self.chosen_dir = QtWidgets.QFileDialog.getExistingDirectory()
			self.showFileSys()
			self.updateFileSys()
		except:
			pass

	def save_file(self):
		try:
			with open(self.opened_files[self.tabWidget.currentIndex()], 'w') as f:
				f.write(self.editors[self.tabWidget.currentIndex()].toPlainText())
				self.opened_files[self.tabWidget.currentIndex()].split("/")[-1]
		except (AttributeError, FileNotFoundError, IndexError):
			try:
				self.opened_files.append(QtWidgets.QFileDialog.getSaveFileName()[0])
				with open(self.opened_files[self.tabWidget.currentIndex()], 'w') as f:
					f.write(self.editors[self.tabWidget.currentIndex()].toPlainText())
			except (FileNotFoundError, IsADirrectoryError) as e:
				print("an error occured ({0})".format(e))
	def new_tab(self, tab_name, fileName="none"):
		tab = QtWidgets.QWidget()
		self.tabWidget.addTab(tab, tab_name)
		
		syn = ""
		if self.SyntaxHighlightState.isChecked():
			if fileName[-2:] == "py":
				syn = fileName
				te = MyTextEdit(syn, self.use_spaces.isChecked(), tab)
			elif fileName[-4:] == "html":
				syn = fileName 
				te = MyTextEdit(syn, self.use_spaces.isChecked(), tab)
			else:
				te = QtWidgets.QTextEdit()
			                         
		else:
			te = QtWidgets.QtextEdit()
		
		self.editors.append(te)
		self.gridLayout = QtWidgets.QGridLayout(tab)
		self.gridLayout.setSpacing(1)
		self.gridLayout.setObjectName("gridLayout")
		self.gridLayout.addWidget(self.editors[len(self.editors)-1], 1, 2, 1, 1)
		
	def close_tab(self, index):
		self.editors.pop(index)
		self.opened_files.pop(index)
			
		self.tabWidget.removeTab(index)

	def new_file(self):
		self.new_tab("new tab")
		self.opened_files.append("untitled")
		self.tabWidget.setCurrentIndex(len(self.opened_files)-1)

	def default_screen(self):
		tab = QtWidgets.QWidget()
		self.tabWidget.addTab(tab, "ALtext")
		self.editors.append(None)
		self.opened_files.append(None)
		l = welcome_tab(tab)

		l.dir.connect(self.open_dir)
		l.file.connect(self.open_file)
		l.new.connect(self.new_file)

	def findAction(self):
		extra = []
		if self.what2find.text() != "":
			self.editors[self.tabWidget.currentIndex()].moveCursor(QtGui.QTextCursor.Start)
			while  self.editors[self.tabWidget.currentIndex()].find(self.what2find.text()):
				selection = self.editors[self.tabWidget.currentIndex()].ExtraSelection()
				selection.format.setBackground(QtGui.QColor(QtCore.Qt.yellow))
				selection.cursor = self.editors[self.tabWidget.currentIndex()].textCursor()
				extra.append(selection)
				for v in extra:
					self.editors[self.tabWidget.currentIndex()].setExtraSelections(extra)
		else:
			selection = self.editors[self.tabWidget.currentIndex()].ExtraSelection()
			selection.format.setBackground(QtGui.QColor(QtCore.Qt.yellow))
			selection.cursor = self.editors[self.tabWidget.currentIndex()].textCursor()
			extra.append(selection)
			self.editors[self.tabWidget.currentIndex()].setExtraSelections(extra)

	def replaceAction(self):
		extra = []
		if self.what2rep.text() != "" and self.what2find.text() != "":
			self.editors[self.tabWidget.currentIndex()].moveCursor(QtGui.QTextCursor.Start)
			while self.editors[self.tabWidget.currentIndex()].find(self.what2find.text()):
				selection = self.editors[self.tabWidget.currentIndex()].ExtraSelection()
				help(selection.format)#.format.setText(what2rep.text())
				selection.cursor = self.editors[self.tabWidget.currentIndex()].textCursor()
				extra.append(selection)
				for v in extra:
					self.editors[self.tabWidget.currentIndex()].setExtraSelections(extra)

	def showFileSys(self):
		self.dockWidget = QtWidgets.QDockWidget(self.window)
		self.dockWidgetContents = QtWidgets.QWidget()
		self.dockWidgetContents.setObjectName("dockWidgetContents")
		self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
		self.verticalLayout_2.setObjectName("verticalLayout_2")
		self.treeWidget = QtWidgets.QTreeWidget(self.dockWidgetContents)
		self.treeWidget.setAnimated(True)
		self.treeWidget.itemClicked.connect(self.openTreeItem)
		self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)  
		self.treeWidget.customContextMenuRequested.connect(self.FileTreeRightClickMenu)  
		
		self.verticalLayout_2.addWidget(self.treeWidget)
		self.dockWidget.setWidget(self.dockWidgetContents)
		self.window.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget)
		
		_translate = QtCore.QCoreApplication.translate
		self.dockWidget.setWindowTitle(_translate("MainWindow", "System"))
		self.treeWidget.headerItem().setText(0, _translate("MainWindow", "File Tree"))
		__sortingEnabled = self.treeWidget.isSortingEnabled()
		self.treeWidget.setSortingEnabled(False)
		self.treeWidget.setSortingEnabled(__sortingEnabled)
	
	def updateFileSys(self):
		self.treeWidget.clear()
		
		global items, cnt
		items, cnt = [self.treeWidget], -1

		def find(w):
			global cnt
			for (dirpath, dirnames, filenames) in os.walk(str(w)):
				for d in dirnames:
					i = QtWidgets.QTreeWidgetItem(items[-1])
					i.setText(0,d)
					items.append(i)
					find(f"{w}/{d}")
				for f in filenames:
					i = QtWidgets.QTreeWidgetItem(items[-1])
					i.setText(0,f)
				items.pop(-1)
				break
		try:
			find(self.chosen_dir)
		except:
			pass

	def openTreeItem(self, item):
		try:
			then_path, p = "", item.parent()
			while p != None: then_path = p.text(0)+"/"+then_path; p = p.parent()
			if os.path.isdir(f"{self.chosen_dir}/{then_path}{item.text(0)}"): return
			if f"{self.chosen_dir}/{then_path}{item.text(0)}" not in self.opened_files:
				self.open_file(0,[f"{self.chosen_dir}/{then_path}{item.text(0)}"])
				self.tabWidget.setCurrentIndex(len(self.opened_files)-1)
			else:
				self.tabWidget.setCurrentIndex(self.opened_files.index(f"{self.chosen_dir}/{then_path}{item.text(0)}"))
		except:
			pass


	def FileTreeRightClickMenu(self, event):	
		self.treeMenu = QtWidgets.QMenu(self.treeWidget)
		newMenu = self.treeMenu.addMenu("new")
		newFile = newMenu.addAction("file")
		newDir = newMenu.addAction("directory")
		self.treeMenu.addSeparator()
		rename =  self.treeMenu.addAction("Rename")
		trash = self.treeMenu.addAction("Trash")
		self.treeMenu.addSeparator()
		refresh = self.treeMenu.addAction("Refresh")
		act = self.treeMenu.exec_(self.treeWidget.mapToGlobal(event))
		if act is not None:
			item = self.treeWidget.indexAt(event)
			then_path, p = "", item.parent()
			while p.data() != None: then_path = p.data(0)+"/"+then_path; p = p.parent()
			file_path = f"{self.chosen_dir}/{then_path}{item.data()}"
			if act == trash:
				os.system("gio trash "+file_path)
			elif act == rename:				
					text, ok = QtWidgets.QInputDialog.getText(self.window,"Rename","new name:", QtWidgets.QLineEdit.Normal)
					if ok and text != "":
						os.system(f"mv {file_path} {self.chosen_dir}/{then_path}{text}")
			elif act == newFile:
				text, ok = QtWidgets.QInputDialog.getText(self.window,"New File","file name:", QtWidgets.QLineEdit.Normal)
				if ok and text != "": 
					if os.path.isdir(file_path): os.system(f"touch {self.chosen_dir}/{then_path}{item.data()}/{text}")
					else: os.system(f"touch {self.chosen_dir}/{then_path}/{text}")
			elif act == newDir:
				text, ok = QtWidgets.QInputDialog.getText(self.window,"New Directory","dir name:", QtWidgets.QLineEdit.Normal)
				if ok and text != "": 
					if os.path.isdir(file_path): os.system(f"mkdir {self.chosen_dir}/{then_path}{item.data()}/{text}")
					else: os.system(f"mkdir {self.chosen_dir}/{then_path}/{text}")
			
		self.updateFileSys()

	def showFindReplaceTool(self):
		self.findRep_wigdet = QtWidgets.QDockWidget(self.window)
		self.findRep_wigdetContents = QtWidgets.QWidget()
		self.findRep_layout = QtWidgets.QVBoxLayout(self.findRep_wigdetContents)
		self.what2find, self.what2rep  = QtWidgets.QLineEdit(self.findRep_wigdetContents), QtWidgets.QLineEdit(self.findRep_wigdetContents)
		self.findRep_layout.addWidget(self.what2find)
		self.findRep_layout.addWidget(self.what2rep)
		self.window.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.findRep_wigdet)
		self.findRep_wigdet.setWidget(self.findRep_wigdetContents)
		self.findRep_wigdet.setWindowTitle( "Find/Replace")
