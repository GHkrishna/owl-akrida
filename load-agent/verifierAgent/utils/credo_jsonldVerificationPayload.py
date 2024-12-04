import uuid


def get_jsonld_verification_payload(connection_id):
  return {
    "connectionId": connection_id,
    "protocolVersion": "v2",
    "proofFormats": {
        "presentationExchange": {
            "presentationDefinition": {
                "id": str(uuid.uuid4()),
                "input_descriptors": [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "registration card",
                        "schema": [
                            {
                                "uri": "https://www.w3.org/2018/credentials/examples/v1"
                            }
                        ],
                        "constraints": {
                            "fields": [
                                {
                                    "path": [
                                        "$.credentialSubject.degree.type"
                                    ]
                                }
                            ]
                        },
                        "purpose": "Verify proof"
                    }
                ]
            }
        }
    },
    "comment": "string",
    "autoAcceptProof": "always"
}
