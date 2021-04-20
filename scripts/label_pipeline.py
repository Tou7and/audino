""" ASR Labeling Pipeline

1. Get data needed for labeling

2. Upload data.

3. Download labeled data.

"""
import os
import sys
import requests
import json

from pathlib import Path
from mtasr.vad import wav2segments
from mtasr.clients import AICASR

# 'audio_file': "/mnt/d/Corpus/leader-893/893.wav",

AIC_ASR = AICASR("http://10.21.98.81:8080/predictions/speech")
CONFIG = dict()
CONFIG = {
    'username': "test", # IMPORTANT: the WAV can only be SEEN/LISTEN by this user 
    'audio_file': "/mnt/d/jameshou/toy_corpus/xiaonan_online/0322-0326/2066_con100.wav",
    'reference_transcription': None, # "REFERENCE FOR SINGLE SENTENCE"
    'host': "10.24.211.161",
    'port': "3080",
    'is_marked_for_review': False,
    'segmentations': [], # List of segmentations for the audio
    'api_key': "7057eaf790b240a2b7f43d6584029c3d" # "f67b71208fa24bcc89de7bb577b11e87"
}

def get_segmentations(config: dict):
    """
    Returns:
        status (int): 0 = OK, 1 = VAD fail, 2 = ASR Fail

    """
    wavpath = config["audio_file"]
    outpath = os.path.join("./tmp", os.path.splitext(os.path.basename(wavpath))[0])

    try:
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        timestamps, _ = wav2segments(wavpath, outputdir=outpath)
    except:
        return 1

    for seg in timestamps:
        seg_audio = "chunk-" + str(seg['id']).zfill(4) + ".wav"
        seg_path = os.path.join(outpath, seg_audio)

        try:
            response = AIC_ASR.post_audio(seg_path)
            hyp = response['result']
            print(hyp)
        except:
            return 2

        config["segmentations"].append(
            {
                "end_time": seg["stop"],
                "start_time": seg["start"],
                "transcription": hyp
            }
        )
    return 0

def upload_audio(config: dict, seg=True):
    audio_path = Path(config['audio_file'])
    audio_filename = audio_path.name

    if audio_path.is_file():
        audio_obj = open(audio_path.resolve(), "rb")
    else:
        print("Audio file does not exist")
        exit()

    file = {"audio_file": (audio_filename, audio_obj)}
    headers = {"Authorization": config['api_key']}
    values = {
        "reference_transcription": config['reference_transcription'],
        "username": config['username'],
        "is_marked_for_review": config['is_marked_for_review']
    }

    if seg:
        values["segmentations"] = json.dumps(config['segmentations']),

    print("Creating datapoint")
    response = requests.post(
        "http://{}:{}/api/data".format(config['host'], config['port']), files=file, data=values, headers=headers
    )

    if response.status_code == 201:
        response_json = response.json()
        print(f"Message: {response_json['message']}")
    else:
        print(f"Error Code: {response.status_code}")
        response_json = response.json()
        print(f"Message: {response_json['message']}")
    return 0

if __name__ == "__main__":
    config_1 = CONFIG 
    status = get_segmentations(config_1)
    print("Get segmentations, status: {}".format(status))
    for key, val in config_1.items():
        print("{} : {}".format(key, val))

    status = upload_audio(config_1)
    print("Upload data to label-system, status: {}".format(status))
