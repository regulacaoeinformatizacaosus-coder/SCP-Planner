import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QMessageBox, 
    QInputDialog, QMenu, QSystemTrayIcon, QSplitter, QStyle, 
    QDateTimeEdit, QComboBox, QFrame, QLineEdit, QTableWidget, QCheckBox,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog, 
    QFormLayout, QDialogButtonBox, QColorDialog
)
from PyQt6.QtCore import Qt, QDateTime, QTimer
from PyQt6.QtGui import QColor, QBrush, QCursor, QIcon
from logic import Categoria, Tarefa
from database import iniciar_db


import os
import json

# --- VERSÃO DA APLICAÇÃO ---
APP_VERSION = "1.0.0"

def obter_caminho_recurso(nome_ficheiro):
    """
    Resolve o caminho absoluto do ficheiro, seja no ambiente de desenvolvimento
    ou no ambiente de produção (executável PyInstaller).
    """
    try:
        # O PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        caminho_base = sys._MEIPASS
    except Exception:
        caminho_base = os.path.abspath(".")
    
    return os.path.join(caminho_base, nome_ficheiro)

# --- GESTÃO DE CONFIGURAÇÕES ---
CONFIG_FILE = "gcp_settings.json"

def guardar_config(key, value):
    """Guarda uma configuração específica num ficheiro JSON."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}
    config[key] = value
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def carregar_config(key, default=None):
    """Carrega uma configuração específica de um ficheiro JSON."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get(key, default)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

