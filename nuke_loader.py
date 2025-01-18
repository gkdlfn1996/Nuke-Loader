try:
    from PySide6.QtWidgets import *
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtGui import QPixmap
    from PySide6.QtCore import QFile, Qt
except:
    from PySide2.QtWidgets import *
    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtGui import QPixmap
    from PySide2.QtCore import QFile, Qt
    
# 이 프로그램이 하는 일은 Nuke 파일을 지정된 경로에 저장하는 프로그램 입니다.

# 저장된 뉴크 파일을 오픈하는 기능도 필요합니다.

# 경로는 다음처럼 저장되게 해주세요~!

# /home/rapa/show/PROJECT/SEQ/SEQ_0010/comp/dev/SEQ_0010_comp_v001.nk

# 일 때 대문자로 작성한 프로젝트 / 시퀀스 / 시퀀스_샷번호는 선택할 수 있어야 합니다.

# 선택한 내용을 바탕으로 뉴크 파일의 이름이 만들어지면 되어요.

# 파일을 저장할 때에는 현재 뉴크에 있는 Read Node, Write Node의 이름과 파일 패스, 저장한 날짜, 시간, 유저 이름

# 딕셔너리 형태로 JSON 파일이 생성되어야 합니다.

import nuke
import sys
import os
import re
import json
import time
import socket # ip 가져오는 모듈

