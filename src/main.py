import cv2

COLORS = {"RED" : [0, 0, 255], "BLACK": [0, 0, 0]}
LINE_THICKNESS = 5
FRAMERATE = 20

face_cascade = cv2.CascadeClassifier(cv2.samples.findFile(
	"C:/Users/torek/PycharmProjects/Security_Camera/venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml"))
body_cascade = cv2.CascadeClassifier(cv2.samples.findFile(
	"C:/Users/torek/PycharmProjects/Security_Camera/venv/Lib/site-packages/cv2/data/haarcascade_fullbody.xml"))


"""
Syntax: cv.VideoWriter(filename, fourcc, fps, frameSize)

Parameters:

filename: Input video file
fourcc: 4-character code of codec used to compress the frames
fps: framerate of videostream
framesize: Height and width of frame
"""


def recordVideo():
	output = cv2.VideoWriter('filename.avi', cv2.VideoWriter_fourcc(*'MJPG'), 10, size)


def detectBodies(frame):
	grayscale_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	scale_factor, overlap = 1.3, 2
	bodies = body_cascade.detectMultiScale(grayscale_img, scale_factor, overlap)

	for (body_top_left_x, body_top_left_y, width, height) in bodies:
		cv2.rectangle(frame, (body_top_left_x, body_top_left_y), (body_top_left_x + width, body_top_left_y + height),
					  COLORS["RED"], LINE_THICKNESS)


def detectFaces(frame):
	"""
	Scale factor: Parameter specifying how much the image size is reduced at each image scale
	Recomm: 1.1 -> 1.5
	The lower, the more accurate it is
	From 1 to 2
	Last Param: How many overlapping "face" do we need, in order to recognize it as a face
	Recomm: 3-6, The lower, the more object gets detected as a face
	"""
	grayscale_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	scale_factor, overlap = 1.4, 6
	faces = face_cascade.detectMultiScale(grayscale_img, scale_factor, overlap)

	for (face_top_left_x, face_top_left_y, width, height) in faces:
		cv2.rectangle(frame, (face_top_left_x, face_top_left_y), (face_top_left_x + width, face_top_left_y + height),
					  COLORS["RED"], LINE_THICKNESS)


cap = cv2.VideoCapture(0)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
size = (frame_width, frame_height)
record = True
while record:
	_, frame = cap.read()

	# recordVideo()
	detectFaces(frame)
	detectBodies(frame)

	cv2.imshow("Security Camera", frame)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		record = False

cap.release()
cv2.destroyAllWindows()
