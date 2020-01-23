import sys
import youtube_dl
from youtube_dl import *


if __name__ == '__main__':
def main(link):
    yt=YoutubeDL(link)
    
    video=yt.get_encoding()
