from PyQt5 import QtCore, QtGui, QtWidgets


class welcome_tab(QtWidgets.QWidget):
    dir = QtCore.pyqtSignal()
    file = QtCore.pyqtSignal()
    new = QtCore.pyqtSignal()
    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self,*args)
        
        dementions = self.parent().frameGeometry()
        print(dementions)
        
        l = QtWidgets.QLabel(self)
        l.resize(2+dementions.width()/3, 2+dementions.height()/3)
        pixmap = QtGui.QPixmap('./ALtext/img/new_icon.png')
        pixmap = pixmap.scaled(dementions.width()/3, dementions.width()/3, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        l.setPixmap(pixmap)
        l.move(dementions.width()/3,(dementions.height()/2)-dementions.height()/4)
        
        open_dir_btn = QtWidgets.QPushButton('Open Directory', self)
        open_dir_btn.setGeometry(32.5+dementions.width()/3, 10+dementions.height()/2, 130, 35)
        open_file_btn = QtWidgets.QPushButton('Open File', self)
        open_file_btn.setGeometry(32.5+dementions.width()/3, 60+dementions.height()/2, 130, 35)
        open_new_btn = QtWidgets.QPushButton('Create New', self)
        open_new_btn.setGeometry(32.5+dementions.width()/3, 110+dementions.height()/2, 130, 35)

        open_dir_btn.clicked.connect(self.dir.emit)
        open_file_btn.clicked.connect(self.file.emit)
        open_new_btn.clicked.connect(self.new.emit)