'''
Created on June 20th 2017
@author: jbi

'''
import unittest
import pqueens.example_simulator_functions.agawal as agawal
import pqueens.example_simulator_functions.branin_hifi  as branin_hifi
import pqueens.example_simulator_functions.branin_medfi as branin_medfi
import pqueens.example_simulator_functions.branin_lofi  as branin_lofi


class TestAgawal(unittest.TestCase):

    def setUp(self):
        self.params1 = {'x1': 0.6, 'x2': 0.4}
        self.params2 = {'x1': 0.4, 'x2': 0.4}
        self.dummy_id = 100

    def test_vals_params(self):
        actual_result1 = agawal.main(self.dummy_id, self.params1)
        desired_result1 = 0.0
        self.assertAlmostEqual(actual_result1, desired_result1, places=8,
                               msg=None, delta=None)

        actual_result2 = agawal.main(self.dummy_id, self.params2)
        desired_result2 = 0.90450849718747361
        self.assertAlmostEqual(actual_result2, desired_result2, places=8,
                               msg=None, delta=None)

class TestBraninMultiFidelity(unittest.TestCase):

    def setUp(self):
        self.params1 = {'x1': -4, 'x2': 5}
        self.dummy_id = 100

    def test_vals_params(self):
        actual_result_hifi = branin_hifi.main(self.dummy_id, self.params1)
        actual_result_medfi = branin_medfi.main(self.dummy_id, self.params1)
        actual_result_lofi = branin_lofi.main(self.dummy_id, self.params1)

        #print("actual_result_hifi {}".format(actual_result_hifi))
        #print("actual_result_medfi {}".format(actual_result_medfi))
        #print("actual_result_lofi {}".format(actual_result_lofi))

        desired_result_hifi  = 92.70795679406056
        desired_result_medfi = 125.49860898539086
        desired_result_lofi  = 1.4307273110713652

        self.assertAlmostEqual(actual_result_hifi, desired_result_hifi,
                               places=8, msg=None, delta=None)

        self.assertAlmostEqual(actual_result_medfi, desired_result_medfi,
                               places=8, msg=None, delta=None)

        self.assertAlmostEqual(actual_result_lofi, desired_result_lofi,
                               places=8, msg=None, delta=None)
