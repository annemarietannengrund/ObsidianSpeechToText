# Project Overview

Obsidian Speech-to-Text Converter (OSTTC) is a "pet project" that i started while playing around with 
[obsidian.md](https://obsidian.md/) built in audio recordings feature.

Obsidian is a personal powerful note taking tool, this by itself is an understatement, but correcting it 
to the full extend would fill the whole document.

In case you are already interested, this is a built in feature you can activate via 
`preferences/settings` > `Obsidian-Extensions` > `Audio-Recorder`.

i wanted to have the audio files transcribed to text, ideally to markdown so i can make use of it in obsidian.
After all, being able to search my audio recordings with `line:(search term)` would be awesome on its own.

this here is the lovechild of couple of days of iterations.

## intended/probable usages
many ideas come to mind for the possible use cases.
this seems extremely useful for people not having a good possibility to write or writing is cumbersome.
or adhs people that forget what activities they did during the day or any other way.
The model is good enough to handle either fast, slow or slurry spoken audio.

## Prerequisites

### Local
prepare a virtual environment (recommended!) for python 3.8+.

```
pip install -r requirements.txt
```

### Docker
Install Docker from [Dockerhub.com](https://hub.docker.com/), as it is required.
please touch the file [docker-compose.yml file](docker-compose.yml) and modify this mounting line to point 
to your dedicated recordings directory within obsidian.

if you dont adapt this line, the local `recordings` folder will be mounted into docker and used as input folder.

```
# linux/mac
- /path/to/your/obsidian/audios:/data
# or on win, the quotes around the whole line is recommended here!
- "C:/path/to/your/obsidian/audios:/data"
```

## Configuration
The script offers various ways to influence the configuration.

The order is `keyword argument` > `environment variables` > `default values`

### Your Voice
Yes, your voice is a configuration tool for whisper (the offline model) at least.

- Slow Speaking & Speaking with pauses => more usage of punctuations.
- fast Speaking => more usage of commas.
- emphasizing on a word/sentence with force (exclamation) => more usage of exclamation marks.
- emphasizing on a word/sentence with high pitched end (question) => more usage of question marks.

### Environment .env files
The script is also supporting .env files, just rename the `template.env` to `.env` and adapt the values to your needs.
the environment variables are mainly used by docker for the RUNS_ON_DOCKER flag that is set during build.

all environment variables used by the script are prefixed with `OSTTC_`.

### Configuration Parameters


| Environment name      | Argument Name   | Purpose                                                                        | Default                  | values                                                                                    |
|-----------------------|-----------------|--------------------------------------------------------------------------------|--------------------------|-------------------------------------------------------------------------------------------|
| `OSTTC_LANGUAGE`      | `LANGUAGE`      | Helping the model define the language it hears for best results.               | `de`                     | `de`, `de-DE`, `en-UK`.                                                                   |
| `OSTTC_MODEL_SIZE`    | `MODEL_SIZE`    | Bigger is better, smaller is faster, tradeoff between quality and performance, | `medium`                 | `tiny.en`, `tiny`, `base.en`, `base`, `small.en`, `small`, `medium.en`, `medium`, `large` |
| `OSTTC_KEYWORDS`      | `KEYWORDS`      | toggles the postprocessing of transcribed text to apply voice commands.        | `1`                      | `0`, `1`.                                                                                 |
| `OSTTC_USE_OFFLINE`   | `USE_OFFLINE`   | toggles between offline (whisper) and online (google)                          | `0`                      | `0`, `1`.                                                                                 |
| `OSTTC_OVERWRITE`     | `OVERWRITE`     | precesses valid audiofiles regardless of existing out file.                    | `1`                      | `0`, `1`.                                                                                 |
| `OSTTC_LOCAL_PATH`    | `LOCAL_PATH`    | Your local path to a directory holding audio files for transcription           | `./recordings`           | `string` path to a folder                                                                 |
| `OSTTC_SOURCE_STRING` | `SOURCE_STRING` | any expected inpit filename format you have to extract datetime dates          | `Recording %Y%m%d%H%M%S` |                                                                                           |
| `OSTTC_TARGET_STRING` | `TARGET_STRING` | best aligned with your preferred obsidian config                               | `%Y-%m-%d-%H-%M.md`      |                                                                                           |
| `OSTTC_MEDIA_FILES`   | `MEDIA_FILES`   | append new file endings if curious                                             | `.webm,.mp3,.wav,.m4a`   |                                                                                           |

For language codes see:
- [supported Google Language Codes](https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages?hl=de) 
- [supported Whisper Language Codes](https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages)


## Execution
The plain call relies either on default values or environment variables from the `.env` file.

```
docker-compose up
# or
python main.py
```

To influence variables you can either use argument's or pass new environment variables 
```
# using a custom path in docker by modifying 
docker-compose run --rm -e OSTTC_LOCAL_PATH=/my/other/path convert

docker-compose run --rm convert --kwargs OPTION1=33 OPTION2=/my/path OPTION3=45
python main.py --kwargs OPTION1=33 OPTION2=/my/path OPTION3=45
```

## features
The OSTTC comes with a handful of features you might like ;)

### custom filename handling
This features is by default built for the obsidian default for naming files, markdown daily logs or audio recordings.

touch this in case you have some 3rd party recording tool that may format filenames differently.

i.e. lets assume I have some cheap standalone dictating device 
that stores its files in this format: `SomyWalkboy-23-03-2003.mp3`.
you can ignore the file extension, in the code this is omitted for better processing.

if you want to preserve the date as base for your markdown files you need to adapt the source pattern.
```
python main.py --kwargs SOURCE_STRING=SomyWalkboy-%d-%m-%Y
docker-compose -f docker-compose.yml run --rm convert --kwargs SOURCE_STRING=SomyWalkboy-%d-%m-%Y

# and since you dont have any indication of hours or minutes in this example, you should omit these in the target.
this step is optional, if you dont do this the values will just end in 0.
python main.py --kwargs TARGET_STRING=%Y-%m-%d.md
docker-compose -f docker-compose.yml run --rm convert --kwargs TARGET_STRING=%Y-%m-%d.md
```

The target format gets important when you use a different format then the obsidian default.
so instead of Y-m-d you might use d-m-Y, then you can influence the output format to match your existing markdown files.

see also what to do if you are having multiple 
file name formats in your audio folder [here](#a-mixed-source-string-date-file-name-pattern-folder).

### language code parameters
Have your language better understood by customizing it according to the audio source you have at hand.

you can now pass a language codes longer than 2 characters.
I havent checked the behavior for whisper, but this should enable a more 
custom language for the usage of the google translator.

when you pass in a 2 letter code the script will adapt it for google in a limited fashion like so: `de` -> `de-DE`
the 2 letter code is the main focus since its the standard used by openai's whisper model which I favor.

### Action Keywords
Action Keywords are this tools way of formatting a transcribed text by commands said during the recording.
the default action keywords are contained in `Config.ACTION_KEYWORDS` in `main.py::Config` along with a short
regular expression tutorial for people that want to build up on that.

for deactivation see [here (environment)](#use-keywords) or [here (argument)](#use-keywords-1)

in general I discovered that codewords within natural text are a bit tricky, here's why.
you may tend to want short codewords like "stop", but these codewords wil manipulate that exact word in the process.

so you can now not say the word "stop" anymore without it being replaced.
this could also be a wanted feature like etend "dsdm" to "dear sir or madam" everytime.

the problem is the line between similarities to other words should be clear.
okay, enough, here is what I have come up with:

we face 2 types of commands (elements) that we make use of in a markup language
- single commands
- pairwise commands

single commands are like "line break", "list item dash" or similiar, equivalent to html's tag's `<br/>`.
double commands are so to speak 1 level harder than single ones.

to handle them better I had to introduce a command prefix `obsidian`, 
then comes the type `link` and then the action `start` to produce obsidians internal `[[` link start.

after all, this is fully customizable, you pick the words, the replacements, the regular expressions.

## Roadmap
### Tag keyword action
being able to add tags to a markdown from the audiofile.

## Known Issues
Issues known and anticipated.
### Docker Performance
the Docker performance on my m2 macbook air is terrible, I prefer to run the script locally.
maybe there is a better fix, but as far as I know docker on mac has no form of gpu support
and its all done by CPU through multiple layers of virtual and real shared components.

if you want to make this run faster on docker, you will need to dig into enabling host 
GPU/CUDA support for your docker container yourself.

also you'll need a RTX enabled nvidia geforce card to have CUDA available.

a switch to a x86 architecture might also have massive performance impact positively speaking.
### whisper pip
im unsure if it was a quirk during development, but I am conflicted between the pip `openai-whisper` module
and the git hosted version.

all sources recommend checking out [the git version](https://github.com/openai/whisper) and installing that with pip.
but code was at some point missing the load_model() method of the whisper package.
so I checked out `pip install openai-whisper` which made the method available again.

so, in the pypI wheel it is there, in the git version it seems to fail.
in the git docs in the examples, they also use the method, so I hope it was just some quirk in the night.
### whisper pip model
everytime I ran the fresh containerized project, when I ran the converter, it downloaded the whisper model.
"that is not a sustainable workflow" I thought to myself.

there where multiple solutions
1. hadbaking wget with the models into the makefile. (NOPE, this would also pinned version numbers and checksums, stuff that whisper handles itself)
2. pre-bake an image that contains the models to be used (NOPE, never done that, stumbled over some overachieving stuff, too much effort)
3. share a directory with the host machine to persist the models during runs (YEP! thats why you have a `models` folder in the project directory) 

### google
Since the scope of the project tends to my favorite flavor, I do prefer the local model over google.
the google implementation was just so small that I added it and I do not plan on digging deeper on this route.

the local models achieve astonishing results, including punctuation, which apparently google lacks completely.
all google translations do not contain any punctuations, commas, question or exclamation marks.

I can not recommend the google thingy unless you are fine with sharing your texts with google and can work with
free flowing text.

if thats the case, you can profit from the speed of the google API which is probably superior to your local potato.
### Video Files
This has not yet been considered or tested.
the strength of this tool comes from the action keywords. so you can format the text at least in a rudimentary way.
so any youtube video one can transcribe will not contain these words, so one can end up with a flowing text 
transcription of a 30 minute video with nonstop talking.

this isnt fun and completely ignores that when you already got a yt video, you also could get the subtitles from yt.
assuming it's about a youtube video...

### a mixed source string date file name pattern folder
I am not willing to solve this programmatically, this is painlessly solvable by separate directory's and custom calls
of this tool.

set up a recording folder for each device that has a non obsidian like standard, then shortcut your script arguments
to define the PATH, SOURCE_STRING and TARGET_STRING.