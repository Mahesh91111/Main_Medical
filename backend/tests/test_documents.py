    
def test_document_upload_requires_authentication(client):
    response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "sample.pdf",
                b"%PDF-1.4 test content",
                "application/pdf",
            )
        },
    )

    assert response.status_code in (401, 403)


def test_document_list_requires_authentication(client):
    response = client.get("/api/v1/documents")

    assert response.status_code in (401, 403)


def test_upload_rejects_non_pdf(client, auth_headers):
    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={
            "file": (
                "sample.txt",
                b"This is not a PDF file.",
                "text/plain",
            )
        },
    )

    assert response.status_code in (400, 415, 422)
