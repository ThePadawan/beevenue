import zipfile
from io import BytesIO


def test_get_backup_sh_as_admin(adminClient):
    res = adminClient.get('/media/backup.sh')
    assert res.status_code == 200


def test_get_single_existing_medium_as_admin(adminClient):
    res = adminClient.get('/medium/1/backup')
    assert res.status_code == 200
    assert res.mimetype == "application/zip"

    zip_data = BytesIO(res.data)

    with zipfile.ZipFile(zip_data, 'r') as zip_response:
        infolist = zip_response.infolist()
        print(infolist)
        assert len(infolist) == 2
        assert len([x for x in infolist if x.filename == "1.metadata.json"]) == 1
        assert len([x for x in infolist if x.filename.endswith(".jpg")]) == 1


def test_get_single_nonexisting_medium_as_admin(adminClient):
    res = adminClient.get('/medium/5678/backup')
    assert res.status_code == 404
