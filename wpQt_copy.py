import requests
from PyQt5 import QtCore, QtGui, QtWidgets
import openai
from PyQt5.QtCore import QThread, pyqtSignal


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
            self.taskFinished.emit("성공적으로 글이 게시되었습니다!", True)
        except Exception as err:
            self.taskFinished.emit(str(err), False)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Auto Posting")
        self.resize(600, 800)
        self.setupUi()

    def setupUi(self):
        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(20)

        self.descLabel = QtWidgets.QLabel(self.centralwidget)
        self.descLabel.setText("<h1><strong><CENTER>AutoPosting v0.1.0</CENTER></strong></h1>")
        self.descLabel.setWordWrap(True)
        self.verticalLayout.addWidget(self.descLabel)

        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)  # Set initial maximum value to 0
        self.progressBar.setValue(0)
        self.verticalLayout.addWidget(self.progressBar)

        self.resultTextBox = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.verticalLayout.addWidget(self.resultTextBox)

        formLayout = QtWidgets.QFormLayout()
        formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        formLayout.setFormAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        self.topicLabel = QtWidgets.QLabel(self.centralwidget)
        self.topicLabel.setText("Topic: ")
        self.topicLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        formLayout.addRow(self.topicLabel, self.topicLineEdit)

        self.apiKeyLabel = QtWidgets.QLabel(self.centralwidget)
        self.apiKeyLabel.setText("API Key:")
        self.apiKeyLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.apiKeyLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        formLayout.addRow(self.apiKeyLabel, self.apiKeyLineEdit)

        self.usernameLabel = QtWidgets.QLabel(self.centralwidget)
        self.usernameLabel.setText("WordPress Username:")
        self.usernameLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        formLayout.addRow(self.usernameLabel, self.usernameLineEdit)

        self.passwordLabel = QtWidgets.QLabel(self.centralwidget)
        self.passwordLabel.setText("WordPress Password:")
        self.passwordLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        formLayout.addRow(self.passwordLabel, self.passwordLineEdit)

        self.wpUrlLabel = QtWidgets.QLabel(self.centralwidget)
        self.wpUrlLabel.setText("WordPress URL:")
        self.wpUrlLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        formLayout.addRow(self.wpUrlLabel, self.wpUrlLineEdit)

        self.numberLabel = QtWidgets.QLabel(self.centralwidget)
        self.numberLabel.setText("Number of Posting:")
        self.numberComboBox = QtWidgets.QComboBox(self.centralwidget)
        for i in range(1, 11):
            self.numberComboBox.addItem(str(i))
        formLayout.addRow(self.numberLabel, self.numberComboBox)

        self.verticalLayout.addLayout(formLayout)

        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacer)

        self.postButton = QtWidgets.QPushButton(self.centralwidget)
        self.postButton.setText("Run")
        self.verticalLayout.addWidget(self.postButton)

        self.setCentralWidget(self.centralwidget)

        self.postButton.clicked.connect(self.start_worker)

        self.setStyleSheet("""
            QLabel {
                font-size: 20px;
            }
            QLineEdit {
                background-color: #f2f2f2;
                font-size: 16px;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                font-size: 20px;
                color: white;
                background-color: #4287f5;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPlainTextEdit {
                background-color: #f2f2f2;
                font-size: 16px;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QProgressBar {
                background-color: #f2f2f2;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 1px;
                text-align: center;
            }
        """)

    def postToWordPress(self, topics_list):
        post_count = int(self.numberComboBox.currentText())
        api_key = self.apiKeyLineEdit.text()
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        wp_url = self.wpUrlLineEdit.text()

        if not all([api_key, username, password, wp_url]):
            raise Exception("모든 필드를 채워주세요.")

        openai.api_key = api_key

        progress_step = 100 // post_count

        for i, topic in enumerate(topics_list, start=1):
            content = self.generate_content(topic)
            self.create_wordpress_post(topic, content, username, password, wp_url, i)
            self.progressBar.setValue(i * progress_step)

    def create_wordpress_post(self, topic, content, username, password, wp_url, post_number):
        wordpress_url = wp_url + '/wp-json/wp/v2/posts'

        headers = {
            'Content-Type': 'application/json',
        }

        data = {
            'title': topic,
            'content': content,
            'status': 'publish',
        }

        response = requests.post(wordpress_url, headers=headers, json=data, auth=(username, password))
        response.raise_for_status()

    def generate_content(self, topic):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "당신은 이제부터 파워블로거 입니다. 사용자가 요구하는 주제에 관련된 블로그 포스팅을 작성하는것이 당신의 역할입니다. 블로그 포스팅의 본문내용만을 작성해야합니다. 본문 내용 외 다른 목차는 작성하지 않습니다. 분량은 최대한 길고 자세하게 작성하세요."},
                {"role": "user", "content": f"주제는  {topic} 입니다.  {topic} + 에 대한 블로그 글을 작성해주세요. "}
            ]
        )
        return completion.choices[0].message['content']

    def generate_topics(self):
        topic = self.topicLineEdit.text()
        count = int(self.numberComboBox.currentText())

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": f"당신은 이제부터 블로그 주제를 생성하는 역할을 맡습니다. 사용자가 제시하는 대주제에 대해 블로그 포스팅 주제를 정하고 핵심 포스팅 제목만 출력합니다. 각 주제는 개행으로 구별되며, {count}개의 포스팅 주제를 출력하세요."},
                {"role": "user", "content": f"{topic}에 대한 {count}개의 블로그 주제를 생성해주세요."}
            ]
        )
        topics_str = completion.choices[0].message['content']
        topics_list = [topic.replace('\"', '').strip() for topic in topics_str.split('\n') if topic.strip()]
        topics_str_without_number = '\n'.join([topic.split('. ')[1] for topic in topics_list])
        topics_list_without_number = [topic for topic in topics_str_without_number.split('\n') if topic.strip()]
        return topics_list_without_number

    def show_topics_list(self, topics_list):
        topics_str = '\n'.join(topics_list)
        self.resultTextBox.setPlainText(topics_str)

    def start_worker(self):
        topic = self.topicLineEdit.text()
        api_key = self.apiKeyLineEdit.text()
        if not all([topic, api_key]):
            self.resultTextBox.setPlainText("실패: 모든 필드를 채워주세요.")
            return
        openai.api_key = api_key

        self.postButton.setEnabled(False)
        self.topicLineEdit.setEnabled(False)
        self.apiKeyLineEdit.setEnabled(False)
        self.usernameLineEdit.setEnabled(False)
        self.passwordLineEdit.setEnabled(False)
        self.wpUrlLineEdit.setEnabled(False)
        self.numberComboBox.setEnabled(False)

        self.progressBar.setMaximum(0)  # Set maximum to 0 initially
        self.loading_screen = LoadingScreen()  # Create an instance of LoadingScreen
        self.loading_screen.show()

        self.worker = Worker(self)  # Pass self (MainWindow instance) as an argument
        self.worker.taskFinished.connect(self.handle_results)
        self.worker.finished.connect(self.loading_screen.close)  # Close the loading screen when the worker finishes
        self.worker.start()


    @QtCore.pyqtSlot(str, bool)
    def handle_results(self, result, status):
        if status:
            self.resultTextBox.setPlainText(result)
        else:
            self.resultTextBox.setPlainText("실패: " + result)

        self.postButton.setEnabled(True)
        self.topicLineEdit.setEnabled(True)
        self.apiKeyLineEdit.setEnabled(True)
        self.usernameLineEdit.setEnabled(True)
        self.passwordLineEdit.setEnabled(True)
        self.wpUrlLineEdit.setEnabled(True)
        self.numberComboBox.setEnabled(True)


class LoadingScreen(QtWidgets.QWidget):
    def __init__(self):
        super(LoadingScreen, self).__init__()
        self.setWindowTitle("Loading")
        self.setFixedSize(200, 100)
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setFixedSize(150, 20)
        self.progressBar.setRange(0, 0)  # Set the progress bar to animate
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.progressBar)
        self.setLayout(layout)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
