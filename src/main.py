import cv2
import argparse
import time
import math
from datetime import datetime
from extraFeatures.send_email import sendAnAlertEmail

SECONDS_TO_RECORD_AFTER_DETECTION = 20
LINE_THICKNESS = 5
COLORS = {"BLUE": [255, 0 , 0],
		  "GREEN": [0, 255, 0]}

parser = argparse.ArgumentParser(description="Cascade classifier path")
parser.add_argument("--face_cascade", type=str, help="full path to frontalface_default.xml")
args = parser.parse_args()

face_cascade = cv2.CascadeClassifier(cv2.samples.findFile(args.face_cascade))


def main():
	camera = cv2.VideoCapture(0)
	cameraWidthIndex, cameraHeightIndex, cameraFpsIndex = (3, 4, 5)
	frame_size = (int(camera.get(cameraWidthIndex)), int(camera.get(cameraHeightIndex)))
	frame_rate = int(camera.get(cameraFpsIndex))

	detection_stopped_time, timer_started, detecting = None, False, False
	tracking_objects = {}
	track_id = 0

	running = True
	while running:
		_, frame = camera.read()

		detected_faces_centers = detectFaces(frame)
		detected_faces_centers, tracking_objects, track_id = \
			calculateIds(detected_faces_centers, tracking_objects, track_id)

		for object_id, center_point in tracking_objects.items():
			cv2.putText(frame, str(object_id), center_point, 0, 1, COLORS["BLUE"], 2)

		number_of_faces = len(detected_faces_centers)
		if number_of_faces > 0:
			if detecting:
				timer_started = False
			else:
				detecting = True
				activation_time = getDateAndTimeFormatted()
				output = cv2.VideoWriter(f"Recordings/{activation_time}.mp4",
										 cv2.VideoWriter_fourcc(*"mp4v"), frame_rate, frame_size)
				print("Started Recording")
				# sendAnAlertEmail(activation_time)
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


def detectFaces(image):
	grayscale_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	scale_factor, overlap = 1.3, 6
	faces = face_cascade.detectMultiScale(grayscale_img, scale_factor, overlap)
	center_coordinates = []

	for (face_top_left_x, face_top_left_y, width, height) in faces:
		cv2.rectangle(image, (face_top_left_x, face_top_left_y), (face_top_left_x + width, face_top_left_y + height),
					  COLORS["BLUE"], LINE_THICKNESS)
		center_x = int((face_top_left_x + face_top_left_x + width) / 2)
		center_y = int((face_top_left_y + face_top_left_y + height) / 2)
		center_coordinates.append((center_x, center_y))

	return center_coordinates


def calculateIds(detected_faces_centers, tracking_objects, track_id):
	diff_threshold = 30

	tracking_objects_copy = tracking_objects.copy()
	detected_faces_centers_copy = detected_faces_centers.copy()
	for object_id, center_old in tracking_objects_copy.items():
		object_visible = False
		for center_new in detected_faces_centers_copy:
			distance = math.hypot(center_old[0] - center_new[0], center_old[1] - center_new[1])

			if distance < diff_threshold:
				tracking_objects[object_id] = center_new
				object_visible = True
				if center_new in detected_faces_centers:
					detected_faces_centers.remove(center_new)
				continue

		if not object_visible:
			tracking_objects.pop(object_id)

	for center_point in detected_faces_centers:
		tracking_objects[track_id] = center_point
		track_id += 1

	return detected_faces_centers, tracking_objects, track_id


def getDateAndTimeFormatted():
	return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def reachedEndOfRecordingTime(detection_stopped_time):
	return time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION


if __name__ == "__main__":
	main()
