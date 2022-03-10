
import pytest

from origin.api import (
    BadRequest,
    MovedPermanently,
    TemporaryRedirect,
)

from .endpoints import (
    EndpointReturnsGeneric,
    EndpointRaisesGeneric,
    EndpointReturnsResponseModel,
    EndpointWithRequestAndResponseModels,
)

from dataclasses import dataclass, field
from typing import List, Optional
from origin.api import Endpoint, Context


class TestEndpointResponse:
    """Testing different responses data types."""

    def test__health_check__should_return_status_200(
            self,
            client,
    ):
        """TODO."""

        # -- Act -------------------------------------------------------------

        r = client.get('/health')

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200

    @pytest.mark.parametrize('obj, response_body', [
        ('string-body', 'string-body'),
        (b'bytes-body', 'bytes-body'),
        # TODO ByteStream, more?
    ])
    def test__endpoint_returns_string_alike__should_return_string_as_body(
            self,
            obj,
            response_body,
            app,
            client,
    ):
        """TODO."""

        # -- Arrange ---------------------------------------------------------

        app.add_endpoint(
            method='POST',
            path='/something',
            endpoint=EndpointReturnsGeneric(obj),
        )

        # -- Act -------------------------------------------------------------

        r = client.post('/something')

        # -- Assert ----------------------------------------------------------

        assert r.text == response_body
        assert r.headers['Content-Type'] == 'text/html; charset=utf-8'

    def test__endpoint_returns_dict__should_return_dict_as_body(
            self,
            app,
            client,
    ):
        """TODO."""

        # -- Arrange ---------------------------------------------------------

        response_data = {
            'foo': 'bar',
            'something': {
                'foo': 1,
                'bar': 22.2,
            },
        }

        app.add_endpoint(
            method='POST',
            path='/something',
            endpoint=EndpointReturnsGeneric(response_data),
        )

        # -- Act -------------------------------------------------------------

        r = client.post('/something')

        # -- Assert ----------------------------------------------------------

        assert r.json() == response_data
        assert r.headers['Content-Type'] == 'application/json'

    def test__fast_api_return_correct(
            self,
            app,
            client,
    ):
        """
        TODO
        """
        class TestEndpoint(Endpoint):
            """Endpoint to get the user's (actor's) profile."""

            @dataclass
            class Response:
                """Response containing UserProfile on success."""
                success: bool
                msg: str

            def handle_request(
                    self,
                    # context: Context
            ) -> Response:
                """
                Handle HTTP request.

                :param context: Context for a single HTTP request.
                :return: The response with the user profile
                """
                return self.Response(
                    success=True,
                    msg="something"
                )


        # -- Arrange ---------------------------------------------------------

        response_data = {
            'success': True,
            'msg': "something",
        }

        app.add_endpoint(
            method='POST',
            path='/something',
            endpoint=TestEndpoint(),
        )

        # -- Act -------------------------------------------------------------

        r = client.post('/something')

        # -- Assert ----------------------------------------------------------

        assert r.json() == response_data
        assert r.headers['Content-Type'] == 'application/json'

    def test__fast_api__with_query_parms(
            self,
            app,
            client,
    ):
        """
        TODO
        """
        from fastapi import  Request as FastAPIRequest
        class TestEndpoint(Endpoint):
            """Endpoint to get the user's (actor's) profile."""

            @dataclass
            class Response:
                """Response containing UserProfile on success."""
                success: bool
                parm1: str
                parm2: str

            @dataclass
            class Request:
                """Response containing UserProfile on success."""
                parm1: str
                parm2: str

            def handle_request(
                    self,
                    request: Request,
                    new_request: FastAPIRequest,
            ) -> Response:
                """
                Handle HTTP request.

                :param context: Context for a single HTTP request.
                :return: The response with the user profile
                """
                return self.Response(
                    success=True,
                    parm1=request.parm1,
                    parm2=request.parm2,
                )

        # -- Arrange ---------------------------------------------------------
        response_data = {
            'success': True,
            'parm1': "test1",
            'parm2': "test2",
        }

        request_data = {
            'parm1': "test1",
            'parm2': "test2",
        }

        app.add_endpoint(
            method='POST',
            path='/something',
            endpoint=TestEndpoint(),
        )

        # -- Act -------------------------------------------------------------

        r = client.post(
            url='/something',
            json=request_data,
        )

        # -- Assert ----------------------------------------------------------

        assert r.json() == response_data
        assert r.headers['Content-Type'] == 'application/json'

    @pytest.mark.parametrize('status_code, obj', [
        (301, MovedPermanently('http://something.com/')),
        (307, TemporaryRedirect('http://something.com/')),
        (400, BadRequest()),
    ])
    def test__endpoint_raises_http_response__should_format_response_appropriately(  # noqa: E501
            self,
            status_code,
            obj,
            app,
            client,
    ):
        """TODO."""

        # -- Arrange ---------------------------------------------------------

        app.add_endpoint(
            method='POST',
            path='/something',
            endpoint=EndpointRaisesGeneric(obj),
        )

        # -- Act -------------------------------------------------------------

        r = client.post('/something')

        # -- Assert ----------------------------------------------------------

        assert r.status_code == status_code

    def test__endpoint_raises_exception__should_return_status_500(
            self,
            app,
            client,
    ):
        """TODO."""

        # -- Arrange ---------------------------------------------------------

        app.add_endpoint(
            method='POST',
            path='/something',
            endpoint=EndpointRaisesGeneric(Exception('foo bar')),
        )

        # -- Act -------------------------------------------------------------

        r = client.post('/something')

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 500

    def test__endpoint_returns_response_model__should_format_response_appropriately(  # noqa: E501
            self,
            app,
            client,
    ):
        """TODO."""

        # -- Arrange ---------------------------------------------------------

        app.add_endpoint(
            method='POST',
            path='/something',
            endpoint=EndpointReturnsResponseModel(),
        )

        # -- Act -------------------------------------------------------------

        r = client.post('/something')

        # -- Assert ----------------------------------------------------------

        assert r.headers['Content-Type'] == 'application/json'
        assert r.json() == {
            'success': True,
            'something': 'something',
        }

    def test__endpoint_with_request_and_response_models(
            self,
            app,
            client,
    ):
        """TODO."""

        # -- Arrange ---------------------------------------------------------

        app.add_endpoint(
            method='POST',
            path='/something',
            endpoint=EndpointWithRequestAndResponseModels(),
        )

        # -- Act -------------------------------------------------------------

        r = client.post(
            url='/something',
            json={'something': 'Hello world'},
        )

        # -- Assert ----------------------------------------------------------

        assert r.headers['Content-Type'] == 'application/json'
        assert r.json() == {
            'success': True,
            'something': 'Hello world',
        }


