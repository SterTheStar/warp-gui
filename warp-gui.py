import sys
import subprocess
import time
import json
import locale
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QTextEdit, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import QTimer, Qt

LANGUAGES = {
    "pt": {
        "title": "Warp Cloudflare - GUI",
        "status": "Status do serviço: {}",
        "ip": "IP atual: {}",
        "unknown": "Desconhecido",
        "starting_service": "Iniciando serviço warp-svc...",
        "service_started": "Serviço warp-svc iniciado.",
        "cannot_start": "Não foi possível iniciar o serviço warp-svc.",
        "already_registered": "Warp já registrado.",
        "not_registered": "Warp não registrado ainda. Iniciando registro...",
        "registering": "Registrando Warp (aceitando termos)...",
        "register_success": "Registro concluído com sucesso.",
        "register_failed": "Registro falhou. Por favor, registre manualmente.",
        "connect": "Conectar Warp",
        "disconnect": "Desconectar Warp",
        "connecting": "Tentando conectar Warp...",
        "disconnecting": "Tentando desconectar Warp...",
        "connected": "Warp conectado com sucesso.",
        "disconnected": "Warp desconectado com sucesso.",
        "connect_fail": "Falha ao conectar Warp.",
        "disconnect_fail": "Falha ao desconectar Warp.",
        "toggle_error": "Falha ao alterar estado do Warp. Veja os logs para mais detalhes.",
        "app_started": "Aplicativo iniciado.",
        "checking_service": "Verificando serviço warp-svc...",
        "inactive": "warp-svc está inativo. Tentando iniciar...",
        "active": "warp-svc está ativo.",
        "loading": "Carregando..."
    },
    "en": {
        "title": "Warp Cloudflare - GUI",
        "status": "Service status: {}",
        "ip": "Current IP: {}",
        "unknown": "Unknown",
        "starting_service": "Starting warp-svc service...",
        "service_started": "warp-svc service started.",
        "cannot_start": "Unable to start warp-svc service.",
        "already_registered": "Warp already registered.",
        "not_registered": "Warp not registered. Starting registration...",
        "registering": "Registering Warp (accepting terms)...",
        "register_success": "Registration successful.",
        "register_failed": "Registration failed. Please register manually.",
        "connect": "Connect Warp",
        "disconnect": "Disconnect Warp",
        "connecting": "Trying to connect Warp...",
        "disconnecting": "Trying to disconnect Warp...",
        "connected": "Warp connected successfully.",
        "disconnected": "Warp disconnected successfully.",
        "connect_fail": "Failed to connect Warp.",
        "disconnect_fail": "Failed to disconnect Warp.",
        "toggle_error": "Failed to change Warp state. Check logs for details.",
        "app_started": "Application started.",
        "checking_service": "Checking warp-svc service...",
        "inactive": "warp-svc is inactive. Trying to start...",
        "active": "warp-svc is active.",
        "loading": "Loading..."
    }
}

SETTINGS_FILE = "settings.json"


