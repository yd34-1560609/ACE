import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QDialog
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPainterPath

class ZoomWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zoomed Section")
        self.setGeometry(100, 100, 400, 400)

        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)

        self.vLayout = QVBoxLayout(self)
        self.vLayout.addWidget(self.imageLabel)

        self.image = None

    def setZoomedImage(self, image):
        self.image = image
        self.displayZoomedImage()

    def displayZoomedImage(self):
        if self.image is None:
            return

        height, width, channel = self.image.shape
        bytesPerLine = 3 * width
        qImg = QImage(self.image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.imageLabel.setPixmap(QPixmap.fromImage(qImg))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Color Curve Extractor")
        self.setGeometry(100, 100, 1000, 600)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.originalLabel = QLabel(self)
        self.originalLabel.setAlignment(Qt.AlignCenter)
        self.originalLabel.setMouseTracking(True)
        self.originalLabel.mouseMoveEvent = self.mouseMoveEvent

        self.zoomWindow = ZoomWindow(self)

        self.vLayout = QVBoxLayout(self.centralWidget)
        self.vLayout.addWidget(self.originalLabel)

        self.setupControls()

        self.image = None
        self.curves = []

    def setupControls(self):
        controlWidget = QWidget()
        controlLayout = QHBoxLayout(controlWidget)

        self.loadButton = QPushButton('Load Image')
        self.loadButton.clicked.connect(self.loadImage)
        controlLayout.addWidget(self.loadButton)

        self.vLayout.addWidget(controlWidget)

    def loadImage(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if fileName:
            self.image = cv2.imread(fileName)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)  # Convert to RGB for displaying with PyQt

            # Display original image
            self.displayOriginalImage()

            # Clear previous result
            self.curves = []

    def displayOriginalImage(self):
        height, width, channel = self.image.shape
        bytesPerLine = 3 * width
        qImg = QImage(self.image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.originalLabel.setPixmap(QPixmap.fromImage(qImg))
        self.originalLabel.setFixedSize(width, height)  # Set fixed size to align with image size

    def mouseMoveEvent(self, event):
        if self.image is None:
            return

        # Get mouse position
        pos = event.pos()
        x = pos.x()
        y = pos.y()

        # Calculate zoom window position
        zoom_width = 200
        zoom_height = 200
        zoom_x = min(max(x - zoom_width // 2, 0), self.image.shape[1] - zoom_width)
        zoom_y = min(max(y - zoom_height // 2, 0), self.image.shape[0] - zoom_height)

        # Crop zoomed section from original image
        zoomed_image = self.image[zoom_y:zoom_y + zoom_height, zoom_x:zoom_x + zoom_width].copy()

        # Resize for display
        zoomed_image = cv2.resize(zoomed_image, (zoom_width * 2, zoom_height * 2))

        # Show zoomed section in zoom window
        self.zoomWindow.setZoomedImage(zoomed_image)
        self.zoomWindow.move(self.mapToGlobal(QPoint(self.originalLabel.frameGeometry().width() + 20, 0)))
        self.zoomWindow.show()

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
