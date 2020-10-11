def test_graphql(client, asAdmin):
    res = client.post(
        "/graphql",
        data={
            "query": """
            {
                statistics
                {
                    ratings
                    {
                        s, q, e, u
                    }
                }
                }
            """
        },
    )
    assert res.status_code == 200
    result_json = res.get_json()
    assert "data" in result_json
    assert "statistics" in result_json["data"]
    assert "ratings" in result_json["data"]["statistics"]
    ratings = result_json["data"]["statistics"]["ratings"]
    assert set(["s", "q", "e", "u"]) == set(ratings.keys())