class WarpGui(QWidget):
    def __init__(self):
        super().__init__()

        self.lang_code = self.load_language()
        self.translations = LANGUAGES[self.lang_code]

        self.setWindowTitle(self.translations["title"])
        self.resize(500, 400)

        # Layout principal
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Seletor de idioma
        lang_selector = QHBoxLayout()
        self.br_button = QPushButton("BR")
        self.en_button = QPushButton("EN")
        self.br_button.setFixedWidth(40)
        self.en_button.setFixedWidth(40)
        self.br_button.clicked.connect(lambda: self.change_language("pt"))
        self.en_button.clicked.connect(lambda: self.change_language("en"))
        lang_selector.addWidget(self.br_button)
        lang_selector.addWidget(self.en_button)
        lang_selector.addStretch()
        self.layout.addLayout(lang_selector)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.ip_label = QLabel()
        self.ip_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.ip_label)

        self.toggle_button = QPushButton()
        self.toggle_button.clicked.connect(self.toggle_warp)
        self.layout.addWidget(self.toggle_button)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.layout.addWidget(self.log_area)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_connection_status)
        self.update_timer.start(7000)

        self.init_warp()

    def translate_ui(self):
        self.setWindowTitle(self.translations["title"])
        self.update_connection_status()

    def save_language(self, lang):
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"lang": lang}, f)

    def load_language(self):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f).get("lang", self.system_language())
        except:
            return self.system_language()

    def system_language(self):
        lang = locale.getdefaultlocale()[0]
        return "pt" if lang and lang.startswith("pt") else "en"

    def change_language(self, lang):
        self.lang_code = lang
        self.translations = LANGUAGES[lang]
        self.save_language(lang)
        self.translate_ui()

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
        self.log(self.translations["starting_service"])
        stdout, stderr = self.run_command(['systemctl', 'start', 'warp-svc'], require_sudo=True)
        if stderr:
            self.log(stderr)
        else:
            self.log(self.translations["service_started"])

    def check_registration(self):
        stdout, _ = self.run_command(['warp-cli', 'registration', 'show'])
        return bool(stdout)

    def accept_terms(self):
        self.log(self.translations["registering"])
        stdout, stderr = self.run_command(['warp-cli', 'registration', 'new'], require_sudo=True, input_text='y\n')
        self.log(stdout)
        if "Success" in stdout:
            self.log(self.translations["register_success"])
            return True
        elif "Old registration is still around" in stderr or "already registered" in stderr.lower():
            self.log(self.translations["already_registered"])
            return True
        else:
            self.log(f"{self.translations['register_failed']}: {stderr}")
            return False

    def get_warp_status(self):
        stdout, _ = self.run_command(['warp-cli', 'status'])
        return "Connected" in stdout

    def get_current_ip(self):
        stdout, _ = self.run_command(['curl', '-s', 'https://ifconfig.me'])
        return stdout if stdout else "-"

    def update_connection_status(self):
        connected = self.get_warp_status()
        ip = self.get_current_ip()
        self.ip_label.setText(self.translations["ip"].format(ip))
        self.status_label.setText(self.translations["status"].format(
            "Conectado" if connected else "Desconectado"
        ))
        self.toggle_button.setText(self.translations["disconnect"] if connected else self.translations["connect"])

    def init_warp(self):
        self.log(self.translations["app_started"])
        self.log(self.translations["checking_service"])
        if not self.is_service_active():
            self.log(self.translations["inactive"])
            self.start_service()
            time.sleep(2)
            if not self.is_service_active():
                self.log(self.translations["cannot_start"])
                self.toggle_button.setEnabled(False)
                return
        else:
            self.log(self.translations["active"])

        if not self.check_registration():
            self.log(self.translations["not_registered"])
            if not self.accept_terms():
                self.toggle_button.setEnabled(False)
                return
        else:
            self.log(self.translations["already_registered"])

        self.toggle_button.setEnabled(True)
        self.update_connection_status()

    def connect_warp(self):
        self.log(self.translations["connecting"])
        stdout, stderr = self.run_command(['warp-cli', 'connect'], require_sudo=True)
        self.log(stdout)
        if stderr:
            self.log(stderr)
        time.sleep(3)
        if self.get_warp_status():
            self.log(self.translations["connected"])
            return True
        else:
            self.log(self.translations["connect_fail"])
            return False

    def disconnect_warp(self):
        self.log(self.translations["disconnecting"])
        stdout, stderr = self.run_command(['warp-cli', 'disconnect'], require_sudo=True)
        self.log(stdout)
        if stderr:
            self.log(stderr)
        time.sleep(2)
        if not self.get_warp_status():
            self.log(self.translations["disconnected"])
            return True
        else:
            self.log(self.translations["disconnect_fail"])
            return False

    def toggle_warp(self):
        self.toggle_button.setEnabled(False)
        connected = self.get_warp_status()
        success = self.disconnect_warp() if connected else self.connect_warp()
        if success:
            self.update_connection_status()
        else:
            QMessageBox.warning(self, "Erro", self.translations["toggle_error"])
        self.toggle_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WarpGui()
    window.show()
    sys.exit(app.exec_())
