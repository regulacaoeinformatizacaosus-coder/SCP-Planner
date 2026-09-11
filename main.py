import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui import MainWindow, APP_VERSION
import ctypes

def main():
    """Função principal que inicializa e executa a aplicação GCP PRO."""
    app = None
    try:
        # Configuração técnica PRO para garantir nitidez em monitores High-DPI.
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
        os.environ["QT_SCALE_FACTOR"] = "1"

        app = QApplication(sys.argv)

        # Define um ID explícito para o processo no Windows.
        myappid = f'mycompany.gcpplanner.{APP_VERSION}'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        app.setStyle("Fusion")
        window = MainWindow()
        window.showMaximized()
        sys.exit(app.exec())
    except Exception:
        erro = traceback.format_exc()
        caminho_log = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "gcpplanner_error.log")
        try:
            with open(caminho_log, "w", encoding="utf-8") as arquivo:
                arquivo.write(erro)
        except OSError:
            pass

        if app is not None:
            QMessageBox.critical(None, "Erro ao iniciar o GCPlanner", f"O programa não conseguiu iniciar.\n\nDetalhes salvos em:\n{caminho_log}")
        else:
            print(erro, file=sys.stderr)
        raise

if __name__ == "__main__":
    main()