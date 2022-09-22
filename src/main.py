import cv2
from datetime import datetime
import time
from email.message import EmailMessage
import smtplib
import ssl
import geocoder
from geopy.geocoders import Nominatim

sender_email = ""
password = ""
EMAIL_SENDER_ID = ""
target_email = ""
EMAIL_HEADER = "Security Alert"
EMAIL_SUBJECT = "Security Camera Activated"
EMAIL_MESSAGE_TIME_SUBSTRING = "The Security Camera Activated at time: "
EMAIL_MESSAGE_LOCATION_SUBSTRING = "The Security Camera Activated at location: "

SECONDS_TO_RECORD_AFTER_DETECTION = 20

face_cascade = cv2.CascadeClassifier(cv2.samples.findFile(
	"C:/Users/torek/PycharmProjects/Security_Camera/venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml"))
body_cascade = cv2.CascadeClassifier(cv2.samples.findFile(
	"C:/Users/torek/PycharmProjects/Security_Camera/venv/Lib/site-packages/cv2/data/haarcascade_fullbody.xml"))


def main():
	camera = cv2.VideoCapture(0)
	cameraWidthIndex, cameraHeightIndex, cameraFpsIndex = (3, 4, 5)
	frame_size = (int(camera.get(cameraWidthIndex)), int(camera.get(cameraHeightIndex)))
	frame_rate = int(camera.get(cameraFpsIndex))

	locationOfCamera = getLocationOfCamera()
	detection_stopped_time, timer_started, detecting = None, False, False

	running = True
	while running:
		_, frame = camera.read()
		number_of_faces = detectFaces(frame)
		number_of_bodies = detectBodiesHOG(frame)
		# number_of_bodies = detectBodiesCascade(frame)
		if number_of_faces > 0 or number_of_bodies > 0:
			if detecting:
				timer_started = False
			else:
				detecting = True
				activation_time = getDateAndTimeFormatted()
				output = cv2.VideoWriter(f"Recordings/{activation_time}.mp4",
										 cv2.VideoWriter_fourcc(*"mp4v"), frame_rate, frame_size)
				print("Started Recording")
				sendAnAlertEmail(activation_time, locationOfCamera)
		elif detecting:
			if timer_started:
				if reachedEndOfRecordingTime(detection_stopped_time):
					detecting = False
					timer_started = False
					output.release()
					print("Stopped Recording")
			else:
				timer_started = True
				detection_stopped_time = time.time()
		if detecting:
			output.write(frame)

		cv2.imshow("Security Camera", frame)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			running = False

	camera.release()
	cv2.destroyAllWindows()


def detectBodiesHOG(frame):
	hog = cv2.HOGDescriptor()
	hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
	bodies, _ = hog.detectMultiScale(frame, winStride=(10, 10), padding=(20, 20), scale=1.09)
	for (body_top_left_x, body_top_left_y, width, height) in bodies:
		cv2.rectangle(frame, (body_top_left_x, body_top_left_y),
					  (body_top_left_x + width, body_top_left_y + height), [255, 0, 0], 10)
	return len(bodies)


def detectBodiesCascade(frame):
	grayscale_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	scale_factor, overlap = 1.3, 4
	bodies = body_cascade.detectMultiScale(grayscale_img, scale_factor, overlap)
	return len(bodies)


def detectFaces(frame):
	grayscale_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	scale_factor, overlap = 1.3, 6
	faces = face_cascade.detectMultiScale(grayscale_img, scale_factor, overlap)
	return len(faces)


def getDateAndTimeFormatted():
	return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def reachedEndOfRecordingTime(detection_stopped_time):
	return time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION


def sendAnAlertEmail(timeOfActivation, location):
	emailToSend = EmailMessage()
	emailToSend["From"] = EMAIL_SENDER_ID
	emailToSend["To"] = target_email
	emailToSend["Header"] = EMAIL_HEADER
	emailToSend["Subject"] = EMAIL_SUBJECT
	emailMessage = EMAIL_MESSAGE_TIME_SUBSTRING + timeOfActivation + '\n' \
				 + EMAIL_MESSAGE_LOCATION_SUBSTRING + location
	emailToSend.set_content(emailMessage)

	SMTP_SERVER = "smtp.gmail.com"
	SMTP_PORT = 465
	print("Sending Email")
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
		server.login(sender_email, password)
		server.sendmail(sender_email, target_email, emailToSend.as_string())
		print(f"Email has been sent to {target_email}")


def getLocationOfCamera():
	ip = geocoder.ip("me")
	userLocationCoordinates = (ip.latlng[0], ip.latlng[1]) #
	"""
	Test(s):
	(32.7831, -96.8067) -> Dallas, United States, 75202, 
	(50.1155, 8.6842) -> Frankfurt am Main, Deutschland, 60313,
	(47.6833, 17.6351) -> Győr, Magyarország, 9021
	"""
	geoLoc = Nominatim(user_agent="_")
	locationOfUser = geoLoc.reverse(userLocationCoordinates)
	locationAsList = [locationOfUser.raw["address"]["city"],
					  locationOfUser.raw["address"]["country"],
					  locationOfUser.raw["address"]["postcode"]]
	return ", ".join(locationAsList)


if __name__ == "__main__":
	main()