# --- TEMAS ---
THEMES = {
    "Dark": """
        QMainWindow, QDialog { background-color: #121212; }
        QWidget { color: #E0E0E0; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
        QFrame#sidebar { background-color: #1E1E1E; border-right: 1px solid #333333; }
        QTableWidget { background-color: #1E1E1E; gridline-color: #2b2b2b; border: none; }
        QTableWidget::item:selected { background-color: #2a2a2a; }
        QTableWidget QWidget { background-color: transparent; }
        QTableWidget QCheckBox::indicator:unchecked { border: 1px solid #555555; }
        QHeaderView::section { background-color: #252525; color: #888888; padding: 10px; border: none; font-weight: bold; }
        QLineEdit, QDateTimeEdit, QComboBox { background-color: #2b2b2b; border: 1px solid #444444; border-radius: 4px; padding: 5px; color: #ffffff; }
        QPushButton#addBtn { background-color: #1f538d; font-weight: bold; border: none; height: 30px; border-radius: 4px; color: white; }
        QPushButton#addBtn { background-color: #4f4f4f; color: #e0e0e0; font-weight: bold; border: none; height: 30px; border-radius: 4px; } QPushButton#addBtn:hover { background-color: #5a5a5a; }
        QPushButton#batchDone { background-color: #28a745; border: none; font-weight: bold; border-radius: 4px; padding: 6px 12px; color: white; }
        QPushButton#batchDel { background-color: #dc3545; border: none; font-weight: bold; border-radius: 4px; padding: 6px 12px; color: white; }
        QLabel#title { font-size: 20px; font-weight: bold; color: white; }
        QLabel#categoryHeaderLabel { font-weight: bold; color: #888888; margin-bottom: 5px; }
        QLabel#themeHeaderLabel { font-weight: bold; color: #888888; margin-top: 10px; }
        
        QPushButton.btnAction { border: none; border-radius: 4px; icon-size: 16px; }
        QPushButton#btnActionDone { background-color: #28a745; } QPushButton#btnActionDone:hover { background-color: #218838; }
        QPushButton#btnActionEdit { background-color: #ffdb58; } QPushButton#btnActionEdit:hover { background-color: #d4b239; }
        QPushButton#btnActionDelete { background-color: #dc3545; } QPushButton#btnActionDelete:hover { background-color: #c82333; }

        QLabel.badgeBase { font-size: 10px; font-weight: bold; color: white; border-radius: 4px; padding: 3px 7px; }
        QLabel.badgePrioAlta { background-color: #dc3545; }
        QLabel.badgePrioMedia { background-color: #fd7e14; }
        QLabel.badgePrioBaixa { background-color: #555555; }
        
        QListWidget { background-color: transparent; border: none; outline: 0; }
        QListWidget::item { padding: 2px; }
        QListWidget::item:selected { background-color: #2a2a2a; border-radius: 6px; }
    """,
    "Light": """
        QMainWindow, QDialog { background-color: #f0f0f0; }
        QWidget { color: #333333; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
        QFrame#sidebar { background-color: #e9e9e9; border-right: 1px solid #cccccc; }
        QTableWidget { background-color: #ffffff; gridline-color: #e0e0e0; border: none; }
        QTableWidget::item:selected { background-color: #d0d0d0; color: #000000; }
        QTableWidget QWidget { background-color: transparent; }
        QTableWidget QCheckBox::indicator:unchecked { border: 1px solid #aaaaaa; }
        QHeaderView::section { background-color: #e9e9e9; color: #555555; padding: 10px; border: none; font-weight: bold; }
        QLineEdit, QDateTimeEdit, QComboBox { background-color: #ffffff; border: 1px solid #cccccc; border-radius: 4px; padding: 5px; color: #000000; }
        QComboBox QAbstractItemView { background-color: #ffffff; border: 1px solid #cccccc; color: #000000; selection-background-color: #d0d0d0; }
        QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #e9e9e9; }
        QCalendarWidget QToolButton { color: #555555; background-color: transparent; border: none; }
        QCalendarWidget QToolButton:hover { background-color: #dcdcdc; border-radius: 3px; }
        QCalendarWidget QMenu { background-color: #ffffff; color: #000000; selection-background-color: #d0d0d0; }
        QCalendarWidget QSpinBox { background-color: #ffffff; color: #000000; border: 1px solid #cccccc; }
        QCalendarWidget QAbstractItemView { background-color: #ffffff; color: #000000; selection-background-color: #005a9e; selection-color: white; }
        QCalendarWidget QAbstractItemView:disabled { color: #c0c0c0; }
        QPushButton#addBtn { background-color: #005a9e; color: white; font-weight: bold; border: none; height: 30px; border-radius: 4px; }
        QPushButton#addBtn { background-color: #dcdcdc; color: #333333; font-weight: bold; border: none; height: 30px; border-radius: 4px; } QPushButton#addBtn:hover { background-color: #c8c8c8; }
        QPushButton#batchDone { background-color: #28a745; color: white; border: none; font-weight: bold; border-radius: 4px; padding: 6px 12px; }
        QPushButton#batchDel { background-color: #dc3545; color: white; border: none; font-weight: bold; border-radius: 4px; padding: 6px 12px; }
        QLabel#title { font-size: 20px; font-weight: bold; color: #333333; }
        QLabel#categoryHeaderLabel { font-weight: bold; color: #555555; margin-bottom: 5px; }
        QLabel#themeHeaderLabel { font-weight: bold; color: #555555; margin-top: 10px; }
        
        QPushButton.btnAction { border: none; border-radius: 4px; icon-size: 16px; }
        QPushButton#btnActionDone { background-color: #28a745; } QPushButton#btnActionDone:hover { background-color: #218838; }
        QPushButton#btnActionEdit { background-color: #ffdb58; } QPushButton#btnActionEdit:hover { background-color: #d4b239; }
        QPushButton#btnActionDelete { background-color: #dc3545; } QPushButton#btnActionDelete:hover { background-color: #c82333; }

        QLabel.badgeBase { font-size: 10px; font-weight: bold; color: white; border-radius: 4px; padding: 3px 7px; }
        QLabel.badgePrioAlta { background-color: #dc3545; }
        QLabel.badgePrioMedia { background-color: #fd7e14; }
        QLabel.badgePrioBaixa { background-color: #555555; }
        
        QListWidget { background-color: transparent; border: none; outline: 0; }
        QListWidget::item { padding: 2px; }
        QListWidget::item:selected { background-color: #d0d0d0; border-radius: 6px; }
    """,
    "Azure": """
        QMainWindow, QDialog { 
            background-color: #eaf6ff;
            /* Para imagem de marca d'água, descomente e ajuste o 'url':
            background-image: url('caminho/para/sua/imagem.png'); 
            background-repeat: no-repeat; 
            background-position: center; 
            */
        }
        QWidget { color: #0b3d5f; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
        QFrame#sidebar { background-color: #d1e9ff; border-right: 1px solid #a8c8e0; }
        QTableWidget { background-color: #f0faff; gridline-color: #cde6f8; border: none; }
        QTableWidget::item:selected { background-color: #a8d5ff; color: #082f4a; }
        QTableWidget QWidget { background-color: transparent; }
        QTableWidget QCheckBox::indicator:unchecked { border: 1px solid #a8c8e0; }
        QHeaderView::section { background-color: #c1d9ed; color: #0b3d5f; padding: 10px; border: none; font-weight: bold; }
        QLineEdit, QDateTimeEdit, QComboBox { background-color: #f0faff; border: 1px solid #a8c8e0; border-radius: 4px; padding: 5px; color: #082f4a; }
        QComboBox QAbstractItemView { background-color: #f0faff; border: 1px solid #a8c8e0; color: #082f4a; selection-background-color: #a8d5ff; }
        QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #c1d9ed; }
        QCalendarWidget QToolButton { color: #0b3d5f; background-color: transparent; border: none; }
        QCalendarWidget QToolButton:hover { background-color: #bde0ff; border-radius: 3px; }
        QCalendarWidget QMenu { background-color: #f0faff; color: #082f4a; selection-background-color: #a8d5ff; }
        QCalendarWidget QSpinBox { background-color: #f0faff; color: #082f4a; border: 1px solid #a8c8e0; }
        QCalendarWidget QAbstractItemView { background-color: #f0faff; color: #082f4a; selection-background-color: #005a9e; selection-color: white; }
        QCalendarWidget QAbstractItemView:disabled { color: #a8c8e0; }
        QPushButton#addBtn { background-color: #005a9e; color: white; font-weight: bold; border: none; height: 30px; border-radius: 4px; }
        QPushButton#addBtn { background-color: #c1d9ed; color: #0b3d5f; font-weight: bold; border: none; height: 30px; border-radius: 4px; } QPushButton#addBtn:hover { background-color: #b1cde4; }
        QPushButton#batchDone { background-color: #19692c; color: white; border: none; font-weight: bold; border-radius: 4px; padding: 6px 12px; }
        QPushButton#batchDel { background-color: #921622; color: white; border: none; font-weight: bold; border-radius: 4px; padding: 6px 12px; }
        QLabel#title { font-size: 20px; font-weight: bold; color: #0b3d5f; }
        QLabel#categoryHeaderLabel { font-weight: bold; color: #0b3d5f; margin-bottom: 5px; }
        QLabel#themeHeaderLabel { font-weight: bold; color: #0b3d5f; margin-top: 10px; }
        
        QPushButton.btnAction { border: none; border-radius: 4px; icon-size: 16px; }
        QPushButton#btnActionDone { background-color: #19692c; } QPushButton#btnActionDone:hover { background-color: #135221; }
        QPushButton#btnActionEdit { background-color: #ffdb58; } QPushButton#btnActionEdit:hover { background-color: #d4b239; }
        QPushButton#btnActionDelete { background-color: #921622; } QPushButton#btnActionDelete:hover { background-color: #7a121c; }

        QLabel.badgeBase { font-size: 10px; font-weight: bold; color: white; border-radius: 4px; padding: 3px 7px; }
        QLabel.badgePrioAlta { background-color: #921622; }
        QLabel.badgePrioMedia { background-color: #ad5300; }
        QLabel.badgePrioBaixa { background-color: #455d6e; }
        
        QListWidget { background-color: transparent; border: none; outline: 0; }
        QListWidget::item { padding: 2px; }
        QListWidget::item:selected { background-color: #a8d5ff; border-radius: 6px; }
    """
}

