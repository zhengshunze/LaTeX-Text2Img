# Import necessary libraries
import sys
import clipboard
import matplotlib
import requests
from PIL import Image
from PySide6 import QtCore, QtGui, QtWidgets
import matplotlib.pyplot as plt
import io
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QTimer
from PySide6.QtGui import QTextDocument, QImage, QColor, QPainter, QPixmap, QFont
from PySide6.QtWidgets import QVBoxLayout, QMessageBox, QApplication, QLabel, QWidget, QDialog
from matplotlib import font_manager
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# Set the backend for matplotlib to use QtAgg
matplotlib.use('QtAgg')


# CustomTextEdit class for displaying LaTeX text
class CustomTextEdit(QtWidgets.QTextEdit):
    # Initialize the class
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set text interaction flags and cursor
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.viewport().setCursor(QtCore.Qt.ArrowCursor)
        self.setDisabled(True)

    # Override wheelEvent to do nothing
    def wheelEvent(self, event):
        pass

    # Override focusInEvent to do nothing
    def focusInEvent(self, event):
        pass

    # Override mousePressEvent to handle left mouse button press
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and event.isAccepted():
            return False
        super().mousePressEvent(event)

    # Override mouseMoveEvent to do nothing
    def mouseMoveEvent(self, event):
        pass

    # Override keyPressEvent to handle Ctrl+A
    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_A:
            pass
        else:
            super().keyPressEvent(event)

    # Override contextMenuEvent to do nothing
    def contextMenuEvent(self, event):
        pass


# CustomTextDocument class for displaying LaTeX text
class CustomTextDocument(QTextDocument):
    # Initialize the class
    def __init__(self, parent=None):
        super().__init__(parent)

    # Override mousePressEvent to do nothing
    def mousePressEvent(self, event):
        pass


# MplCanvas class for embedding Matplotlib figures
class MplCanvas(FigureCanvasQTAgg):
    # Initialize the class
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Create a Matplotlib figure and axes
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        # Initialize the FigureCanvas
        super(MplCanvas, self).__init__(fig)


class RoundedCornerWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setContentsMargins(10, 10, 10, 10)

        self.setStyleSheet(
            """
            background-color: rgba(44, 62, 80, 200);
            color: #ecf0f1;
            border-radius: 15px;
            padding: 10px;
            """
        )

        message_label_text = "Welcome to LaTeX Text2Img!\n\n" \
                             "To convert LaTeX expressions into images:\n" \
                             "1. Copy a LaTeX expression to your clipboard.\n" \
                             "2. Press Ctrl+V to paste the expression here.\n" \
                             "3. The expression will be automatically converted into an image."

        message_label = QLabel(message_label_text)
        message_label.setFont(QtGui.QFont("LiHei Pro", 16))
        message_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        message_label.adjustSize()

        layout = QVBoxLayout(self)
        layout.addWidget(message_label)

        self.setGeometry(
            0,
            0,
            # Set the Y position to the bottom of the screen minus the height of the dialog
            self.sizeHint().width(),
            self.sizeHint().height()
        )

    def run(self):
        self.show()


