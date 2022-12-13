import unittest
import os
from main import *


class TestDetectFaces(unittest.TestCase):
	@unittest.expectedFailure
	def testDetectFaces(self):
		for name in os.listdir("TestImages"):
			numberOfFaces = int(name.split("_")[1])
			self.assertEqual(numberOfFaces,
								len(detectFaces(cv2.imread(f"Testimages/{name}", -1))))


class TestDateFormat(unittest.TestCase):
	def setUp(self):
		self.illegalCharacters = [' ', '\\', '/', '|', '"', '?',
								  '%', '!', '$', '&', '<', '>',
								  '@', '˙', ':', '.', '+']

	def test_formatted_date_is_valid(self):
		for character in self.illegalCharacters:
			self.assertFalse(character in getDateAndTimeFormatted())


class TestValidRecordingTime(unittest.TestCase):
	def test_end_of_recording_time_is_valid(self):
		self.assertTrue(reachedEndOfRecordingTime(time.time() - SECONDS_TO_RECORD_AFTER_DETECTION - 1))
		self.assertTrue(reachedEndOfRecordingTime(time.time() - SECONDS_TO_RECORD_AFTER_DETECTION))
		self.assertFalse(reachedEndOfRecordingTime(time.time() - SECONDS_TO_RECORD_AFTER_DETECTION + 1))
