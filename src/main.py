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

# TODO argparse
face_cascade = cv2.CascadeClassifier(cv2.samples.findFile(
	"C:/Users/torek/PycharmProjects/Security_Camera/venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml"))


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
		#number_of_bodies = detectBodiesHOG(frame)
		if number_of_faces > 0: #  or number_of_bodies > 0
			if detecting:
				timer_started = False
			else:
				detecting = True
				activation_time = getDateAndTimeFormatted()
				output = cv2.VideoWriter(f"Recordings/{activation_time}.mp4",
										 cv2.VideoWriter_fourcc(*"mp4v"), frame_rate, frame_size)
				print("Started Recording")
				# sendAnAlertEmail(activation_time, locationOfCamera)
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


def detectBodiesHOG(image):
	hog = cv2.HOGDescriptor()
	hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
	bodies, _ = hog.detectMultiScale(image, winStride=(10, 10), padding=(20, 20), scale=1.075)
	return len(bodies)


def detectFaces(image):
	grayscale_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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
	try:
		with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
			server.login(sender_email, password)
			server.sendmail(sender_email, target_email, emailToSend.as_string())
			print(f"Email has been sent to {target_email}")
	except PermissionError:
		print("The email address / password is incorrect.")
	except smtplib.SMTPException as error:
		print(f"Error while establishing the connection {error}")



def getLocationOfCamera():
	ip_address = geocoder.ip("me")
	if isinstance(ip_address, type(None)):
		userLocationCoordinates = (ip_address.latlng[0], ip_address.latlng[1])
		geoLoc = Nominatim(user_agent="_")
		try:
			locationOfUser = geoLoc.reverse(userLocationCoordinates)
		except Exception as error:
			print(error)
			return "Unknown Location"
		return ", ".join(getLocationAsList(locationOfUser))
	else:
		return "No internet connection"


def getLocationAsList(location):
	return [location.raw["address"]["city"],
			location.raw["address"]["country"],
			location.raw["address"]["postcode"]]


if __name__ == "__main__":
	main()
