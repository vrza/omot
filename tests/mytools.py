'''
Created on Apr 29, 2012

@author: random
'''
import unittest
from omot.mytools import infer_covers_dir, starts_with_recording_year

class MyToolsTestCase(unittest.TestCase):


    def test_infer_covers_dir(self):
        
        self.assertEqual(infer_covers_dir('bla.flac'),
                                          '')
        
        self.assertEqual(infer_covers_dir('bla/truc/truc.flac'),
                                          'bla/truc')

        self.assertEqual(infer_covers_dir('Artists/d/Donald Byrd/1960 - At the Half Note Cafe - 2CD/CD1/105 - Cecile.flac'),
                                          'Artists/d/Donald Byrd/1960 - At the Half Note Cafe - 2CD')
        
        self.assertEqual(infer_covers_dir('Artists/d/Donald Byrd/1961 Free Form/somefile.flac'),
                                          'Artists/d/Donald Byrd/1961 Free Form')
        
        self.assertEqual(infer_covers_dir('Artists/d/Donald Byrd/discography/1961 - Free Form/somefile.flac'),
                                          'Artists/d/Donald Byrd/discography/1961 - Free Form')
        
        self.assertEqual(infer_covers_dir('Artists/d/Donald Byrd/discography/Donald Byrd & Kenny Burrell/1956 All Night Long/01.flac'),
                                          'Artists/d/Donald Byrd/discography/Donald Byrd & Kenny Burrell/1956 All Night Long')
        
        self.assertEqual(infer_covers_dir('Artists/b/Beatles/2009 Remasters Box Set/1968 The Beatles Disc 1 (2009 Stereo Remaster) [FLAC]/16 - I Will.flac'),
                                          'Artists/b/Beatles/2009 Remasters Box Set/1968 The Beatles Disc 1 (2009 Stereo Remaster) [FLAC]')
                

    def test_starts_with_recording_year(self):
        self.assertTrue(starts_with_recording_year("1960 - At the Half Note Cafe"))
        self.assertFalse(starts_with_recording_year("discography"))
        self.assertTrue(starts_with_recording_year("2012"))
        self.assertFalse(starts_with_recording_year("1435"))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()