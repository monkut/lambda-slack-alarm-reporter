import datetime


def ok_mocked_requests_post(*_, **__):
    ok_res = "OK"

    class MockResponse:
        def __init__(self, res, status_code):
            self.json_data = res
            self.status_code = status_code
            self.content = ok_res.encode("utf8")
            self.ok = True

        def raise_for_status(self):
            return True

        def json(self):
            return self.json_data

        @property
        def text(self):
            return str(self.json_data)

    return MockResponse(ok_res, 200)
