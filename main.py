import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import tkinter as tk
from PIL import ImageGrab
import argostranslate.package
import argostranslate.translate
import pytesseract
import whisper
import csv
import configparser
import os
import warnings
warnings.simplefilter('ignore')

config_ini = configparser.ConfigParser()
config_ini_path = './config.ini'

## 指定したiniファイルが存在しない場合、エラー発生
#if not os.path.exists(config_ini_path):
#    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_ini_path)

config_ini.read(config_ini_path, encoding='utf-8')

read_settings = config_ini['SETTINGS']
TesseractPath = read_settings.get('TesseractPath')
TessdataPath = read_settings.get('TessdataPath')
WhisperModelPath = read_settings.get('WhisperModelPath')

from_code1 = "ru"
from_code_ocr = "eng"
to_code1 = "en"
from_code2 = "en"
to_code2 = "ja"
audio_path = ""
audio_path_list = ""

jaen_model = read_settings.get('jaen_model') #Japanese
enja_model = read_settings.get('enja_model') #EN > JA
ruen_model = read_settings.get('ruen_model') #Russian
koen_model = read_settings.get('koen_model') #Korean
zhen_model = read_settings.get('zhen_model') #Chinese
zten_model = read_settings.get('zten_model') #Chinese(traditional)

argostranslate.package.install_from_path(jaen_model)
argostranslate.package.install_from_path(enja_model)
argostranslate.package.install_from_path(ruen_model)
argostranslate.package.install_from_path(koen_model)
argostranslate.package.install_from_path(zhen_model)
argostranslate.package.install_from_path(zten_model)
    
