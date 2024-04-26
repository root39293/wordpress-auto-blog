import requests
from PyQt5 import QtCore, QtGui, QtWidgets
import openai
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from googletrans import Translator


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.setWindowTitle("로그인")

        layout = QtWidgets.QVBoxLayout()

        program_name_label = QtWidgets.QLabel("Auto Posting")
        layout.addWidget(program_name_label, alignment=QtCore.Qt.AlignCenter)

        login_form_layout = QtWidgets.QFormLayout()

        self.usernameLineEdit = QtWidgets.QLineEdit()
        self.passwordLineEdit = QtWidgets.QLineEdit()
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)

        login_form_layout.addRow("아이디:", self.usernameLineEdit)
        login_form_layout.addRow("비밀번호:", self.passwordLineEdit)

        layout.addLayout(login_form_layout)

        self.loginButton = QtWidgets.QPushButton("로그인")
        self.loginButton.clicked.connect(self.handle_login)
        layout.addWidget(self.loginButton, alignment=QtCore.Qt.AlignCenter)

        self.setLayout(layout)

    def get_username(self):
        return self.usernameLineEdit.text()

    def get_password(self):
        return self.passwordLineEdit.text()

    def handle_login(self):
        username = self.get_username()
        password = self.get_password()

        if username == "root" and password == "password@":
            self.accept()
            self.close()
        else:
            QtWidgets.QMessageBox.warning(
                self, "로그인 실패", "아이디 및 비밀번호가 올바르지 않습니다. 다시 시도해주세요."
            )
            self.passwordLineEdit.clear()


