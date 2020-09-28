# This example shows how to use the Azure STT container
# Examples are taken from:
# https://docs.microsoft.com/en-gb/azure/cognitive-services/speech-service/get-started-speech-to-text?tabs=script%2Cwindowsinstall&pivots=programming-language-python
import json
import time
import azure.cognitiveservices.speech as speechsdk
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('once', 'continuous'))
    parser.add_argument('--show', choices=('all', 'utterance'), default="all")
    parser.add_argument('--file', default="mary_and_sarah.wav")
    args = parser.parse_args()
    return args


def recognize_once(file_name: str):
    # set address of container
    speech_config = speechsdk.SpeechConfig(host="ws://localhost:5000")

    # use file for stt:
    audio_input = speechsdk.AudioConfig(filename=f"data/{file_name}")

    # instantiate speech_recognizer
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    # start recognizing
    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))


def recognize_continuous(show: bool, file_name):
    # use file for stt:
    audio_input = speechsdk.AudioConfig(filename=f"data/{file_name}")

    # set address of container
    speech_config = speechsdk.SpeechConfig(host="ws://localhost:5000")

    # request timing info
    speech_config.request_word_level_timestamps()

    # state of job, once finished == true
    done = False

    # instantiate speech_recognizer
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    def stop_cb(evt) -> None:
        """
        callback to stop continuous recognition when an event is received
        :param evt: event
        """
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        done = True

    def formatted_json(stt_json):
        stt_json = json.loads(stt_json)
        confidences_in_nbest = [item["Confidence"] for item in stt_json["NBest"]]
        best_index = confidences_in_nbest.index(max(confidences_in_nbest))
        words = stt_json["NBest"][best_index]["Words"]
        display_text = stt_json["NBest"][best_index]['Display']
        raw_words = [x['Word'] for x in stt_json["NBest"][best_index]["Words"]]
        return f'words: {words}\ndisplay text: {display_text}\nraw words: {raw_words}'

    # Signal for events containing intermediate recognition results
    if show == "all":
        speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))

    # Signal for events containing final recognition results (indicating a successful recognition attempt)
    # original snippet from azure examples
    #speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))

    # test method, to see all the json-fields
    speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(formatted_json(evt.result.json))))

    # Signal for events indicating the start of a recognition session (operation).
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))

    # Signal for events indicating the end of a recognition session (operation).
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))

    # Signal for events containing canceled recognition results (indicating a recognition attempt that was canceled
    # as a result or a direct cancellation request or, alternatively, a transport or protocol failure)
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))

    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start the actual transcription job
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)


if __name__ == '__main__':
    args = get_args()
    if args.mode == "once":
        recognize_once(args.file)
    elif args.mode == "continuous":
        recognize_continuous(args.show, args.file)
    else:
        print("Specify mode: either once or continuous")


