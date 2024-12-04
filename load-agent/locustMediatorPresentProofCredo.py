from locust import SequentialTaskSet, task, User, between
from locustClient import CustomClient

import os

WITH_MEDIATION = os.getenv("WITH_MEDIATION")

class CustomLocust(User):
    abstract = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.client = CustomClient(self.host)

class UserBehaviour(SequentialTaskSet):
    def on_start(self):
        self.client.startup(withMediation=bool(WITH_MEDIATION))

    def on_stop(self):
        self.client.shutdown()

    @task
    def get_issuer_invite(self):
        invite = self.client.issuer_getinvite()
        self.invite = invite

    @task
    def accept_issuer_invite(self):
        self.client.ensure_is_running()

        connection = self.client.accept_invite(self.invite["invitation_url"])

        self.connection = connection

    @task
    def create_connection(self):
        if (os.getenv("ISSUER_TYPE") == "credo"):
            connection = self.client.create_connection(self.invite['outOfBandId'])
            self.invite['connection_id'] = connection["connection_id"]

    @task
    def create_did(self):
        didKey = self.client.create_holder_didKey()
        self.didKey = didKey

    @task
    def receive_credential(self):
        self.client.ensure_is_running()

        credential = self.client.receive_credential(self.invite["connection_id"], self.didKey)

    # @task
    # def get_verifier_invite(self):
    #     verifier_invite = self.client.verifier_getinvite()
    #     self.verifier_invite = verifier_invite

    # @task
    # def accept_verifier_invite(self):
    #     self.client.ensure_is_running()

    #     verifier_connection = self.client.accept_invite(self.verifier_invite['invitation_url'])
    #     self.verifier_connection = verifier_connection

    @task
    def presentation_exchange(self):
        self.client.ensure_is_running()

        # Need connection id
        presentation = self.client.presentation_exchange(self.invite['connection_id'])


class Issue(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = between(float(os.getenv('LOCUST_MIN_WAIT',0.1)), float(os.getenv('LOCUST_MAX_WAIT',1)))
#    host = "example.com"

