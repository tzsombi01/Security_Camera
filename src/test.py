from main import *
import unittest


class Test(unittest.TestCase):

	def test_formatted_date_is_valid(self):
		characterList = [' ', '\\', '/', '|', '"', '?', '<', '>', ':', '.']
		for character in characterList:
			self.assertFalse(character in getDateAndTimeFormatted())

		self.assertFalse(getDateAndTimeFormatted().endswith(' '))
		self.assertFalse(getDateAndTimeFormatted().endswith('~'))

	def test_end_of_recording_time_is_valid(self):
		self.assertTrue(reachedEndOfRecordingTime(time.time() - SECONDS_TO_RECORD_AFTER_DETECTION - 1))
		self.assertTrue(reachedEndOfRecordingTime(time.time() - SECONDS_TO_RECORD_AFTER_DETECTION))
		self.assertFalse(reachedEndOfRecordingTime(time.time() - SECONDS_TO_RECORD_AFTER_DETECTION + 1))

	def test_get_location(self):
		geoLoc = Nominatim(user_agent="_")

		self.assertEqual(["Dallas", "United States", "75202"],
						 getLocationAsList(geoLoc.reverse((32.7831, -96.8067))))
		self.assertEqual(["Frankfurt am Main", "Deutschland", "60313"],
						 getLocationAsList(geoLoc.reverse((50.1155, 8.6842))))
		self.assertEqual(["Győr", "Magyarország", "9021"],
						 getLocationAsList(geoLoc.reverse((47.6833, 17.6351))))

	def test_detectBodiesHOG(self):
		pass

	def test_detectFaces(self):
		pass
