# Lossless Precise Cut

## Dependencies
- pyaaf2 for parsing aaf file
- edl for parsing edl file

## Usage

1. You can use cli.py to get a interactive guide
2. You can use (edf|aaf)_handler.py to non-interactively use this tool
3. You can use cmd_handler.py to manually special the inpoint and outpoint then cut the file

## How does it works

I learned the trick from a [StackOverflow Answer](https://video.stackexchange.com/questions/23533/can-you-losslessly-ediit-h264-at-the-gop-level)
The main idea is to retrive the first segment and the last segment, re-encode it to the needed duration, and then concat it with the main body. 
In this way we can preserve as much GOP as possible, so the process would be VERY fast and *almost* lossless