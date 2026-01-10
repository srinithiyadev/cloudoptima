def test_mock_scan_returns_data():
    from scanner import mock_scan
    result = mock_scan()
    assert 'resources' in result
    assert isinstance(result['resources'], list)