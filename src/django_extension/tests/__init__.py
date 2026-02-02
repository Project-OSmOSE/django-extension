from graphene_django.utils import GraphQLTestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

__all__ = ["ExtendedTestCase"]


class ExtendedTestCase(GraphQLTestCase, APITestCase):

    username = None

    def setUp(self):
        self.log_client()

    def tearDown(self):
        """Logout when tests ends"""
        self.client.logout()

    def log_client(self, user=None, headers=None):
        token = None
        if self.username is not None:
            token, _ = Token.objects.get_or_create(user__username=self.username)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)

        if token is None:
            return
        if headers is None:
            headers = {}
        headers["HTTP_AUTHORIZATION"] = f"Bearer {token}"

        self.client = APIClient()
        self.client.force_authenticate(user=user, token=token)

    def gql_query(
        self,
        query,
        user=None,
        operation_name=None,
        input_data=None,
        variables=None,
        headers=None,
    ):
        self.log_client(user, headers)
        return super().query(query, operation_name, input_data, variables, headers)

    def upload_csv_file_as_string(self, url: str, path: str):
        """Upload a CSV file to the given URL"""
        with open(path, "rb") as data:
            data = data.read().decode("utf-8")
            return self.client.post(url, {"data": data})
