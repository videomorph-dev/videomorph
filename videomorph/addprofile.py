# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QSpacerItem, QDialogButtonBox)


class AddProfileDialog(QDialog):
    def __init__(self, parent=None):
        super(AddProfileDialog, self).__init__(parent)
        self.setWindowTitle(self.tr("Add Customized Profile"))
        self.resize(399, 295)

        self.layoutWidget = QWidget(self)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 361, 257))

        self.verticalLayout_4 = QVBoxLayout(self.layoutWidget)

        self.verticalLayout = QVBoxLayout()

        self.label = QLabel(self.layoutWidget)
        self.label.setText(self.tr("Pr&ofile Name (e.g. MP4)"))
        self.verticalLayout.addWidget(self.label)

        self.le_profile_name = QLineEdit(self.layoutWidget)
        self.verticalLayout.addWidget(self.le_profile_name)

        self.verticalLayout_4.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setText(self.tr(
            "&Preset Target Quality Name (e.g. MP4 Widescreen (16:9))"))
        self.verticalLayout_2.addWidget(self.label_2)

        self.le_preset_name = QLineEdit(self.layoutWidget)
        self.verticalLayout_2.addWidget(self.le_preset_name)

        self.verticalLayout_4.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()

        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setText(self.tr(
            "Prest &Command Line Parameters for Tarrget Quality"))
        self.verticalLayout_3.addWidget(self.label_3)

        self.le_params = QLineEdit(self.layoutWidget)
        self.verticalLayout_3.addWidget(self.le_params)

        self.verticalLayout_4.addLayout(self.verticalLayout_3)

        self.verticalLayout_5 = QVBoxLayout()

        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setText(self.tr(
            "Output File &Extension"))
        self.verticalLayout_5.addWidget(self.label_4)

        self.le_extension = QLineEdit(self.layoutWidget)
        self.verticalLayout_5.addWidget(self.le_extension)

        self.verticalLayout_4.addLayout(self.verticalLayout_5)

        spacerItem = QSpacerItem(20, 48,
                                 QtWidgets.QSizePolicy.Minimum,
                                 QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)

        self.buttonBox = QDialogButtonBox(self.layoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.verticalLayout_4.addWidget(self.buttonBox)

        self.label.setBuddy(self.le_profile_name)
        self.label_2.setBuddy(self.le_preset_name)
        self.label_3.setBuddy(self.le_params)
        self.label_4.setBuddy(self.le_extension)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
