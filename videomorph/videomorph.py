#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#   MediaMorph - A PyQt5 frontend to ffmpeg
#   Copyright 2015-2016 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

__version__ = '0.3'

from os.path import splitext
import re

from PyQt5.QtWidgets import (QMainWindow,
                             QApplication,
                             QWidget,
                             QVBoxLayout,
                             QHBoxLayout,
                             QSizePolicy,
                             QGroupBox,
                             QLabel,
                             QSpacerItem,
                             QComboBox,
                             QProgressBar,
                             QToolBar,
                             QTableWidget,
                             QTableWidgetItem,
                             QLineEdit,
                             QAction,
                             QStyle,
                             QAbstractItemView,
                             QFileDialog,
                             QMessageBox,
                             QHeaderView,
                             QToolButton,
                             qApp)

from PyQt5.QtCore import (QSize,
                          Qt,
                          QSettings,
                          QDir,
                          QPoint,
                          QProcess,
                          QLocale,
                          QTranslator,
                          QLibraryInfo)
from PyQt5.QtGui import QPixmap, QIcon

from videomorph.converter.presets import presets_list
from videomorph.converter.ffmpeg import FFMpeg
from videomorph.converter.utils import write_time
from videomorph.converter.tasks import Task, STATUS


class MMWindow(QMainWindow):

    """ Class doc """

    def __init__(self):
        """ Class initializer """
        super(MMWindow, self).__init__()
        self.resize(680, 576)
        self.setWindowTitle(u'VideoMorph' + ' ' + __version__)
        icon = QIcon()
        icon.addPixmap(
            QPixmap("/usr/share/icons/videomorph.png"))
        self.setWindowIcon(icon)
        self.centralwidget = QWidget(self)
        self.vl = QVBoxLayout(self.centralwidget)
        self.hl = QHBoxLayout()
        self.vl1 = QVBoxLayout()
        self.vl2 = QVBoxLayout()

        self.group_settings()
        self.fix_layout()
        self.group_tasks()
        self.group_output()
        self.group_progress()
        self.setup_toolbar()

        self.hl.addLayout(self.vl2)
        self.vl.addLayout(self.hl)
        self.setCentralWidget(self.centralwidget)

        self.setup_actions()

        self.populate_profiles()

        self.medialist = []
        self.tasks = []
        self.stopped = False

        self.proc = QProcess()
        self.proc.setProcessChannelMode(QProcess.MergedChannels)
        self.proc.readyRead.connect(self.read_encoding)
        self.proc.finished.connect(self.finish_encoding)
        self.read_settings()

    def group_settings(self):
        """ Function doc """
        gb_settings = QGroupBox(self.centralwidget)
        gb_settings.setTitle(self.tr(u'Settings'))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            gb_settings.sizePolicy().hasHeightForWidth())
        gb_settings.setSizePolicy(sizePolicy)
        hl = QHBoxLayout(gb_settings)
        vl = QVBoxLayout()
        hl1 = QHBoxLayout()
        label = QLabel(self.tr('Profiles:'))
        hl1.addWidget(label)
        spacerItem = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hl1.addItem(spacerItem)
        vl.addLayout(hl1)
        self.cb_profiles = QComboBox(gb_settings)
        self.cb_profiles.setMinimumSize(QSize(200, 0))
        self.cb_profiles.currentIndexChanged.connect(self.populate_presets)
        vl.addWidget(self.cb_profiles)
        hl2 = QHBoxLayout()
        label = QLabel(self.tr('Presets:'))
        hl2.addWidget(label)
        spacerItem1 = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hl2.addItem(spacerItem1)
        vl.addLayout(hl2)
        self.cb_presets = QComboBox(gb_settings)
        self.cb_presets.setMinimumSize(QSize(200, 0))
        self.cb_presets.currentIndexChanged.connect(self.update_media)
        vl.addWidget(self.cb_presets)
        hl.addLayout(vl)
        self.vl1.addWidget(gb_settings)

    def fix_layout(self):
        """ Function doc """
        spacerItem = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vl1.addItem(spacerItem)
        self.hl.addLayout(self.vl1)

    def group_tasks(self):
        """ Function doc """
        gb_tasks = QGroupBox(self.centralwidget)
        gb_tasks.setTitle(self.tr(u'Tasks'))
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(gb_tasks.sizePolicy().hasHeightForWidth())
        gb_tasks.setSizePolicy(sizePolicy)
        hl = QHBoxLayout(gb_tasks)
        self.tb_tasks = QTableWidget(gb_tasks)
        self.tb_tasks.setColumnCount(4)
        self.tb_tasks.setRowCount(0)
        self.tb_tasks.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tb_tasks.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tb_tasks.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch)
        self.tb_tasks.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tb_tasks.setHorizontalHeaderLabels(
            [self.tr(u'Name'),
             self.tr(u'Duration'),
             self.tr(u'Target'),
             self.tr(u'Progress')])
        hl.addWidget(self.tb_tasks)
        self.vl2.addWidget(gb_tasks)

    def group_output(self):
        """ Function doc """
        gb_output = QGroupBox(self.centralwidget)
        gb_output.setTitle(self.tr(u'Output'))
        vl = QVBoxLayout(gb_output)
        vl1 = QVBoxLayout()
        hl = QHBoxLayout()
        self.le_output = QLineEdit(str(QDir.homePath()))
        self.le_output.setReadOnly(True)
        hl.addWidget(self.le_output)
        self.tb_output = QToolButton(gb_output)
        self.tb_output.setText(u'...')
        self.tb_output.clicked.connect(self.output_folder)
        hl.addWidget(self.tb_output)
        vl1.addLayout(hl)
        vl.addLayout(vl1)
        self.vl2.addWidget(gb_output)

    def group_progress(self):
        """ Function doc """
        gb_progress = QGroupBox(self.centralwidget)
        gb_progress.setTitle(self.tr(u'Progress'))
        vl = QVBoxLayout(gb_progress)
        self.pb_progress = QProgressBar(gb_progress)
        self.pb_progress.setProperty("value", 24)
        vl.addWidget(self.pb_progress)
        self.vl2.addWidget(gb_progress)

    def setup_toolbar(self):
        self.toolBar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolBar)

    def read_settings(self):
        settings = QSettings(
            QDir.homePath() + '/.videomorph/config.ini', QSettings.IniFormat)
        pos = settings.value("pos", QPoint(600, 200), type=QPoint)
        size = settings.value("size", QSize(1096, 510), type=QSize)
        self.resize(size)
        self.move(pos)
        if 'profile' and 'preset' in settings.allKeys():
            prof = settings.value('profile')
            pres = settings.value('preset')
            self.cb_profiles.setCurrentIndex(int(prof))
            self.cb_presets.setCurrentIndex(int(pres))
        if 'output_dir' in settings.allKeys():
            self.le_output.setText(str(settings.value('output_dir')))

    def write_settings(self):
        settings = QSettings(
            QDir.homePath() + '/.videomorph/config.ini', QSettings.IniFormat)
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())
        settings.setValue("profile", self.cb_profiles.currentIndex())
        settings.setValue("preset", self.cb_presets.currentIndex())
        settings.setValue("output_dir", self.le_output.text())

    def closeEvent(self, event):
        self.write_settings()
        event.accept()

    def check_ffmpeg(self):
        """ Function doc """
        try:
            self.ffmpeg = FFMpeg()
            return True
        except Exception as ex:
            msgBox = QMessageBox(QMessageBox.Critical, self.tr(u'Error!'),
                                 self.tr(str(ex)), QMessageBox.NoButton, self)
            msgBox.addButton("&Ok", QMessageBox.AcceptRole)
            if msgBox.exec_() == QMessageBox.AcceptRole:
                qApp.closeAllWindows()
                return False

    def setup_actions(self):
        self.open_action = QAction(
            self.style().standardIcon(QStyle.SP_DialogOpenButton),
            self.tr(u'Open'),
            self,
            shortcut="Ctrl+O",
            enabled=True,
            triggered=self.add_media)
        self.clear_tasks_action = QAction(
            self.style().standardIcon(QStyle.SP_TrashIcon),
            self.tr(u'Clear Tasks'),
            self, shortcut="Ctrl+Del", enabled=True,
            triggered=self.delete_media)
        self.convert_action = QAction(
            self.style().standardIcon(QStyle.SP_MediaPlay),
            self.tr(u'Convert'),
            self, shortcut="Ctrl+P", enabled=True,
            triggered=self.start_encoding
        )
        self.stop_action = QAction(
            self.style().standardIcon(QStyle.SP_MediaStop),
            self.tr(u'Stop'),
            self, shortcut="Ctrl+P", enabled=False,
            triggered=self.stop_encoding)
        self.info_action = QAction(
            self.style().standardIcon(QStyle.SP_MessageBoxInformation),
            self.tr(u'About'),
            self, shortcut="Ctrl+H", enabled=True,
            triggered=self.about)
        self.quit_action = QAction(
            self.style().standardIcon(QStyle.SP_DialogCloseButton),
            self.tr(u'Quit'),
            self, shortcut="Ctrl+Q", enabled=True,
            triggered=self.close)

        self.toolBar.addAction(self.open_action)
        self.toolBar.addAction(self.clear_tasks_action)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.convert_action)
        self.toolBar.addAction(self.stop_action)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.info_action)
        self.toolBar.addAction(self.quit_action)

    def about(self):
        """ Function doc """
        QMessageBox.about(
            self,
            'VideoMorph',
            '<p><b>VideoMorph version {v}</b>'
            '<p><b>VideoMorph</b> is a small GUI wrapper for'
            ' <a href="http://ffmpeg.org/ffmpeg.html">'
            ' ffmpeg</a>.'
            '<p>Website: <a href=http://codeshard.github.io/videomorph>'
            'http://codeshard.github.io/videomorph</a>'
            '<p><b>VideoMorph</b> features a sleek, intuitive, and clean UI,'
            ' with commonly used set of presets, making the video conversion'
            ' task as simple as possible.'
            '<p> <b>Code & Artwork by:</b>'
            ' <a href=mailto:codeshard@openmailbox.org>Ozkar L. Garcell</a>'
            '<p> <b>Contributors:</b><br>'
            '<b>*</b> Maikel Llamaret Heredia (tester, naming suggestion'
            ' and a few insults(mostly of them deserved)).<br>'
            '<b>*</b> Ludwig Causilla (tester, and thanks for'
            ' helping me with your GIMP skills).<br>'.format(
                v=__version__)
        )

    def populate_profiles(self):
        """ Function doc """
        profiles = [
            '---',
            'MP4',
            'DVD',
            'VCD',
            'AVI',
            'FLV',
            'WMV'
        ]
        self.cb_profiles.addItems(profiles)

    def populate_presets(self):
        """ Function doc """
        profile = self.cb_profiles.currentText()
        self.cb_presets.clear()
        for k, j in enumerate(presets_list):
            if profile == str(presets_list[k].profile_name):
                self.cb_presets.addItem(str(presets_list[k].profile_label))

    def output_folder(self):
        """ Function doc """
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(
            self,
            self.tr('Choose output directory'),
            QDir.homePath(),
            options=options)
        if directory:
            self.le_output.setText(directory)

    def add_media(self):
        """ Function doc """
        title = self.tr(u'Select Files')
        vFilter = self.tr(u'Video files') + u'(*.mkv *.ogg *.mp4 *.mpg *.f4v'
        ' *.flv *.wv *.3gp *.avi *.wmv *.mov *.vob'
        ' *.ogv);;' + self.tr(u'All files') + u'(*.*)'
        medias, _ = QFileDialog.getOpenFileNames(
            self,
            title,
            QDir.homePath(),
            vFilter)

        if not medias:
            return

        i = self.tb_tasks.rowCount()

        self.tb_tasks.setRowCount(i + len(medias))
        for m in medias:
            self.info = self.ffmpeg.probe(m)
            item = QTableWidgetItem()
            item.setText(str(m).split('/')[-1])
            self.tb_tasks.setItem(i, 0, item)
            item = QTableWidgetItem()
            item.setText(str(write_time(self.info.format.duration)))
            self.tb_tasks.setItem(i, 1, item)
            item = QTableWidgetItem()
            item.setText(str(self.cb_presets.currentText()))
            self.tb_tasks.setItem(i, 2, item)
            item = QTableWidgetItem()
            item.setText(self.tr(u''))
            self.tb_tasks.setItem(i, 3, item)

            i += 1

            self.medialist.append({'media': m, 'info': self.info})

    def delete_media(self):
        """ Function doc """
        if self.tb_tasks.rowCount() > 0:
            msgBox = QMessageBox(
                QMessageBox.Warning,
                self.tr(u'Warning!'),
                self.tr(u'Clear all tasks?'), QMessageBox.NoButton, self)
            msgBox.addButton("&Clear", QMessageBox.AcceptRole)
            msgBox.addButton("C&ancel", QMessageBox.RejectRole)
            if msgBox.exec_() == QMessageBox.AcceptRole:
                self.tb_tasks.clearContents()
                self.tb_tasks.setRowCount(0)
            else:
                return

    def update_media(self):
        """ Function doc """
        item = self.tb_tasks.currentItem()
        if item is not None:
            self.tb_tasks.item(item.row(), 2).setText(
                str(self.cb_presets.currentText()))

    def read_encoding(self):
        """ Function doc """
        pat = re.compile(r'time=([0-9.:]+) ')
        ret = str(self.proc.readAll())
        tmp = pat.findall(ret)
        if len(tmp) == 1:
            timespec = tmp[0]
            if ':' in timespec:
                timecode = 0
                for part in timespec.split(':'):
                    timecode = 60 * timecode + float(part)
            else:
                timecode = float(tmp[0])
            for i in self.tasks:
                if i.task_status == 'RUNNING':
                    value = int(
                        (100.0 * timecode) /
                        self.medialist[i.number]['info'].format.duration)
                    self.pb_progress.setProperty("value", value)
                    self.tb_tasks.item(i.number, 3).setText(str(value) + " %")
                    self.convert_action.setEnabled(False)
                    self.clear_tasks_action.setEnabled(False)
                    self.stop_action.setEnabled(True)

    def start_encoding(self):
        """ Function doc """
        self.tasks = []
        if self.tb_tasks.rowCount() > 0:
            for k in range(self.tb_tasks.rowCount()):
                preset = self.tb_tasks.item(k, 2).text()
                for i, j in enumerate(presets_list):
                    if preset == str(presets_list[i].profile_label):
                        params = str(presets_list[i].profile_params).rsplit()
                        extension = str(presets_list[i].profile_extension)
                output_file = self.le_output.text() + '/' + \
                    splitext(self.tb_tasks.item(k, 0).text())[0] + extension
                t = Task(
                    k,
                    self.medialist[k]['media'],
                    output_file,
                    STATUS[0],
                    params)
                self.tasks.append(t)
            cmds = ['-i', self.tasks[0].input_file]
            cmds.extend(self.tasks[0].params)
            cmds.extend(['-y', self.tasks[0].output_file])
            self.tasks[0].task_status = 'RUNNING'
            self.proc.start(self.ffmpeg.ffmpeg_path, cmds)
        else:
            msgBox = QMessageBox(
                QMessageBox.Critical,
                self.tr(u'Error!'),
                self.tr(u'No video files added!'),
                QMessageBox.Ok,
                self)
            msgBox.show()

    def stop_encoding(self):
        """ Function doc """
        self.stopped = True
        self.proc.terminate()
        if self.proc.state() == QProcess.Running:
            self.proc.kill()
        msgBox = QMessageBox(
            QMessageBox.Information,
            self.tr(u'Stopped!'),
            self.tr(u'Encoding tasks succesfully stopped!'),
            QMessageBox.Ok,
            self)
        msgBox.show()
        self.convert_action.setEnabled(True)
        self.clear_tasks_action.setEnabled(True)
        self.stop_action.setEnabled(False)

    def finish_encoding(self):
        """ Function doc """
        if not self.stopped:
            self.proc.close()
            for i in self.tasks:
                if i.task_status == 'RUNNING':
                    i.task_status = 'FINISHED'
                if i.task_status == 'QUEUED':
                    cmds = ['-i', i.input_file]
                    cmds.extend(i.params)
                    cmds.extend(['-y', i.output_file])
                    i.task_status = 'RUNNING'
                    self.proc.start(self.ffmpeg.ffmpeg_path, cmds)
            if self.proc.state() == QProcess.NotRunning:
                msgBox = QMessageBox(
                    QMessageBox.Information,
                    self.tr(u'Finished!'),
                    self.tr(u'Encoding tasks succesfully finished!'),
                    QMessageBox.Ok,
                    self)
                msgBox.show()
            self.convert_action.setEnabled(True)
            self.clear_tasks_action.setEnabled(True)
            self.stop_action.setEnabled(False)


def main():
    """ Function doc """
    import sys
    from os.path import dirname, realpath, exists
    app = QApplication(sys.argv)
    filePath = dirname(realpath(__file__))
    locale = QLocale.system().name()
    if locale == 'es_CU':
        locale = 'es_ES'
    appTranslator = QTranslator()
    if exists(filePath + '/translations/'):
        appTranslator.load(filePath + "/translations/videomorph_" + locale)
    else:
        appTranslator.load(
            "/usr/share/videomorph/translations/videomorph_" + locale)
    app.installTranslator(appTranslator)
    qtTranslator = QTranslator()
    qtTranslator.load("qt_" + locale,
                      QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qtTranslator)
    mainWin = MMWindow()
    if mainWin.check_ffmpeg():
        mainWin.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
