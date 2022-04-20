import unittest
from http import HTTPStatus
from unittest import mock

from marvin.handlers.sns import post_to_slack

from .mocks import ok_mocked_requests_post


class MyTestCase(unittest.TestCase):
    @mock.patch("marvin.handlers.sns.requests.post", side_effect=ok_mocked_requests_post)
    def test_post_to_slack(self, *_):
        event = {
            "Records": [
                {
                    "Sns": {"Message": "test-message"},
                }
            ]
        }
        results = post_to_slack(event=event, context={})
        self.assertTrue(results)
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result, HTTPStatus.OK)
