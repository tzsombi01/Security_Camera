import cv2
from datetime import datetime
import time

COLORS = {"RED" : [0, 0, 255], "BLACK": [0, 0, 0], "BLUE": [255, 0, 0]}
LINE_THICKNESS = 5
FRAME_RATE = 20
SECONDS_TO_RECORD_AFTER_DETECTION = 10

face_cascade = cv2.CascadeClassifier(cv2.samples.findFile(
	"C:/Users/torek/PycharmProjects/Security_Camera/venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml"))


def main():
	cap = cv2.VideoCapture(0)
	frame_size = (int(cap.get(3)), int(cap.get(4)))
	fourCC = cv2.VideoWriter_fourcc(*'mp4v')
	detection_stopped_time = None
	timer_started = False
	detecting = False
	running = True
	while running:
		_, frame = cap.read()
		number_of_faces = detectFaces(frame)
		if  number_of_faces > 0: #  or detectBodiesHOG(frame) > 0
			if detecting:
				timer_started = False
			else:
				detecting = True
				output = cv2.VideoWriter(f'Recordings/{getDateAndTimeFormatted()}.mp4', fourCC, FRAME_RATE, frame_size)
				print(f"Started Recording at time: {time.time()}")
		elif detecting:
			if timer_started:
				if reachedEndOfRecordingTime(detection_stopped_time):
					detecting = False
					timer_started = False
					output.release()
					print(f"Stopped Recording at time: {time.time()}")
			else:
				timer_started = True
				detection_stopped_time = time.time()
		if detecting:
			output.write(frame)

		cv2.imshow("Security Camera", frame)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			running = False
	try:
		output.release()
	except:
		pass
	cap.release()
	cv2.destroyAllWindows()


def detectBodiesHOG(frame):
	hog = cv2.HOGDescriptor()
	hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

	bodies = hog.detectMultiScale(frame, winStride=(5, 5), padding=(3, 3), scale=1.3)

	# for (body_top_left_x, body_top_left_y, width, height) in bodies:
	# 	cv2.rectangle(frame, (body_top_left_x, body_top_left_y), (body_top_left_x + width, body_top_left_y + height),
	# 				  COLORS["BLUE"], LINE_THICKNESS)
	return len(bodies)


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
	scale_factor, overlap = 1.3, 6
	faces = face_cascade.detectMultiScale(grayscale_img, scale_factor, overlap)

	# for (face_top_left_x, face_top_left_y, width, height) in faces:
	# 	cv2.rectangle(frame, (face_top_left_x, face_top_left_y), (face_top_left_x + width, face_top_left_y + height),
	# 				  COLORS["RED"], LINE_THICKNESS)
	return len(faces)


def getDateAndTimeFormatted():
	return datetime.now().strftime("%Y%m%d-%H%M%S")


def reachedEndOfRecordingTime(detection_stopped_time):
	return time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION


if __name__ == "__main__":
	main()
