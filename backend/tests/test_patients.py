
def test_patient_list_with_clinician_token(client, auth_headers):
    response = client.get(
        "/api/v1/patients",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


def test_create_patient_with_valid_payload(client, auth_headers):
    response = client.post(
        "/api/v1/patients",
        headers=auth_headers,
        json={
            "patient_code": "TEST-001",
            "full_name": "Synthetic Patient",
            "date_of_birth": "1990-05-10",
        },
    )

    assert response.status_code in (200, 201), response.text
    body = response.json()

    assert body["patient_code"] == "TEST-001"
    assert body["full_name"] == "Synthetic Patient"


def test_create_patient_rejects_missing_required_fields(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/patients",
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 422
