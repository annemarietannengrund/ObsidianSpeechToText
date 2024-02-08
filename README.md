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

see my [personal benchmarking script](Test-Talk-Script.md) and the [obsidian markdown file created](Test-Talk-Result.md).

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
Yes, your voice is a configuration tool for whisper.

- Slow Speaking & Speaking with pauses => more usage of punctuations.
- fast Speaking => more usage of commas and spaces between words.
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
| `OSTTC_OVERWRITE`     | `OVERWRITE`     | precesses valid audiofiles regardless of existing out file.                    | `1`                      | `0`, `1`.                                                                                 |
| `OSTTC_LOCAL_PATH`    | `LOCAL_PATH`    | Your local path to a directory holding audio files for transcription           | `./recordings`           | `string` path to a folder                                                                 |
| `OSTTC_SOURCE_STRING` | `SOURCE_STRING` | any expected inpit filename format you have to extract datetime dates          | `Recording %Y%m%d%H%M%S` |                                                                                           |
| `OSTTC_TARGET_STRING` | `TARGET_STRING` | best aligned with your preferred obsidian config                               | `%Y-%m-%d-%H-%M.md`      |                                                                                           |
| `OSTTC_MEDIA_FILES`   | `MEDIA_FILES`   | append new file endings if curious                                             | `.webm,.mp3,.wav,.m4a`   |                                                                                           |

For language codes see:
- [supported Whisper Language Codes](https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages)

the whisper model uses a 2 letter language code system!

### Action Keywords

Action keywords are a sequence of characters that are extracted from the transcribed audio file and processed by
regular expressions.

the flow here is:
1. you say a existing keyword (sequence) in the audio recording
2. audio recording gets transcribed to text
3. all action keywords regular expression replacements get applied (i.e.: "Line Break." => "\n"

#### Components
The Action Keywords are triggered by one word or a sequence of words whose 
transcription should then match a regular expression.

There are 3 types of action keyword components.

##### Master Keyword
In case your action is so common that you want to make sure it doesn't accidental replaces something you didnt want to.

The default master `ACTION_KEYWORD` is `Obsidian`, this keyword has the same meaning as Star Trek's famous `Computer` keyword (or `hey siri`, `hey google`, etc)

##### Action Type Keyword

Defines a `ACTION_TYPE_*` you want to execute, multiple possible keywords are seperated by pipe "|" and can be further
enhanced with regeular expressions.

| ACTION_TYPE                            | values       | Description                                                                                                                 |
|----------------------------------------|--------------|-----------------------------------------------------------------------------------------------------------------------------|
| `ACTION_TYPE_LINK`                     | `link`       | Used for Obisian's `[[` and `]]` link syntax. [is a paired element](#action-type-start-end-paired-elements)!                |
| `ACTION_TYPE_TAGS`                     | `text\|tech` | Used for Obisian's file property tag's. [is a paired element](#action-type-start-end-paired-elements)!                      |
| `ACTION_TYPE_CITATION`                 | `xxxx`       |                                                                                                                             |
| `ACTION_TYPE_DIVIDER`                  | `xxxx`       |                                                                                                                             |
| `ACTION_TYPE_HEADLINE`                 | `xxxx`       |                                                                                                                             |
| `ACTION_TYPE_LINEBREAK`                | `xxxx`       |                                                                                                                             |
| `ACTION_TYPE_LONG_DASH`                | `xxxx`       |                                                                                                                             |
| `ACTION_TYPE_LIST_ELEMENT`             | `xxxx`       |                                                                                                                             |
| `ACTION_TYPE_CHECKED_CHECKBOX_ELEMENT` | `xxxx`       |                                                                                                                             |
| `ACTION_TYPE_CHECKBOX_ELEMENT`         | `xxxx`       |                                                                                                                             |
| `ACTION_TYPE_BADWORDS`                 | `xxxx`       |                                                                                                                             |
| `ACTION_TYPE_HASHTAG`                  | `xxxx`       |                                                                                                                             |
| `ACTION_TYPE_AUDIO_FILE_LINK`          | `xxxx`       | Flag. if detected in text it add's a file property "audiolog" with a link to the source audio and a banged link at the top |


##### Action Type start-end paired elements

#### Default Composition

| Phrase | Gets replaced with | Description |
|--------|--------------------|-------------|
| `xxx`  | `yyy`              |             |


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

## Features
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

### Action Keywords Concept
RE-DO me again!

## Feature Roadmap
- [x] Runs out-of-the box ([see](#execution)).
- [x] Being able to add tags (inline) to a markdown from the audiofile.
- [x] Being able to add tags (header) to a markdown from the audiofile.
- [x] Handle custom filename date extraction/matching  ([see](#custom-filename-handling)).
- [x] Have all moving parts configurable via arguments or environment ([see](#configuration-parameters)).
- [x] Action keyword adds audiofile link into markdown.
- [x] Bad word/foul language filter.
- [x] Freely configurable actions and action keywords.
- [x] Traverses the whole given audio recordings directory inclusive sub-folders.
- [ ] Predefined set of tags that is added to all created files of a script run
- [ ] Write tests
- [ ] Clean up code. the proof of concept grew out of its simple script stage.
- [ ] Also run a linter across the project

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
1. hard baking wget with the models into the makefile. (NOPE, this would also pinned version numbers and checksums, stuff that whisper handles itself)
2. pre-bake an image that contains the models to be used (NOPE, never done that, stumbled over some overachieving stuff, too much effort)
3. share a directory with the host machine to persist the models during runs (YEP! thats why you have a `models` folder in the project directory) 

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