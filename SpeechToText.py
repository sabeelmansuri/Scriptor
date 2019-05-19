##
# Takes in directory to 
# Remember to set "GOOGLE_APPLICATION_CREDENTIALS" in current session. 
# <export GOOGLE_APPLICATION_CREDENTIALS="/home/nikhilpathak/CSE110/Scriptor-c224a4acbb7a.json">
# <export GOOGLE_APPLICATION_CREDENTIALS="/Users/Pranav/CSE110/Scriptor/GoogleSpeechAPI/Scriptor/*.json">
# Requires sox ("sudo apt-get install sox" + "sudo apt-get install libsox-fmt-all")
#
# Citation: This code is heavily reliant upon https://towardsdatascience.com/how-to-use-google-speech-to-text-api-to-transcribe-long-audio-files-1c886f4eb3e9 and Google Tutorials
##

# Import libraries
from pydub import AudioSegment
import io
import sys
import os
import json
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import wave
from google.cloud import storage



# Change environment variables depending on whoever is using the API on their local machine
#PATHTOAUDIOFILE = "/home/nikhilpathak/CSE110/Scriptor/PodcastAudios/" 
PATHTOAUDIOFILE = sys.argv[1]
BUCKETNAME = "audiofilesscriptor"

NUMBEROFWORDSPERBLURB = 70

# AUDIOFILENAME = "cse101_c00-05162019-0930.mp3"
# AUDIOFILEOUTPUT = "cse101_c00-05162019-0930.flac"
# PATHTOAUDIOFILE = "/Users/Pranav/CSE110/Scriptor/GoogleSpeechAPI/Scriptor/resources/" 
# BUCKETNAME = "scriptor"


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()

bucket_name = BUCKETNAME

if not os.path.isdir(PATHTOAUDIOFILE + "JSONS"):
     os.mkdir(PATHTOAUDIOFILE + "JSONS")

for fileName in os.listdir(PATHTOAUDIOFILE):
     if not fileName.endswith(".mp3"):
          continue
     
     print()
     print("Working on " + fileName + "...")
     audio_file_name = fileName
     audio_file_output = fileName.split(".mp3")[0] + ".flac"

     file_name = PATHTOAUDIOFILE + audio_file_output

     source_file_name = PATHTOAUDIOFILE + audio_file_name
     output_file_name = PATHTOAUDIOFILE + audio_file_output
     destination_blob_name = audio_file_output

     print("Turning MP3 file into FLAC file...")
     os.system("sox " + source_file_name + " --rate 16k --bits 16 --channels 1 " + output_file_name)
    
     print("Uploading to Google Cloud Storage bucket...")
     upload_blob(bucket_name, output_file_name, destination_blob_name)

     print("Running Google Speech-To-Text API...")
     gcs_uri = 'gs://' + bucket_name + '/' + audio_file_output
     transcript = ''
    
     client = speech.SpeechClient()
     audio = types.RecognitionAudio(uri=gcs_uri)

     config = types.RecognitionConfig(
             encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
             sample_rate_hertz=16000,
             language_code='en-US',
             enable_word_time_offsets=True, 
             enable_automatic_punctuation=True)

     operation = client.long_running_recognize(config, audio)
     response = operation.result(timeout=10000)

     blurbMap = dict()
     fullTranscript = ''
     currBlurb = ''
     currStartTime = None
     currEndTime = None
     numWordsInCurrBlurb = 0
     for result in response.results:
          alternative = result.alternatives[0]
          textBlurb = alternative.transcript

          fullTranscript += textBlurb + " "

          for wordInfo in alternative.words:
               word = wordInfo.word
               if numWordsInCurrBlurb == 0:
                    currStartTime = wordInfo.start_time.seconds + wordInfo.start_time.nanos * 1e-9
                    if currStartTime is None: #first word of video
                         currStartTime = 0.0
        
               currBlurb += word + " "
               numWordsInCurrBlurb += 1

               currEndTime = wordInfo.end_time.seconds + wordInfo.end_time.nanos * 1e-9
               if numWordsInCurrBlurb == NUMBEROFWORDSPERBLURB:
                    blurbMap[currBlurb] = (currStartTime, currEndTime)

                    currBlurb = ''
                    numWordsInCurrBlurb = 0

     if numWordsInCurrBlurb != 0:
          blurbMap[currBlurb] = (currStartTime, currEndTime)
             

     #HERE WE HAVE ACCESS TO FULL TRANSCRIPT (fullTranscript) AND DICT (blurbMap) FOR BLURBS OF 70 WORDS TO TUPLE OF (STARTTIME, ENDTIME)
     #EXPORT JSON HERE
     print("Exporting to JSON file...")
     json_out = {}

     # # Creating json file name
     file_prefix = audio_file_output.split(".")
     json_file = file_prefix[0] + ".json"

     # # Parsing mp3 file name for metadata
     metadata = audio_file_output.split("_")

     class_name = metadata[0]
     section_date_time = metadata[1].split("-")

     section = section_date_time[0]
     date = section_date_time[1]
     time_raw = section_date_time[2].split(".")
     time = time_raw[0]

     # Create Python Dictionary
     json_out["Class Name"] = class_name
     json_out["Section"] = section
     json_out["Date"] = date
     json_out["Time"] = time
     json_out["Full Transcript"] = fullTranscript
     json_out["Blurbs"] = blurbMap

     # Convert from Python Dict to JSON object
     json_data = json.dumps(json_out, indent=4, sort_keys=True)

     # Write to .json file
     with open(PATHTOAUDIOFILE + "JSONS/" + json_file, 'w') as f:
     	f.write(json_data)

     print("Deleting from Google Storage Bucket...")
     delete_blob(bucket_name, destination_blob_name)

     print()