class Worker(QThread):
    taskFinished = pyqtSignal(str, bool)

    def __init__(self, mainWindow):
        QThread.__init__(self)
        self.mainWindow = mainWindow

    @QtCore.pyqtSlot()
    def run(self):
        try:
            topics_list = self.mainWindow.generate_topics()
            self.mainWindow.show_topics_list(topics_list)
            self.mainWindow.postToWordPress(topics_list)
            self.taskFinished.emit("[결과] 작업이 완료되었습니다.", True)
        except Exception as err:
            self.taskFinished.emit(str(err), False)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Auto Posting")
        self.resize(500, 800)
        self.setupUi()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.start_worker)

        login_dialog = LoginDialog()
        result = login_dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            if not self.authenticate(login_dialog):
                QMessageBox.warning(self, "로그인 실패", "로그인 인증에 실패하였습니다.")
                sys.exit()
            self.show()
        else:
            sys.exit()

    def setupUi(self):
        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(20)

        self.descLabel = QtWidgets.QLabel(self.centralwidget)
        self.descLabel.setText("<CENTER><h1>AutoPosting v0.2.0</CENTER></h1>")
        self.verticalLayout.addWidget(self.descLabel)

        self.resultTextBox = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.verticalLayout.addWidget(self.resultTextBox)

        formLayout = QtWidgets.QFormLayout()
        formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        formLayout.setFormAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        self.topicLineEdit = QtWidgets.QLineEdit()
        self.apiKeyLineEdit = QtWidgets.QLineEdit()
        self.apiKeyLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.usernameLineEdit = QtWidgets.QLineEdit()
        self.passwordLineEdit = QtWidgets.QLineEdit()
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.wpUrlLineEdit = QtWidgets.QLineEdit()

        formLayout.addRow("Topic:", self.topicLineEdit)
        formLayout.addRow("API Key:", self.apiKeyLineEdit)
        formLayout.addRow("WordPress Username:", self.usernameLineEdit)
        formLayout.addRow("WordPress Password:", self.passwordLineEdit)
        formLayout.addRow("WordPress URL:", self.wpUrlLineEdit)

        self.numberLabel = QtWidgets.QLabel(self.centralwidget)
        self.numberLabel.setText("Number of Posting:")

        self.numberSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.numberSpinBox.setRange(2, 10)
        self.numberSpinBox.setValue(2)

        formLayout.addRow(self.numberLabel, self.numberSpinBox)

        self.autoPostCheckBox = QtWidgets.QCheckBox(
            "Enable Auto Posting", self.centralwidget
        )
        self.autoPostIntervalSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.autoPostIntervalSpinBox.setRange(1, 60)
        self.autoPostIntervalSpinBox.setSuffix(" min")
        self.autoPostIntervalSpinBox.setValue(30)
        formLayout.addRow(self.autoPostCheckBox, self.autoPostIntervalSpinBox)

        self.verticalLayout.addLayout(formLayout)

        self.autoPostCheckBox.stateChanged.connect(self.check_auto_posting)
        self.autoPostIntervalSpinBox.valueChanged.connect(self.check_auto_posting)

        self.postButton = QtWidgets.QPushButton(self.centralwidget)
        self.postButton.setText("Run")
        self.verticalLayout.addWidget(self.postButton)

        self.usageButton = QtWidgets.QPushButton(self.centralwidget)
        self.usageButton.setText("How to Use")
        self.verticalLayout.addWidget(self.usageButton)

        self.setCentralWidget(self.centralwidget)

        self.postButton.clicked.connect(self.start_worker)
        self.usageButton.clicked.connect(self.show_usage)

    def start_worker(self):
        topic = self.topicLineEdit.text()
        api_key = self.apiKeyLineEdit.text()
        post_count = int(self.numberSpinBox.text())
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        wp_url = self.wpUrlLineEdit.text()
        if not all([topic, api_key, post_count, username, password, wp_url]):
            self.resultTextBox.appendPlainText(f"\n [오류] 모든 필드를 유효한 값으로 채워주세요.")
            return
        openai.api_key = api_key

        self.postButton.setEnabled(False)
        self.topicLineEdit.setEnabled(False)
        self.apiKeyLineEdit.setEnabled(False)
        self.usernameLineEdit.setEnabled(False)
        self.passwordLineEdit.setEnabled(False)
        self.wpUrlLineEdit.setEnabled(False)
        self.numberSpinBox.setEnabled(False)

        self.worker = Worker(self)
        self.worker.taskFinished.connect(self.handle_results)
        self.worker.start()

    def authenticate(self, login_dialog):
        username = login_dialog.get_username()
        password = login_dialog.get_password()

        if username == "root" and password == "password@":
            return True
        else:
            return False

    @QtCore.pyqtSlot()
    def check_auto_posting(self):
        if self.autoPostCheckBox.isChecked():
            interval = self.autoPostIntervalSpinBox.value() * 60000
            self.timer.start(interval)
        else:
            self.timer.stop()

    def postToWordPress(self, topics_list):
        post_count = int(self.numberSpinBox.value())
        api_key = self.apiKeyLineEdit.text()
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        wp_url = self.wpUrlLineEdit.text()

        openai.api_key = api_key

        for topic in topics_list:
            self.resultTextBox.appendPlainText(f"\n[진행 중] '{topic}'에 대한 글 작성 중...")
            content = self.generate_content(topic)
            try:
                self.create_wordpress_post(topic, content, username, password, wp_url)
                self.handle_posting_result(f"[완료] '{topic}'에 대한 글 게시됨")
            except Exception as err:
                self.handle_posting_result(f"[실패] '{topic}'에 대한 글 게시 [실패]: {str(err)}")

    def handle_posting_result(self, result):
        QtCore.QMetaObject.invokeMethod(
            self,
            "update_result_textbox",
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, result),
        )

    @QtCore.pyqtSlot(str)
    def update_result_textbox(self, result):
        self.resultTextBox.appendPlainText(result)

    def create_wordpress_post(self, topic, content, username, password, wp_url):
        translator = Translator()
        translated_topic = translator.translate(topic, dest="en").text
        image_url = f"https://source.unsplash.com/featured/?{translated_topic}"

        wordpress_url = wp_url + "/wp-json/wp/v2/posts"

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "title": topic,
            "content": f'<img src="{image_url}">\n\n{content}',
            "status": "publish",
        }

        response = requests.post(
            wordpress_url, headers=headers, json=data, auth=(username, password)
        )
        response.raise_for_status()

    def generate_content(self, topic):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 이제부터 파워블로거 입니다. 사용자가 요구하는 주제에 관련된 블로그 포스팅을 작성하는 것이 당신의 역할입니다. 블로그 포스팅의 본문 내용만을 작성해야 합니다. 본문 내용 외 다른 목차는 작성하지 않습니다. 분량은 최대한 길고 자세하게 작성하세요."
                },
                {
                    "role": "user",
                    "content": f"주제는 {topic}입니다. {topic}에 대한 블로그 글을 작성해주세요."
                }
            ]
        )
        return completion.choices[0].message.content

    def generate_topics(self):
        topics = self.topicLineEdit.text().split(",")
        count = int(self.numberSpinBox.value())
        entire_topic_list = []

        for topic in topics:
            topic = topic.strip()
            if topic:
                try:
                    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": f"당신은 이제부터 블로그 주제를 생성하는 역할을 맡습니다. 사용자가 제시하는 큰 주제에 대해 블로그 포스팅 주제를 정하고 핵심 포스팅 제목만 출력합니다. 제목은 짧고 핵심적인 내용만 담습니다. 각 주제는 개행으로 구별해야 합니다. 출력값은 {count}줄로 출력합니다."
                            },
                            {
                                "role": "user",
                                "content": f"{topic}에 대한 {count}개의 블로그 주제를 생성해주세요."
                            }
                        ]
                    )
                    topics_str = completion.choices[0].message.content
                    topics_list = [
                        topic.replace('"', "").strip()
                        for topic in topics_str.split("\n")
                        if topic.strip()
                    ]

                    for topic in topics_list:
                        topic_parts = topic.split(". ")
                        if len(topic_parts) > 1:
                            topic_without_number = topic_parts[1]
                        else:
                            topic_without_number = topic_parts[0]

                        topic_without_extra_symbols = topic_without_number.split("-")[
                            0].split(":")[0]
                        entire_topic_list.append(topic_without_extra_symbols)
                except Exception as e:
                    return e
        return entire_topic_list

    def show_topics_list(self, topics_list):
        topics_str = "\n".join(topics_list)
        self.resultTextBox.appendPlainText(topics_str)

    def show_usage(self):
            usage_text = "<h3><CENTER>How to Use</CENTER></h3><br>"
            usage_text += "<p>1. 'Topic' 필드에 블로그 주제를 입력합니다. 여러 주제를 입력하려면 쉼표로 구분합니다. (ex. 주제1, 주제2, 주제3)</p><br>"
            usage_text += "<p>2. 'API Key' 필드에 OpenAI API 키를 입력합니다.</p><br>"
            usage_text += "<p>3. 'WordPress Username'과 'WordPress Password' 필드에 WordPress 계정 정보를 입력합니다.</p><br>"
            usage_text += "<p>4. 'WordPress URL' 필드에 WordPress 사이트 URL을 입력합니다. (URL의 마지막에 '/'는 포함하지 않습니다)</p><br>"
            usage_text += "<p>5. 'Number of Posting' 스핀 박스에서 게시할 포스팅 개수를 선택합니다.</p><br>"
            usage_text += "<p>6. 'Enable Auto Posting' 체크박스를 선택하고 자동 게시 간격을 설정하면 일정 시간마다 포스팅이 자동으로 게시됩니다.</p><br>"
            usage_text += "<p>7. 'Run' 버튼을 클릭하여 포스팅 작성 및 게시를 시작합니다.</p><br>"
            usage_text += "<p><b>※ 주의사항:</b> 프로그램을 사용하기 전에 OpenAI API 키와 WordPress 계정 정보를 정확히 입력해야 합니다.</p><br>"

            QMessageBox.information(self, "How to Use", usage_text)

    @QtCore.pyqtSlot(str, bool)
    def handle_results(self, result, status):
        if status:
            self.resultTextBox.appendPlainText(f"\n {result}")
        else:
            self.resultTextBox.appendPlainText(f"\n [실패] 유효한 API 키 및 입력 값들을 확인하세요.")

        self.postButton.setEnabled(True)
        self.topicLineEdit.setEnabled(True)
        self.apiKeyLineEdit.setEnabled(True)
        self.usernameLineEdit.setEnabled(True)
        self.passwordLineEdit.setEnabled(True)
        self.wpUrlLineEdit.setEnabled(True)
        self.numberSpinBox.setEnabled(True)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    mainWindow = MainWindow()

    app.exec_()