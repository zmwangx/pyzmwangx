#!/usr/bin/env python3

import random
import subprocess
import unittest

from zmwangx.humansize import humansize


class TestHumansize(unittest.TestCase):

    NUM_CASES_IN_EACH_RANGE = 1000
    seed = None

    def gen_test_cases(self):
        if self.seed is None:
            random.seed()
            self.seed = random.randrange(10 ** 9)
            random.seed(self.seed)

        cases = []

        # fixed cases
        for exponent in range(1, 6):
            for multiplier in range(1, 1024):
                base1 = multiplier * (1000 ** exponent)
                base2 = multiplier * (1024 ** exponent)
                cases.extend([base1 - 1, base1, base1 + 1,
                              base2 - 1, base2, base2 + 1])

        # random cases
        for exponent in range(1, 19):
            low = 10 ** (exponent - 1)
            high = 10 ** exponent - 1
            for _ in range(self.NUM_CASES_IN_EACH_RANGE):
                cases.append(random.randint(low, high))

        # give special attention to the ranges [1000^e, 1024^e]
        for exponent in range(1, 7):
            low = 1000 ** exponent
            high = 1024 ** exponent
            for _ in range(self.NUM_CASES_IN_EACH_RANGE):
                cases.append(random.randint(low, high))
        return cases

    def test_numfmt(self):
        cases = self.gen_test_cases()
        numfmt_input = '\n'.join([str(n) for n in cases])
        for prefix in ['iec', 'si']:
            p = subprocess.Popen(["numfmt", "--to=%s" % prefix],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 universal_newlines=True)
            stdout, stderr = p.communicate(input=numfmt_input)
            numfmt_results = stdout.split()
            humansize_results = [humansize(n, prefix=prefix, unit="", numfmt=True)
                                 for n in cases]
            for i in range(len(cases)):
                self.assertEqual(humansize_results[i], numfmt_results[i],
                                 msg="size: %s, seed %s" % (cases[i], self.seed))


if __name__ == '__main__':
    unittest.main()
