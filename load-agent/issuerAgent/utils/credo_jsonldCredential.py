def get_jsonld_credential_payload(connection_id, issuer_did, didKey):
  return {
    "protocolVersion": "v2",
    "connectionId": connection_id,
    "credentialFormats": {
        "jsonld": {
            "credential": {
                "@context": [
                    "https://www.w3.org/2018/credentials/v1",
                    "https://www.w3.org/2018/credentials/examples/v1"
                ],
                "type": [
                    "VerifiableCredential",
                    "UniversityDegreeCredential"
                ],
                "issuer": {
                    "id": issuer_did
                },
                "issuanceDate": "2019-10-12T07:20:50.52Z",
                "credentialSubject": {
                    "id": didKey,
                    "degree": {
                        "type": "BachelorDegree",
                        "name": "Bachelor of Science and Arts"
                    }
                }
            },
            "options": {
                "proofType": "Ed25519Signature2018",
                "proofPurpose": "assertionMethod"
            }
        }
    },
    "autoAcceptCredential": "always",
    "comment": "string"
}