class EditTaskDialog(QDialog):
    def __init__(self, parent, tarefa_id):
        super().__init__(parent)
        self.setWindowTitle("Editar Demanda")
        self.setFixedSize(400, 380)
        self.tarefa_id = tarefa_id
        self.dados = dict(Tarefa.obter_por_id(tarefa_id))
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(15)

        self.ent_titulo = QLineEdit(self.dados['titulo'])
        
        self.cb_cat = QComboBox()
        for c in Categoria.listar():
            c_dict = dict(c)
            self.cb_cat.addItem(c_dict['nome'], c_dict['id'])
            if c_dict['id'] == self.dados['categoria_id']: 
                self.cb_cat.setCurrentText(c_dict['nome'])
            
        self.cb_prio = QComboBox()
        self.cb_prio.addItems(["Baixa", "Média", "Alta"])
        self.cb_prio.setCurrentIndex(self.dados['priority'] - 1)
        
        try:
            dt_obj = QDateTime.fromString(self.dados['data_vencimento'], "yyyy-MM-dd HH:mm:ss")
            self.dt_alerta = QDateTimeEdit(dt_obj)
        except:
            self.dt_alerta = QDateTimeEdit(QDateTime.currentDateTime())
            
        self.dt_alerta.setCalendarPopup(True)
        self.dt_alerta.setDisplayFormat("dd/MM/yyyy HH:mm")
        
        self.cb_rep = QComboBox()
        self.cb_rep.addItems(["Aviso Único", "5 min", "10 min", "15 min", "30 min"])
        rep_map = {0: 0, 5: 1, 10: 2, 15: 3, 30: 4}
        self.cb_rep.setCurrentIndex(rep_map.get(self.dados.get('alert_interval', 0), 0))

        layout.addRow("Descrição:", self.ent_titulo)
        layout.addRow("Categoria:", self.cb_cat)
        layout.addRow("Urgência:", self.cb_prio)
        layout.addRow("Alerta:", self.dt_alerta)
        layout.addRow("Repetição:", self.cb_rep)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Save).setStyleSheet("background-color: #1f538d; border: none; font-weight: bold; padding: 5px 15px;")
        layout.addRow(btns)

    def get_values(self):
        rep_values = [0, 5, 10, 15, 30]
        return (
            self.ent_titulo.text(),
            self.dt_alerta.dateTime().toPyDateTime(),
            self.cb_prio.currentIndex() + 1,
            self.cb_cat.currentData(),
            rep_values[self.cb_rep.currentIndex()]
        )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        iniciar_db()
        self.setWindowTitle(f"GCPlanner - Gestor de Demandas v{APP_VERSION}")
        self.setWindowIcon(QIcon(obter_caminho_recurso("icone.ico")))
        self.setGeometry(100, 100, 1250, 750)
        
        self.cat_id_filtro = None
        self.setup_ui()
        
        tema_guardado = carregar_config('tema', 'Dark')
        self.aplicar_tema(tema_guardado, setup=True)

        self.setup_tray()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.verificar_alertas)
        self.timer.start(30000)

        self.refresh_all()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # --- SIDEBAR ---
        sidebar = QFrame(); sidebar.setObjectName("sidebar")
        side_lay = QVBoxLayout(sidebar)
        
        lbl_cat = QLabel("FILTROS E CATEGORIAS")
        lbl_cat.setObjectName("categoryHeaderLabel")
        
        # O novo botão de visão global
        btn_todas = QPushButton("≡ Todas as Demandas")
        btn_todas.setStyleSheet("background-color: #333333; font-weight: bold; padding: 8px; border-radius: 4px; color: white; border: 1px solid #444444;")
        btn_todas.setToolTip("Mostrar todas as demandas")
        btn_todas.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_todas.clicked.connect(lambda: self.filtrar(None))

        btn_new_cat = QPushButton("+ Nova Categoria")
        btn_new_cat.setObjectName("addBtn")
        btn_new_cat.setToolTip("Adicionar uma nova categoria")
        btn_new_cat.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_new_cat.clicked.connect(self.nova_categoria)
        
        self.cat_list = QListWidget()
        self.cat_list.setToolTip("Clique para filtrar por categoria ou clique com o botão direito para mais opções")
        self.cat_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.cat_list.customContextMenuRequested.connect(self.menu_categoria)
        self.cat_list.itemClicked.connect(lambda i: self.filtrar(i.data(Qt.ItemDataRole.UserRole)))
        
        side_lay.addWidget(lbl_cat)
        side_lay.addWidget(btn_todas)
        side_lay.addWidget(btn_new_cat)
        side_lay.addWidget(self.cat_list)
        
        side_lay.addStretch(1)

        # Seletor de Tema
        lbl_tema = QLabel("Tema Visual")
        lbl_tema.setObjectName("themeHeaderLabel")
        self.cb_temas = QComboBox()
        self.cb_temas.addItems(list(THEMES.keys()))
        self.cb_temas.setToolTip("Selecionar o tema visual da aplicação")
        self.cb_temas.currentTextChanged.connect(self.aplicar_tema)

        side_lay.addWidget(lbl_tema)
        side_lay.addWidget(self.cb_temas)
        
        splitter.addWidget(sidebar)

        # --- ÁREA PRINCIPAL ---
        main_area = QWidget()
        main_lay = QVBoxLayout(main_area)
        
        head = QHBoxLayout()
        self.lbl_title = QLabel("Todas as Demandas"); self.lbl_title.setObjectName("title")
        btn_done = QPushButton("✓ Concluir Selecionados"); btn_done.setObjectName("batchDone")
        btn_del = QPushButton("X Excluir Selecionados"); btn_del.setObjectName("batchDel")
        btn_done.setToolTip("Marcar as demandas selecionadas na tabela como concluídas")
        btn_del.setToolTip("Excluir permanentemente as demandas selecionadas na tabela")
        btn_done.clicked.connect(self.lote_concluir)
        btn_del.clicked.connect(self.lote_excluir)
        
        head.addWidget(self.lbl_title); head.addStretch()
        head.addWidget(btn_done); head.addWidget(btn_del)
        main_lay.addLayout(head)

        inp_frame = QFrame()
        inp_lay = QHBoxLayout(inp_frame)
        self.ent_task = QLineEdit(); self.ent_task.setPlaceholderText("Descrição da nova demanda...")
        self.ent_task.setToolTip("Digite a descrição da nova demanda")
        self.dt_task = QDateTimeEdit(QDateTime.currentDateTime()); self.dt_task.setCalendarPopup(True)
        self.dt_task.setToolTip("Selecione a data e hora do alerta")
        self.cb_rep_main = QComboBox(); self.cb_rep_main.addItems(["Único", "5 min", "10 min", "15 min", "30 min"])
        self.cb_rep_main.setToolTip("Intervalo de repetição do alerta após o vencimento")
        self.cb_prio_main = QComboBox(); self.cb_prio_main.addItems(["Baixa", "Média", "Alta"])
        self.cb_prio_main.setToolTip("Defina o nível de urgência da demanda")
        btn_reg = QPushButton("Registrar"); btn_reg.setObjectName("addBtn")
        btn_reg.setToolTip("Registrar nova demanda com os dados informados")
        btn_reg.clicked.connect(self.registrar_tarefa)
        
        inp_lay.addWidget(self.ent_task, 3); inp_lay.addWidget(self.dt_task, 1)
        inp_lay.addWidget(self.cb_rep_main, 1); inp_lay.addWidget(self.cb_prio_main, 1)
        inp_lay.addWidget(btn_reg, 1)
        main_lay.addWidget(inp_frame)

        # --- TABELA ---
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["", "Demanda", "Categoria", "Urgência", "Alerta", "Ações"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setWordWrap(True) 

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(0, 40)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) 
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(5, 100)
        
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.menu_tabela)
        main_lay.addWidget(self.table)
        
        splitter.addWidget(main_area)
        splitter.setSizes([220, 1030])

    def aplicar_tema(self, nome_tema, setup=False):
        """Aplica o tema selecionado à aplicação e guarda a seleção."""
        stylesheet = THEMES.get(nome_tema, THEMES['Dark'])
        self.setStyleSheet(stylesheet)
        
        if hasattr(self, 'cb_temas') and self.cb_temas.currentText() != nome_tema:
            self.cb_temas.setCurrentText(nome_tema)
        
        if not setup:
            guardar_config('tema', nome_tema)

    def setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon(obter_caminho_recurso("icone.ico")))
        menu = QMenu()
        menu.addAction("Abrir GCP").triggered.connect(self.showNormal)
        menu.addAction("Sair").triggered.connect(QApplication.instance().quit)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def closeEvent(self, event):
        self.hide()
        event.ignore()
        self.tray.showMessage(
            "GCPlanner em Execução",
            "O programa continua a verificar suas demandas em segundo plano. Clique com o botão direito no ícone para sair.",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    # --- MÉTODOS RECUPERADOS: REGISTO E COR ---
    def registrar_tarefa(self):
        titulo = self.ent_task.text().strip()
        if not titulo: return
        
        rep_map = {0: 0, 1: 5, 2: 10, 3: 15, 4: 30}
        intervalo = rep_map[self.cb_rep_main.currentIndex()]
        
        Tarefa.adicionar(
            titulo, 
            self.dt_task.dateTime().toPyDateTime(), 
            self.cat_id_filtro if self.cat_id_filtro else 1, 
            self.cb_prio_main.currentIndex() + 1,
            intervalo
        )
        
        self.ent_task.clear()
        self.cb_rep_main.setCurrentIndex(0)
        self.refresh_all()

    def obter_cor_cat(self, cat_id):
        for c in Categoria.listar():
            c_dict = dict(c)
            if c_dict['id'] == cat_id: return c_dict.get('cor', '#1f538d')
        return '#1f538d'

    # --- ATUALIZAÇÃO DA INTERFACE ---
    def refresh_all(self):
        self.cat_list.clear()
        for c in Categoria.listar():
            c_dict = dict(c)
            item = QListWidgetItem()
            self.cat_list.addItem(item)
            
            container = QWidget()
            lay = QVBoxLayout(container); lay.setContentsMargins(4, 4, 4, 4)
            
            lbl = QLabel(c_dict['nome'].upper())
            cor = c_dict.get('cor', '#1f538d')
            lbl.setStyleSheet(f"background-color: {cor}; color: white; font-weight: bold; border-radius: 6px; padding: 6px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            
            lay.addWidget(lbl)
            item.setSizeHint(container.sizeHint())
            self.cat_list.setItemWidget(item, container)
            item.setData(Qt.ItemDataRole.UserRole, c_dict['id'])

        self.table.setRowCount(0)
        tarefas = Tarefa.listar_pendentes_por_categoria(self.cat_id_filtro) if self.cat_id_filtro else Tarefa.listar_todas_pendentes()
        
        for i, t in enumerate(tarefas):
            t_dict = dict(t)
            self.table.insertRow(i)
            
            # --- Checkbox Centralizado ---
            w_chk = QWidget()
            l_chk = QHBoxLayout(w_chk)
            l_chk.setContentsMargins(0,0,0,0)
            chk = QCheckBox(); chk.setProperty("task_id", t_dict['id'])
            l_chk.addWidget(chk)
            l_chk.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(i, 0, w_chk)
            
            icone = " 🔄" if t_dict.get('alert_interval', 0) > 0 else ""
            self.table.setItem(i, 1, QTableWidgetItem(t_dict['titulo'] + icone))
            
            cor_cat = self.obter_cor_cat(t_dict['categoria_id'])
            lbl_cat = QLabel(t_dict['categoria_nome'].upper())
            lbl_cat.setProperty("class", "badgeBase")
            lbl_cat.setStyleSheet(f"background-color: {cor_cat};")
            lbl_cat.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            w_cat = QWidget(); l_cat = QHBoxLayout(w_cat); l_cat.setContentsMargins(5,5,5,5); l_cat.addWidget(lbl_cat)
            self.table.setCellWidget(i, 2, w_cat)
            
            p_class = "badgePrioAlta" if t_dict['priority'] == 3 else ("badgePrioMedia" if t_dict['priority'] == 2 else "badgePrioBaixa")
            lbl_prio = QLabel(["BAIXA", "MÉDIA", "ALTA"][t_dict['priority']-1])
            lbl_prio.setProperty("class", f"badgeBase {p_class}")
            lbl_prio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            w_prio = QWidget(); l_prio = QHBoxLayout(w_prio); l_prio.setContentsMargins(5,5,5,5); l_prio.addWidget(lbl_prio)
            self.table.setCellWidget(i, 3, w_prio)
            
            self.table.setItem(i, 4, QTableWidgetItem(t_dict['data_vencimento']))

            # --- Botões de Ação com Ícones ---
            w_act = QWidget(); l_act = QHBoxLayout(w_act)
            l_act.setContentsMargins(2,2,2,2); l_act.setSpacing(4)

            btn_done_act = QPushButton(QIcon(obter_caminho_recurso("icon_concluido.png")), "")
            btn_done_act.setObjectName("btnActionDone")
            btn_done_act.setProperty("class", "btnAction")
            btn_done_act.setToolTip("Marcar como concluída")
            btn_done_act.setCursor(QCursor(Qt.CursorShape.PointingHandCursor)); btn_done_act.setFixedSize(28, 28)
            btn_done_act.clicked.connect(lambda _, tid=t_dict['id']: self.marcar_concluida_direta(tid))

            btn_edit_act = QPushButton(QIcon(obter_caminho_recurso("icon_editar.png")), "")
            btn_edit_act.setObjectName("btnActionEdit")
            btn_edit_act.setProperty("class", "btnAction")
            btn_edit_act.setToolTip("Editar demanda")
            btn_edit_act.setCursor(QCursor(Qt.CursorShape.PointingHandCursor)); btn_edit_act.setFixedSize(28, 28)
            btn_edit_act.clicked.connect(lambda _, tid=t_dict['id']: self.abrir_edicao_direta(tid))

            btn_del_act = QPushButton(QIcon(obter_caminho_recurso("icon_excluir.png")), "")
            btn_del_act.setObjectName("btnActionDelete")
            btn_del_act.setProperty("class", "btnAction")
            btn_del_act.setToolTip("Excluir demanda")
            btn_del_act.setCursor(QCursor(Qt.CursorShape.PointingHandCursor)); btn_del_act.setFixedSize(28, 28)
            btn_del_act.clicked.connect(lambda _, tid=t_dict['id']: self.deletar_tarefa_direta(tid))
            
            l_act.addWidget(btn_done_act); l_act.addWidget(btn_edit_act); l_act.addWidget(btn_del_act)
            self.table.setCellWidget(i, 5, w_act)

        self.table.resizeRowsToContents() 

    # --- MÉTODOS DE CONTROLO ---
    def nova_categoria(self):
        nome, ok = QInputDialog.getText(self, "Nova Categoria", "Nome:")
        if ok and nome.strip(): Categoria.adicionar(nome.strip()); self.refresh_all()

    def menu_categoria(self, pos):
        item = self.cat_list.itemAt(pos)
        if not item: return
        cat_id = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu()
        ren_act = menu.addAction("Renomear"); col_act = menu.addAction("Mudar Cor")
        act = menu.exec(self.cat_list.mapToGlobal(pos))
        cat_dict = next((dict(c) for c in Categoria.listar() if c['id'] == cat_id), None)
        if act == ren_act:
            novo, ok = QInputDialog.getText(self, "Renomear", "Novo nome:", text=cat_dict['nome'])
            if ok: Categoria.atualizar(cat_id, novo.strip(), cat_dict['cor']); self.refresh_all()
        elif act == col_act:
            cor = QColorDialog.getColor(QColor(cat_dict['cor']))
            if cor.isValid(): Categoria.atualizar(cat_id, cat_dict['nome'], cor.name()); self.refresh_all()

    def filtrar(self, cid): self.cat_id_filtro = cid; self.refresh_all()
    def filtrar(self, cid):
        self.cat_id_filtro = cid
        if cid is None:
            self.lbl_title.setText("Todas as Demandas")
        else:
            categoria = Categoria.obter_por_id(cid)
            if categoria:
                self.lbl_title.setText(dict(categoria)['nome'].upper())
            else:
                self.lbl_title.setText("Filtro Ativo") # Fallback
        self.refresh_all()

    def marcar_concluida_direta(self, tid):
        Tarefa.concluir(tid); self.refresh_all()

    def deletar_tarefa_direta(self, tid):
        if QMessageBox.question(self, "Aviso", "Excluir permanentemente?") == QMessageBox.StandardButton.Yes:
            Tarefa.excluir(tid); self.refresh_all()

    def abrir_edicao_direta(self, tid):
        diag = EditTaskDialog(self, tid)
        if diag.exec():
            Tarefa.atualizar(tid, *diag.get_values())
            self.refresh_all()

    def lote_concluir(self):
        ids_a_concluir = []
        for r in range(self.table.rowCount()):
            widget = self.table.cellWidget(r, 0)
            if widget and (checkbox := widget.findChild(QCheckBox)) and checkbox.isChecked():
                ids_a_concluir.append(checkbox.property("task_id"))
        
        if ids_a_concluir:
            for tid in ids_a_concluir:
                Tarefa.concluir(tid)
            self.refresh_all()

    def lote_excluir(self):
        ids_a_excluir = []
        for r in range(self.table.rowCount()):
            widget = self.table.cellWidget(r, 0)
            if widget and (checkbox := widget.findChild(QCheckBox)) and checkbox.isChecked():
                ids_a_excluir.append(checkbox.property("task_id"))

        if ids_a_excluir and QMessageBox.question(self, "Aviso", f"Excluir permanentemente as {len(ids_a_excluir)} demandas selecionadas?") == QMessageBox.StandardButton.Yes:
            for tid in ids_a_excluir:
                Tarefa.excluir(tid)
            self.refresh_all()

    def menu_tabela(self, pos):
        idx = self.table.indexAt(pos)
        if idx.isValid():
            widget = self.table.cellWidget(idx.row(), 0)
            if not widget or not (checkbox := widget.findChild(QCheckBox)):
                return
            tid = checkbox.property("task_id")
            menu = QMenu()
            edit = menu.addAction("Editar"); done = menu.addAction("Concluir")
            act = menu.exec(self.table.mapToGlobal(pos))
            if act == edit: self.abrir_edicao_direta(tid)
            elif act == done: self.marcar_concluida_direta(tid)

    def verificar_alertas(self):
        agora = datetime.now()
        for t in Tarefa.listar_todas_pendentes():
            t_dict = dict(t)
            if not t_dict['data_vencimento']: continue
            venc = datetime.strptime(t_dict['data_vencimento'], "%Y-%m-%d %H:%M:%S")
            if agora >= venc:
                enviar = False
                if not t_dict['notificado']: enviar = True
                elif t_dict.get('alert_interval', 0) > 0 and t_dict.get('last_alerted_at'):
                    prox = datetime.strptime(t_dict['last_alerted_at'], "%Y-%m-%d %H:%M:%S") + timedelta(minutes=t_dict['alert_interval'])
                    if agora >= prox: enviar = True
                if enviar:
                    self.tray.showMessage("🚨 ALERTA GCP", f"Demanda: {t_dict['titulo']}", QSystemTrayIcon.MessageIcon.Warning)
                    Tarefa.registrar_alerta_enviado(t_dict['id'], agora.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