# LaTeXDisplayWindow class for the main application window
class LaTeXDisplayWindow(QtWidgets.QMainWindow):
    # Initialize the class
    def __init__(self):
        super().__init__()

        # Create a CustomTextEdit instance
        self.text_edit = CustomTextEdit(self)

        # Initialize an empty QImage
        self.image = QImage()

        # Initialize the user interface
        self.init_ui()
        self.rounded_message = RoundedCornerWindow(self)
        self.rounded_message.setParent(self)
        self.rounded_message.run()

    # Initialize the user interface
    def init_ui(self):
        # Set window properties
        self.setWindowIcon(QtGui.QIcon('APPICON.png'))
        self.setWindowTitle('LaTeX Text2Img')
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(self.size())
        self.center_window()
        # Create a vertical layout
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)

        # Configure the text_edit widget
        self.text_edit.setMaximumWidth(self.size().width())
        self.text_edit.setMaximumHeight(self.size().height())
        self.text_edit.setReadOnly(True)
        self.text_edit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.text_edit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # Create a central widget and set the layout
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        central_widget.setStyleSheet("background-color:white; border: none;")
        self.setCentralWidget(central_widget)

        # Default LaTeX formula
        default_formula = r"f(x) = \frac{1}{2\pi} \int_{-\infty}^{\infty} F(\omega) e^{i\omega x} d\omega"

        # Initialize and render the default formula
        self.init_render_formula(formula=default_formula)

    def center_window(self):
        self.setGeometry(
            (QApplication.primaryScreen().size().width() - 800) // 2,
            (QApplication.primaryScreen().size().height() - 600) // 2,
            800,
            600
        )

    # Initialize and render a LaTeX formula
    def init_render_formula(self, formula):
        # Generate and display the image of the formula
        img = self.generate_image(formula)
        self.crop_image(img)

    # Generate an image of a LaTeX formula
    def generate_image(self, formula):
        try:
            # Create and save the image using matplotlib
            fig, ax = plt.subplots()
            # Customize font properties and alignment
            font_path = '.\\noto_sans_math.ttf'
            font_prop = font_manager.FontProperties(fname=font_path)
            font_prop.set_family('cursive')
            font_prop.set_variant("normal")
            font_prop.set_weight("bold")
            font_prop.set_size("36")
            font_prop.set_math_fontfamily("stixsans")
            alignment = {'horizontalalignment': 'center', 'verticalalignment': 'baseline'}

            # Add the formula text to the plot
            ax.text(0.5, 0.5, r"${}$".format(formula), ha='center', va='center', fontproperties=font_prop, **alignment)
            ax.axis('off')

            # Save the plot as an image buffer
            buffer = io.BytesIO()
            plt.rcParams['text.usetex'] = True
            plt.savefig(buffer, format='png', dpi=800)
            plt.close(fig)
            buffer.seek(0)

            # Create a QImage from the image buffer
            img = QtGui.QImage.fromData(buffer.getvalue())
            self.crop_image(img)
            return img

        except Exception as err:
            # Handle exception by generating image using online service
            dpi = 600
            encoded_formula = formula.replace(' ', '%20')
            url = f"https://latex.codecogs.com/png.image?\\dpi{{{dpi}}}{encoded_formula}"
            response = requests.get(url, stream=True)
            self.image.loadFromData(response.content)
            dest_background = QImage(self.image.size(), QImage.Format.Format_RGB32)
            dest_background.fill(Qt.GlobalColor.white)
            painter = QPainter(dest_background)
            painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
            painter.drawImage(0, 0, self.image)

            img = Image.open(io.BytesIO(response.content))
            sc = MplCanvas(self, dpi=600)
            self.setCentralWidget(sc)
            sc.axes.axis('off')
            sc.axes.imshow(img)
            sc.draw()
            return dest_background

    # Change the background of an image
    def change_background(self, resource, background_color):
        res_source = QImage(resource)
        dest_background = QImage(res_source.size(), QImage.Format_RGB32)
        dest_background.fill(background_color)

        painter = QPainter(dest_background)
        painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
        painter.drawImage(0, 0, res_source)
        return QPixmap.fromImage(dest_background)

    # Crop and display an image
    def crop_image(self, img):
        new_image_width = self.width()
        scale_factor = new_image_width / img.width()
        new_image_height = int(img.height() * scale_factor)
        img = img.scaled(new_image_width, new_image_height, QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                         QtCore.Qt.TransformationMode.FastTransformation)
        self.display_image(img)

    # Display an image in the text edit widget
    def display_image(self, img):
        text_document = CustomTextDocument()
        text_cursor = QtGui.QTextCursor(text_document)
        text_cursor.insertImage(img)
        self.text_edit.setDocument(text_document)
        self.text_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)

    # Prompt the user to save an image
    def prompt_to_save(self, img):
        response = QtWidgets.QMessageBox.question(self, 'Save Image', 'Do you want to save the rendered image?',
                                                  QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if response == QtWidgets.QMessageBox.Yes:
            file_dialog = QtWidgets.QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, 'Save Image', '', 'PNG Images (*.png)')
            if file_path:
                pixmap = QtGui.QPixmap.fromImage(img)
                pil_image = Image.fromqpixmap(pixmap)
                pil_image.save(file_path, quality=100)
        else:
            return

    # Save an image response
    def save_response_image(self, image_pixmap):
        res = QtWidgets.QMessageBox.question(self, 'Save Image', 'Do you want to save the rendered image?',
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if res == QtWidgets.QMessageBox.Yes:
            file_dialog = QtWidgets.QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, 'Save Image', '', 'PNG Images (*.png)')
            if file_path:
                image_pixmap.save(file_path, 'PNG')
        else:
            return

    # Handle key press events
    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_V:
            # Handle Ctrl+V event (paste)
            clipboard_text = clipboard.paste()
            if clipboard_text:
                try:
                    img = self.generate_image(clipboard_text)
                    self.prompt_to_save(img)
                except Exception as err:
                    QMessageBox.information(self, "Error", "Internet No Connection.")
        else:
            super().keyPressEvent(event)


# Main entry point
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = LaTeXDisplayWindow()
    window.show()
    sys.exit(app.exec())
