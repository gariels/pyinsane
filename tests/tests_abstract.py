import sys
sys.path = ["src"] + sys.path

import sys
import traceback
import unittest


class TestSaneGetDevices(unittest.TestCase):
    def set_module(self, module):
        self.module = module

    def setUp(self):
        pass

    def test_get_devices(self):
        devices = self.module.get_devices()
        self.assertTrue(len(devices) > 0)

    def tearDown(self):
        pass


class TestSaneOptions(unittest.TestCase):
    def set_module(self, module):
        self.module = module

    def setUp(self):
        self.devices = self.module.get_devices()
        self.assertTrue(len(self.devices) > 0)

    def test_get_option(self):
        for dev in self.devices:
            val = dev.options['mode'].value
            self.assertNotEqual(val, None)

    def test_set_option(self):
        for dev in self.devices:
            dev.options['mode'].value = "Gray"
            val = dev.options['mode'].value
            self.assertEqual(val, "Gray")

    def __set_opt(self, opt_name, opt_val):
        for dev in self.devices:
            dev.options[opt_name].value = opt_val

    def test_set_inexisting_option(self):
        self.assertRaises(KeyError, self.__set_opt, 'xyz', "Gray")

    def test_set_invalid_value(self):
        self.assertRaises(self.module.SaneException, self.__set_opt, 'mode', "XYZ")

    def tearDown(self):
        for dev in self.devices:
            del(dev)
        del(self.devices)


class TestSaneScan(unittest.TestCase):
    def set_module(self, module):
        self.module = module

    def setUp(self):
        devices = self.module.get_devices()
        self.assertTrue(len(devices) > 0)
        self.dev = devices[0]

    def test_simple_scan_lineart(self):
        self.assertTrue("Lineart" in self.dev.options['mode'].constraint)
        self.dev.options['mode'].value = "Lineart"
        scan_session = self.dev.scan(multiple=False)
        try:
            assert(scan_session.scan is not None)
            while True:
                scan_session.scan.read()
        except EOFError:
            pass
        img = scan_session.images[0]
        self.assertNotEqual(img, None)

    def test_simple_scan_gray(self):
        self.assertTrue("Gray" in self.dev.options['mode'].constraint)
        self.dev.options['mode'].value = "Gray"
        scan_session = self.dev.scan(multiple=False)
        try:
            while True:
                scan_session.scan.read()
        except EOFError:
            pass
        img = scan_session.images[0]
        self.assertNotEqual(img, None)

    def test_simple_scan_color(self):
        self.assertTrue("Color" in self.dev.options['mode'].constraint)
        self.dev.options['mode'].value = "Color"
        scan_session = self.dev.scan(multiple=False)
        try:
            while True:
                scan_session.scan.read()
        except EOFError:
            pass
        img = scan_session.images[0]
        self.assertNotEqual(img, None)

    def test_multi_scan_on_flatbed(self):
        self.assertTrue("Flatbed" in self.dev.options['source'].constraint)
        self.dev.options['source'].value = "Flatbed"
        self.dev.options['mode'].value = "Color"
        scan_session = self.dev.scan(multiple=True)
        try:
            while True:
                scan_session.scan.read()
        except EOFError:
            pass
        self.assertEqual(len(scan_session.images), 1)
        self.assertNotEqual(scan_session.images[0], None)

    def test_multi_scan_on_adf(self):
        self.assertTrue("ADF" in self.dev.options['source'].constraint)
        self.dev.options['source'].value = "ADF"
        self.dev.options['mode'].value = "Color"
        scan_session = self.dev.scan(multiple=True)
        try:
            while True:
                try:
                    scan_session.scan.read()
                except EOFError:
                    pass
        except StopIteration:
            pass
        self.assertEqual(len(scan_session.images), 0)

    def test_expected_size(self):
        self.assertTrue("ADF" in self.dev.options['source'].constraint)
        self.dev.options['source'].value = "Flatbed"
        self.dev.options['mode'].value = "Color"
        scan_session = self.dev.scan(multiple=False)
        scan_size = scan_session.scan.expected_size
        self.assertTrue(scan_size[0] > 100)
        self.assertTrue(scan_size[1] > 100)
        scan_session.scan.cancel()

    def test_get_progressive_scan(self):
        self.assertTrue("ADF" in self.dev.options['source'].constraint)
        self.dev.options['source'].value = "Flatbed"
        self.dev.options['mode'].value = "Color"
        scan_session = self.dev.scan(multiple=False)
        last_line = 0
        expected_size = scan_session.scan.expected_size
        try:
            while True:
                scan_session.scan.read()

                self.assertEqual(scan_session.scan.available_lines[0], 0)
                current_line = scan_session.scan.available_lines[1]
                self.assertTrue(last_line <= current_line)
                last_line = current_line

                img = scan_session.scan.get_image(0, current_line)
                self.assertEqual(img.size[0], expected_size[0])
                self.assertEqual(img.size[1], current_line)
        except EOFError:
            pass
        self.assertTrue(last_line <= current_line)
        self.assertEqual(current_line, expected_size[1])
        last_line = current_line
        img = scan_session.scan.get_image(0, current_line)
        self.assertEqual(img.size[0], expected_size[0])
        self.assertEqual(img.size[1], current_line)

        img = scan_session.images[0]
        self.assertNotEqual(img, None)

    def tearDown(self):
        del(self.dev)


def get_all_tests(module):
    all_tests = unittest.TestSuite()

    tests = [
        TestSaneGetDevices("test_get_devices")
    ]
    for test in tests:
        test.set_module(module)
    all_tests.addTest(unittest.TestSuite(tests))

    tests = [
        TestSaneOptions("test_get_option"),
        TestSaneOptions("test_set_option"),
        TestSaneOptions("test_set_inexisting_option"),
        TestSaneOptions("test_set_invalid_value"),
    ]
    for test in tests:
        test.set_module(module)
    all_tests.addTest(unittest.TestSuite(tests))

    tests = [
        TestSaneScan("test_simple_scan_lineart"),
        TestSaneScan("test_simple_scan_gray"),
        TestSaneScan("test_simple_scan_color"),
        TestSaneScan("test_multi_scan_on_flatbed"),
        TestSaneScan("test_multi_scan_on_adf"),
        TestSaneScan("test_expected_size"),
        TestSaneScan("test_get_progressive_scan"),
    ]
    for test in tests:
        test.set_module(module)
    all_tests.addTest(unittest.TestSuite(tests))

    return all_tests

