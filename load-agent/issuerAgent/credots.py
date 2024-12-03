from .base import BaseIssuer
import json
import os
import requests
import time
from .utils.jsonldCredential import get_jsonld_credential_payload
from json.decoder import JSONDecodeError

VERIFIED_TIMEOUT_SECONDS = int(os.getenv("VERIFIED_TIMEOUT_SECONDS", 120))
class CredoIssuer(BaseIssuer):
        
        def get_invite(self, out_of_band=False):
                headers = json.loads(os.getenv("ISSUER_HEADERS"))
                headers["Content-Type"] = "application/json"
                headers["Accept"] = "application/json"
                headers["Authorization"] = ""

                r = requests.post(
                        url=os.getenv("ISSUER_URL") + "/multi-tenancy/create-invitation/" + os.getenv("ISSUER_TENANT_ID"), 
                        json={
                        "autoAcceptConnection": True        
                        },
                        headers=headers
                )

                try:
                        try_var = r.json()["invitationUrl"]
                except Exception:
                        raise Exception("Failed to get invitation url. Request: ", r.json())
                if r.status_code != 200:
                        raise Exception(r.content)

                r = r.json()

                return {
                        'invitation_url': r['invitationUrl'], 
                        'outOfBandId': r['outOfBandRecord']['id']
                }
        def get_connectionId(self, outOfBandId):
                headers = json.loads(os.getenv("ISSUER_HEADERS"))
                headers["Content-Type"] = "application/json"
                headers["Accept"] = "application/json"
                headers["Authorization"] = ""
                iteration = 0
                try:
                        while iteration < VERIFIED_TIMEOUT_SECONDS:
                                g = requests.get(
                                        url=os.getenv("ISSUER_URL") + "/multi-tenancy/connections/" + os.getenv("ISSUER_TENANT_ID"),
                                        headers=headers,
                                        params={"outOfBandId": outOfBandId}
                                )
                                if (len(g.json()) > 0 and g.json()[0]["state"] == "completed"):
                                        break
                                iteration += 1
                                time.sleep(1)

                        if g.json()[0]["state"] != "completed":
                                raise AssertionError(
                                        f"Connection was not successfully Created. Connection in state {g.json()['state']}"
                                )

                except JSONDecodeError as e:
                        raise Exception(
                                "Encountered JSONDecodeError while getting the connection record: ", g
                        )


                g = g.json()
                connection_id = g[0]['id']
                return {
                        "connection_id": connection_id
                }

        def is_up(self):
                try:
                        headers = json.loads(os.getenv("ISSUER_HEADERS"))
                        headers["Content-Type"] = "application/json"
                        r = requests.get(
                                os.getenv("ISSUER_URL") + "/agent",
                                headers=headers,
                        )
                        if r.status_code != 200:
                                raise Exception(r.content)

                        r = r.json()
                except:
                        return False

                return True

        def issue_credential(self, connection_id):
                headers = json.loads(os.getenv("ISSUER_HEADERS"))
                headers["Content-Type"] = "application/json"

                issuer_did = os.getenv("CRED_DEF").split(":")[0]
                schema_parts = os.getenv("SCHEMA").split(":")

                r = requests.post(
                        os.getenv("ISSUER_URL") + "/issue-credential/send",
                        json={
                                "auto_remove": True,
                                "comment": "Performance Issuance",
                                "connection_id": connection_id,
                                "cred_def_id": os.getenv("CRED_DEF"),
                                "credential_proposal": {
                                "@type": "issue-credential/1.0/credential-preview",
                                "attributes": json.loads(os.getenv("CRED_ATTR")),
                                },
                                "issuer_did": issuer_did,
                                "schema_id": os.getenv("SCHEMA"),
                                "schema_issuer_did": schema_parts[0],
                                "schema_name": schema_parts[2],
                                "schema_version": schema_parts[3],
                                "trace": True,
                        },
                        headers=headers,
                )
                if r.status_code != 200:
                        raise Exception(r.content)

                r = r.json()

                return {
                        "connection_id": r["connection_id"], 
                        "cred_ex_id": r["credential_exchange_id"]
                }

        def issue_jsonld_credential(self, connection_id, didKey):
                headers = json.loads(os.getenv("ISSUER_HEADERS"))
                headers["Content-Type"] = "application/json"

                json_data=os.getenv("JSONLD_ISSUANCE_PAYLOAD")
                if (json_data):
                        json_data = json.loads(json_data)
                        json_data['connection_id']=connection_id
                        json_data['filter']['ld_proof']['credential']['credentialSubject']['id'] = didKey
                else:
                        json_data=get_jsonld_credential_payload(connection_id, os.getenv("JSONLD_ISSUANCE_DID"), didKey)
                        
                r = requests.post(
                        os.getenv("ISSUER_URL") + "/issue-credential-2.0/send-offer",
                        json=json_data,
                        headers=headers,
                )
                if r.status_code != 200:
                        raise Exception(r.content)

                r = r.json()

                return {
                        "connection_id": r["connection_id"], 
                        "cred_ex_id": r["cred_ex_id"]
                }

        def revoke_credential(self, connection_id, credential_exchange_id):
                headers = json.loads(os.getenv("ISSUER_HEADERS"))
                headers["Content-Type"] = "application/json"

                issuer_did = os.getenv("CRED_DEF").split(":")[0]
                schema_parts = os.getenv("SCHEMA").split(":")

                time.sleep(1)

                r = requests.post(
                        os.getenv("ISSUER_URL") + "/revocation/revoke",
                        json={
                                "comment": "load test",
                                "connection_id": connection_id,
                                "cred_ex_id": credential_exchange_id,
                                "notify": True,
                                "notify_version": "v1_0",
                                "publish": True,
                        },
                        headers=headers,
                )
                if r.status_code != 200:
                        raise Exception(r.content)

        def send_message(self, connection_id, msg):
                headers = json.loads(os.getenv("ISSUER_HEADERS"))
                headers["Content-Type"] = "application/json"

                r = requests.post(
                        os.getenv("ISSUER_URL") + "/connections/" + connection_id + "/send-message",
                        json={"content": msg},
                        headers=headers,
                )
                r = r.json()
