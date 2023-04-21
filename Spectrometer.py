#===========#
#= Imports =#
#===========#
import cv2
import datetime
import PyQt5.QtWidgets as wid
import PyQt5.QtGui as gui
import PyQt5.QtCore as cor
import subprocess

#===========#
#= Objects =#
#===========#
class Camera:
    def openCamera(self):
        """
        Procedure when camera is opened
        """
        self.capture = cv2.VideoCapture(0, cv2.CAP_V4L)
        #Sets the resolution of the camera
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        #Should the camera not open
        if not self.capture.isOpened():
            msgBox = wid.QMessageBox()
            msgBox.setText("Failed to open camera.")
            msgBox.exec()
            return

class GUIWindow(wid.QWidget):
    """
    User Interface (UI) with the Camera
    """
    def __init__(self):
        """
        Creates controls for the UI
        """
        super().__init__()
        
        #Sets up the camera in the GUI
        self.camera = Camera()
        
        #Framerate setup.
        self.timer = cor.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timePerFrame = 40
        
        #Create video widget for video viewing
        self.video = wid.QLabel()
        
        #Buttons to open camera, switch between RGB and HSV views, and take image
        self.openCamera = wid.QPushButton("Open camera")
        self.snapshot = wid.QPushButton("Take Picture")
        
        #Make all but "Open Camera" Button Visible at start up
        self.snapshot.setVisible(False)
        
        #Layout of the GUI
        layout = wid.QGridLayout()
        layout.addWidget(self.openCamera, 0, 0, 4, 4, cor.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.video, 0, 0, 4, 4, cor.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.snapshot, 4, 3, 1, 1)
        self.setLayout(layout)
        
        #Setting the window name and dimensions
        self.setWindowTitle("Spectrometer - Alexander Keays")
        self.setFixedSize(800, 800)
        
        #Connecting buttons to functions
        self.snapshot.clicked.connect(self.saveImage)
        self.openCamera.clicked.connect(self.start)
    
    def saveImage(self):
        """
        Saves an image of the camera's view at max resolution.
        """
        #Stops the video feed to free camera
        self.timer.stop()
        self.camera.capture.release()
        
        #Gathers the date and time to use to name folder and image file
        now = datetime.datetime.now()
        date, time = now.strftime("%d-%b-%Y"), now.strftime("%H-%M-%S")
        
        #Directory to save images
        directory = "~/Pictures/Spectrometer"
        
        #Checks to see if folder for telescope images exists, and if not, creates one
        directoryCheck = f"mkdir -p {directory}"
        subprocess.call(directoryCheck, shell = True)
        
        #Checks to see if folder with date exists, and if not, creates one
        dateCheck = f"mkdir -p {directory}/{date}"
        subprocess.call(dateCheck, shell = True)
        
        #Saves the image as the time.jpeg in the date folder
        callImage = f"raspistill -o {directory}/{date}/{time}.jpeg -n -t 1"
        subprocess.call(callImage, shell = True)
        
        #Restarts the video feed
        self.camera.openCamera()
        self.timer.start(self.timePerFrame)
    
    def start(self):
        """
        Start up sequence of the GUI
        """
        #Switches visibility of buttons
        self.openCamera.setVisible(False)
        self.snapshot.setVisible(True)
        
        #Starts video feed
        self.camera.openCamera()
        self.timer.start(self.timePerFrame)
    
    def nextFrameSlot(self):
        """
        Next frame information.
        """
        #Read the frame
        frame = self.camera.capture.read()[-1]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        #Set frame wanted to be viewed in video feed on GUI.
        image = gui.QImage(frame, frame.shape[1], frame.shape[0], gui.QImage.Format_RGB888)
        pixmap = gui.QPixmap.fromImage(image)
        self.video.setPixmap(pixmap)

#Start the functions for each core of the Raspberry Pi 4B
app = wid.QApplication([])
start_window = GUIWindow()
start_window.show()
app.exit(app.exec())