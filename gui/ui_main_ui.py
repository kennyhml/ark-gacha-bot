# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QSpinBox, QTabWidget, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(652, 473)
        Form.setMinimumSize(QSize(652, 473))
        Form.setMaximumSize(QSize(652, 473))
        Form.setStyleSheet(u"")
        self.MainUi = QWidget(Form)
        self.MainUi.setObjectName(u"MainUi")
        font = QFont()
        font.setPointSize(13)
        self.MainUi.setFont(font)
        self.LeftBackground = QLabel(self.MainUi)
        self.LeftBackground.setObjectName(u"LeftBackground")
        self.LeftBackground.setEnabled(True)
        self.LeftBackground.setGeometry(QRect(0, 0, 261, 621))
        self.LeftBackground.setStyleSheet(u"border-image: url(assets/gui/lbackground.png);\n"
"")
        self.LeftBackground.setPixmap(QPixmap(u"assets/gui/settings.png"))
        self.LeftBackground.setScaledContents(True)
        self.label_8 = QLabel(self.MainUi)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(0, 10, 261, 41))
        self.label_8.setStyleSheet(u"image: url(assets/gui/settings.png);")
        self.label_8.setPixmap(QPixmap(u"assets/gui/settings.png"))
        self.label_8.setScaledContents(False)
        self.label_8.setAlignment(Qt.AlignCenter)
        self.label_4 = QLabel(self.MainUi)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(0, 10, 261, 41))
        self.label_4.setStyleSheet(u"background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(150, 123, 111, 219), stop:1 rgba(85, 81, 84, 226));")
        self.ytrap_stations = QPushButton(self.MainUi)
        self.ytrap_stations.setObjectName(u"ytrap_stations")
        self.ytrap_stations.setGeometry(QRect(-20, 120, 271, 41))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI Variable Display"])
        font1.setPointSize(14)
        font1.setBold(False)
        font1.setItalic(False)
        font1.setUnderline(False)
        font1.setStrikeOut(False)
        font1.setKerning(True)
        self.ytrap_stations.setFont(font1)
        self.ytrap_stations.setStyleSheet(u"\n"
"QPushButton{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(11, 131, 120, 219), stop:1 rgba(85, 98, 112, 226));\n"
"	color:rgba(255, 255, 255, 210);\n"
"	border-bottom-right-radius: 20px;\n"
"	border-top-left-radius: 20px;\n"
"\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(150, 123, 111, 219), stop:1 rgba(85, 81, 84, 226));\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"	background-color:rgba(150, 123, 111, 255);\n"
"}\n"
"\n"
"Line#line{\n"
"	color: white;\n"
"}")
        icon = QIcon()
        icon.addFile(u"assets/gui/ytrap.png", QSize(), QIcon.Normal, QIcon.Off)
        self.ytrap_stations.setIcon(icon)
        self.ytrap_stations.setIconSize(QSize(40, 40))
        self.grinding = QPushButton(self.MainUi)
        self.grinding.setObjectName(u"grinding")
        self.grinding.setGeometry(QRect(-20, 240, 271, 41))
        self.grinding.setFont(font1)
        self.grinding.setStyleSheet(u"\n"
"QPushButton{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(11, 131, 120, 219), stop:1 rgba(85, 98, 112, 226));\n"
"	color:rgba(255, 255, 255, 210);\n"
"	border-bottom-right-radius: 20px;\n"
"	border-top-left-radius: 20px;\n"
"\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(150, 123, 111, 219), stop:1 rgba(85, 81, 84, 226));\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"	background-color:rgba(150, 123, 111, 255);\n"
"}\n"
"\n"
"Line#line{\n"
"	color: white;\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u"assets/gui/grinder.png", QSize(), QIcon.Normal, QIcon.Off)
        self.grinding.setIcon(icon1)
        self.grinding.setIconSize(QSize(40, 40))
        self.bullets_station = QPushButton(self.MainUi)
        self.bullets_station.setObjectName(u"bullets_station")
        self.bullets_station.setGeometry(QRect(-20, 300, 271, 41))
        self.bullets_station.setFont(font1)
        self.bullets_station.setStyleSheet(u"\n"
"QPushButton{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(11, 131, 120, 219), stop:1 rgba(85, 98, 112, 226));\n"
"	color:rgba(255, 255, 255, 210);\n"
"	border-bottom-right-radius: 20px;\n"
"	border-top-left-radius: 20px;\n"
"\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(150, 123, 111, 219), stop:1 rgba(85, 81, 84, 226));\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"	background-color:rgba(150, 123, 111, 255);\n"
"}\n"
"\n"
"Line#line{\n"
"	color: white;\n"
"}")
        icon2 = QIcon()
        icon2.addFile(u"assets/gui/arb.png", QSize(), QIcon.Normal, QIcon.Off)
        self.bullets_station.setIcon(icon2)
        self.bullets_station.setIconSize(QSize(40, 40))
        self.discord_settings = QPushButton(self.MainUi)
        self.discord_settings.setObjectName(u"discord_settings")
        self.discord_settings.setGeometry(QRect(-20, 420, 271, 41))
        self.discord_settings.setFont(font1)
        self.discord_settings.setStyleSheet(u"\n"
"QPushButton{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(11, 131, 120, 219), stop:1 rgba(85, 98, 112, 226));\n"
"	color:rgba(255, 255, 255, 210);\n"
"	border-bottom-right-radius: 20px;\n"
"	border-top-left-radius: 20px;\n"
"\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(150, 123, 111, 219), stop:1 rgba(85, 81, 84, 226));\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"	background-color:rgba(150, 123, 111, 255);\n"
"}\n"
"\n"
"Line#line{\n"
"	color: white;\n"
"}")
        icon3 = QIcon()
        icon3.addFile(u"assets/gui/discord.png", QSize(), QIcon.Normal, QIcon.Off)
        self.discord_settings.setIcon(icon3)
        self.discord_settings.setIconSize(QSize(40, 40))
        self.feed_station = QPushButton(self.MainUi)
        self.feed_station.setObjectName(u"feed_station")
        self.feed_station.setGeometry(QRect(-20, 360, 271, 41))
        self.feed_station.setFont(font1)
        self.feed_station.setCursor(QCursor(Qt.ArrowCursor))
        self.feed_station.setLayoutDirection(Qt.LeftToRight)
        self.feed_station.setStyleSheet(u"\n"
"QPushButton{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(11, 131, 120, 219), stop:1 rgba(85, 98, 112, 226));\n"
"	color:rgba(255, 255, 255, 210);\n"
"	border-bottom-right-radius: 20px;\n"
"	border-top-left-radius: 20px;\n"
"\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(150, 123, 111, 219), stop:1 rgba(85, 81, 84, 226));\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"	background-color:rgba(150, 123, 111, 255);\n"
"}\n"
"\n"
"Line#line{\n"
"	color: white;\n"
"}")
        icon4 = QIcon()
        icon4.addFile(u"assets/gui/raw_meat.png", QSize(), QIcon.Normal, QIcon.Off)
        self.feed_station.setIcon(icon4)
        self.feed_station.setIconSize(QSize(30, 30))
        self.label_57 = QLabel(self.MainUi)
        self.label_57.setObjectName(u"label_57")
        self.label_57.setGeometry(QRect(750, 560, 71, 41))
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush)
#endif
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush)
#endif
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush)
#endif
        self.label_57.setPalette(palette)
        font2 = QFont()
        font2.setPointSize(14)
        self.label_57.setFont(font2)
        self.label_57.setStyleSheet(u"color:rgb(255,255,255)")
        self.general_config = QPushButton(self.MainUi)
        self.general_config.setObjectName(u"general_config")
        self.general_config.setGeometry(QRect(-20, 60, 271, 41))
        self.general_config.setFont(font1)
        self.general_config.setStyleSheet(u"\n"
"QPushButton{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(11, 131, 120, 219), stop:1 rgba(85, 98, 112, 226));\n"
"	color:rgba(255, 255, 255, 210);\n"
"	border-bottom-right-radius: 20px;\n"
"	border-top-left-radius: 20px;\n"
"\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(150, 123, 111, 219), stop:1 rgba(85, 81, 84, 226));\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"	background-color:rgba(150, 123, 111, 255);\n"
"}\n"
"\n"
"Line#line{\n"
"	color: white;\n"
"}")
        icon5 = QIcon()
        icon5.addFile(u"assets/gui/dust.png", QSize(), QIcon.Normal, QIcon.Off)
        self.general_config.setIcon(icon5)
        self.general_config.setIconSize(QSize(40, 40))
        self.crystal_station = QPushButton(self.MainUi)
        self.crystal_station.setObjectName(u"crystal_station")
        self.crystal_station.setGeometry(QRect(-20, 180, 271, 41))
        self.crystal_station.setFont(font1)
        self.crystal_station.setStyleSheet(u"\n"
"QPushButton{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(11, 131, 120, 219), stop:1 rgba(85, 98, 112, 226));\n"
"	color:rgba(255, 255, 255, 210);\n"
"	border-bottom-right-radius: 20px;\n"
"	border-top-left-radius: 20px;\n"
"\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(150, 123, 111, 219), stop:1 rgba(85, 81, 84, 226));\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"	background-color:rgba(150, 123, 111, 255);\n"
"}\n"
"\n"
"Line#line{\n"
"	color: white;\n"
"}")
        icon6 = QIcon()
        icon6.addFile(u"assets/gui/gacha_crystal.png", QSize(), QIcon.Normal, QIcon.Off)
        self.crystal_station.setIcon(icon6)
        self.crystal_station.setIconSize(QSize(40, 40))
        self.tabWidget = QTabWidget(self.MainUi)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(260, -30, 531, 651))
        self.tabWidget.setStyleSheet(u"background-color: rgb(0,0,0);\n"
"color: rgb(0, 255, 255)")
        self.tabWidget.setTabBarAutoHide(False)
        self.tab_7 = QWidget()
        self.tab_7.setObjectName(u"tab_7")
        self.label = QLabel(self.tab_7)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 60, 121, 31))
        self.label.setFont(font)
        self.label.setStyleSheet(u"color: white")
        self.account_name = QLineEdit(self.tab_7)
        self.account_name.setObjectName(u"account_name")
        self.account_name.setGeometry(QRect(10, 90, 113, 20))
        self.account_name.setFont(font)
        self.account_name.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_2 = QLabel(self.tab_7)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(150, 60, 51, 31))
        self.label_2.setFont(font)
        self.label_2.setStyleSheet(u"color: white")
        self.label_3 = QLabel(self.tab_7)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(280, 60, 121, 31))
        self.label_3.setFont(font)
        self.label_3.setStyleSheet(u"color: white")
        self.game_launcher = QComboBox(self.tab_7)
        self.game_launcher.addItem("")
        self.game_launcher.addItem("")
        self.game_launcher.setObjectName(u"game_launcher")
        self.game_launcher.setGeometry(QRect(280, 90, 71, 22))
        self.game_launcher.setFont(font)
        self.game_launcher.setFocusPolicy(Qt.NoFocus)
        self.game_launcher.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.game_launcher.setAcceptDrops(False)
        self.game_launcher.setStyleSheet(u"QComboBox{\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30)\n"
"\n"
"}")
        self.label_5 = QLabel(self.tab_7)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 130, 121, 31))
        self.label_5.setFont(font)
        self.label_5.setStyleSheet(u"color: white")
        self.pod_name = QLineEdit(self.tab_7)
        self.pod_name.setObjectName(u"pod_name")
        self.pod_name.setGeometry(QRect(150, 136, 201, 20))
        self.pod_name.setFont(font)
        self.pod_name.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_6 = QLabel(self.tab_7)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(0, 10, 391, 31))
        font3 = QFont()
        font3.setPointSize(20)
        self.label_6.setFont(font3)
        self.label_6.setAlignment(Qt.AlignCenter)
        self.line = QFrame(self.tab_7)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(7, 170, 371, 20))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.label_9 = QLabel(self.tab_7)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(10, 250, 111, 31))
        self.label_9.setFont(font)
        self.label_9.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.health = QSpinBox(self.tab_7)
        self.health.setObjectName(u"health")
        self.health.setGeometry(QRect(120, 255, 61, 22))
        self.health.setFont(font)
        self.health.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.health.setMinimum(100)
        self.health.setMaximum(1000)
        self.health.setSingleStep(10)
        self.label_10 = QLabel(self.tab_7)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(10, 290, 91, 31))
        self.label_10.setFont(font)
        self.label_10.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.food = QSpinBox(self.tab_7)
        self.food.setObjectName(u"food")
        self.food.setGeometry(QRect(120, 295, 61, 22))
        self.food.setFont(font)
        self.food.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.food.setMinimum(100)
        self.food.setMaximum(1000)
        self.food.setSingleStep(10)
        self.weight = QSpinBox(self.tab_7)
        self.weight.setObjectName(u"weight")
        self.weight.setGeometry(QRect(120, 375, 61, 22))
        self.weight.setFont(font)
        self.weight.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.weight.setMinimum(100)
        self.weight.setMaximum(1500)
        self.weight.setSingleStep(10)
        self.label_11 = QLabel(self.tab_7)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(10, 370, 111, 31))
        self.label_11.setFont(font)
        self.label_11.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.water = QSpinBox(self.tab_7)
        self.water.setObjectName(u"water")
        self.water.setGeometry(QRect(120, 335, 61, 22))
        self.water.setFont(font)
        self.water.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.water.setMinimum(100)
        self.water.setMaximum(1000)
        self.water.setSingleStep(10)
        self.label_12 = QLabel(self.tab_7)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(10, 330, 111, 31))
        self.label_12.setFont(font)
        self.label_12.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.map = QComboBox(self.tab_7)
        self.map.addItem("")
        self.map.addItem("")
        self.map.addItem("")
        self.map.setObjectName(u"map")
        self.map.setGeometry(QRect(150, 90, 91, 21))
        font4 = QFont()
        font4.setFamilies([u"Segoe UI Variable Display Light"])
        font4.setPointSize(13)
        self.map.setFont(font4)
        self.map.setFocusPolicy(Qt.NoFocus)
        self.map.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.map.setLayoutDirection(Qt.LeftToRight)
        self.map.setAutoFillBackground(False)
        self.map.setStyleSheet(u"QComboBox{\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30)\n"
"\n"
"}")
        self.map.setInputMethodHints(Qt.ImhNone)
        self.map.setEditable(False)
        self.map.setMaxVisibleItems(12)
        self.map.setInsertPolicy(QComboBox.InsertAtBottom)
        self.map.setFrame(False)
        self.reset_local_data = QPushButton(self.tab_7)
        self.reset_local_data.setObjectName(u"reset_local_data")
        self.reset_local_data.setGeometry(QRect(270, 420, 111, 41))
        font5 = QFont()
        font5.setPointSize(10)
        self.reset_local_data.setFont(font5)
        self.reset_local_data.setCursor(QCursor(Qt.ArrowCursor))
        self.reset_local_data.setMouseTracking(False)
        self.reset_local_data.setStyleSheet(u"QPushButton:pressed {\n"
"    background-color: rgb(100,100,100);\n"
"}\n"
"\n"
"QPushButton {\n"
"    background-color: rgb(40,40,40);\n"
"}")
        self.verify_ark_settings = QPushButton(self.tab_7)
        self.verify_ark_settings.setObjectName(u"verify_ark_settings")
        self.verify_ark_settings.setGeometry(QRect(140, 420, 121, 41))
        self.verify_ark_settings.setFont(font5)
        self.verify_ark_settings.setCursor(QCursor(Qt.ArrowCursor))
        self.verify_ark_settings.setMouseTracking(False)
        self.verify_ark_settings.setStyleSheet(u"QPushButton:pressed {\n"
"    background-color: rgb(100,100,100);\n"
"}\n"
"\n"
"QPushButton {\n"
"    background-color: rgb(40,40,40);\n"
"}")
        self.show_ark_settings = QPushButton(self.tab_7)
        self.show_ark_settings.setObjectName(u"show_ark_settings")
        self.show_ark_settings.setGeometry(QRect(10, 420, 121, 41))
        self.show_ark_settings.setFont(font5)
        self.show_ark_settings.setCursor(QCursor(Qt.ArrowCursor))
        self.show_ark_settings.setMouseTracking(False)
        self.show_ark_settings.setStyleSheet(u"QPushButton:pressed {\n"
"    background-color: rgb(100,100,100);\n"
"}\n"
"\n"
"QPushButton {\n"
"    background-color: rgb(40,40,40);\n"
"}")
        self.label_7 = QLabel(self.tab_7)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(10, 164, 121, 31))
        self.label_7.setFont(font)
        self.label_7.setStyleSheet(u"color: white")
        self.ark_path = QLineEdit(self.tab_7)
        self.ark_path.setObjectName(u"ark_path")
        self.ark_path.setGeometry(QRect(150, 170, 201, 20))
        self.ark_path.setFont(font)
        self.ark_path.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.tesseract_path = QLineEdit(self.tab_7)
        self.tesseract_path.setObjectName(u"tesseract_path")
        self.tesseract_path.setGeometry(QRect(150, 206, 201, 20))
        self.tesseract_path.setFont(font)
        self.tesseract_path.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_13 = QLabel(self.tab_7)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(10, 200, 121, 31))
        self.label_13.setFont(font)
        self.label_13.setStyleSheet(u"color: white")
        self.timer_pop = QSpinBox(self.tab_7)
        self.timer_pop.setObjectName(u"timer_pop")
        self.timer_pop.setGeometry(QRect(290, 255, 51, 22))
        self.timer_pop.setFont(font)
        self.timer_pop.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.timer_pop.setMinimum(0)
        self.timer_pop.setMaximum(300)
        self.timer_pop.setSingleStep(5)
        self.timer_pop.setValue(20)
        self.label_21 = QLabel(self.tab_7)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setGeometry(QRect(200, 250, 91, 31))
        self.label_21.setFont(font)
        self.label_21.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.tabWidget.addTab(self.tab_7, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.label_14 = QLabel(self.tab_2)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(0, 10, 391, 31))
        self.label_14.setFont(font3)
        self.label_14.setAlignment(Qt.AlignCenter)
        self.label_15 = QLabel(self.tab_2)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(10, 90, 71, 31))
        self.label_15.setFont(font)
        self.label_15.setStyleSheet(u"color: white")
        self.mode = QComboBox(self.tab_2)
        self.mode.addItem("")
        self.mode.addItem("")
        self.mode.addItem("")
        self.mode.addItem("")
        self.mode.setObjectName(u"mode")
        self.mode.setGeometry(QRect(10, 120, 111, 21))
        self.mode.setFont(font4)
        self.mode.setFocusPolicy(Qt.NoFocus)
        self.mode.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.mode.setLayoutDirection(Qt.LeftToRight)
        self.mode.setAutoFillBackground(False)
        self.mode.setStyleSheet(u"QComboBox{\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30)\n"
"\n"
"}")
        self.mode.setInputMethodHints(Qt.ImhNone)
        self.mode.setEditable(False)
        self.mode.setMaxVisibleItems(12)
        self.mode.setInsertPolicy(QComboBox.InsertAtBottom)
        self.mode.setFrame(False)
        self.turn_direction = QComboBox(self.tab_2)
        self.turn_direction.addItem("")
        self.turn_direction.addItem("")
        self.turn_direction.setObjectName(u"turn_direction")
        self.turn_direction.setGeometry(QRect(140, 120, 71, 21))
        self.turn_direction.setFont(font4)
        self.turn_direction.setFocusPolicy(Qt.NoFocus)
        self.turn_direction.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.turn_direction.setLayoutDirection(Qt.LeftToRight)
        self.turn_direction.setAutoFillBackground(False)
        self.turn_direction.setStyleSheet(u"QComboBox{\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30)\n"
"\n"
"}")
        self.turn_direction.setInputMethodHints(Qt.ImhNone)
        self.turn_direction.setEditable(False)
        self.turn_direction.setMaxVisibleItems(12)
        self.turn_direction.setInsertPolicy(QComboBox.InsertAtBottom)
        self.turn_direction.setFrame(False)
        self.label_16 = QLabel(self.tab_2)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setGeometry(QRect(140, 90, 71, 31))
        self.label_16.setFont(font)
        self.label_16.setStyleSheet(u"color: white")
        self.plot_stacks = QSpinBox(self.tab_2)
        self.plot_stacks.setObjectName(u"plot_stacks")
        self.plot_stacks.setGeometry(QRect(150, 160, 61, 22))
        self.plot_stacks.setFont(font)
        self.plot_stacks.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.plot_stacks.setMinimum(1)
        self.plot_stacks.setMaximum(3)
        self.plot_stacks.setSingleStep(1)
        self.label_17 = QLabel(self.tab_2)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setGeometry(QRect(10, 155, 141, 31))
        self.label_17.setFont(font)
        self.label_17.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.plots_per_stack = QSpinBox(self.tab_2)
        self.plots_per_stack.setObjectName(u"plots_per_stack")
        self.plots_per_stack.setGeometry(QRect(310, 160, 61, 22))
        self.plots_per_stack.setFont(font)
        self.plots_per_stack.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.plots_per_stack.setMinimum(6)
        self.plots_per_stack.setMaximum(13)
        self.plots_per_stack.setSingleStep(1)
        self.plots_per_stack.setValue(10)
        self.label_18 = QLabel(self.tab_2)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setGeometry(QRect(220, 155, 81, 31))
        self.label_18.setFont(font)
        self.label_18.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.label_19 = QLabel(self.tab_2)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setGeometry(QRect(10, 200, 201, 31))
        self.label_19.setFont(font)
        self.label_19.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.min_pellet_coverage = QSpinBox(self.tab_2)
        self.min_pellet_coverage.setObjectName(u"min_pellet_coverage")
        self.min_pellet_coverage.setGeometry(QRect(220, 205, 51, 22))
        self.min_pellet_coverage.setFont(font)
        self.min_pellet_coverage.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.min_pellet_coverage.setMinimum(20)
        self.min_pellet_coverage.setMaximum(100)
        self.min_pellet_coverage.setSingleStep(1)
        self.min_pellet_coverage.setValue(80)
        self.label_20 = QLabel(self.tab_2)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setGeometry(QRect(280, 200, 91, 31))
        self.label_20.setFont(font)
        self.label_20.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.label_22 = QLabel(self.tab_2)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setGeometry(QRect(10, 240, 331, 31))
        self.label_22.setFont(font)
        self.label_22.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.crop_plot_turns = QLineEdit(self.tab_2)
        self.crop_plot_turns.setObjectName(u"crop_plot_turns")
        self.crop_plot_turns.setGeometry(QRect(10, 280, 361, 20))
        self.crop_plot_turns.setFont(font)
        self.crop_plot_turns.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_87 = QLabel(self.tab_2)
        self.label_87.setObjectName(u"label_87")
        self.label_87.setGeometry(QRect(10, 320, 361, 151))
        self.label_87.setWordWrap(True)
        self.checkBox = QCheckBox(self.tab_2)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setGeometry(QRect(230, 120, 141, 17))
        self.checkBox.setFont(font)
        self.checkBox.setChecked(True)
        self.label_41 = QLabel(self.tab_2)
        self.label_41.setObjectName(u"label_41")
        self.label_41.setGeometry(QRect(10, 50, 91, 31))
        self.label_41.setFont(font)
        self.label_41.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.ytrap_prefix = QLineEdit(self.tab_2)
        self.ytrap_prefix.setObjectName(u"ytrap_prefix")
        self.ytrap_prefix.setGeometry(QRect(100, 55, 111, 20))
        self.ytrap_prefix.setFont(font)
        self.ytrap_prefix.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_42 = QLabel(self.tab_2)
        self.label_42.setObjectName(u"label_42")
        self.label_42.setGeometry(QRect(230, 50, 51, 31))
        self.label_42.setFont(font)
        self.label_42.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.ytrap_beds = QSpinBox(self.tab_2)
        self.ytrap_beds.setObjectName(u"ytrap_beds")
        self.ytrap_beds.setGeometry(QRect(290, 54, 61, 22))
        self.ytrap_beds.setFont(font)
        self.ytrap_beds.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.ytrap_beds.setMinimum(4)
        self.ytrap_beds.setMaximum(100)
        self.ytrap_beds.setSingleStep(1)
        self.ytrap_beds.setValue(16)
        self.ytrap_enabled = QCheckBox(self.tab_2)
        self.ytrap_enabled.setObjectName(u"ytrap_enabled")
        self.ytrap_enabled.setGeometry(QRect(230, 90, 141, 17))
        self.ytrap_enabled.setFont(font)
        self.ytrap_enabled.setChecked(False)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.label_23 = QLabel(self.tab_3)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setGeometry(QRect(0, 10, 391, 31))
        self.label_23.setFont(font3)
        self.label_23.setAlignment(Qt.AlignCenter)
        self.label_24 = QLabel(self.tab_3)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setGeometry(QRect(10, 100, 141, 31))
        self.label_24.setFont(font)
        self.label_24.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.crystal_interval = QSpinBox(self.tab_3)
        self.crystal_interval.setObjectName(u"crystal_interval")
        self.crystal_interval.setGeometry(QRect(160, 106, 51, 22))
        self.crystal_interval.setFont(font)
        self.crystal_interval.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.crystal_interval.setMinimum(5)
        self.crystal_interval.setMaximum(15)
        self.crystal_interval.setSingleStep(1)
        self.label_25 = QLabel(self.tab_3)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setGeometry(QRect(220, 100, 141, 31))
        self.label_25.setFont(font)
        self.label_25.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.label_26 = QLabel(self.tab_3)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setGeometry(QRect(10, 145, 221, 31))
        self.label_26.setFont(font)
        self.label_26.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.min_ytraps_collected = QSpinBox(self.tab_3)
        self.min_ytraps_collected.setObjectName(u"min_ytraps_collected")
        self.min_ytraps_collected.setGeometry(QRect(230, 150, 71, 22))
        self.min_ytraps_collected.setFont(font)
        self.min_ytraps_collected.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.min_ytraps_collected.setMinimum(0)
        self.min_ytraps_collected.setMaximum(3000)
        self.min_ytraps_collected.setSingleStep(100)
        self.min_ytraps_collected.setValue(2000)
        self.stryder_depositing = QCheckBox(self.tab_3)
        self.stryder_depositing.setObjectName(u"stryder_depositing")
        self.stryder_depositing.setGeometry(QRect(10, 200, 171, 21))
        self.stryder_depositing.setFont(font)
        self.vault_above = QCheckBox(self.tab_3)
        self.vault_above.setObjectName(u"vault_above")
        self.vault_above.setGeometry(QRect(200, 200, 141, 21))
        self.vault_above.setFont(font)
        self.keep_items = QLineEdit(self.tab_3)
        self.keep_items.setObjectName(u"keep_items")
        self.keep_items.setGeometry(QRect(10, 260, 361, 21))
        self.keep_items.setFont(font)
        self.keep_items.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_27 = QLabel(self.tab_3)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setGeometry(QRect(10, 230, 271, 31))
        self.label_27.setFont(font)
        self.label_27.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.label_28 = QLabel(self.tab_3)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setGeometry(QRect(10, 290, 271, 31))
        self.label_28.setFont(font)
        self.label_28.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.drop_items = QLineEdit(self.tab_3)
        self.drop_items.setObjectName(u"drop_items")
        self.drop_items.setGeometry(QRect(10, 320, 361, 21))
        self.drop_items.setFont(font)
        self.drop_items.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_88 = QLabel(self.tab_3)
        self.label_88.setObjectName(u"label_88")
        self.label_88.setGeometry(QRect(10, 340, 361, 131))
        self.label_88.setWordWrap(True)
        self.crystal_beds = QSpinBox(self.tab_3)
        self.crystal_beds.setObjectName(u"crystal_beds")
        self.crystal_beds.setGeometry(QRect(290, 54, 61, 22))
        self.crystal_beds.setFont(font)
        self.crystal_beds.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.crystal_beds.setMinimum(1)
        self.crystal_beds.setMaximum(4)
        self.crystal_beds.setSingleStep(1)
        self.crystal_beds.setValue(4)
        self.label_43 = QLabel(self.tab_3)
        self.label_43.setObjectName(u"label_43")
        self.label_43.setGeometry(QRect(10, 50, 91, 31))
        self.label_43.setFont(font)
        self.label_43.setStyleSheet(u"color: white")
        self.crystal_prefix = QLineEdit(self.tab_3)
        self.crystal_prefix.setObjectName(u"crystal_prefix")
        self.crystal_prefix.setGeometry(QRect(100, 55, 111, 20))
        self.crystal_prefix.setFont(font)
        self.crystal_prefix.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_44 = QLabel(self.tab_3)
        self.label_44.setObjectName(u"label_44")
        self.label_44.setGeometry(QRect(230, 50, 51, 31))
        self.label_44.setFont(font)
        self.label_44.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.label_29 = QLabel(self.tab_4)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setGeometry(QRect(0, 10, 391, 31))
        self.label_29.setFont(font3)
        self.label_29.setAlignment(Qt.AlignCenter)
        self.item_to_craft = QComboBox(self.tab_4)
        self.item_to_craft.addItem("")
        self.item_to_craft.addItem("")
        self.item_to_craft.addItem("")
        self.item_to_craft.addItem("")
        self.item_to_craft.addItem("")
        self.item_to_craft.addItem("")
        self.item_to_craft.addItem("")
        self.item_to_craft.addItem("")
        self.item_to_craft.addItem("")
        self.item_to_craft.setObjectName(u"item_to_craft")
        self.item_to_craft.setGeometry(QRect(120, 66, 171, 21))
        self.item_to_craft.setFont(font4)
        self.item_to_craft.setFocusPolicy(Qt.NoFocus)
        self.item_to_craft.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.item_to_craft.setLayoutDirection(Qt.LeftToRight)
        self.item_to_craft.setAutoFillBackground(False)
        self.item_to_craft.setStyleSheet(u"QComboBox{\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30)\n"
"\n"
"}")
        self.item_to_craft.setInputMethodHints(Qt.ImhNone)
        self.item_to_craft.setEditable(False)
        self.item_to_craft.setMaxVisibleItems(12)
        self.item_to_craft.setInsertPolicy(QComboBox.InsertAtBottom)
        self.item_to_craft.setFrame(False)
        self.label_30 = QLabel(self.tab_4)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setGeometry(QRect(10, 60, 101, 31))
        self.label_30.setFont(font)
        self.label_30.setStyleSheet(u"color: white")
        self.text_rgb = QLineEdit(self.tab_4)
        self.text_rgb.setObjectName(u"text_rgb")
        self.text_rgb.setGeometry(QRect(120, 116, 161, 21))
        self.text_rgb.setFont(font)
        self.text_rgb.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_31 = QLabel(self.tab_4)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setGeometry(QRect(10, 110, 101, 31))
        self.label_31.setFont(font)
        self.label_31.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.label_32 = QLabel(self.tab_4)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setGeometry(QRect(10, 145, 111, 31))
        self.label_32.setFont(font)
        self.label_32.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.pearls_region = QLineEdit(self.tab_4)
        self.pearls_region.setObjectName(u"pearls_region")
        self.pearls_region.setGeometry(QRect(120, 150, 171, 21))
        self.pearls_region.setFont(font)
        self.pearls_region.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_33 = QLabel(self.tab_4)
        self.label_33.setObjectName(u"label_33")
        self.label_33.setGeometry(QRect(10, 175, 111, 31))
        self.label_33.setFont(font)
        self.label_33.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.paste_region = QLineEdit(self.tab_4)
        self.paste_region.setObjectName(u"paste_region")
        self.paste_region.setGeometry(QRect(120, 180, 171, 21))
        self.paste_region.setFont(font)
        self.paste_region.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.electronics_region = QLineEdit(self.tab_4)
        self.electronics_region.setObjectName(u"electronics_region")
        self.electronics_region.setGeometry(QRect(120, 210, 171, 21))
        self.electronics_region.setFont(font)
        self.electronics_region.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_34 = QLabel(self.tab_4)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setGeometry(QRect(10, 205, 111, 31))
        self.label_34.setFont(font)
        self.label_34.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.ingots_region = QLineEdit(self.tab_4)
        self.ingots_region.setObjectName(u"ingots_region")
        self.ingots_region.setGeometry(QRect(120, 240, 171, 21))
        self.ingots_region.setFont(font)
        self.ingots_region.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_35 = QLabel(self.tab_4)
        self.label_35.setObjectName(u"label_35")
        self.label_35.setGeometry(QRect(10, 235, 111, 31))
        self.label_35.setFont(font)
        self.label_35.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.crystal_region = QLineEdit(self.tab_4)
        self.crystal_region.setObjectName(u"crystal_region")
        self.crystal_region.setGeometry(QRect(120, 270, 171, 21))
        self.crystal_region.setFont(font)
        self.crystal_region.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_36 = QLabel(self.tab_4)
        self.label_36.setObjectName(u"label_36")
        self.label_36.setGeometry(QRect(10, 265, 111, 31))
        self.label_36.setFont(font)
        self.label_36.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.hide_region = QLineEdit(self.tab_4)
        self.hide_region.setObjectName(u"hide_region")
        self.hide_region.setGeometry(QRect(120, 300, 171, 21))
        self.hide_region.setFont(font)
        self.hide_region.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_37 = QLabel(self.tab_4)
        self.label_37.setObjectName(u"label_37")
        self.label_37.setGeometry(QRect(10, 295, 111, 31))
        self.label_37.setFont(font)
        self.label_37.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.label_89 = QLabel(self.tab_4)
        self.label_89.setObjectName(u"label_89")
        self.label_89.setGeometry(QRect(10, 330, 361, 141))
        self.label_89.setWordWrap(True)
        self.grinding_enabled = QCheckBox(self.tab_4)
        self.grinding_enabled.setObjectName(u"grinding_enabled")
        self.grinding_enabled.setGeometry(QRect(300, 68, 141, 17))
        self.grinding_enabled.setFont(font)
        self.grinding_enabled.setChecked(False)
        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.label_38 = QLabel(self.tab_5)
        self.label_38.setObjectName(u"label_38")
        self.label_38.setGeometry(QRect(0, 10, 391, 31))
        self.label_38.setFont(font3)
        self.label_38.setAlignment(Qt.AlignCenter)
        self.label_40 = QLabel(self.tab_5)
        self.label_40.setObjectName(u"label_40")
        self.label_40.setGeometry(QRect(0, 120, 391, 31))
        font6 = QFont()
        font6.setPointSize(9)
        self.label_40.setFont(font6)
        self.label_40.setStyleSheet(u"color: rgb(255, 0, 0)")
        self.label_40.setAlignment(Qt.AlignCenter)
        self.arb_enabled = QCheckBox(self.tab_5)
        self.arb_enabled.setObjectName(u"arb_enabled")
        self.arb_enabled.setGeometry(QRect(10, 70, 141, 17))
        self.arb_enabled.setFont(font)
        self.arb_enabled.setChecked(False)
        self.tabWidget.addTab(self.tab_5, "")
        self.tab_6 = QWidget()
        self.tab_6.setObjectName(u"tab_6")
        self.label_45 = QLabel(self.tab_6)
        self.label_45.setObjectName(u"label_45")
        self.label_45.setGeometry(QRect(0, 10, 391, 31))
        self.label_45.setFont(font3)
        self.label_45.setAlignment(Qt.AlignCenter)
        self.label_46 = QLabel(self.tab_6)
        self.label_46.setObjectName(u"label_46")
        self.label_46.setGeometry(QRect(260, 85, 51, 31))
        self.label_46.setFont(font)
        self.label_46.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.meat_beds = QSpinBox(self.tab_6)
        self.meat_beds.setObjectName(u"meat_beds")
        self.meat_beds.setGeometry(QRect(310, 89, 61, 22))
        self.meat_beds.setFont(font)
        self.meat_beds.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.meat_beds.setMinimum(0)
        self.meat_beds.setMaximum(16)
        self.meat_beds.setSingleStep(1)
        self.meat_beds.setValue(4)
        self.label_47 = QLabel(self.tab_6)
        self.label_47.setObjectName(u"label_47")
        self.label_47.setGeometry(QRect(10, 85, 121, 31))
        self.label_47.setFont(font)
        self.label_47.setStyleSheet(u"color: white")
        self.meat_prefix = QLineEdit(self.tab_6)
        self.meat_prefix.setObjectName(u"meat_prefix")
        self.meat_prefix.setGeometry(QRect(140, 90, 111, 20))
        self.meat_prefix.setFont(font)
        self.meat_prefix.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_48 = QLabel(self.tab_6)
        self.label_48.setObjectName(u"label_48")
        self.label_48.setGeometry(QRect(10, 206, 121, 31))
        self.label_48.setFont(font)
        self.label_48.setStyleSheet(u"color: white")
        self.berry_prefix = QLineEdit(self.tab_6)
        self.berry_prefix.setObjectName(u"berry_prefix")
        self.berry_prefix.setGeometry(QRect(140, 211, 111, 20))
        self.berry_prefix.setFont(font)
        self.berry_prefix.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.berry_beds = QSpinBox(self.tab_6)
        self.berry_beds.setObjectName(u"berry_beds")
        self.berry_beds.setGeometry(QRect(310, 210, 61, 22))
        self.berry_beds.setFont(font)
        self.berry_beds.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.berry_beds.setMinimum(0)
        self.berry_beds.setMaximum(16)
        self.berry_beds.setSingleStep(1)
        self.berry_beds.setValue(4)
        self.label_49 = QLabel(self.tab_6)
        self.label_49.setObjectName(u"label_49")
        self.label_49.setGeometry(QRect(260, 206, 51, 31))
        self.label_49.setFont(font)
        self.label_49.setStyleSheet(u"color: rgb(255, 255, 255)")
        self.label_50 = QLabel(self.tab_6)
        self.label_50.setObjectName(u"label_50")
        self.label_50.setGeometry(QRect(10, 130, 121, 31))
        self.label_50.setFont(font)
        self.label_50.setStyleSheet(u"color: white")
        self.meat_interval = QSpinBox(self.tab_6)
        self.meat_interval.setObjectName(u"meat_interval")
        self.meat_interval.setGeometry(QRect(140, 136, 71, 22))
        self.meat_interval.setFont(font)
        self.meat_interval.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.meat_interval.setMinimum(30)
        self.meat_interval.setMaximum(4320)
        self.meat_interval.setSingleStep(1)
        self.label_51 = QLabel(self.tab_6)
        self.label_51.setObjectName(u"label_51")
        self.label_51.setGeometry(QRect(220, 130, 121, 31))
        self.label_51.setFont(font)
        self.label_51.setStyleSheet(u"color: white")
        self.label_52 = QLabel(self.tab_6)
        self.label_52.setObjectName(u"label_52")
        self.label_52.setGeometry(QRect(220, 250, 121, 31))
        self.label_52.setFont(font)
        self.label_52.setStyleSheet(u"color: white")
        self.berry_interval = QSpinBox(self.tab_6)
        self.berry_interval.setObjectName(u"berry_interval")
        self.berry_interval.setGeometry(QRect(140, 256, 71, 22))
        self.berry_interval.setFont(font)
        self.berry_interval.setStyleSheet(u"border: None;\n"
"background-color: rgb(30, 30, 30);")
        self.berry_interval.setMinimum(300)
        self.berry_interval.setMaximum(4320)
        self.berry_interval.setSingleStep(1)
        self.label_53 = QLabel(self.tab_6)
        self.label_53.setObjectName(u"label_53")
        self.label_53.setGeometry(QRect(10, 250, 121, 31))
        self.label_53.setFont(font)
        self.label_53.setStyleSheet(u"color: white")
        self.meat_enabled = QCheckBox(self.tab_6)
        self.meat_enabled.setObjectName(u"meat_enabled")
        self.meat_enabled.setGeometry(QRect(10, 60, 131, 17))
        self.meat_enabled.setFont(font)
        self.berry_enabled = QCheckBox(self.tab_6)
        self.berry_enabled.setObjectName(u"berry_enabled")
        self.berry_enabled.setGeometry(QRect(10, 180, 131, 17))
        self.berry_enabled.setFont(font)
        self.tabWidget.addTab(self.tab_6, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.label_54 = QLabel(self.tab)
        self.label_54.setObjectName(u"label_54")
        self.label_54.setGeometry(QRect(0, 10, 391, 31))
        self.label_54.setFont(font3)
        self.label_54.setAlignment(Qt.AlignCenter)
        self.label_55 = QLabel(self.tab)
        self.label_55.setObjectName(u"label_55")
        self.label_55.setGeometry(QRect(10, 55, 121, 31))
        self.label_55.setFont(font)
        self.label_55.setStyleSheet(u"color: white")
        self.user_id = QLineEdit(self.tab)
        self.user_id.setObjectName(u"user_id")
        self.user_id.setGeometry(QRect(140, 60, 231, 20))
        self.user_id.setFont(font)
        self.user_id.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_56 = QLabel(self.tab)
        self.label_56.setObjectName(u"label_56")
        self.label_56.setGeometry(QRect(10, 95, 131, 31))
        self.label_56.setFont(font)
        self.label_56.setStyleSheet(u"color: white")
        self.webhook_gacha = QLineEdit(self.tab)
        self.webhook_gacha.setObjectName(u"webhook_gacha")
        self.webhook_gacha.setGeometry(QRect(140, 100, 231, 20))
        self.webhook_gacha.setFont(font)
        self.webhook_gacha.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_58 = QLabel(self.tab)
        self.label_58.setObjectName(u"label_58")
        self.label_58.setGeometry(QRect(10, 135, 131, 31))
        self.label_58.setFont(font)
        self.label_58.setStyleSheet(u"color: white")
        self.webhook_alert = QLineEdit(self.tab)
        self.webhook_alert.setObjectName(u"webhook_alert")
        self.webhook_alert.setGeometry(QRect(140, 140, 231, 20))
        self.webhook_alert.setFont(font)
        self.webhook_alert.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_59 = QLabel(self.tab)
        self.label_59.setObjectName(u"label_59")
        self.label_59.setGeometry(QRect(10, 175, 131, 31))
        self.label_59.setFont(font)
        self.label_59.setStyleSheet(u"color: white")
        self.webhook_logs = QLineEdit(self.tab)
        self.webhook_logs.setObjectName(u"webhook_logs")
        self.webhook_logs.setGeometry(QRect(140, 180, 231, 20))
        self.webhook_logs.setFont(font)
        self.webhook_logs.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_60 = QLabel(self.tab)
        self.label_60.setObjectName(u"label_60")
        self.label_60.setGeometry(QRect(10, 220, 131, 31))
        self.label_60.setFont(font)
        self.label_60.setStyleSheet(u"color: white")
        self.webhook_state = QLineEdit(self.tab)
        self.webhook_state.setObjectName(u"webhook_state")
        self.webhook_state.setGeometry(QRect(140, 225, 231, 20))
        self.webhook_state.setFont(font)
        self.webhook_state.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_61 = QLabel(self.tab)
        self.label_61.setObjectName(u"label_61")
        self.label_61.setGeometry(QRect(10, 285, 161, 31))
        self.label_61.setFont(font)
        self.label_61.setStyleSheet(u"color: white")
        self.state_message_id = QLineEdit(self.tab)
        self.state_message_id.setObjectName(u"state_message_id")
        self.state_message_id.setGeometry(QRect(160, 290, 181, 20))
        self.state_message_id.setFont(font)
        self.state_message_id.setStyleSheet(u"\n"
"color: rgb(0, 255, 255);\n"
"background-color: rgb(30, 30, 30);\n"
"border: None\n"
"\n"
"")
        self.label_90 = QLabel(self.tab)
        self.label_90.setObjectName(u"label_90")
        self.label_90.setGeometry(QRect(10, 330, 361, 131))
        self.label_90.setWordWrap(True)
        self.tabWidget.addTab(self.tab, "")
        Form.setCentralWidget(self.MainUi)
        self.LeftBackground.raise_()
        self.label_4.raise_()
        self.label_8.raise_()
        self.ytrap_stations.raise_()
        self.grinding.raise_()
        self.bullets_station.raise_()
        self.discord_settings.raise_()
        self.feed_station.raise_()
        self.label_57.raise_()
        self.general_config.raise_()
        self.crystal_station.raise_()
        self.tabWidget.raise_()

        self.retranslateUi(Form)

        self.tabWidget.setCurrentIndex(5)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Ling Ling", None))
        self.LeftBackground.setText("")
        self.label_8.setText("")
        self.label_4.setText("")
        self.ytrap_stations.setText(QCoreApplication.translate("Form", u"YTrap Stations", None))
        self.grinding.setText(QCoreApplication.translate("Form", u"Grinding Station", None))
        self.bullets_station.setText(QCoreApplication.translate("Form", u"Bullets Station", None))
        self.discord_settings.setText(QCoreApplication.translate("Form", u"Discord Settings", None))
        self.feed_station.setText(QCoreApplication.translate("Form", u"Feed Stations", None))
        self.label_57.setText(QCoreApplication.translate("Form", u"Mode", None))
        self.general_config.setText(QCoreApplication.translate("Form", u"General Config", None))
        self.crystal_station.setText(QCoreApplication.translate("Form", u"Crystal Stations", None))
        self.label.setText(QCoreApplication.translate("Form", u"Account:", None))
        self.account_name.setPlaceholderText(QCoreApplication.translate("Form", u"DinoLover900", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Map:", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Launcher:", None))
        self.game_launcher.setItemText(0, QCoreApplication.translate("Form", u"Steam", None))
        self.game_launcher.setItemText(1, QCoreApplication.translate("Form", u"Epic", None))

        self.label_5.setText(QCoreApplication.translate("Form", u"Recovery pod:", None))
        self.pod_name.setPlaceholderText(QCoreApplication.translate("Form", u"Gacha Heal", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"General Configuration", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"Player Health:", None))
        self.label_10.setText(QCoreApplication.translate("Form", u"Player Food:", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"Player Weight", None))
        self.label_12.setText(QCoreApplication.translate("Form", u"Player Water:", None))
        self.map.setItemText(0, QCoreApplication.translate("Form", u"Genesis 2", None))
        self.map.setItemText(1, QCoreApplication.translate("Form", u"Aberration", None))
        self.map.setItemText(2, QCoreApplication.translate("Form", u"Other", None))

#if QT_CONFIG(tooltip)
        self.map.setToolTip(QCoreApplication.translate("Form", u"Create, rename and delete presets!", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.reset_local_data.setToolTip(QCoreApplication.translate("Form", u"Add a new preset", None))
#endif // QT_CONFIG(tooltip)
        self.reset_local_data.setText(QCoreApplication.translate("Form", u"Reset local data", None))
#if QT_CONFIG(tooltip)
        self.verify_ark_settings.setToolTip(QCoreApplication.translate("Form", u"Add a new preset", None))
#endif // QT_CONFIG(tooltip)
        self.verify_ark_settings.setText(QCoreApplication.translate("Form", u"Verify Ark Settings", None))
#if QT_CONFIG(tooltip)
        self.show_ark_settings.setToolTip(QCoreApplication.translate("Form", u"Add a new preset", None))
#endif // QT_CONFIG(tooltip)
        self.show_ark_settings.setText(QCoreApplication.translate("Form", u"Show Ark Settings", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"Ark folder path:", None))
        self.ark_path.setPlaceholderText(QCoreApplication.translate("Form", u"F:\\ARKSurvivalEvolved", None))
        self.tesseract_path.setPlaceholderText(QCoreApplication.translate("Form", u"C:\\Program Files\\Tesseract-OCR", None))
        self.label_13.setText(QCoreApplication.translate("Form", u"Tesseract path:", None))
        self.label_21.setText(QCoreApplication.translate("Form", u"Timer pop:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_7), QCoreApplication.translate("Form", u"GC", None))
        self.label_14.setText(QCoreApplication.translate("Form", u"YTrap Configuration", None))
        self.label_15.setText(QCoreApplication.translate("Form", u"Mode:", None))
        self.mode.setItemText(0, QCoreApplication.translate("Form", u"normal", None))
        self.mode.setItemText(1, QCoreApplication.translate("Form", u"precise", None))
        self.mode.setItemText(2, QCoreApplication.translate("Form", u"precise refill", None))
        self.mode.setItemText(3, QCoreApplication.translate("Form", u"set folders", None))

#if QT_CONFIG(tooltip)
        self.mode.setToolTip(QCoreApplication.translate("Form", u"Create, rename and delete presets!", None))
#endif // QT_CONFIG(tooltip)
        self.turn_direction.setItemText(0, QCoreApplication.translate("Form", u"right", None))
        self.turn_direction.setItemText(1, QCoreApplication.translate("Form", u"left", None))

#if QT_CONFIG(tooltip)
        self.turn_direction.setToolTip(QCoreApplication.translate("Form", u"Create, rename and delete presets!", None))
#endif // QT_CONFIG(tooltip)
        self.label_16.setText(QCoreApplication.translate("Form", u"Turn:", None))
        self.label_17.setText(QCoreApplication.translate("Form", u"Crop Plot stacks:", None))
        self.label_18.setText(QCoreApplication.translate("Form", u"Per Stack:", None))
        self.label_19.setText(QCoreApplication.translate("Form", u"Minimum pellet coverage:", None))
        self.label_20.setText(QCoreApplication.translate("Form", u"%", None))
        self.label_22.setText(QCoreApplication.translate("Form", u"Crop Plot Turns (Requires pythonic syntax):", None))
        self.crop_plot_turns.setPlaceholderText(QCoreApplication.translate("Form", u"[-130, *[-17] * 5, 50, -17]", None))
        self.label_87.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-size:10pt; color:#00aaff;\">Turn values are not related to your ingame sensitivity. To customize the turns, please follow pythons </span><a href=\"https/docs.python.org/3/tutorial/datastructures.html#more-on-lists\"><span style=\" text-decoration: underline; color:#0000ff;\">list</span></a><span style=\" font-size:10pt; color:#00aaff;\"> syntax, as the entered values will only be evaluated as such.</span></p><p><span style=\" font-size:10pt; color:#00aaff;\">This simply allows quicker creation, for instance instead of writing out -17 five times, it can be written as </span><span style=\" font-family:'Consolas','Courier New','monospace'; font-size:9pt; color:#00ff00;\">[*[-17] * 5]</span><span style=\" font-family:'Consolas','Courier New','monospace'; font-size:9pt; color:#00aaff;\">. </span></p><p><span style=\" font-family:'Consolas','Courier New','monospace'; font-size:10pt; color:#ff0000;\">The amount of turns must match the amount of crop plots!</span></p></body>"
                        "</html>", None))
        self.checkBox.setText(QCoreApplication.translate("Form", u"Find dead plots", None))
        self.label_41.setText(QCoreApplication.translate("Form", u"Bed prefix:", None))
        self.ytrap_prefix.setPlaceholderText(QCoreApplication.translate("Form", u"gachaseed", None))
        self.label_42.setText(QCoreApplication.translate("Form", u"Beds:", None))
        self.ytrap_enabled.setText(QCoreApplication.translate("Form", u"Enabled", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Form", u"YTRAP", None))
        self.label_23.setText(QCoreApplication.translate("Form", u"Collection Configuration", None))
        self.label_24.setText(QCoreApplication.translate("Form", u"Collection interval:", None))
        self.label_25.setText(QCoreApplication.translate("Form", u"minutes.", None))
        self.label_26.setText(QCoreApplication.translate("Form", u"Minimum YTraps deposited:", None))
        self.stryder_depositing.setText(QCoreApplication.translate("Form", u"Deposit into Stryder", None))
        self.vault_above.setText(QCoreApplication.translate("Form", u"Vault above", None))
        self.keep_items.setPlaceholderText(QCoreApplication.translate("Form", u"[\"riot\", \"fab\", \"pump\", \"ass\", \"miner\"]", None))
        self.label_27.setText(QCoreApplication.translate("Form", u"Keep (follows pythonic list syntax):", None))
        self.label_28.setText(QCoreApplication.translate("Form", u"Drop (follows pythonic list syntax):", None))
        self.drop_items.setText("")
        self.drop_items.setPlaceholderText(QCoreApplication.translate("Form", u"[\"prim\", \"ram\"]", None))
        self.label_88.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-size:10pt; color:#00aaff;\">Each term will be searched and transferred / dropped, when adding or removing terms please follow pythons </span><a href=\"https/docs.python.org/3/tutorial/datastructures.html#more-on-lists\"><span style=\" font-weight:600; text-decoration: underline; color:#0000ff;\">list</span></a><span style=\" font-size:10pt; color:#00aaff;\"> syntax, as the entered values will only be evaluated as such.</span></p><p><span style=\" font-size:10pt; color:#00aaff;\">When choosing what to keep, be mindful of materials required for the structure you are crafting, i.e not keeping miner helmets when crafting heavies would be stupid.</span></p></body></html>", None))
        self.label_43.setText(QCoreApplication.translate("Form", u"Bed prefix:", None))
        self.crystal_prefix.setPlaceholderText(QCoreApplication.translate("Form", u"crystal", None))
        self.label_44.setText(QCoreApplication.translate("Form", u"Beds:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("Form", u"CRYSTAL", None))
        self.label_29.setText(QCoreApplication.translate("Form", u"Grinding Configuration", None))
        self.item_to_craft.setItemText(0, QCoreApplication.translate("Form", u"None", None))
        self.item_to_craft.setItemText(1, QCoreApplication.translate("Form", u"Heavy Auto Turret", None))
        self.item_to_craft.setItemText(2, QCoreApplication.translate("Form", u"Tek Turret", None))
        self.item_to_craft.setItemText(3, QCoreApplication.translate("Form", u"Auto Turret", None))
        self.item_to_craft.setItemText(4, QCoreApplication.translate("Form", u"C4 Remote Detonator", None))
        self.item_to_craft.setItemText(5, QCoreApplication.translate("Form", u"Rocket Launcher", None))
        self.item_to_craft.setItemText(6, QCoreApplication.translate("Form", u"Metal Gate", None))
        self.item_to_craft.setItemText(7, QCoreApplication.translate("Form", u"Metal Triangle Foundation", None))
        self.item_to_craft.setItemText(8, QCoreApplication.translate("Form", u"Metal Foundation", None))

#if QT_CONFIG(tooltip)
        self.item_to_craft.setToolTip(QCoreApplication.translate("Form", u"Create, rename and delete presets!", None))
#endif // QT_CONFIG(tooltip)
        self.label_30.setText(QCoreApplication.translate("Form", u"Craft item:", None))
        self.text_rgb.setPlaceholderText(QCoreApplication.translate("Form", u"(56, 232, 231)", None))
        self.label_31.setText(QCoreApplication.translate("Form", u"Text RGB:", None))
        self.label_32.setText(QCoreApplication.translate("Form", u"Pearls region:", None))
        self.pearls_region.setPlaceholderText(QCoreApplication.translate("Form", u"(25, 350, 510, 355)", None))
        self.label_33.setText(QCoreApplication.translate("Form", u"Paste region:", None))
        self.paste_region.setText("")
        self.paste_region.setPlaceholderText(QCoreApplication.translate("Form", u"(17, 697, 560, 370)", None))
        self.electronics_region.setText("")
        self.electronics_region.setPlaceholderText(QCoreApplication.translate("Form", u"(593, 390, 590, 303)", None))
        self.label_34.setText(QCoreApplication.translate("Form", u"Electr. region:", None))
        self.ingots_region.setText("")
        self.ingots_region.setPlaceholderText(QCoreApplication.translate("Form", u"(570, 730, 640, 305)", None))
        self.label_35.setText(QCoreApplication.translate("Form", u"Ingots region:", None))
        self.crystal_region.setText("")
        self.crystal_region.setPlaceholderText(QCoreApplication.translate("Form", u"(1245, 365, 560, 315)", None))
        self.label_36.setText(QCoreApplication.translate("Form", u"Crystal region:", None))
        self.hide_region.setText("")
        self.hide_region.setPlaceholderText(QCoreApplication.translate("Form", u"(1240, 690, 613, 355)", None))
        self.label_37.setText(QCoreApplication.translate("Form", u"Hide region:", None))
        self.label_89.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-size:10pt; color:#00aaff;\">The regions are relevant for determining the amount of materials within the respective dedi. You can test whether your regions are fine by using the grinding calibrate option and then check the open-cv window for each dedi.</span></p><p><span style=\" font-size:10pt; color:#00aaff;\">To change the region, take a fullscreen image of your game with the view on the dedis, then open it in paint and select the region, the box is displayed in the bottom left corner.</span></p></body></html>", None))
        self.grinding_enabled.setText(QCoreApplication.translate("Form", u"Enabled", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("Form", u"GRIND", None))
        self.label_38.setText(QCoreApplication.translate("Form", u"ARB/Bullet Configuration", None))
        self.label_40.setText(QCoreApplication.translate("Form", u"Will have the option to craft other gunpowder stuff / not use arb bps", None))
        self.arb_enabled.setText(QCoreApplication.translate("Form", u"Enabled", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QCoreApplication.translate("Form", u"ARB", None))
        self.label_45.setText(QCoreApplication.translate("Form", u"Feeding Configuration", None))
        self.label_46.setText(QCoreApplication.translate("Form", u"Beds:", None))
        self.label_47.setText(QCoreApplication.translate("Form", u"Meat bed prefix:", None))
        self.meat_prefix.setText("")
        self.meat_prefix.setPlaceholderText(QCoreApplication.translate("Form", u"automeat", None))
        self.label_48.setText(QCoreApplication.translate("Form", u"Berry bed prefix:", None))
        self.berry_prefix.setText("")
        self.berry_prefix.setPlaceholderText(QCoreApplication.translate("Form", u"autoberry", None))
        self.label_49.setText(QCoreApplication.translate("Form", u"Beds:", None))
        self.label_50.setText(QCoreApplication.translate("Form", u"Meat interval:", None))
        self.label_51.setText(QCoreApplication.translate("Form", u"minutes.", None))
        self.label_52.setText(QCoreApplication.translate("Form", u"minutes.", None))
        self.label_53.setText(QCoreApplication.translate("Form", u"Berry interval:", None))
        self.meat_enabled.setText(QCoreApplication.translate("Form", u"Enabled", None))
        self.berry_enabled.setText(QCoreApplication.translate("Form", u"Enabled", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), QCoreApplication.translate("Form", u"FEED", None))
        self.label_54.setText(QCoreApplication.translate("Form", u"Discord Configuration", None))
        self.label_55.setText(QCoreApplication.translate("Form", u"User ID:", None))
        self.user_id.setText("")
        self.user_id.setPlaceholderText(QCoreApplication.translate("Form", u"529805265252646914", None))
        self.label_56.setText(QCoreApplication.translate("Form", u"Info webhook:", None))
        self.webhook_gacha.setText("")
        self.webhook_gacha.setPlaceholderText(QCoreApplication.translate("Form", u"https/discord.com/api/webhooks", None))
        self.label_58.setText(QCoreApplication.translate("Form", u"Alert webhook:", None))
        self.webhook_alert.setText("")
        self.webhook_alert.setPlaceholderText(QCoreApplication.translate("Form", u"https/discord.com/api/webhooks", None))
        self.label_59.setText(QCoreApplication.translate("Form", u"Logs webhook:", None))
        self.webhook_logs.setText("")
        self.webhook_logs.setPlaceholderText(QCoreApplication.translate("Form", u"https/discord.com/api/webhooks", None))
        self.label_60.setText(QCoreApplication.translate("Form", u"Timer webhook:", None))
        self.webhook_state.setText("")
        self.webhook_state.setPlaceholderText(QCoreApplication.translate("Form", u"https/discord.com/api/webhooks", None))
        self.label_61.setText(QCoreApplication.translate("Form", u"Timer message ID:", None))
        self.state_message_id.setText("")
        self.state_message_id.setPlaceholderText(QCoreApplication.translate("Form", u"1078004041038168104", None))
        self.label_90.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><span style=\" font-size:10pt; color:#00aaff;\">Webhooks are not optional, please make sure you enter them. You can use the same channel for every hook, but I </span><span style=\" font-size:10pt; font-weight:600; color:#00aaff;\">strongly</span><span style=\" font-size:10pt; color:#00aaff;\"> recommend against doing so, assign them to designated channels.</span></p><p><span style=\" font-size:10pt; color:#00aaff;\">If a discord user ID is entered, it will be @ed when the bot runs into an error.</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Form", u"DISCORD", None))
    # retranslateUi

