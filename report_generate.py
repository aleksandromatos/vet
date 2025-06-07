import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTabWidget, QLabel, QTextEdit, QPushButton, QFileDialog,
                            QScrollArea, QGridLayout, QFrame, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from PIL import Image

class UltrasoundReportSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_paths = []
        self.initUI()
        
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
        
        # Informações do paciente
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
        
        # Tabs para órgãos
        self.tab_widget = QTabWidget()
        
        # Definir os órgãos para abas
        organs = ["Fígado", "Vesícula Biliar", "Baço", "Rins", "Bexiga", 
                  "Estômago", "Alças Intestinais", "Pâncreas", "Adrenais", 
                  "Aparelho Reprodutor", "Observações"]
        
        self.organ_texts = {}
        
        for organ in organs:
            tab = QWidget()
            tab_layout = QVBoxLayout()
            
            # Texto padrão para cada órgão
            default_text = self.get_default_text(organ)
            
            text_edit = QTextEdit()
            text_edit.setText(default_text)
            self.organ_texts[organ] = text_edit
            
            tab_layout.addWidget(text_edit)
            tab.setLayout(tab_layout)
            self.tab_widget.addTab(tab, organ)
        
        main_layout.addWidget(self.tab_widget)
        
        # Área para imagens
        images_label = QLabel("Imagens do Ultrassom")
        images_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(images_label)
        
        # Layout para botões das imagens
        img_buttons_layout = QHBoxLayout()
        add_img_btn = QPushButton("Adicionar Imagens")
        add_img_btn.clicked.connect(self.add_images)
        clear_img_btn = QPushButton("Limpar Imagens")
        clear_img_btn.clicked.connect(self.clear_images)
        img_buttons_layout.addWidget(add_img_btn)
        img_buttons_layout.addWidget(clear_img_btn)
        main_layout.addLayout(img_buttons_layout)
        
        # Área de exibição de imagens com scroll
        self.images_scroll = QScrollArea()
        self.images_scroll.setWidgetResizable(True)
        self.images_widget = QWidget()
        self.images_layout = QGridLayout(self.images_widget)
        self.images_scroll.setWidget(self.images_widget)
        main_layout.addWidget(self.images_scroll)
        
        # Botões de ação
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
    
    def get_default_text(self, organ):
        # Textos padrão para cada órgão
        defaults = {
            "Fígado": "Parênquima hepático de dimensões normais, com ecogenicidade normal, contornos regulares e ecotextura homogênea. Não foram observadas lesões focais ou difusas. Vasos hepáticos com calibre e trajeto normais.",
            
            "Vesícula Biliar": "Vesícula biliar de dimensões normais, com formato piriforme, contornos regulares e conteúdo anecogênico. Parede com espessura normal. Não foram observados cálculos ou sedimentos em seu interior.",
            
            "Baço": "Baço de dimensões normais, com ecogenicidade e ecotextura preservadas. Contornos regulares e parênquima homogêneo. Não foram observadas lesões focais ou difusas.",
            
            "Rins": "Rins de dimensões, contornos e ecogenicidade normais. Relação córtico-medular preservada. Não foram observadas dilatações do sistema pielocalicial ou presença de cálculos. Região pélvica sem alterações.",
            
            "Bexiga": "Bexiga de paredes finas e regulares, com conteúdo anecogênico. Volume adequado no momento do exame. Não foram observados cálculos, sedimentos ou massas.",
            
            "Estômago": "Estômago com paredes de espessura normal, estratificação das camadas preservada. Conteúdo e peristaltismo compatíveis com a normalidade.",
            
            "Alças Intestinais": "Alças intestinais com paredes de espessura normal, estratificação das camadas preservada. Peristaltismo dentro dos padrões de normalidade. Não foram observadas obstruções ou massas.",
            
            "Pâncreas": "Pâncreas de dimensões e ecogenicidade normais, sem alterações estruturais evidentes.",
            
            "Adrenais": "Glândulas adrenais com forma, dimensões e ecogenicidade normais.",
            
            "Aparelho Reprodutor": "Estruturas do aparelho reprodutor sem alterações evidentes ao exame ultrassonográfico.",
            
            "Observações": "Nenhuma observação adicional."
        }
        
        return defaults.get(organ, "")
    
    def add_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Selecionar Imagens", "", 
                                              "Imagens (*.png *.jpg *.jpeg *.bmp)")
        
        if not files:
            return
            
        # Limpar o layout atual
        self.clear_images()
        
        # Armazenar os caminhos das imagens selecionadas
        self.image_paths = files
        
        # Adicionar as imagens à área de exibição
        col = 0
        row = 0
        max_cols = 3  # Número máximo de colunas
        
        for img_path in self.image_paths:
            if col >= max_cols:
                col = 0
                row += 1
                
            # Carregar e redimensionar a imagem
            pixmap = QPixmap(img_path)
            img_width = int(2.59 * 37.8)  # Converter cm para pixels (aproximadamente)
            img_height = int(4.65 * 37.8)  # Converter cm para pixels (aproximadamente)
            pixmap = pixmap.scaled(img_width, img_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Criar e adicionar o label da imagem
            img_label = QLabel()
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignCenter)
            img_label.setFixedSize(img_width, img_height)
            img_label.setStyleSheet("border: 1px solid #cccccc;")
            
            self.images_layout.addWidget(img_label, row, col)
            col += 1
    
    def clear_images(self):
        # Limpar todas as imagens
        self.image_paths = []
        
        # Remover widgets do layout
        while self.images_layout.count():
            item = self.images_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def get_complete_report(self):
        # Gerar o relatório completo
        report = ""
        
        # Informações do paciente
        report += "LAUDO DE ULTRASSONOGRAFIA VETERINÁRIA\n\n"
        report += f"Nome do Animal: {self.animal_name.toPlainText()}\n"
        report += f"Espécie: {self.species.toPlainText()}\n"
        report += f"Raça: {self.breed.toPlainText()}\n"
        report += f"Idade: {self.age.toPlainText()}\n"
        report += f"Proprietário: {self.owner.toPlainText()}\n"
        report += f"Data: {self.date.toPlainText()}\n\n"
        
        # Informações dos órgãos
        for organ in self.organ_texts:
            report += f"{organ.upper()}:\n"
            report += f"{self.organ_texts[organ].toPlainText()}\n\n"
        
        return report
    
    def print_preview(self):
        # Visualizar antes de imprimir
        dialog = QPrintPreviewDialog()
        dialog.paintRequested.connect(self.print_document)
        dialog.exec_()
    
    def print_report(self):
        # Imprimir o relatório
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QPrintDialog.Accepted:
            self.print_document(printer)
    
    def print_document(self, printer):
        # Função para imprimir o documento
        from PyQt5.QtGui import QTextDocument
        
        document = QTextDocument()
        document.setHtml(self.get_formatted_html())
        document.print_(printer)
    
    def get_formatted_html(self):
        # Formatar o relatório em HTML para impressão
        html = "<html><body>"
        html += "<h1 style='text-align:center;'>LAUDO DE ULTRASSONOGRAFIA VETERINÁRIA</h1>"
        
        # Informações do paciente
        html += "<table width='100%' style='border-collapse: collapse;'>"
        html += f"<tr><td><b>Nome do Animal:</b> {self.animal_name.toPlainText()}</td>"
        html += f"<td><b>Espécie:</b> {self.species.toPlainText()}</td></tr>"
        html += f"<tr><td><b>Raça:</b> {self.breed.toPlainText()}</td>"
        html += f"<td><b>Idade:</b> {self.age.toPlainText()}</td></tr>"
        html += f"<tr><td><b>Proprietário:</b> {self.owner.toPlainText()}</td>"
        html += f"<td><b>Data:</b> {self.date.toPlainText()}</td></tr>"
        html += "</table><hr>"
        
        # Informações dos órgãos - todos os órgãos primeiro
        for organ in self.organ_texts:
            html += f"<h3>{organ}</h3>"
            text = self.organ_texts[organ].toPlainText().replace('\n', '<br>')
            html += f"<p>{text}</p>"
        
        # Adicionar uma quebra clara antes das imagens
        html += "<div style='page-break-before: always;'></div>" if self.image_paths else ""
        
        # Adicionar imagens ao final
        if self.image_paths:
            html += "<h3>Imagens</h3>"
            html += "<table style='width:100%; border-collapse: collapse;'><tr>"
            
            for i, img_path in enumerate(self.image_paths):
                if i > 0 and i % 3 == 0:  # 3 imagens por linha
                    html += "</tr><tr>"
                
                html += f"<td style='text-align:center;'>"
                html += f"<img src='{img_path}' width='98px' height='176px' style='object-fit:contain;'>"
                html += "</td>"
            
            html += "</tr></table>"
        
        html += "</body></html>"
        return html
    
    def save_as_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar como PDF", "", "PDF Files (*.pdf)")
        
        if not file_path:
            return
            
        if not file_path.endswith('.pdf'):
            file_path += '.pdf'
        
        try:
            # Criar PDF usando ReportLab
            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4
            
            # Título
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width/2, height - 30, "LAUDO DE ULTRASSONOGRAFIA VETERINÁRIA")
            
            # Informações do paciente
            c.setFont("Helvetica-Bold", 12)
            y = height - 60
            
            # Linha 1
            c.drawString(50, y, f"Nome do Animal: ")
            c.setFont("Helvetica", 12)
            c.drawString(150, y, self.animal_name.toPlainText())
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(width/2, y, f"Espécie: ")
            c.setFont("Helvetica", 12)
            c.drawString(width/2 + 60, y, self.species.toPlainText())
            
            # Linha 2
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"Raça: ")
            c.setFont("Helvetica", 12)
            c.drawString(90, y, self.breed.toPlainText())
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(width/2, y, f"Idade: ")
            c.setFont("Helvetica", 12)
            c.drawString(width/2 + 50, y, self.age.toPlainText())
            
            # Linha 3
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"Proprietário: ")
            c.setFont("Helvetica", 12)
            c.drawString(130, y, self.owner.toPlainText())
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(width/2, y, f"Data: ")
            c.setFont("Helvetica", 12)
            c.drawString(width/2 + 40, y, self.date.toPlainText())
            
            # Linha separadora
            y -= 10
            c.line(50, y, width-50, y)
            
            # Conteúdo dos órgãos
            y -= 30
            
            for organ in self.organ_texts:
                if y < 100:  # Se estiver próximo do final da página, crie uma nova
                    c.showPage()
                    y = height - 50
                
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, f"{organ}:")
                y -= 20
                
                # Texto do órgão (pode precisar quebrar em várias linhas)
                text = self.organ_texts[organ].toPlainText()
                c.setFont("Helvetica", 10)
                
                # Texto com quebra de linha automática
                text_object = c.beginText(50, y)
                text_object.setFont("Helvetica", 10)
                
                # Quebrar o texto em linhas para caber na página
                lines = []
                current_line = ""
                for word in text.split():
                    test_line = current_line + " " + word if current_line else word
                    if c.stringWidth(test_line, "Helvetica", 10) < width - 100:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                # Adicionar linhas ao texto
                for line in lines:
                    text_object.textLine(line)
                    y -= 12  # Reduzir a posição Y para a próxima linha
                
                c.drawText(text_object)
                y -= 20  # Espaço adicional após o texto de cada órgão
            
            # Adicionar imagens
            if self.image_paths:
                if y < 200:  # Se estiver próximo do final da página, crie uma nova
                    c.showPage()
                    y = height - 50
                
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, "Imagens:")
                y -= 30
                
                # Definir tamanho das imagens (em cm convertidos para pontos)
                img_width = 2.59 * cm
                img_height = 4.65 * cm
                
                # Organizar as imagens em 3 colunas
                col = 0
                start_x = 50
                
                for img_path in self.image_paths:
                    if col >= 3:  # Nova linha após 3 imagens
                        col = 0
                        y -= (img_height + 10)  # Espaço vertical entre as linhas
                        
                        if y < img_height + 50:  # Se não couber na página atual
                            c.showPage()
                            y = height - 50
                    
                    # Calcular posição X para a imagem atual
                    x = start_x + col * (img_width + 20)
                    
                    # Adicionar a imagem
                    try:
                        img = Image.open(img_path)
                        img_aspect = img.width / img.height
                        
                        # Calcular dimensões respeitando o aspect ratio
                        if img_aspect > (img_width / img_height):  # Imagem mais larga
                            new_width = img_width
                            new_height = new_width / img_aspect
                        else:  # Imagem mais alta
                            new_height = img_height
                            new_width = new_height * img_aspect
                        
                        # Centralizar a imagem dentro do espaço alocado
                        x_offset = (img_width - new_width) / 2
                        y_offset = (img_height - new_height) / 2
                        
                        c.drawImage(img_path, x + x_offset, y - new_height - y_offset, width=new_width, height=new_height)
                    except Exception as e:
                        print(f"Erro ao adicionar imagem: {e}")
                    
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
