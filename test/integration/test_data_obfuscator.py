import os
import unittest

from dataobfuscator import *

PATH = path.dirname(os.path.realpath(__file__))
JPEG_HEADER = bytes(b"\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01")


class TestDataObfuscator(unittest.TestCase):

    input_file = path.join(PATH, '..', '..', 'defaults/blank.jpg')
    input_file_lsb = path.join(PATH, '..', '..', 'defaults/blank-big.jpg')
    data_file = os.path.join(PATH, 'test-files', 'test.txt')
    header_output_file = '{}-header.jpg'.format(os.path.splitext(data_file)[0])
    header_deobfuscate_file = '{}-header-obfuscated.jpg'.format(os.path.splitext(data_file)[0])
    header_output_deobfuscate_file = '{}-header-obfuscated-recovered'.format(os.path.splitext(data_file)[0])
    append_output_file = '{}-append.jpg'.format(os.path.splitext(data_file)[0])
    append_deobfuscate_file = '{}-append-obfuscated.jpg'.format(os.path.splitext(data_file)[0])
    append_output_deobfuscate_file = '{}-append-obfuscated-recovered'.format(os.path.splitext(data_file)[0])
    lsb_output_file = '{}-lsb.png'.format(os.path.splitext(data_file)[0])
    lsb_deobfuscate_file = '{}-lsb-obfuscated.png'.format(os.path.splitext(data_file)[0])
    lsb_output_deobfuscate_file = '{}-lsb-obfuscated-recovered'.format(os.path.splitext(data_file)[0])

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(cls.header_output_file)
            os.remove(cls.header_output_deobfuscate_file)
            os.remove(cls.append_output_file)
            os.remove(cls.append_output_deobfuscate_file)
            os.remove(cls.lsb_output_file)
            os.remove(cls.lsb_output_deobfuscate_file)
        except IOError:
            pass

    def test_obfuscate_header(self):
        obfuscate_via_header(self.data_file, self.header_output_file)
        self.assertTrue(os.path.exists(self.header_output_file))
        self._compare_file_contents(self.header_output_file, self.header_deobfuscate_file)

    def test_deobfuscate_header(self):
        deobfuscate_via_header(self.header_deobfuscate_file, self.header_output_deobfuscate_file)
        self.assertTrue(os.path.exists(self.header_output_deobfuscate_file))
        self._check_deobfuscated_text(self.header_output_deobfuscate_file)

    def test_obfuscate_append(self):
        obfuscate_via_append(self.data_file, self.input_file, self.append_output_file)
        self.assertTrue(os.path.exists(self.append_output_file))
        self._compare_file_contents(self.append_output_file, self.append_deobfuscate_file)

    def test_deobfuscate_append(self):
        deobfuscate_via_append(self.append_deobfuscate_file, self.append_output_deobfuscate_file)
        self.assertTrue(os.path.exists(self.append_output_deobfuscate_file))
        self._check_deobfuscated_text(self.append_output_deobfuscate_file)

    def test_obfuscate_lsb(self):
        obfuscate_via_lsb(self.data_file, self.input_file_lsb, self.lsb_output_file)
        self.assertTrue(os.path.exists(self.lsb_output_file))
        self._compare_file_contents(self.lsb_output_file, self.lsb_deobfuscate_file)

    def test_deobfuscate_lsb(self):
        deobfuscate_via_lsb(self.lsb_deobfuscate_file, self.lsb_output_deobfuscate_file)
        self.assertTrue(os.path.exists(self.lsb_output_deobfuscate_file))
        self._check_deobfuscated_text(self.lsb_output_deobfuscate_file)

    def _compare_file_contents(self, file1, file2):
        with open(file1, "rb") as f:
            data1 = f.read()
        with open(file2, "rb") as f:
            data2 = f.read()
        self.assertEqual(data1, data2)

    def _check_deobfuscated_text(self, file):
        with open(file, "rb") as f:
            data = f.read()
        with open(self.data_file, "rb") as f:
            text = f.read()
        self.assertEqual(text, data)
