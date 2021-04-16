#!/bin/sh
task_api_key=2a16ad8150024ea9899f52fd16a69ecc
user=admin
audio=
host=0.0.0.0
port=5566
segmentations='[{"end_time": 7.7407, "start_time": 3.8604, "transcription": "Sample transcription data" }, { "end_time": 17.7407, "start_time": 13.8604, "transcription": "Sample transcription data"}]'

API_KEY=$task_api_key python scripts/upload_data.py --username $user --audio_file $audio --host $host --port $port --segmentations $segmentations
