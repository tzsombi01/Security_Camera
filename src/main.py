import cv2
from datetime import datetime
import time
from email.message import EmailMessage
import smtplib
import ssl

sender_email = ""
password = ""
EMAIL_SENDER_ID = ""
target_email = ""
EMAIL_HEADER = "Security Alert"
EMAIL_SUBJECT = "Security Camera Activated"
EMAIL_MESSAGE = "The Security Camera Activated at time: "

FRAME_RATE = 20
SECONDS_TO_RECORD_AFTER_DETECTION = 20

face_cascade = cv2.CascadeClassifier(cv2.samples.findFile(
	"C:/Users/torek/PycharmProjects/Security_Camera/venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml"))


def main():
	cap = cv2.VideoCapture(0)
	frame_size = (int(cap.get(3)), int(cap.get(4)))
	fourCC = cv2.VideoWriter_fourcc(*'mp4v')
	detection_stopped_time, timer_started, detecting = (None, False, False)
	running = True
	while running:
		_, frame = cap.read()
		number_of_faces = detectFaces(frame)
		# number_of_bodies = detectBodiesHOG(frame)
		if number_of_faces > 0:
			if detecting:
				timer_started = False
			else:
				detecting = True
				activation_time = getDateAndTimeFormatted()
				output = cv2.VideoWriter(f'Recordings/{activation_time}.mp4', fourCC, FRAME_RATE, frame_size)
				print(f"Started Recording")
				sendAnAlertEmail(activation_time)
		elif detecting:
			if timer_started:
				if reachedEndOfRecordingTime(detection_stopped_time):
					detecting = False
					timer_started = False
					output.release()
					print(f"Stopped Recording")
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

	bodies, _ = hog.detectMultiScale(frame, winStride=(5, 5), padding=(3, 3), scale=1.3)

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

	return len(faces)


def getDateAndTimeFormatted():
	return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def reachedEndOfRecordingTime(detection_stopped_time):
	return (time.time() - detection_stopped_time) >= SECONDS_TO_RECORD_AFTER_DETECTION


def sendAnAlertEmail(timeOfActivation):
	emailToSend = EmailMessage()
	emailToSend["From"] = EMAIL_SENDER_ID
	emailToSend["Header"] = EMAIL_HEADER
	emailToSend["Subject"] = EMAIL_SUBJECT
	emailToSend.set_content(EMAIL_MESSAGE + timeOfActivation)

	SMTP_SERVER = "smtp.gmail.com"
	SMTP_PORT = 465
	print("Sending Email")
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
		server.login(sender_email, password)
		server.sendmail(sender_email, target_email, emailToSend.as_string())
		print(f"Email has been sent to {target_email}")


if __name__ == "__main__":
	main()
