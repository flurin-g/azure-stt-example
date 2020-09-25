# azure-stt-example

## Start the container
To start the container, enter:
```
docker run --rm -it -p 5000:5000 --memory 4g --cpus 4 \
mcr.microsoft.com/azure-cognitive-services/speechservices/speech-to-text \
Eula=accept \
BILLING=<azure billing url> \
APIKEY=<api key>
```

## Run the script

To only transcribe the firs word run:

`python main.py --mode once`

To transcribe the whole audio file:

`python main.py --mode continuous`

If you only want to see complete utterances without the intermediate results:

`python main.py --mode continuous --show utterance`

## Audio file
Per default the file `mary_and_sarah.wav` will be transcribed, 
if you want to use another file instead, place it in the data-folder
and specify it as an argument, like so:

`python main.py --mode once --file mary_and_sarah.wav`

