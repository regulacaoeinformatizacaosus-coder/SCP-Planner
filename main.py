import sys
import os
from PyQt6.QtWidgets import QApplication
from gui import MainWindow, APP_VERSION
import ctypes

def main():
    """Função principal que inicializa e executa a aplicação GCP PRO."""
    
    # Configuração técnica PRO para garantir nitidez em monitores High-DPI (como o seu LG)
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)

    # --- Correção para o ícone da barra de tarefas no Windows ---
    # Define um ID de modelo de usuário explícito para o processo.
    # Isso impede que o Windows agrupe a janela com outros processos Python,
    # garantindo que o ícone definido na janela seja exibido corretamente.
    myappid = f'mycompany.gcpplanner.{APP_VERSION}' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    # Fusion é o estilo base mais moderno do Qt, ideal para aplicar QSS customizado
    app.setStyle("Fusion") 
    
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()