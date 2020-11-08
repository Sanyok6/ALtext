from PyQt5 import QtGui,QtCore, QtWidgets
import jedi


class MyTextEdit(QtWidgets.QTextEdit):
    def __init__(self,syntax="none", use_spaces=True, *args):
        QtWidgets.QLineEdit.__init__(self,*args)
        if syntax[-2:] == "py":
             import pySyntax
             highlight = pySyntax.PythonHighlighter(self)
             self.completeMenu = QtWidgets.QListWidget(self)
             self.completeMenu.hide()

             self.thread = completeThread(self.completeMenu)
             self.thread.clearSignal.connect(lambda: self.completeMenu.hide())
             self.thread.showSignal.connect(self.showMenu)
        elif syntax[-4:] == "html":
             import htmlSyntax
             highlight = htmlSyntax.HtmlHighlighter(self)
    
        font=QtGui.QFont()
        font.setPointSize(11)
        self.setFont(font)
        self.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.setTabStopWidth(33)
        self.setAcceptRichText(False)

        self.old_key = None
        self.tab_count = 0
        self.syntax = syntax
        self.use_spaces = use_spaces

    def showMenu(self, comps):
        cr = self.cursorRect()
        cr.setWidth(50)
        cr = QtCore.QRect(cr)
        for a in comps:
           self.completeMenu.addItem(a.name)
        self.completeMenu.setCurrentRow(0)
        self.completeMenu.move(cr.getCoords()[0], cr.getCoords()[3])
        self.completeMenu.show()

    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = (len(completion) - len(self.textUnderCursor()))
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        if extra != 0:
             tc.insertText(completion[-extra:])
             self.setTextCursor(tc)
    
    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        if tc.selectedText() == ")":
            tc.setPosition(tc.position()-2)
            tc.select(QtGui.QTextCursor.WordUnderCursor)
        #print(tc.selectedText())
        return tc.selectedText()
        
    def mousePressEvent(self, event):
        if self.syntax[-2:] == "py":
            self.completeMenu.hide()
        QtWidgets.QTextEdit.mousePressEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_ParenLeft:
            tc = self.textCursor()
            tc.insertText(")")
            tc.movePosition(QtGui.QTextCursor.Left)
            self.setTextCursor(tc)
        elif event.key() in (QtCore.Qt.Key_BracketLeft, QtCore.Qt.Key_BraceLeft, QtCore.Qt.Key_QuoteDbl):
            tc = self.textCursor()
            if event.key() == 91: tc.insertText("]")
            elif event.key() == 34: tc.insertText('"') 
            else: tc.insertText("}")
            tc.movePosition(QtGui.QTextCursor.Left)
            self.setTextCursor(tc)
         
        if self.syntax[-2:] == "py":
            self.pressEventPython(event)
        elif self.syntax[-4:] == "html":
            self.htmlPressEvent(event)

    def pressEventPython(self, event):
        if self.textUnderCursor().__len__() > 0 and self.old_key not in (QtCore.Qt.Key_Up, QtCore.Qt.Key_Down, QtCore.Qt.Key_Left, QtCore.Qt.Key_Right, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Tab, QtCore.Qt.Key_Return):
            if event.key() in (QtCore.Qt.Key_Enter,QtCore.Qt.Key_Return,QtCore.Qt.Key_Tab):
                self.old_key = event.key()
                try:
                    self.insertCompletion(self.completeMenu.currentItem().text())
                    self.completeMenu.hide()
                    return
                except:
                    pass
            elif event.key() in (QtCore.Qt.Key_Up, QtCore.Qt.Key_Down):
                if event.key() == QtCore.Qt.Key_Up:
                    self.completeMenu.setCurrentRow(self.completeMenu.currentRow()-1)
                else:
                    self.completeMenu.setCurrentRow(self.completeMenu.currentRow()+1)
                    return
        elif event.key() == QtCore.Qt.Key_Return:
            self.insertPlainText("\n")
            for v in range(self.tab_count): self.insertPlainText('    ' if self.use_spaces else "\t")
            self.old_key = "indent"
            return
        elif event.key() == QtCore.Qt.Key_Tab:
            self.insertPlainText('    ' if self.use_spaces else "\t")
            self.tab_count += 1
            return
        elif event.key() == QtCore.Qt.Key_Backspace and self.old_key == "indent" or type(self.old_key)  == int:
            if not self.use_spaces: self.tab_count -= 1
            else: 
                if self.old_key == "indent": self.old_key = 1
                elif self.old_key == 4: self.tab_count -=1; self.old_key = 1; print("changed")
                else: self.old_key += 1
            
        self.completeMenu.hide()
        QtWidgets.QTextEdit.keyPressEvent(self, event)        
       
        completionPrefix = self.textUnderCursor()
        if completionPrefix.__len__() > 0 and self.old_key not in (QtCore.Qt.Key_Up, QtCore.Qt.Key_Down, QtCore.Qt.Key_Left, QtCore.Qt.Key_Right):
            self.completeMenu.clear()
            self.thread.passArgs(self.toPlainText(), (self.textCursor().blockNumber()+1, self.textCursor().columnNumber()))
            self.thread.start()	

        if event.key() != QtCore.Qt.Key_Backspace: self.old_key = event.key()

    def htmlPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Less:
            tc = self.textCursor()
            tc.insertText(">")
            tc.movePosition(QtGui.QTextCursor.Left)
            self.setTextCursor(tc)
        elif event.key() == QtCore.Qt.Key_Slash and self.old_key == QtCore.Qt.Key_Less:
            text = self.toPlainText()
            opened = []
            num = 0
            phrase = ""
            while num < text.__len__()-1:
                if text[num] == "<":
                    while text[num] not in (" ",">") and num < text.__len__()-1:
                        phrase += text[num]
                        num += 1
                    if phrase.__len__() < 2:
                        break
                    elif phrase[1] == "/":
                        opened.remove(phrase[2:])
                    elif phrase[1:] not in ("input", "br", "!--"):
                        opened.append(phrase[1:])
                    phrase = ""
                elif text[num] in ("'", '"'):
                    paren = text[num]
                    num += 1
                    while text[num] != paren and num < text.__len__()-1:
                        num += 1
                    num+=1
                else:
                    num += 1
            if opened != []:
                tc = self.textCursor()
                tc.insertText("/"+opened[-1])
                tc.movePosition(QtGui.QTextCursor.EndOfLine)
                self.setTextCursor(tc)
                return 
        elif event.key() == QtCore.Qt.Key_Return:
            self.insertPlainText("\n")
            for v in range(self.tab_count): self.insertPlainText('    ' if self.use_spaces else "\t")
            self.old_key = "indent"
            return
        elif event.key() == QtCore.Qt.Key_Tab:
            self.insertPlainText('    ' if self.use_spaces else "\t")
            self.tab_count += 1
            return
        elif event.key() == QtCore.Qt.Key_Backspace and self.old_key == "indent" or type(self.old_key)  == int:
            if not self.use_spaces: self.tab_count -= 1
            else: 
                if self.old_key == "indent": self.old_key = 1
                elif self.old_key == 4: self.tab_count -=1; self.old_key = 1; print("changed")
                else: self.old_key += 1
        
        QtWidgets.QTextEdit.keyPressEvent(self, event)
        
        if event.key() != QtCore.Qt.Key_Backspace: self.old_key = event.key()



class completeThread(QtCore.QThread):
    clearSignal = QtCore.pyqtSignal()
    showSignal = QtCore.pyqtSignal(list)
    def __init__(self, parent=None):
       QtCore.QThread.__init__(self, parent)
       self.menu = parent
       self.old_len = 0
       
    def passArgs(self, edit, cursor):
       self.edit = edit
       self.cursor = cursor

    def run(self):
        try:
            script = jedi.Script(self.edit)
            self.completions = script.complete(*self.cursor)
            if len(self.completions) == self.old_len: #this checks if the newly generated completions are shorter
                script = jedi.Script(self.edit)               #than the new ones, this is implemented to reduse error.
                self.completions = script.complete(*self.cursor)
            if self.completions != []:
                self.showSignal.emit(self.completions)
            else: self.clearSignal.emit() 
            self.old_len = len(self.completions)

        except: self.clearSignal.emit()




