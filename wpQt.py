import requests
from PyQt5 import QtCore, QtGui, QtWidgets
import openai

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Auto Posting")
        self.resize(600, 800)  # 화면 크기 설정
        self.setupUi()

    def setupUi(self):
        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)

        self.verticalLayout.setSpacing(20)  # Set spacing between layout elements

        # 설명 레이블 추가
        self.descLabel = QtWidgets.QLabel(self.centralwidget)
        self.descLabel.setText(
            "<h1><strong><CENTER>AutoPosting v0.1.0</CENTER></strong></h1>"
        )
        self.descLabel.setWordWrap(True)
        self.verticalLayout.addWidget(self.descLabel)

        # Create a QFormLayout for the line edits and labels
        formLayout = QtWidgets.QFormLayout()
        formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        formLayout.setFormAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        # 주제 입력 칸
        self.topicLabel = QtWidgets.QLabel(self.centralwidget)
        self.topicLabel.setText("Topic: ")
        self.topicLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        formLayout.addRow(self.topicLabel, self.topicLineEdit)

        # API 키 입력 칸
        self.apiKeyLabel = QtWidgets.QLabel(self.centralwidget)
        self.apiKeyLabel.setText("API Key:")
        self.apiKeyLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.apiKeyLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        formLayout.addRow(self.apiKeyLabel, self.apiKeyLineEdit)

        # WordPress 계정 입력 칸
        self.usernameLabel = QtWidgets.QLabel(self.centralwidget)
        self.usernameLabel.setText("WordPress Username:")
        self.usernameLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        formLayout.addRow(self.usernameLabel, self.usernameLineEdit)

        self.passwordLabel = QtWidgets.QLabel(self.centralwidget)
        self.passwordLabel.setText("WordPress Password:")
        self.passwordLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        formLayout.addRow(self.passwordLabel, self.passwordLineEdit)

        # WordPress URL 입력 칸
        self.wpUrlLabel = QtWidgets.QLabel(self.centralwidget)
        self.wpUrlLabel.setText("WordPress URL:")
        self.wpUrlLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        formLayout.addRow(self.wpUrlLabel, self.wpUrlLineEdit)

        # 포스팅 개수 콤보 박스
        self.numberLabel = QtWidgets.QLabel(self.centralwidget)
        self.numberLabel.setText("Number of Posting:")
        self.numberComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.numberComboBox.addItem("1")
        self.numberComboBox.addItem("2")
        self.numberComboBox.addItem("3")
        self.numberComboBox.addItem("4")
        self.numberComboBox.addItem("5")
        self.numberComboBox.addItem("6")
        self.numberComboBox.addItem("7")
        self.numberComboBox.addItem("8")
        self.numberComboBox.addItem("9")
        self.numberComboBox.addItem("10")
        formLayout.addRow(self.numberLabel, self.numberComboBox)

        # 위젯 간에 공간 추가
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacer)

        self.verticalLayout.addLayout(formLayout)

        # 블로그 포스팅 버튼
        self.postButton = QtWidgets.QPushButton(self.centralwidget)
        self.postButton.setText("Run")
        self.verticalLayout.addWidget(self.postButton)

        # 텍스트 박스
        self.resultTextBox = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.verticalLayout.addWidget(self.resultTextBox)

        self.setCentralWidget(self.centralwidget)

        # 버튼 클릭 시 이벤트 연결
        self.postButton.clicked.connect(self.postToWordPress)
        # 각 위젯에 스타일 적용
        self.setStyleSheet("""
            QLabel {
                font-size: 15px;
            }
            QLineEdit {
                background-color: lightgray;
                font-size: 15px;
            }
            QPushButton {
                font-size: 20px;
                color: white;
                background-color: blue;
            }
            QPlainTextEdit {
                background-color: lightgray;
                font-size: 15px;
            }
        """)


    def postToWordPress(self):
        # 입력된 값 가져오기
        topic = self.topicLineEdit.text()
        post_count = int(self.numberComboBox.currentText())
        api_key = self.apiKeyLineEdit.text()
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        wp_url = self.wpUrlLineEdit.text()

        # 입력값 체크
        if not all([topic, api_key, username, password, wp_url]):
            self.show_error_message("에러 발생", "모든 필드를 채워주세요.")
            return

        try:
            # OpenAI API 키 설정
            openai.api_key = api_key

            # 주제 생성
            topics_str = self.generate_topics(topic, post_count)
            topics_list = [topic.strip('\"') for topic in topics_str.split('\n')]
            topics_str_without_number = '\n'.join([topic.split('. ')[1] for topic in topics_list])
            topics_list_without_number = [topic for topic in topics_str_without_number.split('\n') if topic.strip()]

            # 결과 표시
            self.resultTextBox.setPlainText(topics_str_without_number)

            # 포스팅 버튼 비활성화
            self.postButton.setEnabled(False)

            for i, topic in enumerate(topics_list_without_number, start=1):
                content = self.generate_content(topic)
                self.create_wordpress_post(topic, content, username, password, wp_url, i)

            self.show_success_message("성공", "블로그 포스팅이 성공적으로 작성되었습니다.")
        except Exception as err:
            self.show_error_message("에러 발생", str(err))

        # 포스팅 버튼 다시 활성화
        self.postButton.setEnabled(True)

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
        response.raise_for_status()  # 응답 상태코드 확인

    def generate_content(self, topic):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 이제부터 파워블로거 입니다. 사용자가 요구하는 주제에 관련된 블로그 포스팅을 작성하는것이 당신의 역할입니다. 블로그 포스팅의 본문내용만을 작성해야합니다. 본문 내용 외 다른 목차는 작성하지 않습니다. 분량은 최대한 길고 자세하게 작성하세요."},
                {"role": "user", "content": f"주제는  {topic} 입니다.  {topic} + 에 대한 블로그 글을 작성해주세요. "}
            ]
        )
        return completion.choices[0].message['content']
    
    def generate_topics(self, topic, count):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"당신은 이제부터 블로그 주제를 생성하는 역할을 맡습니다. 사용자가 제시하는 대주제에 대해 블로그 포스팅 주제를 정하고 핵심 포스팅 제목만 출력합니다. 각 주제는 개행으로 구별되며, {count}개의 포스팅 목록을 반환해야합니다. 다른 부연설명은 필요하지않고 오로지 목록만 출력합니다."},
                {"role": "user", "content": f"사용자가 제시한 대주제는 {topic} 입니다. 블로그 주제를 생성하고 목록만 출력하세요."}
            ]
        )
        return completion.choices[0].message['content']

    def show_error_message(self, title, message):
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        error_dialog.exec_()

    def show_success_message(self, title, message):
        success_dialog = QtWidgets.QMessageBox()
        success_dialog.setIcon(QtWidgets.QMessageBox.Information)
        success_dialog.setWindowTitle(title)
        success_dialog.setText(message)
        success_dialog.exec_()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
