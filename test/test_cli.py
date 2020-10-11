def test_cli_cannot_upload_txt(client):
    runner = client.app_under_test.test_cli_runner()
    result = runner.invoke(args=["import", "test/resources/text_file.txt"])
    assert result.exit_code == 0
    assert result.exception is None
