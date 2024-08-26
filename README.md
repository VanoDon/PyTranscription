# PyTranscription
Transcribe your audio to text.


A python front-end for OpenAI's Whisper using Groq.

Very makeshift and WIP. Currently you need to put ffmpeg and ffmpeg probe next to the compiled binary / python script.
Give it an api key (optionaly save in plain text)

Choose an audio file and transcribe. When it is complete it will allow you to choose a name and location for your transcription.

Note Command prompt windows / black boxes are ffmpeg a command line tool for converting media, and the library I use for spliting the audio to chucks has the side effect of ffmpeg not run silently. The GUi isnt multi threaded so the progress bar wont move while transcribing.

This is a hobby project, I do aim to make improvements. Contributions are welcome.
