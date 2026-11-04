
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


def test_patient_profile_search_and_timeline(client, auth_headers):
    created = client.post(
        "/api/v1/patients",
        headers=auth_headers,
        json={
            "patient_code": "PROFILE-001",
            "full_name": "Avery Patient",
            "gender": "female",
            "email": "avery@example.test",
            "medical_history": "Asthma",
            "allergies": "Penicillin",
        },
    )
    assert created.status_code == 201, created.text
    patient = created.json()

    assert patient["medical_history"] == "Asthma"
    assert patient["allergies"] == "Penicillin"

    unspecified_response = client.post(
        "/api/v1/patients",
        headers=auth_headers,
        json={
            "patient_code": "PROFILE-002",
            "full_name": "Jordan Patient",
        },
    )
    assert unspecified_response.status_code == 201, unspecified_response.text

    search = client.get(
        "/api/v1/patients",
        headers=auth_headers,
        params={"search": "avery", "gender": "female"},
    )
    assert search.status_code == 200, search.text
    assert [item["id"] for item in search.json()] == [patient["id"]]

    timeline = client.get(
        f"/api/v1/patients/{patient['id']}/timeline",
        headers=auth_headers,
    )
    assert timeline.status_code == 200, timeline.text
    assert timeline.json() == []

    unknown_gender = client.get(
        "/api/v1/patients",
        headers=auth_headers,
        params={"gender": "unknown"},
    )
    assert unknown_gender.status_code == 200, unknown_gender.text
    assert {item["id"] for item in unknown_gender.json()} == {
        unspecified_response.json()["id"],
    }


def test_patient_medication_and_vitals_appear_in_timeline(
    client,
    auth_headers,
):
    patient_response = client.post(
        "/api/v1/patients",
        headers=auth_headers,
        json={
            "patient_code": "CLINICAL-001",
            "full_name": "Taylor Patient",
        },
    )
    assert patient_response.status_code == 201, patient_response.text
    patient = patient_response.json()

    encounter_response = client.post(
        "/api/v1/encounters",
        headers=auth_headers,
        json={
            "patient_id": patient["id"],
            "clinical_notes": "Routine follow-up",
            "blood_pressure": "120/80",
            "heart_rate": 72,
        },
    )
    assert encounter_response.status_code == 201, encounter_response.text
    encounter = encounter_response.json()
    assert encounter["blood_pressure"] == "120/80"
    assert encounter["heart_rate"] == 72

    medication_response = client.post(
        f"/api/v1/patients/{patient['id']}/medications",
        headers=auth_headers,
        json={
            "medication_name": "Example medication",
            "dose": "10 mg",
            "frequency": "Daily",
        },
    )
    assert medication_response.status_code == 201, medication_response.text

    timeline_response = client.get(
        f"/api/v1/patients/{patient['id']}/timeline",
        headers=auth_headers,
    )
    assert timeline_response.status_code == 200, timeline_response.text
    timeline = timeline_response.json()
    assert {event["kind"] for event in timeline} == {
        "encounter",
        "medication",
    }
    encounter_event = next(event for event in timeline if event["kind"] == "encounter")
    assert "Blood pressure: 120/80" in encounter_event["details"]
