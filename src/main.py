import cv2

COLORS = {"RED" : [0, 0, 255]}
LINE_THICKNESS = 5

face_cascade = cv2.CascadeClassifier(cv2.samples.findFile(
	"C:/Users/torek/PycharmProjects/Security_Camera/venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml"))
body_cascade = cv2.CascadeClassifier(cv2.samples.findFile(
	"C:/Users/torek/PycharmProjects/Security_Camera/venv/Lib/site-packages/cv2/data/haarcascade_fullbody.xml"))


def detectBodies(frame):
	"""
	Scale factor: Parameter specifying how much the image size is reduced at each image scale
	Recomm: 1.1 -> 1.5
	The lower, the more accurate it is
	From 1 to 2
	Last Param: How many overlapping "face" do we need, in order to recognize it as a face
	Recomm: 3-6, The lower, the more object gets detected as a face
	"""
	grayscale_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	scale_factor, overlap = 1.3, 5
	faces = face_cascade.detectMultiScale(grayscale_img, scale_factor, overlap)

	for (face_top_left_x, face_top_left_y, width, height) in faces:
		cv2.rectangle(frame, (face_top_left_x, face_top_left_y), (face_top_left_x + width, face_top_left_y + height),
					  COLORS["RED"], LINE_THICKNESS)


cap = cv2.VideoCapture(0)
record = True
while record:
	_, frame = cap.read()

	detectBodies(frame)

	cv2.imshow("Security Camera", frame)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		record = False

cap.release()
cv2.destroyAllWindows()
