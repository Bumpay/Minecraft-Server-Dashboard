def test_read_main(test_client):
    response = test_client.get("/servers")