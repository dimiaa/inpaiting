# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import telea
import functions

from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QFileDialog
)
from PySide2.QtCore import (
    QFile,
    QDir
)
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import (
    QPixmap,
    QPainter,
    QColor,
    QImage,
    QCursor
)


class Widget(QWidget):
    def __init__(self):
        super(Widget, self).__init__()

        self.load_ui()

        self.browseButton = self.findChild(QPushButton, "browseButton")
        self.browseButton.clicked.connect(self.openImage)

        self.recoveryButton = self.findChild(QPushButton, "recoveryButton")
        self.recoveryButton.clicked.connect(self.interactionWithMethod)

        self.saveButton = self.findChild(QPushButton, "saveButton")
        self.saveButton.clicked.connect(self.saveImage)

        self.imageWidget = self.findChild(QLabel, "imageWidget")

        self.transparent = QLabel(parent=self.imageWidget)

        self.outputWidget = self.findChild(QLabel, "outputWidget")

        self.last_x, self.last_y = None, None

        self.show()

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()

    def openImage(self):
        self.imageWidget.clear()
        self.transparent.clear()

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Open image',
            QDir.currentPath(),
            'Image files (*.jpg *.png *.jpeg)'
        )

        if file_path:
            self.image = QImage(file_path)
            self.pixmapImage = QPixmap.fromImage(self.image)
            self.imageWidget.resize(self.image.width(), self.image.height())
            self.imageWidget.setPixmap(self.pixmapImage)

        self.transparent.resize(self.pixmapImage.size())
        self.outputWidget.resize(self.pixmapImage.size())
        self.pixmapMask = QPixmap(self.pixmapImage.size())
        self.pixmapMask.fill(QColor(0, 0, 0, 0))
        self.transparent.setPixmap(self.pixmapMask)

    def saveImage(self):

        file_path = QFileDialog.getSaveFileName(
            self,
            'Save image',
            QDir.currentPath(),
            'Image files (*.jpg *.png *.jpeg)'
        )
        print(file_path)
        ok = self.outputImage.save(file_path)

        if not ok:
            raise ValueError("Image not saved")

    def interactionWithMethod(self):

        tmp = self.imageWidget.pixmap().toImage()

        img = functions.toArray(tmp)
#        print("Before", self.imageWidget.pixmap().toImage())

        tmp = self.transparent.pixmap().toImage()

        for x in range(tmp.width()):
            for y in range(tmp.height()):
                if tmp.pixel(x, y) == QColor(255, 255, 255, 255):
                    continue
                tmp.setPixel(x, y, QColor(0, 0, 0, 255).rgb())

        tmp_mask = functions.toArray(tmp)
        print(tmp_mask)
        mask = tmp_mask[:, :, 0].astype(bool, copy=False)

        telea.inpaint(img, mask, 15)
        self.outputImage = functions.toQImage(img)

        outputPixmap = QPixmap.fromImage(self.outputImage)
        self.outputWidget.setPixmap(outputPixmap)

    def mouseMoveEvent(self, event):

        image = self.transparent.pixmap().toImage()

        qp = self.imageWidget.mapFromGlobal(QCursor.pos())

        if self.last_x is None:
            self.last_x, self.last_y = qp.x(), qp.y()
            return

        painter = QPainter()
        painter.begin(image)
        color = QColor(255, 255, 255, 255).rgb()

        painter.setPen(color)

#        if (self.last_y < 0 or self.last_y >= self.transparent.height()
#            or self.last_x < 0 or self.last_x >= self.transparent.width()):

        image.setPixel(self.last_x, self.last_y, color)

        painter.drawLine(self.last_x, self.last_y, qp.x(), qp.y())

        painter.end()

        self.update()

        self.transparent.setPixmap(QPixmap.fromImage(image))

        # Update the origin for next time.
        self.last_x = qp.x()
        self.last_y = qp.y()

    def mouseReleaseEvent(self, event):
        self.last_x = None
        self.last_y = None


if __name__ == "__main__":
    app = QApplication([])
    widget = Widget()
    widget.show()
    sys.exit(app.exec_())
