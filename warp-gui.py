import sys
import subprocess
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QTextEdit, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt

class WarpGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warp Cloudflare - GUI")
        self.resize(500, 400)

        self.layout = QVBoxLayout()

        self.status_label = QLabel("Status do serviço: Desconhecido")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.ip_label = QLabel("IP atual: -")
        self.ip_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.ip_label)

        self.toggle_button = QPushButton("Carregando...")
        self.toggle_button.clicked.connect(self.toggle_warp)
        self.layout.addWidget(self.toggle_button)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.layout.addWidget(self.log_area)

        self.setLayout(self.layout)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_connection_status)
        self.update_timer.start(7000)  # Atualiza status da conexão a cada 7 segundos

        self.init_warp()

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_area.append(f"{timestamp} {message}")
        self.log_area.ensureCursorVisible()

    def run_command(self, cmd, require_sudo=False, input_text=None):
        try:
            if require_sudo:
                cmd = ['sudo'] + cmd
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate(input=input_text, timeout=20)
            return stdout.strip(), stderr.strip()
        except Exception as e:
            self.log(f"Erro ao executar comando: {e}")
            return "", str(e)

    def is_service_active(self):
        stdout, _ = self.run_command(['systemctl', 'is-active', 'warp-svc'])
        return stdout == "active"

    def start_service(self):
        self.log("Iniciando serviço warp-svc...")
        stdout, stderr = self.run_command(['systemctl', 'start', 'warp-svc'], require_sudo=True)
        if stderr:
            self.log(f"Erro ao iniciar serviço: {stderr}")
        else:
            self.log("Serviço warp-svc iniciado.")

    def check_registration(self):
        stdout, _ = self.run_command(['warp-cli', 'registration', 'show'])
        # Se tiver info no output, considera registrado
        return bool(stdout)

    def accept_terms(self):
        self.log("Registrando Warp (aceitando termos)...")
        stdout, stderr = self.run_command(['warp-cli', 'registration', 'new'], require_sudo=True, input_text='y\n')
        self.log(stdout)
        if "Success" in stdout:
            self.log("Registro concluído com sucesso.")
            return True
        elif "Old registration is still around" in stderr or "already registered" in stderr.lower():
            self.log("Warp já está registrado. Prosseguindo...")
            return True
        else:
            self.log(f"Falha no registro: {stderr}")
            return False

    def get_warp_status(self):
        stdout, _ = self.run_command(['warp-cli', 'status'])
        return "Connected" in stdout

    def get_current_ip(self):
        stdout, _ = self.run_command(['curl', '-s', 'https://ifconfig.me'])
        return stdout if stdout else "-"

    def update_connection_status(self):
        # Atualiza status de conexão e IP, sem tocar no registro
        connected = self.get_warp_status()
        ip = self.get_current_ip()
        self.ip_label.setText(f"IP atual: {ip}")
        if connected:
            self.toggle_button.setText("Desconectar Warp")
        else:
            self.toggle_button.setText("Conectar Warp")

    def init_warp(self):
        self.log("Aplicativo iniciado.")
        self.log("Verificando serviço warp-svc...")
        if not self.is_service_active():
            self.log("warp-svc está inativo. Tentando iniciar...")
            self.start_service()
            time.sleep(2)
            if not self.is_service_active():
                self.log("Não foi possível iniciar o serviço warp-svc.")
                self.toggle_button.setEnabled(False)
                return
        else:
            self.log("warp-svc está ativo.")

        if not self.check_registration():
            self.log("Warp não registrado ainda. Iniciando registro...")
            if not self.accept_terms():
                self.log("Registro falhou. Por favor, registre manualmente.")
                self.toggle_button.setEnabled(False)
                return
        else:
            self.log("Warp já registrado.")

        self.toggle_button.setEnabled(True)
        self.update_connection_status()

    def connect_warp(self):
        self.log("Tentando conectar Warp...")
        stdout, stderr = self.run_command(['warp-cli', 'connect'], require_sudo=True)
        self.log(stdout)
        if stderr:
            self.log(stderr)

        time.sleep(3)

        if self.get_warp_status():
            self.log("Warp conectado com sucesso.")
            return True
        else:
            self.log("Falha ao conectar Warp.")
            return False

    def disconnect_warp(self):
        self.log("Tentando desconectar Warp...")
        stdout, stderr = self.run_command(['warp-cli', 'disconnect'], require_sudo=True)
        self.log(stdout)
        if stderr:
            self.log(stderr)

        time.sleep(2)

        if not self.get_warp_status():
            self.log("Warp desconectado com sucesso.")
            return True
        else:
            self.log("Falha ao desconectar Warp.")
            return False

    def toggle_warp(self):
        self.toggle_button.setEnabled(False)
        connected = self.get_warp_status()

        if connected:
            success = self.disconnect_warp()
        else:
            success = self.connect_warp()

        if success:
            self.update_connection_status()
        else:
            QMessageBox.warning(self, "Erro", "Falha ao alterar estado do Warp. Veja os logs para mais detalhes.")

        self.toggle_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WarpGui()
    window.show()
    sys.exit(app.exec_())
