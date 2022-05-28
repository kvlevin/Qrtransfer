#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import qrcode
import time
import os
from queue import Queue

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QEvent,QObject,QThread,pyqtSignal,Qt
from PyQt5.QtGui import QImage,QPixmap


from render import Image


from uis.Ui_main_window import Ui_MainWindow

class QrCodeGenerateWorker(QThread):
    def __init__(self,tranfer):
        super(QrCodeGenerateWorker, self).__init__() 
        self.tranfer=tranfer


    def __del__(self):
        self.wait()

    def run(self):
        while True:
            frame,i= self.tranfer.next_frame()
            print('generate framee:'+str(i))
            self.tranfer.imageQueue.put({'index':i,'image':qrcode.make(frame, image_factory=Image).pixmap()},block=True)
            if(i>self.tranfer.totalFrame):
                return
             
         


class Tranfer():
    def __init__(self, path, chunk_size):
        self.path = path
        self.file = open(path, 'rb')
        import os
        import math
        self.fileSize=os.path.getsize(path)
        self.totalFrame=math.ceil( self.fileSize/chunk_size)
        self.current_frame = 0
        self.chunk_size = chunk_size
        self.headLength=4
        self.imageQueue=Queue(maxsize=20)
        QrCodeGenerateWorker(self).start()

    def next_frame(self):
        self.current_frame=self.current_frame+1
        #frame=bytes([0b01110000,0b00110000])
        # frame= frame+self.current_frame.to_bytes(4, 'big')
        frame=self.current_frame.to_bytes(4, 'big')
        frame =frame+ self.file.read(self.chunk_size)
        return frame,self.current_frame

    def next_image(self):
        item=self.imageQueue.get()
        return item['image'],item['index']

    def rewind(self, frame):
        self.file.seek((frame-self.current_frame)*chunk_size, 1)
        self.current_frame = frame

    def close(self):
        self.file.close()




def isFile(filename):
    with open(filename) as file:
        return True
    return False


class TickTock(QThread):
    _signal = pyqtSignal(str)
    
    def __init__(self,fps:int,ratio:float):
        super(TickTock, self).__init__() 
        self.fps = fps
        self.ratio = ratio
        self.run=True
        
        

    def __del__(self):
        self.wait()
    
    def run(self):
        self._signal.emit('tick')
        time.sleep(1)
        while self.run:
            self._signal.emit('tock')
            time.sleep((1-self.ratio)*(1/self.fps))
            self._signal.emit('tick')
            time.sleep(self.ratio*(1/self.fps))



            
        

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_ui()
        self.canResume = False;
        image = QImage(819, 819, QImage.Format_RGB16)
        image.fill(Qt.white)
        self._image=QPixmap.fromImage(image)
        


    def init_ui(self):
        self.setWindowTitle("Generate QR Code")
        self.setWindowIcon(QtGui.QIcon("./icons/qr-scan.png"))
        self.ui.pushButton.clicked.connect(self.generate_qr_code_)
        self.ui.fileChoose.clicked.connect(self.choose_click)
        self.ui.startBtn.clicked.connect(self.start)
        self.ui.stopBtn.clicked.connect(self.stop)
        self.ui.restartBtn.clicked.connect(self.restart)


    def generate_qr_code_(self):
        generate_qr_code(self.ui.fileName.text())

    def showImage(self,image):
        self.ui.label.setPixmap(image)

    def generate_qr_code(self,_str):
        # from datetime import datetime
        qr_image = qrcode.make(_str, image_factory=Image).pixmap()

            # set image to the label
        self.showImage(qr_image)
        
    

        # from tempfile import NamedTemporaryFile
        # with NamedTemporaryFile(mode="w+b",delete=False) as f:
        #     # _file_name = str(int(time.time()*1000)) + ".png"



            # img = qrcode.make(_str)
            # img.save(f)
            #  print(open(f.name).read())
            # pixmap = QPixmap(f.name)
            # #TODO
            #  self.ui.label.setPixmap(pixmap.scaled(819,819))
            # f.close()
            # import os
            #os.unlink(f.name)
           
    

    def choose_click(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            QtWidgets.QWidget(), 'open', r".")
        print(filename)
        self.ui.fileName.setText(filename)
        if isFile(self.ui.fileName.text()):
            self.init_transfer()
        else:
            self.generate_qr_code_()



    def init_transfer(self):
        self.transfer=Tranfer(self.ui.fileName.text(),int(self.ui.reso.text()))   
        self.ui.statusText.clear()
        self.ui.statusText.append("file name:"+self.ui.fileName.text())
        self.ui.statusText.append("chuck size:"+self.ui.reso.text())
        self.ui.statusText.append("frame per second:"+self.ui.fps.text())
        self.ui.statusText.append("frame count:"+str(self.transfer.totalFrame))
        self.ui.statusText.append("headLength:"+str(self.transfer.headLength))

        import json
        para={}
        para['fileName'] =os.path.basename(self.ui.fileName.text())
        para["chunkSize"]=self.ui.reso.text()
        para['fps']=self.ui.fps.text()
        para['fileSize']=self.transfer.fileSize
        para['headLength']=self.transfer.headLength 
        para['totalFrame']=self.transfer.totalFrame

        self.generate_qr_code(json.dumps(para))
        self.ui.statusText.append("ready to transfer")

        
            

    def start_tranfer(self):

        self.tickTock=TickTock(int(self.ui.fps.text()),0.9)
        self.tickTock._signal.connect(self.refresh)
        self.tickTock.start()
        pass


    def refresh(self,tickTock):   
        if tickTock=='tick':
            frame,frame_i=self.transfer.next_image()
            self.ui.statusText.append("current Frame:"+str(frame_i))
            if self.transfer.totalFrame<frame_i:
                self.end()
            else :
                self.showImage(frame)
        else:
    
        # TODO
            self.ui.label.setPixmap(self._image)



    def start(self):
        if self.canResume :
            self.resume()
        else:
            self.start_tranfer()
          
                

    def resume(self):
        pass


    def stop(self):
        self.canResume=True
        self.tickTock.run=False

        self.ui.frames.setText(str(self.transfer.current_frame-int(self.ui.fps.text())*5))


    def end(self):
        self.ui.statusText.clear()
        self.restart()

    def restart(self):
        self.canResume=False
        self.tickTock.run=False
        self.init_transfer()
        pass



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
