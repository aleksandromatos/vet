#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import yaml
import logging
import datetime

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTabWidget, QLabel, QTextEdit, QPushButton, QFileDialog,
                            QScrollArea, QGridLayout, QFrame, QMessageBox, QCheckBox)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from PIL import Image
from pathlib import Path

class UltrasoundReportSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_paths = []
        self.laudos_data = {} # <--- Dicionário para armazenar os dados do YAML
        self.checkbox_map = {} # <--- Dicionário para mapear checkboxes de cada órgão
        self.logger = logging.getLogger(__name__)
        self.load_laudos_data() # <--- Carrega os dados na inicialização
        self.initUI()
        self.current_path = str(Path(__file__).parent.resolve())
        print(f"Current path: {self.current_path}")
    
    # def confLogging(self):
    #     """
    #     Configura o logging para registrar mensagens de depuração e erros.
    #     """
    #     logging.basicConfig(filemode=datetime.now()\
    #         strftime())     
    
    def load_laudos_data(self):
        try:
            with open('laudo_corrigido.yaml', 'r', encoding='utf-8') as file:
                self.laudos_data = yaml.safe_load(file)
                if not self.laudos_data:
                    self.laudos_data = {}
                    raise Exception("O arquivo laudos.yaml está vazio.")
                
        except FileNotFoundError:
            QMessageBox.critical(self, "Erro", "Arquivo 'laudos.yaml' não encontrado. Certifique-se de que ele está na mesma pasta do programa.")
            sys.exit(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Carregar Dados", f"Não foi possível ler o arquivo 'laudos.yaml':\n{e}")
            sys.exit(1)

    def initUI(self):
        self.setWindowTitle("Sistema de Laudos de Ultrassonografia Veterinária")
        self.setGeometry(100, 100, 1000, 800)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        header_label = QLabel("LAUDO DE ULTRASSONOGRAFIA VETERINÁRIA")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(header_label)
        main_layout.addLayout(header_layout)
        
        # Informações do paciente (sem alterações)
        patient_layout = QGridLayout()
        patient_layout.addWidget(QLabel("Nome do Animal:"), 0, 0)
        self.animal_name = QTextEdit()
        self.animal_name.setMaximumHeight(30)
        patient_layout.addWidget(self.animal_name, 0, 1)
        
        patient_layout.addWidget(QLabel("Espécie:"), 0, 2)
        self.species = QTextEdit()
        self.species.setMaximumHeight(30)
        patient_layout.addWidget(self.species, 0, 3)
        
        patient_layout.addWidget(QLabel("Raça:"), 1, 0)
        self.breed = QTextEdit()
        self.breed.setMaximumHeight(30)
        patient_layout.addWidget(self.breed, 1, 1)
        
        patient_layout.addWidget(QLabel("Idade:"), 1, 2)
        self.age = QTextEdit()
        self.age.setMaximumHeight(30)
        patient_layout.addWidget(self.age, 1, 3)
        
        patient_layout.addWidget(QLabel("Proprietário:"), 2, 0)
        self.owner = QTextEdit()
        self.owner.setMaximumHeight(30)
        patient_layout.addWidget(self.owner, 2, 1)
        
        patient_layout.addWidget(QLabel("Data:"), 2, 2)
        self.date = QTextEdit()
        self.date.setMaximumHeight(30)
        patient_layout.addWidget(self.date, 2, 3)
        
        main_layout.addLayout(patient_layout)
        
        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # ---- Início da Lógica Modificada para as Tabs ----
        self.tab_widget = QTabWidget()
        self.organ_texts = {}
        
        # Gera as abas dinamicamente a partir do arquivo YAML
        for organ, abnormalities in self.laudos_data.items():
                        
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            # Área de scroll para os checkboxes
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_widget = QWidget()
            checkbox_layout = QVBoxLayout(scroll_widget)
            checkbox_layout.setAlignment(Qt.AlignTop)
            
            self.checkbox_map[organ] = []

            if abnormalities: # Verifica se existem anormalidades listadas
                for abnormality_name, description_list in abnormalities.items():
                    # O YAML retorna uma lista, pegamos o primeiro item.
                    description = description_list[0] if description_list else "Descrição não encontrada."
                    
                    checkbox = QCheckBox(abnormality_name)
                    checkbox.setToolTip(description)
                    checkbox.stateChanged.connect(lambda state, org=organ: self.update_report_text(org))
                    
                    checkbox_layout.addWidget(checkbox)
                    self.checkbox_map[organ].append(checkbox)

            scroll_area.setWidget(scroll_widget)
            
            # Label indicando a área de resultado
            result_label = QLabel("Texto do Laudo para este Órgão:")
            result_label.setFont(QFont("Arial", 10, QFont.Bold))
            
            # QTextEdit para exibir o texto concatenado
            text_edit = QTextEdit()
            text_edit.setReadOnly(True) # O texto é gerado pelos checkboxes
            self.organ_texts[organ] = text_edit
            
            # Adicionando os widgets ao layout da aba
            tab_layout.addWidget(scroll_area)
            tab_layout.addWidget(result_label)
            tab_layout.addWidget(text_edit)
            
            self.tab_widget.addTab(tab, organ)
        
        main_layout.addWidget(self.tab_widget)
        # ---- Fim da Lógica Modificada para as Tabs ----

        # Área de imagens (sem alterações)
        images_label = QLabel("Imagens do Ultrassom")
        images_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(images_label)
        
        img_buttons_layout = QHBoxLayout()
        add_img_btn = QPushButton("Adicionar Imagens")
        add_img_btn.clicked.connect(self.add_images)
        clear_img_btn = QPushButton("Limpar Imagens")
        clear_img_btn.clicked.connect(self.clear_images)
        img_buttons_layout.addWidget(add_img_btn)
        img_buttons_layout.addWidget(clear_img_btn)
        main_layout.addLayout(img_buttons_layout)
        
        self.images_scroll = QScrollArea()
        self.images_scroll.setWidgetResizable(True)
        self.images_widget = QWidget()
        self.images_layout = QGridLayout(self.images_widget)
        self.images_scroll.setWidget(self.images_widget)
        main_layout.addWidget(self.images_scroll)
        
        # Botões de ação (sem alterações)
        buttons_layout = QHBoxLayout()
        preview_btn = QPushButton("Visualizar Impressão")
        preview_btn.clicked.connect(self.print_preview)
        print_btn = QPushButton("Imprimir")
        print_btn.clicked.connect(self.print_report)
        save_pdf_btn = QPushButton("Salvar como PDF")
        save_pdf_btn.clicked.connect(self.save_as_pdf)
        
        buttons_layout.addWidget(preview_btn)
        buttons_layout.addWidget(print_btn)
        buttons_layout.addWidget(save_pdf_btn)
        main_layout.addLayout(buttons_layout)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    # <--- Nova função para atualizar o texto do laudo ----
    def update_report_text(self, organ):
        """
        Chamado sempre que um checkbox de um órgão é marcado/desmarcado.
        Ele reconstrói o texto para o QTextEdit daquele órgão.
        """
        selected_texts = []
        print(f"Atualizando texto para o órgão: {organ}")
        # Itera sobre todos os checkboxes do órgão específico
        for checkbox in self.checkbox_map.get(organ, []):
            if checkbox.isChecked():
                # Adiciona o texto do tooltip à lista se o checkbox estiver marcado
                selected_texts.append(checkbox.toolTip())
        
        # Concatena os textos com um espaço e uma nova linha para melhor formatação
        final_text = "\n\n".join(selected_texts)
        
        # Atualiza o QTextEdit correspondente
        self.organ_texts[organ].setText(final_text)

    # Função get_default_text não é mais necessária e foi removida

    def add_images(self, files=None): # Pequena alteração para consistência
        if not files:
            files, _ = QFileDialog.getOpenFileNames(self, "Selecionar Imagens", "", 
                                                  "Imagens (*.png *.jpg *.jpeg *.bmp)")
        
        if not files:
            return
            
        self.clear_images()
        self.image_paths = files
        
        col = 0
        row = 0
        max_cols = 3
        
        for img_path in self.image_paths:
            if col >= max_cols:
                col = 0
                row += 1
                
            pixmap = QPixmap(img_path)
            # Mantido o tamanho para consistência com o PDF
            img_width = int(2.59 * 37.8)
            img_height = int(4.65 * 37.8)
            pixmap = pixmap.scaled(img_width, img_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            img_label = QLabel()
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignCenter)
            img_label.setFixedSize(img_width, img_height)
            img_label.setStyleSheet("border: 1px solid #cccccc;")
            
            self.images_layout.addWidget(img_label, row, col)
    
    def clear_images(self):
        self.image_paths = []
        while self.images_layout.count():
            item = self.images_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    # As funções abaixo (get_complete_report, print, save_pdf) funcionam sem alterações,
    # pois elas já leem do dicionário self.organ_texts, que continua sendo atualizado.
    
    def get_complete_report(self):
        report = ""
        report += "LAUDO DE ULTRASSONOGRAFIA VETERINÁRIA\n\n"
        report += f"Nome do Animal: {self.animal_name.toPlainText()}\n"
        report += f"Espécie: {self.species.toPlainText()}\n"
        report += f"Raça: {self.breed.toPlainText()}\n"
        report += f"Idade: {self.age.toPlainText()}\n"
        report += f"Proprietário: {self.owner.toPlainText()}\n"
        report += f"Data: {self.date.toPlainText()}\n\n"
        
        for organ in self.organ_texts:
            text = self.organ_texts[organ].toPlainText()
            if text: # Só adiciona ao relatório se houver texto
                report += f"{organ.upper()}:\n"
                report += f"{text}\n\n"
        
        return report
    
    def print_preview(self):
        dialog = QPrintPreviewDialog()
        dialog.paintRequested.connect(self.print_document)
        dialog.exec_()
    
    def print_report(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QPrintDialog.Accepted:
            self.print_document(printer)
    
    def print_document(self, printer):
        from PyQt5.QtGui import QTextDocument
        document = QTextDocument()
        document.setHtml(self.get_formatted_html())
        document.print_(printer)
    
    def get_formatted_html(self):
        html = "<html><body>"
        html += "<h1 style='text-align:center;'>LAUDO DE ULTRASSONOGRAFIA VETERINÁRIA</h1>"
        
        html += "<table width='100%' style='border-collapse: collapse;'>"
        html += f"<tr><td><b>Nome do Animal:</b> {self.animal_name.toPlainText()}</td>"
        html += f"<td><b>Espécie:</b> {self.species.toPlainText()}</td></tr>"
        html += f"<tr><td><b>Raça:</b> {self.breed.toPlainText()}</td>"
        html += f"<td><b>Idade:</b> {self.age.toPlainText()}</td></tr>"
        html += f"<tr><td><b>Proprietário:</b> {self.owner.toPlainText()}</td>"
        html += f"<td><b>Data:</b> {self.date.toPlainText()}</td></tr>"
        html += "</table><hr>"
        
        for organ in self.organ_texts:
            text = self.organ_texts[organ].toPlainText()
            if text: # Só adiciona ao relatório se houver texto
                html += f"<h3>{organ}</h3>"
                # O texto já está formatado, basta substituir quebras de linha por <br>
                html += f"<p>{text.replace('/n', '<br>')}</p>"
        
        html += "<div style='page-break-before: always;'></div>" if self.image_paths else ""
        
        if self.image_paths:
            html += "<h3>Imagens</h3>"
            html += "<table style='width:100%; border-collapse: collapse;'><tr>"
            
            for i, img_path in enumerate(self.image_paths):
                if i > 0 and i % 3 == 0:
                    html += "</tr><tr>"
                
                # Usando file URI para garantir que caminhos com caracteres especiais funcionem
                from pathlib import Path
                img_uri = Path(img_path).as_uri()
                html += f"<td style='text-align:center; padding: 5px;'>"
                html += f"<img src='{img_uri}' style='width:98px; height:176px; object-fit:contain; border: 1px solid #ccc;'>"
                html += "</td>"
            
            html += "</tr></table>"
        
        html += "</body></html>"
        return html
    
    def save_as_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar como PDF", "", "PDF Files (*.pdf)")
        
        if not file_path:
            return
            
        if not file_path.endswith('.pdf'):
            file_path += '.pdf'
        
        try:
            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4
            
            # Helper para desenhar texto com quebra de linha
            def draw_wrapped_text(canvas_obj, text, x, y, max_width, font_name, font_size):
                text_object = canvas_obj.beginText(x, y)
                text_object.setFont(font_name, font_size)
                
                lines = []
                for paragraph in text.split('\n'):
                    words = paragraph.split()
                    current_line = ""
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        if canvas_obj.stringWidth(test_line, font_name, font_size) < max_width:
                            current_line = test_line
                        else:
                            lines.append(current_line)
                            current_line = word
                    lines.append(current_line)

                for line in lines:
                    text_object.textLine(line)
                
                canvas_obj.drawText(text_object)
                return text_object.getY() - y # Retorna a altura total do texto desenhado

            # Título
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width/2, height - 30, "LAUDO DE ULTRASSONOGRAFIA VETERINÁRIA")
            
            # Informações do paciente
            y = height - 60
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"Nome do Animal: ")
            c.setFont("Helvetica", 12)
            c.drawString(150, y, self.animal_name.toPlainText())
            c.setFont("Helvetica-Bold", 12)
            c.drawString(width/2, y, f"Espécie: ")
            c.setFont("Helvetica", 12)
            c.drawString(width/2 + 60, y, self.species.toPlainText())
            
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"Raça: ")
            c.setFont("Helvetica", 12)
            c.drawString(90, y, self.breed.toPlainText())
            c.setFont("Helvetica-Bold", 12)
            c.drawString(width/2, y, f"Idade: ")
            c.setFont("Helvetica", 12)
            c.drawString(width/2 + 50, y, self.age.toPlainText())
            
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"Proprietário: ")
            c.setFont("Helvetica", 12)
            c.drawString(130, y, self.owner.toPlainText())
            c.setFont("Helvetica-Bold", 12)
            c.drawString(width/2, y, f"Data: ")
            c.setFont("Helvetica", 12)
            c.drawString(width/2 + 40, y, self.date.toPlainText())
            
            y -= 15
            c.line(50, y, width-50, y)
            y -= 25

            # Conteúdo dos órgãos
            for organ in self.organ_texts:
                text = self.organ_texts[organ].toPlainText()
                if not text:
                    continue

                if y < 100:
                    c.showPage()
                    y = height - 50
                
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, f"{organ}:")
                y -= 5
                
                text_height = draw_wrapped_text(c, text, 50, y, width - 100, "Helvetica", 10)
                y += text_height - 20 # Ajusta y com base na altura do texto


            # Adicionar imagens
            if self.image_paths:
                if y < 200:
                    c.showPage()
                    y = height - 50
                
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, "Imagens:")
                y -= 15
                
                img_width = 2.59 * cm
                img_height = 4.65 * cm
                
                col = 0
                start_x = 50
                start_y = y
                
                for img_path in self.image_paths:
                    if col >= 3:
                        col = 0
                        start_y -= (img_height + 10)
                        
                        if start_y < img_height + 50:
                            c.showPage()
                            start_y = height - 50
                    
                    x = start_x + col * (img_width + 20)
                    
                    try:
                        c.drawImage(img_path, x, start_y - img_height, width=img_width, height=img_height, preserveAspectRatio=True, anchor='c')
                    except Exception as e:
                        print(f"Erro ao adicionar imagem ao PDF: {e}")
                    
                    col += 1
            
            c.save()
            QMessageBox.information(self, "Sucesso", "PDF salvo com sucesso!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar o PDF: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UltrasoundReportSystem()
    window.show()
    sys.exit(app.exec_())