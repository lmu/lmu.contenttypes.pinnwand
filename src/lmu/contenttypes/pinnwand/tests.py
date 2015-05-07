import doctest
import unittest

from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

import lmu.contenttypes.pinnwand

OPTION_FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

ptc.setupPloneSite(products=['lmu.contenttypes.pinnwand'])


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            zcml.load_config('configure.zcml',
                             lmu.contenttypes.pinnwand)

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='lmu.contenttypes.pinnwand',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='lmu.contenttypes.pinnwand.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'INTEGRATION.txt',
            package='lmu.contenttypes.pinnwand',
            optionflags=OPTION_FLAGS,
            test_class=TestCase),

        # -*- extra stuff goes here -*-

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