class TestEndpointRedirect:
    """TODO."""

    @pytest.mark.parametrize('status_code, response', [
        (301, MovedPermanently('http://something.com/')),
        (307, TemporaryRedirect('http://something.com/')),
    ])
    def test__endpoint_returns_redirect(
            self,
            status_code,
            response,
            app,
            client,
    ):
        """TODO."""

        # -- Arrange ---------------------------------------------------------

        app.add_endpoint(
            method='GET',
            path='/something',
            endpoint=EndpointReturnsGeneric(response),
        )

        # -- Act -------------------------------------------------------------

        r = client.get('/something')

        # -- Assert ----------------------------------------------------------

        assert r.status_code == status_code
        assert r.headers['Location'] == 'http://something.com/'

    @pytest.mark.parametrize('status_code, response', [
        (301, MovedPermanently('http://something.com/')),
        (307, TemporaryRedirect('http://something.com/')),
    ])
    def test__endpoint_raises_redirect(
            self,
            status_code,
            response,
            app,
            client,
    ):
        """TODO."""

        # -- Arrange ---------------------------------------------------------

        app.add_endpoint(
            method='POST',
            path='/something',
            endpoint=EndpointRaisesGeneric(response),
        )

        # -- Act -------------------------------------------------------------

        r = client.post('/something')

        # -- Assert ----------------------------------------------------------

        assert r.status_code == status_code
        assert r.headers['Location'] == 'http://something.com/'
