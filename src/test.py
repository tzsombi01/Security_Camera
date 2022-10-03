from main import *
import unittest


class Test(unittest.TestCase):
	def setUp(self):
		self.illegalCharacters = [' ', '\\', '/', '|', '"', '?',
								  '%', '!', '$', '&', '<', '>',
								  '@', '˙', ':', '.', '-', '_', '+']
		self.testImage1 = cv2.imread("TestImages/testImage1.jpg", -1)
		self.testImage2 = cv2.imread("TestImages/testImage2.jpg", -1)
		self.testImage3 = cv2.imread("TestImages/testImage3.jpg", -1)
		self.testImage4 = cv2.imread("TestImages/testImage4.jpg", -1)

	def test_formatted_date_is_valid(self):
		for character in self.illegalCharacters:
			self.assertFalse(character in getDateAndTimeFormatted())

	def test_end_of_recording_time_is_valid(self):
		self.assertTrue(reachedEndOfRecordingTime(time.time() - SECONDS_TO_RECORD_AFTER_DETECTION - 1))
		self.assertTrue(reachedEndOfRecordingTime(time.time() - SECONDS_TO_RECORD_AFTER_DETECTION))
		self.assertFalse(reachedEndOfRecordingTime(time.time() - SECONDS_TO_RECORD_AFTER_DETECTION + 1))

	def test_detectBodiesHOG(self):
		self.assertEqual(0, detectBodiesHOG(self.testImage1))
		self.assertEqual(2, detectBodiesHOG(self.testImage2))
		self.assertEqual(0, detectBodiesHOG(self.testImage3)) # Failure's reason is unknown
		self.assertEqual(3, detectBodiesHOG(self.testImage4))

	def test_detectFaces(self):
		self.assertEqual(1, detectFaces(self.testImage1))
		self.assertEqual(0, detectFaces(self.testImage2))
		self.assertEqual(15, detectFaces(self.testImage3))
		self.assertEqual(3, detectFaces(self.testImage4)) # Will Fail Most Likely -> 1 Face is sideways