class Loader(QWidget):
    def __init__(self):
        super().__init__()
        self.setting()
        self.project_cb()
        
        
        self.ui.comboBox_proj.currentIndexChanged.connect(self.sequence_cb)
        self.ui.comboBox_seq.currentIndexChanged.connect(self.shot_number_tb)
        self.ui.tableWidget_shot.cellClicked.connect(self.files_tb)
        self.ui.tableWidget_files.cellDoubleClicked.connect(self.open_file)
        self.ui.pushButton_save.clicked.connect(self.save)
    
    def save_json(self):
        self.js_path = "/home/rapa/show/.json_files"
        if not os.path.exists(self.js_path):
            os.makedirs(self.js_path)
            pass
        """
        Read노드 이름과 파일 패스 가져오기
        """
        reads = nuke.allNodes("Read")
        n_r = len(reads)
        read_names_list = []
        read_files_list = []
        for i in reads:
            name = i.knob("name").value()
            file = i.knob("file").value()
            read_names_list.append(name)
            read_files_list.append(file)
        read_file = {}
        for j in range(n_r):
            read_file[read_names_list[j]] = read_files_list[j]
        """
        Write노드 이름과 파일 패스 가져오기
        """
        writes = nuke.allNodes("Write")
        n_w = len(writes)
        write_names_list = []
        write_files_list = []
        for i in writes:
            name = i.knob("name").value()
            file = i.knob("file").value()
            write_names_list.append(name)
            write_files_list.append(file)
        write_file = {}
        for j in range(n_w):
            write_file[write_names_list[j]] = write_files_list[j]
        
        """
        날짜,시간 구하기
        """
        now = time
        now_date = now.strftime('%y-%m-%d')
        now_time = now.strftime('%H:%M:%S')
        """
        유저이름(ip주소) 구하기
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        """
        json으로 저장해주기
        """
        data = {}
        data["File Name"] = self.save_file_name
        data["Nuke Path"] = self.nuke_file_path
        data["Read Nodes_name"] = read_names_list
        data["Read Nodes_file"] = read_file
        data["Write Nodes_name"] = write_names_list
        data["Write Nodes_file"] = write_file
        data["Date"] = now_date
        data["Time"] = now_time
        data["User Name"] = ip
        
        js_full_path = f"{self.js_path}/{self.save_file_name}.json"
        with open(js_full_path, "w") as f:
            json.dump(data, f, indent=4)
    
    def save(self):
        """
        파일 저장하기
        """
        save_file_dir = f"/home/rapa/show/{self.project}/seq/{self.sequence}/{self.shot_number}/comp/dev"
        ver_files = os.listdir(save_file_dir)
        if not ver_files:
            self.save_file_name = f"{self.shot_number}_comp_v001.nknc"
        else:
            ver_check = []
            for ver_file in ver_files:
                p = re.compile("[v]\d{2,4}")
                p_data = p.search(ver_file)
                if p_data:
                    p_ver = p_data.group()
                    ver_check.append(p_ver)
            ver_check.sort()
            last_ver = ver_check[-1]
            last_ver_num = int(last_ver[1:])
            ver_num_str = str(last_ver_num + 1)
            ver_num = ver_num_str.zfill(3)
            self.save_file_name = f"{self.shot_number}_comp_v{ver_num}"
        
        self.nuke_file_path = f"{save_file_dir}/{self.save_file_name}.nknc"
        if not os.path.exists(save_file_dir):
            os.makedirs(save_file_dir)
            pass
        nuke.scriptSaveAs(self.nuke_file_path)
        self.save_json()
        
        """
        저장한 파일 띄우기
        """
        files = os.listdir(save_file_dir)
        row = len(files)
        self.ui.tableWidget_files.setRowCount(row)
        self.ui.tableWidget_files.setColumnCount(2)
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""
        file_row = 0
        for file in files:
            """
            파일 이름 넣기
            """
            label_name = QLabel()
            label_name.setText(file)
            label_name.setAlignment(Qt.AlignCenter)
            
            self.widget = QWidget()
            
            v = QVBoxLayout(self.widget)
            v.addWidget(label_name)
            
            """
            시간 넣기
            """
            file_without_ext = file.split(".")[0]
            file_js = f"/home/rapa/show/.json_files/{file_without_ext}.json"
            if not os.path.exists(file_js):
                pass
            else:
                with open(file_js, 'r') as f:
                    json_data = json.load(f)
                for key,value in json_data.items():
                    if key == "Date":
                        f_date = value
                    elif key == "Time":
                        f_time = value
                datetime = f"{f_date} {f_time}"

                label_time = QLabel()
                label_time.setText(datetime)
                label_time.setStyleSheet("color: rgb(136, 138, 133);")
                label_time.setAlignment(Qt.AlignCenter)
                v.addWidget(label_time)
            self.ui.tableWidget_files.setCellWidget(file_row,1,self.widget)
            """
            누크 이미지 넣기
            """
            v = self.ui.tableWidget_files.verticalHeader()
            v.setSectionResizeMode(QHeaderView.ResizeToContents)
            self.ui.tableWidget_files.setColumnWidth(0,50)
            
            file_ext = file.split(".")[1]
            if file_ext == "nknc":
                img = QLabel()
                img_path = "/home/rapa/test_nuke/0731/nuke_img.png"
                pix = QPixmap(img_path)
                sc_pix = pix.scaledToWidth(50)
                img.setPixmap(sc_pix)
                self.ui.tableWidget_files.setCellWidget(file_row,0,img) # 테이블위젯에 label넣기
            file_row+=1

    def project_cb(self):
        """
        project 콤보박스 만들기
        """
        proj_path = "/home/rapa/show"
        all_projects = os.listdir(proj_path)
        projects = []
        for i in all_projects:
            if not i[0] == ".":
                projects.append(i)
        projects.insert(0,"")
        self.ui.comboBox_proj.addItems(projects)
        
    def sequence_cb(self):
        """
        빈칸 클릭시
        """
        if self.ui.comboBox_proj.currentIndex() == 0:
            self.project = ""
            self.sequence = ""
            self.shot_number = ""
            self.ui.label_proj.setText(self.project)
            self.ui.label_seq.setText(self.sequence)
            self.ui.label_shot.setText(self.shot_number)
            self.ui.tableWidget_shot.setRowCount(0)
            self.ui.tableWidget_shot.setColumnCount(0)
            self.ui.tableWidget_files.setRowCount(0)
            self.ui.tableWidget_files.setColumnCount(0)
        """
        sequence 콤보박스 만들기
        """
    
        self.project = self.ui.comboBox_proj.currentText()
        self.ui.comboBox_seq.clear()
        if self.project == "":
            return
        seq_path = f"/home/rapa/show/{self.project}/seq"
        sequences = os.listdir(seq_path)
        self.ui.comboBox_seq.addItems(sequences)
        if self.ui.comboBox_seq.currentIndex() == 0:
            self.shot_number_tb()
        
        self.ui.label_proj.setText(self.project) # 저장할 프로젝트 띄우기
        self.shot_number = ""
        self.ui.label_shot.setText(self.shot_number)
        
    def shot_number_tb(self):
        """
        shot_number 테이블 만들기
        """
        self.ui.tableWidget_files.setRowCount(0)
        self.ui.tableWidget_files.setColumnCount(0)
        self.sequence = self.ui.comboBox_seq.currentText()
        self.ui.tableWidget_shot.clear()
        self.ui.tableWidget_shot.setEditTriggers(QAbstractItemView.NoEditTriggers) 
        if self.project == "":
            return
        shot_path = f"/home/rapa/show/{self.project}/seq/{self.sequence}"
        shots = os.listdir(shot_path)
        row = len(shots)
        self.ui.tableWidget_shot.setRowCount(row)
        self.ui.tableWidget_shot.setColumnCount(2)
        
        shot_row = 0
        for shot in shots:
            """
            샷 넘버 넣기
            """
            item = QTableWidgetItem()
            item.setText(shot)
            item.setTextAlignment(Qt.AlignCenter)
            self.ui.tableWidget_shot.setItem(shot_row,1,item)
            """
            샷 이미지 넣기
            """
            v = self.ui.tableWidget_shot.verticalHeader()
            v.setSectionResizeMode(QHeaderView.ResizeToContents)
            img = QLabel()
            img_path = "/home/rapa/test_nuke/0731/shot.jpg"
            pix = QPixmap(img_path)
            sc_pix = pix.scaledToWidth(100)
            img.setPixmap(sc_pix)
            self.ui.tableWidget_shot.setCellWidget(shot_row,0,img) # 테이블위젯에 label넣기
            shot_row+=1
        
        self.ui.label_seq.setText(self.sequence) # 저장할 시퀀스 띄우기
        self.shot_number = ""
        self.ui.label_shot.setText(self.shot_number)
        
    def files_tb(self,row,column):
        """
        파일명 및 저장시간 나오는 테이블 띄우기
        """
        self.shot_number = self.ui.tableWidget_shot.item(row,column).text()
        self.ui.tableWidget_files.clear()
        self.ui.tableWidget_files.setEditTriggers(QAbstractItemView.NoEditTriggers) 
        if self.project == "":
            return
        file_path = f"/home/rapa/show/{self.project}/seq/{self.sequence}/{self.shot_number}/comp/dev"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        files = os.listdir(file_path)
        row = len(files)
        self.ui.tableWidget_files.setRowCount(row)
        self.ui.tableWidget_files.setColumnCount(2)
        
        file_row = 0
        for file in files:
            """
            파일 이름 넣기
            """
            label_name = QLabel()
            label_name.setText(file)
            label_name.setAlignment(Qt.AlignCenter)
            
            self.widget = QWidget()
            
            v = QVBoxLayout(self.widget)
            v.addWidget(label_name)
            
            """
            시간 넣기
            """
            file_without_ext = file.split(".")[0]
            file_js = f"/home/rapa/show/.json_files/{file_without_ext}.json"
            if not os.path.exists(file_js):
                pass
            else:
                with open(file_js, 'r') as f:
                    json_data = json.load(f)
                for key,value in json_data.items():
                    if key == "Date":
                        f_date = value
                    elif key == "Time":
                        f_time = value
                datetime = f"{f_date} {f_time}"

                label_time = QLabel()
                label_time.setText(datetime)
                label_time.setStyleSheet("color: rgb(136, 138, 133);")
                label_time.setAlignment(Qt.AlignCenter)
                v.addWidget(label_time)
            
            self.ui.tableWidget_files.setCellWidget(file_row,1,self.widget)
            
            """
            누크 이미지 넣기
            """
            v = self.ui.tableWidget_files.verticalHeader()
            v.setSectionResizeMode(QHeaderView.ResizeToContents)
            self.ui.tableWidget_files.setColumnWidth(0,50)
            
            file_ext = file.split(".")[1]
            if file_ext == "nknc":
                img = QLabel()
                img_path = "/home/rapa/test_nuke/0731/nuke_img.png"
                pix = QPixmap(img_path)
                sc_pix = pix.scaledToWidth(50)
                img.setPixmap(sc_pix)
                self.ui.tableWidget_files.setCellWidget(file_row,0,img) # 테이블위젯에 label넣기
            file_row+=1   
        
        self.ui.label_shot.setText(self.shot_number) # 저장할 시퀀스 띄우기
        
    def open_file(self,row,column):
        widget = self.ui.tableWidget_files.cellWidget(row, column)
        vbox = widget.findChildren(QVBoxLayout)[0]
        label_file = vbox.itemAt(0).widget()
        file = label_file.text()
        file_path = f"/home/rapa/show/{self.project}/seq/{self.sequence}/{self.shot_number}/comp/dev/{file}"
        nuke.scriptOpen(file_path)
        self.close()
        
    def setting(self):
        ui_file_path = "/home/rapa/test_nuke/0731/loader_sj.ui"
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(ui_file,self)
        ui_file.close
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Loader()
    win.show()
    app.exec()
    
