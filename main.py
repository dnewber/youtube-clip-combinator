#!/usr/bin/env python3

import csv
import argparse

from pytube import YouTube
from moviepy.editor import VideoFileClip
from moviepy.editor import concatenate_videoclips


def main():
    parser = argparse.ArgumentParser(description='YouTube Clip Combinator')
    parser.add_argument(
        dest='playlist',
        type=str,
        help='Path to your playlist csv.')
    args = parser.parse_args()
    process_playlist(args.playlist)


def process_playlist(playlist_filename):
    clips = []
    with open(playlist_filename) as fp:
        reader = csv.DictReader(fp)
        for video in reader:
            print('Processing clip: ', video['url'])
            filename = download_video(video['url'])
            clip = VideoFileClip(filename)
            if video['start'] or video['end']:
                clip = clip.subclip(int(video['start']), int(video['end']))  # Todo: convert times to seconds for me
            clips.append(clip)
    print('Combining clips:\n', clips)
    concat_videos(clips)
    print('Video Complete.')
    # Todo: cleanup clips when done


def download_video(url, destination=None, filename=None):
    # todo: handle deleted videos
    video = YouTube(url).streams.first()
    video.download(output_path=destination, filename=filename)
    return video.default_filename


def concat_videos(videos):
    try:
        combined = concatenate_videoclips(videos)
        combined.write_videofile("final.mp4", audio_codec="aac")
    except Exception:
        print('Something went wrong.')
        import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    main()
