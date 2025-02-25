import json

from django.test import Client, TestCase


class GraphQLTestCase(TestCase):
    """
    Provides a best-practice wrapper for easily testing GraphQL endpoints.
    """

    # URL to graphql endpoint
    GRAPHQL_URL = '/graphql/'
    # Here you need to set your graphql schema for the tests
    GRAPHQL_SCHEMA = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        if not cls.GRAPHQL_SCHEMA:
            raise AttributeError('Variable GRAPHQL_SCHEMA not defined in GraphQLTestCase.')

        cls._client = Client(cls.GRAPHQL_SCHEMA)

    def query(self, query: str, op_name: str = None, input_data: dict = None):
        """
        :param query:       GraphQL query to run
        :param op_name:     If the query is a mutation or named query, you must supply the op_name.
                            For annon queries ("{ ... }"), should be None (default).
        :param input_data:  If provided, the $input variable in GraphQL will be set to this value
        :return:            Response object from client
        """

        body = {'query': query}
        if op_name:
            body['operation_name'] = op_name
        if input_data:
            body['variables'] = {'input': input_data}

        resp = self._client.post(self.GRAPHQL_URL, json.dumps(body), content_type='application/json')
        return resp

    def assertResponseNoErrors(self, resp):  # noqa: N802
        """
        Assert that the call went through correctly. 200 means the syntax is ok, if there are no `errors`,
        the call was fine.
        :resp HttpResponse: Response
        """
        content = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('errors', list(content.keys()))

    def assertResponseHasErrors(self, resp):  # noqa: N802
        """
        Assert that the call was failing. Take care: Even with errors, GraphQL returns status 200!
        :resp HttpResponse: Response
        """
        content = json.loads(resp.content)
        self.assertIn('errors', list(content.keys()))
