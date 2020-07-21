

def test_read_from_file_happy_flow(assert_record_and_replay, scripts_path):
    file_name = "myfile.txt"
    script_name = "open_and_read.py"
    expected_output = b'Hi Son'
    with open(str(scripts_path / file_name), 'wb') as f:
        f.write(expected_output)
    assert_record_and_replay(script_name, runtime_arguments=[expected_output])