class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('ocrtrans+ ver2.2')
  
        self.outputEditor = QtWidgets.QTextEdit()
        self.outputEditorENG = QtWidgets.QTextEdit()

        TransBTN = QtWidgets.QPushButton("Trans",self)
        DeleteBTN = QtWidgets.QPushButton("Delete",self) 
        OcrBTN = QtWidgets.QPushButton("OCR",self)
        WhisBTN = QtWidgets.QPushButton("Whisper",self)
        csvBTN = QtWidgets.QPushButton("Wh+Tr->CSV")
        AudBTN = QtWidgets.QPushButton("Open Audio",self)
        AudBTN.setFixedWidth(100)
        self.OriginalComboBox = QtWidgets.QComboBox(self)
        self.WhisperComboBox = QtWidgets.QComboBox(self)
        self.WhisperComboBox.setFixedWidth(70)
        
        self.editorOriginal = QtWidgets.QTextEdit()
        TransBTN.clicked.connect(self.TransBTNClick)
        self.editorOriginal.setPlainText('入力…')
        OcrBTN.clicked.connect(self.OcrBTNClick)
        DeleteBTN.clicked.connect(self.DeleteBTNClick)
        WhisBTN.clicked.connect(self.WhisBTNClick)
        csvBTN.clicked.connect(self.csvBTNClick)
        AudBTN.clicked.connect(self.AudBTNClick)
        self.OriginalComboBox.addItems(["en","ru","ko","zh","zt"])
        self.WhisperComboBox.addItems(["tiny","base","small","medium","turbo","large"])

        BTNlayout = QtWidgets.QVBoxLayout()
        BTNlayout.addWidget(TransBTN)
        BTNlayout.addWidget(OcrBTN)
        BTNlayout.addWidget(DeleteBTN)
        BTNlayout.addWidget(WhisBTN)
        BTNlayout.addWidget(csvBTN)
        
        label1 = QtWidgets.QLabel('翻訳元')
        Textlayout1 = QtWidgets.QHBoxLayout()
        Textlayout1.addWidget(label1)
        Textlayout1.addWidget(self.OriginalComboBox)
        Textlayout10 = QtWidgets.QVBoxLayout()
        Textlayout10.addLayout(Textlayout1)
        Textlayout10.addWidget(self.editorOriginal)
        
        self.label_aud = QtWidgets.QTextBrowser()
        self.label_aud.setText("\n".join(audio_path_list))
        self.label_aud.setFixedHeight(100)
        layout_aud = QtWidgets.QHBoxLayout()
        layout_aud.addWidget(self.WhisperComboBox)
        layout_aud.addWidget(AudBTN)
        layout_aud.addWidget(self.label_aud)
        
        label2 = QtWidgets.QLabel('英訳')
        Textlayout2 = QtWidgets.QVBoxLayout()
        Textlayout2.addWidget(label2)
        Textlayout2.addWidget(self.outputEditorENG) 
        
        label3 = QtWidgets.QLabel('日訳')
        Textlayout3 = QtWidgets.QVBoxLayout()
        Textlayout3.addWidget(label3)
        Textlayout3.addWidget(self.outputEditor)
        
        layoutH = QtWidgets.QHBoxLayout()
        layoutH.addLayout(Textlayout10)
        layoutH.addLayout(BTNlayout)
        layoutH.addLayout(Textlayout2)
        layoutH.addLayout(Textlayout3)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(layoutH)
        layout.addLayout(layout_aud)    

    def editEditor(txt):
        editor.editorOriginal.setPlainText(txt)

    def FromChecker():
        global from_code1 
        from_code1 = editor.OriginalComboBox.currentText()
    
    def TransBTNClick(self):
        text = self.editorOriginal.toPlainText()
        global from_code1 
        from_code1 = self.OriginalComboBox.currentText()
        from_code2 = "en"
        to_code2 = "ja"
        try:
            translate_Text1 = argostranslate.translate.translate(text, from_code1, to_code1)
            self.outputEditorENG.setPlainText(translate_Text1)
            translate_Text2 = argostranslate.translate.translate(translate_Text1, from_code2, to_code2)
            self.outputEditor.setPlainText(translate_Text2)
        except Exception as e:
            QMessageBox.warning(None, "error", "exception error", QMessageBox.Yes)
        
    def OcrBTNClick(self):
        self.window = OcrWindow()
        self.window.show()
        
    def DeleteBTNClick(self):
        self.editorOriginal.setPlainText('')
        self.outputEditorENG.setPlainText('')
        self.outputEditor.setPlainText('')
    
    def AudBTNClick(self):
        global audio_path
        global audio_path_list
        audio_path = QFileDialog.getOpenFileNames(self,'Open files',os.getcwd(),"All Files (*.*)")
        audio_path_list,a = audio_path
        editor.label_aud.setText('\n'.join(audio_path_list))
    
    def WhisBTNClick(self):
        try:
            model_current = self.WhisperComboBox.currentText()
            whisper_model = whisper.load_model(model_current, download_root=WhisperModelPath)
            result = whisper_model.transcribe(audio_path[0], fp16=False)
            OUTPUT_DIR = './'
            output_file_path = os.path.join(OUTPUT_DIR, f"Whisper.txt")
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(result["text"])
            editor.editorOriginal.setPlainText(result["text"])
        except Exception as e:
            QMessageBox.warning(None, "error", "Exception Error\nAudio File Only", QMessageBox.Yes)
            
    def csvBTNClick(self):
        def whisCSV(data):
            model_current = editor.WhisperComboBox.currentText()
            whisper_model = whisper.load_model(model_current, download_root=WhisperModelPath)
            result = []
            result.append(data) 
            result.append(os.path.split(result[0])[1])
            file_info = os.stat(result[0])
            result.append(file_info.st_ctime)
            c = whisper_model.transcribe(result[0], fp16=False)
            result.append(c["text"])
            translate_Text1 = argostranslate.translate.translate(result[3], from_code1, to_code1)
            result.append(translate_Text1)
            translate_Text2 = argostranslate.translate.translate(translate_Text1, from_code2, to_code2)
            result.append(translate_Text2)
            #print(result[3] + "\n")
            #with open("whistrans.csv","a",encoding='utf-8') as f:
            #    writer = csv.writer(f,delimiter = "\t")
            #    writer.writerow(result)
            #editor.editorOriginal.append("終了" + result[0])
            return result
        csv_data = map(whisCSV,audio_path_list)
        with open("whistrans.csv","w",encoding='utf-8',newline="") as f:
            writer = csv.writer(f,delimiter = "\t")
            writer.writerows(csv_data)
        
        
class OcrWindow(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__()
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.setGeometry(0,0,screen_width, screen_height)
        self.setWindowTitle("")
        self.setWindowOpacity(0.3)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor("black"), 3))
        qp.setBrush(QtGui.QColor(128, 128, 255, 128))
        qp.drawRect(QtCore.QRect(self.begin, self.end)) 
     
    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.close()

        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        img = ImageGrab.grab(bbox=(x1,y1,x2,y2))

        # Tesseractのフルパスを指定
        pytesseract.pytesseract.tesseract_cmd = TesseractPath

        OUTPUT_DIR = './'

        # OCRでテキストを抽出
        global from_code1 
        MainWindow.FromChecker()
        global from_code_ocr
        if from_code1 == "en":
            from_code_ocr = "jpn+eng"
        elif from_code1 == "ru":
            from_code_ocr = "rus+eng"
        elif from_code1 == "ko":
            from_code_ocr = "kor+eng"
        elif from_code1 == "zh":
            from_code_ocr = "chi_sim+eng"
        elif from_code1 == "zt":
            from_code_ocr = "chi_tra+eng"
        text = pytesseract.image_to_string(img, lang=from_code_ocr)
 
        output_file_path = os.path.join(OUTPUT_DIR, f"OCR.txt")
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        #元ウィンドウに反映
        MainWindow.editEditor(text)
 
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    editor = MainWindow()
    editor.show()
    sys.exit(app.exec_())
