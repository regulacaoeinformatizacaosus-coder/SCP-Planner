import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QMessageBox, 
    QInputDialog, QMenu, QSystemTrayIcon, QSplitter, QStyle, 
    QDateTimeEdit, QDateEdit, QComboBox, QFrame, QLineEdit, QTableWidget, QCheckBox,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog, 
    QFormLayout, QDialogButtonBox, QColorDialog
)
from PyQt6.QtCore import Qt, QDate, QDateTime, QTimer
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
        QPushButton { border: 1px solid #b8c0c7; }
        QFrame#sidebar { background-color: #1E1E1E; border-right: 1px solid #333333; }
        QTableWidget { background-color: #1E1E1E; gridline-color: #2b2b2b; border: none; }
        QTableWidget::item:selected { background-color: #2a2a2a; }
        QTableWidget QWidget { background-color: transparent; }
        QTableWidget QLineEdit { background-color: #2b2b2b; color: #ffffff; border: 1px solid #4f86b8; }
        QTableWidget QCheckBox::indicator:unchecked { border: 1px solid #555555; }
        QHeaderView::section { background-color: #252525; color: #888888; padding: 10px; border: none; font-weight: bold; }
        QLineEdit, QDateTimeEdit, QComboBox { background-color: #2b2b2b; border: 1px solid #444444; border-radius: 4px; padding: 5px; color: #ffffff; }
        QPushButton#addBtn { background-color: #1f538d; font-weight: bold; border: none; height: 30px; border-radius: 4px; color: white; }
        QPushButton#addBtn { background-color: #4f4f4f; color: #e0e0e0; font-weight: bold; border: 1px solid #b8c0c7; height: 30px; border-radius: 4px; } QPushButton#addBtn:hover { background-color: #5a5a5a; }
        QPushButton#allTasksBtn { background-color: #333333; color: white; border: 1px solid #b8c0c7; font-weight: bold; padding: 8px; border-radius: 4px; }
        QPushButton#batchSelect { background-color: #3d566e; border: 1px solid #b8c0c7; font-weight: bold; border-radius: 4px; padding: 6px 12px; color: white; }
        QPushButton#batchSelect:hover { background-color: #4a6680; }
        QPushButton#batchDel { background-color: #7a454b; border: 1px solid #b8c0c7; font-weight: bold; border-radius: 4px; padding: 6px 12px; color: white; }
        QPushButton#batchDel:hover { background-color: #8d5259; }
        QLabel#title { font-size: 20px; font-weight: bold; color: white; }
        QLabel#categoryHeaderLabel { font-weight: bold; color: #888888; margin-bottom: 5px; }
        QLabel#themeHeaderLabel { font-weight: bold; color: #888888; margin-top: 10px; }
        
        QPushButton.btnAction { border: none; border-radius: 4px; icon-size: 16px; }
        QPushButton#btnActionDone, QPushButton#btnActionEdit, QPushButton#btnActionDelete { background-color: transparent; border: none; }
        QPushButton#btnActionDone:hover, QPushButton#btnActionEdit:hover, QPushButton#btnActionDelete:hover { background-color: transparent; }

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
        QPushButton { background-color: #e2e7eb; color: #27343d; border: 1px solid #b8c0c7; border-radius: 4px; padding: 5px 10px; }
        QPushButton:hover { background-color: #d5dde3; }
        QFrame#sidebar { background-color: #e9e9e9; border-right: 1px solid #cccccc; }
        QTableWidget { background-color: #ffffff; gridline-color: #e0e0e0; border: none; }
        QTableWidget::item:selected { background-color: #d0d0d0; color: #000000; }
        QTableWidget QWidget { background-color: transparent; }
        QTableWidget QLineEdit { background-color: #ffffff; color: #000000; border: 1px solid #005a9e; }
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
        QPushButton#addBtn { background-color: #dcdcdc; color: #333333; font-weight: bold; border: 1px solid #b8c0c7; height: 30px; border-radius: 4px; } QPushButton#addBtn:hover { background-color: #c8c8c8; }
        QPushButton#batchSelect { background-color: #d7e2eb; color: #29455c; border: 1px solid #b8c0c7; font-weight: bold; border-radius: 4px; padding: 6px 12px; }
        QPushButton#batchSelect:hover { background-color: #c5d5e1; }
        QPushButton#batchDel { background-color: #dfe3e6; color: #27343d; border: 1px solid #b8c0c7; font-weight: bold; border-radius: 4px; padding: 6px 12px; }
        QPushButton#batchDel:hover { background-color: #d1d7db; }
        QPushButton#allTasksBtn { background-color: #dfe3e6; color: #27343d; border: 1px solid #b8c0c7; }
        QPushButton#allTasksBtn:hover { background-color: #d1d7db; }
        QLabel#title { font-size: 20px; font-weight: bold; color: #333333; }
        QLabel#categoryHeaderLabel { font-weight: bold; color: #555555; margin-bottom: 5px; }
        QLabel#themeHeaderLabel { font-weight: bold; color: #555555; margin-top: 10px; }
        
        QPushButton.btnAction { border: none; border-radius: 4px; icon-size: 16px; }
        QPushButton#btnActionDone, QPushButton#btnActionEdit, QPushButton#btnActionDelete { background-color: transparent; border: none; }
        QPushButton#btnActionDone:hover, QPushButton#btnActionEdit:hover, QPushButton#btnActionDelete:hover { background-color: transparent; }

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
        QPushButton { background-color: #dfe3e6; color: #27343d; border: 1px solid #b8c0c7; border-radius: 4px; padding: 5px 10px; }
        QPushButton:hover { background-color: #d1d7db; }
        QFrame#sidebar { background-color: #d1e9ff; border-right: 1px solid #a8c8e0; }
        QTableWidget { background-color: #f0faff; gridline-color: #cde6f8; border: none; }
        QTableWidget::item:selected { background-color: #a8d5ff; color: #082f4a; }
        QTableWidget QWidget { background-color: transparent; }
        QTableWidget QLineEdit { background-color: #f0faff; color: #082f4a; border: 1px solid #4d9bd1; }
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
        QPushButton#addBtn { background-color: #dfe3e6; color: #27343d; font-weight: bold; border: 1px solid #b8c0c7; height: 30px; border-radius: 4px; }
        QPushButton#addBtn:hover { background-color: #d1d7db; }
        QPushButton#batchSelect { background-color: #dfe3e6; color: #27343d; border: 1px solid #b8c0c7; font-weight: bold; border-radius: 4px; padding: 6px 12px; }
        QPushButton#batchSelect:hover { background-color: #d1d7db; }
        QPushButton#batchDel { background-color: #dfe3e6; color: #27343d; border: 1px solid #b8c0c7; font-weight: bold; border-radius: 4px; padding: 6px 12px; }
        QPushButton#batchDel:hover { background-color: #d1d7db; }
        QPushButton#allTasksBtn { background-color: #dfe3e6; color: #27343d; border: 1px solid #b8c0c7; }
        QPushButton#allTasksBtn:hover { background-color: #d1d7db; }
        QLabel#title { font-size: 20px; font-weight: bold; color: #0b3d5f; }
        QLabel#categoryHeaderLabel { font-weight: bold; color: #0b3d5f; margin-bottom: 5px; }
        QLabel#themeHeaderLabel { font-weight: bold; color: #0b3d5f; margin-top: 10px; }
        
        QPushButton.btnAction { border: none; border-radius: 4px; icon-size: 16px; }
        QPushButton#btnActionDone, QPushButton#btnActionEdit, QPushButton#btnActionDelete { background-color: transparent; border: none; }
        QPushButton#btnActionDone:hover, QPushButton#btnActionEdit:hover, QPushButton#btnActionDelete:hover { background-color: transparent; }

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
        self.setFixedSize(500, 520)
        self.tarefa_id = tarefa_id
        self.dados = dict(Tarefa.obter_por_id(tarefa_id))
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(15)

        self.ent_titulo = QLineEdit(self.dados['titulo'])
        self.ent_prestador = QLineEdit(self.dados.get('prestador', ''))
        self.ent_tipo = QLineEdit(self.dados.get('tipo_pagamento', ''))
        self.ent_financiamento = QLineEdit(self.dados.get('financiamento', ''))
        self.ent_observacao = QLineEdit(self.dados.get('observacao', ''))
        
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

        ano, mes = map(int, self.dados.get('mes_referencia', datetime.now().strftime('%Y-%m')).split('-'))
        self.dt_mes = QDateEdit(QDate(ano, mes, 1))
        self.dt_mes.setDisplayFormat("MM/yyyy")
        self.dt_mes.setCalendarPopup(True)
        
        self.cb_rep = QComboBox()
        self.cb_rep.addItems(["Aviso Único", "5 min", "10 min", "15 min", "30 min"])
        rep_map = {0: 0, 5: 1, 10: 2, 15: 3, 30: 4}
        self.cb_rep.setCurrentIndex(rep_map.get(self.dados.get('alert_interval', 0), 0))

        layout.addRow("Descrição:", self.ent_titulo)
        layout.addRow("Prestador:", self.ent_prestador)
        layout.addRow("Tipo de pagamento:", self.ent_tipo)
        layout.addRow("Financiamento:", self.ent_financiamento)
        layout.addRow("Obs.:", self.ent_observacao)
        layout.addRow("Mês de referência:", self.dt_mes)
        layout.addRow("Categoria:", self.cb_cat)
        layout.addRow("Urgência:", self.cb_prio)
        layout.addRow("Alerta:", self.dt_alerta)
        layout.addRow("Repetição:", self.cb_rep)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Save).setMinimumWidth(80)
        layout.addRow(btns)

    def get_values(self):
        rep_values = [0, 5, 10, 15, 30]
        return (
            self.ent_titulo.text(),
            self.dt_alerta.dateTime().toPyDateTime(),
            self.cb_prio.currentIndex() + 1,
            self.cb_cat.currentData(),
            rep_values[self.cb_rep.currentIndex()],
            self.ent_prestador.text().strip(),
            self.ent_tipo.text().strip(),
            self.ent_financiamento.text().strip(),
            self.dt_mes.date().toString("yyyy-MM"),
            self.ent_observacao.text().strip()
        )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        iniciar_db()
        self.setWindowTitle(f"GCPlanner - Gestor de Demandas v{APP_VERSION}")
        self.setWindowIcon(QIcon(obter_caminho_recurso("icone.ico")))
        area_disponivel = QApplication.primaryScreen().availableGeometry()
        largura = min(1250, area_disponivel.width() - 20)
        altura = min(750, area_disponivel.height() - 20)
        self.resize(largura, altura)
        self.move(area_disponivel.left() + (area_disponivel.width() - largura) // 2,
              area_disponivel.top() + (area_disponivel.height() - altura) // 2)
        
        self.cat_id_filtro = None
        self.mes_atual = datetime.now().strftime("%Y-%m")
        self.filtros_colunas = {}
        self.controles_filtro = {}
        self._atualizando_tabela = False
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
        btn_todas.setObjectName("allTasksBtn")
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
        btn_select_all = QPushButton("Selecionar todos"); btn_select_all.setObjectName("batchSelect")
        btn_del = QPushButton("X Excluir Selecionados"); btn_del.setObjectName("batchDel")
        btn_select_all.setToolTip("Selecionar ou desmarcar todas as demandas visíveis")
        btn_del.setToolTip("Excluir permanentemente as demandas selecionadas na tabela")
        btn_select_all.clicked.connect(self.selecionar_todos)
        btn_del.clicked.connect(self.lote_excluir)

        self.dt_mes_filtro = QDateEdit(QDateTime.currentDateTime().date())
        self.dt_mes_filtro.setDisplayFormat("MM/yyyy")
        self.dt_mes_filtro.setCalendarPopup(True)
        self.dt_mes_filtro.setToolTip("Selecione o mês do checklist")
        self.dt_mes_filtro.dateChanged.connect(self.mudar_mes)
        btn_copiar = QPushButton("Copiar mês anterior")
        btn_copiar.setToolTip("Copiar os itens do mês anterior para o mês selecionado")
        btn_copiar.clicked.connect(self.copiar_mes_anterior)
        
        head.addWidget(self.lbl_title); head.addStretch()
        head.addWidget(QLabel("Mês:")); head.addWidget(self.dt_mes_filtro); head.addWidget(btn_copiar)
        head.addWidget(btn_select_all); head.addWidget(btn_del)
        main_lay.addLayout(head)

        inp_frame = QFrame()
        inp_lay = QHBoxLayout(inp_frame)
        self.ent_task = QLineEdit(); self.ent_task.setPlaceholderText("Descrição da nova demanda...")
        self.ent_prestador = QLineEdit(); self.ent_prestador.setPlaceholderText("Prestador")
        self.ent_tipo = QLineEdit(); self.ent_tipo.setPlaceholderText("Tipo de pagamento")
        self.ent_financiamento = QLineEdit(); self.ent_financiamento.setPlaceholderText("Financiamento")
        self.ent_observacao = QLineEdit(); self.ent_observacao.setPlaceholderText("Obs.")
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
        
        inp_lay.addWidget(self.ent_task, 3); inp_lay.addWidget(self.ent_prestador, 2)
        inp_lay.addWidget(self.ent_tipo, 2); inp_lay.addWidget(self.ent_financiamento, 2); inp_lay.addWidget(self.ent_observacao, 2)
        inp_lay.addWidget(self.dt_task, 2)
        inp_lay.addWidget(self.cb_rep_main, 1); inp_lay.addWidget(self.cb_prio_main, 1)
        inp_lay.addWidget(btn_reg, 1)
        main_lay.addWidget(inp_frame)

        filtro_frame = QFrame()
        filtro_lay = QHBoxLayout(filtro_frame)
        filtro_lay.setContentsMargins(0, 0, 0, 0)
        filtro_lay.addWidget(QLabel("Filtros:"))
        nomes_filtro = {
            1: "Descrição", 2: "Prestador", 3: "Tipo de pagamento", 4: "Financiamento",
            5: "Categoria", 6: "Urgência", 7: "Status", 8: "Vencimento"
        }
        for coluna, nome in nomes_filtro.items():
            filtro_coluna = QWidget()
            filtro_coluna_lay = QVBoxLayout(filtro_coluna)
            filtro_coluna_lay.setContentsMargins(0, 0, 0, 0)
            filtro_coluna_lay.setSpacing(2)
            filtro_coluna_lay.addWidget(QLabel(nome))
            combo = QComboBox()
            combo.setToolTip(f"Filtrar por {nome}")
            combo.currentIndexChanged.connect(lambda _, col=coluna: self.aplicar_filtro_coluna(col))
            self.controles_filtro[coluna] = combo
            filtro_coluna_lay.addWidget(combo)
            filtro_lay.addWidget(filtro_coluna, 1)
        btn_limpar_filtros = QPushButton("Limpar filtros")
        btn_limpar_filtros.setToolTip("Remover todos os filtros das colunas")
        btn_limpar_filtros.clicked.connect(self.limpar_filtros)
        filtro_lay.addWidget(btn_limpar_filtros)
        main_lay.addWidget(filtro_frame)

        # --- TABELA ---
        self.table = QTableWidget(0, 11)
        self.table.setHorizontalHeaderLabels(["", "Descrição", "Prestador", "Tipo de pagamento", "Financiamento", "Categoria", "Urgência", "Status", "Vencimento", "Obs.", "Ações"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setWordWrap(True) 

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(0, 40)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for column in (2, 3, 4, 5, 6, 7, 8, 9):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(10, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(10, 100)
        
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.menu_tabela)
        self.table.itemChanged.connect(self.salvar_edicao_celula)
        main_lay.addWidget(self.table)
        
        splitter.addWidget(main_area)
        splitter.setSizes([220, 1030])

    def aplicar_tema(self, nome_tema, setup=False):
        """Aplica o tema selecionado à aplicação e guarda a seleção."""
        estava_maximizada = self.isMaximized()
        geometria_anterior = self.geometry()
        stylesheet = THEMES.get(nome_tema, THEMES['Dark'])
        self.setStyleSheet(stylesheet)

        if estava_maximizada:
            self.showMaximized()
        else:
            area = self.screen().availableGeometry()
            largura = min(geometria_anterior.width(), area.width())
            altura = min(geometria_anterior.height(), area.height())
            x = max(area.left(), min(geometria_anterior.x(), area.right() - largura + 1))
            y = max(area.top(), min(geometria_anterior.y(), area.bottom() - altura + 1))
            self.setGeometry(x, y, largura, altura)
        
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
        self.timer.stop()
        self.tray.hide()
        event.accept()

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
            intervalo,
            self.ent_prestador.text().strip(),
            self.ent_tipo.text().strip(),
            self.ent_financiamento.text().strip(),
            self.mes_atual,
            self.ent_observacao.text().strip()
        )
        
        self.ent_task.clear()
        self.ent_prestador.clear(); self.ent_tipo.clear(); self.ent_financiamento.clear(); self.ent_observacao.clear()
        self.cb_rep_main.setCurrentIndex(0)
        self.refresh_all()

    def obter_cor_cat(self, cat_id):
        for c in Categoria.listar():
            c_dict = dict(c)
            if c_dict['id'] == cat_id: return c_dict.get('cor', '#1f538d')
        return '#1f538d'

    # --- ATUALIZAÇÃO DA INTERFACE ---
    def refresh_all(self):
        self._atualizando_tabela = True
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
        categoria = Categoria.obter_por_id(self.cat_id_filtro) if self.cat_id_filtro else None
        categoria_geral = categoria and dict(categoria).get('nome', '').strip().casefold() == 'geral'
        if categoria_geral:
            tarefas = Tarefa.listar_por_categoria(self.cat_id_filtro)
        else:
            tarefas = Tarefa.listar_por_mes(self.mes_atual, self.cat_id_filtro)
        self.atualizar_opcoes_filtros(tarefas)
        tarefas = [t for t in tarefas if self.tarefa_corresponde_a_filtros(t)]
        
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
            self.table.setItem(i, 2, QTableWidgetItem(t_dict.get('prestador', '')))
            self.table.setItem(i, 3, QTableWidgetItem(t_dict.get('tipo_pagamento', '')))
            self.table.setItem(i, 4, QTableWidgetItem(t_dict.get('financiamento', '')))
            
            cor_cat = self.obter_cor_cat(t_dict['categoria_id'])
            lbl_cat = QLabel(t_dict['categoria_nome'].upper())
            lbl_cat.setProperty("class", "badgeBase")
            lbl_cat.setStyleSheet(f"background-color: {cor_cat};")
            lbl_cat.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            w_cat = QWidget(); l_cat = QHBoxLayout(w_cat); l_cat.setContentsMargins(5,5,5,5); l_cat.addWidget(lbl_cat)
            self.table.setCellWidget(i, 5, w_cat)
            
            p_class = "badgePrioAlta" if t_dict['priority'] == 3 else ("badgePrioMedia" if t_dict['priority'] == 2 else "badgePrioBaixa")
            lbl_prio = QLabel(["BAIXA", "MÉDIA", "ALTA"][t_dict['priority']-1])
            lbl_prio.setProperty("class", f"badgeBase {p_class}")
            lbl_prio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            w_prio = QWidget(); l_prio = QHBoxLayout(w_prio); l_prio.setContentsMargins(5,5,5,5); l_prio.addWidget(lbl_prio)
            self.table.setCellWidget(i, 6, w_prio)
            status = "CONCLUÍDA" if t_dict['status'] == 'Concluida' else "PENDENTE"
            self.table.setItem(i, 7, QTableWidgetItem(status))
            
            self.table.setItem(i, 8, QTableWidgetItem(t_dict['data_vencimento'] or ""))
            self.table.setItem(i, 9, QTableWidgetItem(t_dict.get('observacao', '')))

            # --- Botões de Ação com Ícones ---
            w_act = QWidget(); l_act = QHBoxLayout(w_act)
            l_act.setContentsMargins(2,2,2,2); l_act.setSpacing(4)

            btn_done_act = QPushButton(QIcon(obter_caminho_recurso("icon_concluido.png")), "")
            btn_done_act.setObjectName("btnActionDone")
            btn_done_act.setProperty("class", "btnAction")
            concluida = t_dict['status'] == 'Concluida'
            btn_done_act.setToolTip("Reabrir pagamento" if concluida else "Marcar como concluído")
            btn_done_act.setCursor(QCursor(Qt.CursorShape.PointingHandCursor)); btn_done_act.setFixedSize(28, 28)
            btn_done_act.clicked.connect(lambda _, tid=t_dict['id'], done=concluida: self.alternar_conclusao(tid, done))

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
            self.table.setCellWidget(i, 10, w_act)

        self.table.resizeRowsToContents()
        self._atualizando_tabela = False

    def salvar_edicao_celula(self, item):
        if self._atualizando_tabela or item.column() not in (1, 2, 3, 4, 8, 9):
            return

        widget = self.table.cellWidget(item.row(), 0)
        checkbox = widget.findChild(QCheckBox) if widget else None
        if not checkbox:
            return

        tarefa = Tarefa.obter_por_id(checkbox.property("task_id"))
        if not tarefa:
            return

        dados = dict(tarefa)
        valor = item.text().strip()
        if item.column() == 1 and valor.endswith(" 🔄"):
            valor = valor[:-2].rstrip()

        campos = {
            1: "titulo",
            2: "prestador",
            3: "tipo_pagamento",
            4: "financiamento",
            8: "data_vencimento",
            9: "observacao",
        }
        dados[campos[item.column()]] = valor or None if item.column() == 8 else valor

        Tarefa.atualizar(
            dados['id'], dados['titulo'], dados['data_vencimento'],
            dados['priority'], dados['categoria_id'], dados['alert_interval'],
            dados.get('prestador', ''), dados.get('tipo_pagamento', ''),
            dados.get('financiamento', ''), dados['mes_referencia'],
            dados.get('observacao', '')
        )

    def valor_da_coluna(self, tarefa, coluna):
        tarefa = dict(tarefa)
        valores = {
            1: tarefa.get('titulo', ''),
            2: tarefa.get('prestador', ''),
            3: tarefa.get('tipo_pagamento', ''),
            4: tarefa.get('financiamento', ''),
            5: tarefa.get('categoria_nome', ''),
            6: ["BAIXA", "MÉDIA", "ALTA"][tarefa.get('priority', 1) - 1],
            7: "CONCLUÍDA" if tarefa.get('status') == 'Concluida' else "PENDENTE",
            8: tarefa.get('data_vencimento', '') or ''
        }
        return valores[coluna]

    def tarefa_corresponde_a_filtros(self, tarefa, ignorar_coluna=None):
        return all(
            coluna == ignorar_coluna or not valor or self.valor_da_coluna(tarefa, coluna) == valor
            for coluna, valor in self.filtros_colunas.items()
        )

    def atualizar_opcoes_filtros(self, tarefas):
        for coluna, combo in self.controles_filtro.items():
            valor_atual = self.filtros_colunas.get(coluna, '')
            opcoes = sorted({
                self.valor_da_coluna(tarefa, coluna)
                for tarefa in tarefas
                if self.tarefa_corresponde_a_filtros(tarefa, ignorar_coluna=coluna)
            })
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("Tudo", "")
            for opcao in opcoes:
                if opcao:
                    combo.addItem(opcao, opcao)
            indice = combo.findData(valor_atual)
            if indice >= 0:
                combo.setCurrentIndex(indice)
            else:
                self.filtros_colunas.pop(coluna, None)
            combo.blockSignals(False)

    def aplicar_filtro_coluna(self, coluna):
        valor = self.controles_filtro[coluna].currentData()
        if valor:
            self.filtros_colunas[coluna] = valor
        else:
            self.filtros_colunas.pop(coluna, None)
        self.refresh_all()

    def limpar_filtros(self):
        self.filtros_colunas.clear()
        self.refresh_all()

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

    def mudar_mes(self, data):
        self.mes_atual = data.toString("yyyy-MM")
        self.refresh_all()

    def copiar_mes_anterior(self):
        total = Tarefa.copiar_mes_anterior(self.mes_atual)
        QMessageBox.information(self, "Checklist mensal", f"{total} pagamento(s) copiado(s) para {self.mes_atual}.")
        self.refresh_all()

    def alternar_conclusao(self, tid, concluida):
        if concluida:
            Tarefa.reabrir(tid)
        else:
            Tarefa.concluir(tid)
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
        tarefas_selecionadas = []
        for r in range(self.table.rowCount()):
            widget = self.table.cellWidget(r, 0)
            if widget and (checkbox := widget.findChild(QCheckBox)) and checkbox.isChecked():
                tarefas_selecionadas.append((checkbox.property("task_id"), self.table.item(r, 7).text()))
        
        if tarefas_selecionadas:
            for tid, status in tarefas_selecionadas:
                if status == "CONCLUÍDA":
                    Tarefa.reabrir(tid)
                else:
                    Tarefa.concluir(tid)
            self.refresh_all()

    def selecionar_todos(self):
        checkboxes = []
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            checkbox = widget.findChild(QCheckBox) if widget else None
            if checkbox:
                checkboxes.append(checkbox)
        marcar = any(not checkbox.isChecked() for checkbox in checkboxes)
        for checkbox in checkboxes:
            checkbox.setChecked(marcar)

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
            edit = menu.addAction("Editar")
            tarefa = Tarefa.obter_por_id(tid)
            concluida = tarefa and tarefa['status'] == 'Concluida'
            done = menu.addAction("Reabrir como pendente" if concluida else "Concluir")
            act = menu.exec(self.table.mapToGlobal(pos))
            if act == edit: self.abrir_edicao_direta(tid)
            elif act == done: self.alternar_conclusao(tid, concluida)

    def verificar_alertas(self):
        agora = datetime.now()
        for t in Tarefa.listar_todas_pendentes():
            t_dict = dict(t)
            if not t_dict['data_vencimento']: continue
            try:
                venc = datetime.strptime(t_dict['data_vencimento'], "%Y-%m-%d %H:%M:%S")
            except (TypeError, ValueError):
                continue
            if agora >= venc:
                enviar = False
                if not t_dict['notificado']: enviar = True
                elif t_dict.get('alert_interval', 0) > 0 and t_dict.get('last_alerted_at'):
                    try:
                        ultimo_alerta = datetime.strptime(t_dict['last_alerted_at'], "%Y-%m-%d %H:%M:%S")
                    except (TypeError, ValueError):
                        ultimo_alerta = None
                    prox = ultimo_alerta + timedelta(minutes=t_dict['alert_interval']) if ultimo_alerta else agora
                    if agora >= prox: enviar = True
                if enviar:
                    self.tray.showMessage("🚨 ALERTA GCP", f"Demanda: {t_dict['titulo']}", QSystemTrayIcon.MessageIcon.Warning)
                    Tarefa.registrar_alerta_enviado(t_dict['id'], agora.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec())
