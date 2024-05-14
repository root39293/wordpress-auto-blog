from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from worker import Worker
from utils import generate_topics, generate_content, create_wordpress_post

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Auto Posting")
        self.resize(500, 800)
        self.setupUi()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.start_worker)

        self.show()

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
        self.numberLabel.setText("Number of Posts:")

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
            self.resultTextBox.appendPlainText(f"\n [Error] Please fill in all fields with valid values.")
            return

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

    def generate_topics(self):
        topic = self.topicLineEdit.text()
        api_key = self.apiKeyLineEdit.text()
        count = int(self.numberSpinBox.value())
        topics_list = generate_topics(topic, count, api_key)
        return topics_list

    @QtCore.pyqtSlot()
    def check_auto_posting(self):
        if self.autoPostCheckBox.isChecked():
            interval = self.autoPostIntervalSpinBox.value() * 60000
            self.timer.start(interval)
        else:
            self.timer.stop()

    def postToWordPress(self, topics_list):
        api_key = self.apiKeyLineEdit.text()
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        wp_url = self.wpUrlLineEdit.text()

        for topic in topics_list:
            self.resultTextBox.appendPlainText(f"\n[In Progress] Writing post for '{topic}'...")
            content = generate_content(topic, api_key)
            try:
                create_wordpress_post(topic, content, username, password, wp_url)
                self.handle_posting_result(f"[Completed] Post for '{topic}' published")
            except Exception as err:
                self.handle_posting_result(f"[Failed] Failed to publish post for '{topic}': {str(err)}")

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

    def show_topics_list(self, topics_list):
        topics_str = "\n".join(topics_list)
        self.resultTextBox.appendPlainText(topics_str)

    def show_usage(self):
        usage_text = "<h3><CENTER>How to Use</CENTER></h3><br>"
        usage_text += "<p>1. Enter the blog topic in the 'Topic' field. Use commas to separate multiple topics (e.g., topic1, topic2, topic3).</p><br>"
        usage_text += "<p>2. Enter the OpenAI API key in the 'API Key' field.</p><br>"
        usage_text += "<p>3. Enter your WordPress account information in the 'WordPress Username' and 'WordPress Password' fields.</p><br>"
        usage_text += "<p>4. Enter your WordPress site URL in the 'WordPress URL' field (do not include a trailing '/').</p><br>"
        usage_text += "<p>5. Select the number of posts to be published from the 'Number of Posts' spin box.</p><br>"
        usage_text += "<p>6. Check the 'Enable Auto Posting' checkbox and set the interval for automatic posting to enable auto posting.</p><br>"
        usage_text += "<p>7. Click the 'Run' button to start writing and publishing posts.</p><br>"
        usage_text += "<p><b>Note:</b> Ensure that you enter the correct OpenAI API key and WordPress account information before using the program.</p><br>"

        QMessageBox.information(self, "How to Use", usage_text)

    @QtCore.pyqtSlot(str, bool)
    def handle_results(self, result, status):
        if status:
            self.resultTextBox.appendPlainText(f"\n {result}")
        else:
            self.resultTextBox.appendPlainText(f"\n [Failed] Please check your API key and input values.")

        self.postButton.setEnabled(True)
        self.topicLineEdit.setEnabled(True)
        self.apiKeyLineEdit.setEnabled(True)
        self.usernameLineEdit.setEnabled(True)
        self.passwordLineEdit.setEnabled(True)
        self.wpUrlLineEdit.setEnabled(True)
        self.numberSpinBox.setEnabled(True)
