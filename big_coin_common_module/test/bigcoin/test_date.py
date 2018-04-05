
import unittest
import bigcoin.date as bcdate
import datetime

class TestDate(unittest.TestCase):

    def test_is_date_format_yyyy_mm_dd_valid(self):
		self.assertTrue(bcdate.is_date_format_yyyy_mm_dd_valid("2011-05-22"))
		self.assertFalse(bcdate.is_date_format_yyyy_mm_dd_valid("2011.05.22"))
		self.assertFalse(bcdate.is_date_format_yyyy_mm_dd_valid("2011_05_22"))
		self.assertFalse(bcdate.is_date_format_yyyy_mm_dd_valid("11-05-22"))
		self.assertFalse(bcdate.is_date_format_yyyy_mm_dd_valid("2011-5-22"))
		self.assertFalse(bcdate.is_date_format_yyyy_mm_dd_valid("2011-05-2"))
		self.assertFalse(bcdate.is_date_format_yyyy_mm_dd_valid("201-05-2"))
		self.assertFalse(bcdate.is_date_format_yyyy_mm_dd_valid(""))
		self.assertFalse(bcdate.is_date_format_yyyy_mm_dd_valid(54))

    def test_get_date_string_yyyy_mm_dd_from_datetime(self):
        today_string = datetime.datetime.today().strftime("%Y-%m-%d")
        self.assertEquals(bcdate.get_date_string_yyyy_mm_dd_from_datetime(datetime.datetime(2018,2,18)),"2018-02-18")
        self.assertEquals(bcdate.get_date_string_yyyy_mm_dd_from_datetime(None),today_string)

    def test_get_datetime_from_string(self):
        today_string = datetime.datetime.today().strftime("%Y-%m-%d")
        self.assertEquals(bcdate.get_datetime_from_string("2018-02-18"),datetime.datetime(2018,2,18))
        self.assertEquals(bcdate.get_datetime_from_string('invalid'),None)


    def test_increment_a_day_from_date_as_string(self):
        #test normal date
        self.assertEquals(bcdate.increment_a_day_from_date_as_string("2018-02-18"),"2018-02-19")
        #test increment month if last day of month
        self.assertEquals(bcdate.increment_a_day_from_date_as_string("2018-03-31"),"2018-04-01")
        #test increment year if last day of year
        self.assertEquals(bcdate.increment_a_day_from_date_as_string("2017-12-31"),"2018-01-01")
        #test invalid format date
        self.assertEquals(bcdate.increment_a_day_from_date_as_string("18-2-19"),None)
        self.assertEquals(bcdate.increment_a_day_from_date_as_string("not even a date"),None)

if __name__ == "__main__":
    unittest.main()
