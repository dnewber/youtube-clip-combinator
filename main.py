#!/usr/bin/env python3

import csv
import argparse

from pytube import YouTube, Playlist
from moviepy.editor import VideoFileClip
from moviepy.editor import concatenate_videoclips


def main():
    parser = argparse.ArgumentParser(description='YouTube Clip Combinator')
    parser.add_argument(
        '--playlist',
        dest='playlist',
        type=str,
        default=None,
        help='Path to your playlist csv.')
    parser.add_argument(
        '--convert',
        dest='convert',
        type=str,
        default=None,
        help='Convert a youtube playlist URL to a csv.')
    args = parser.parse_args()

    if args.convert:
        playlist_csv = generate_playlist(args.convert)
        print('Playlist file created: {}'.format(playlist_csv))

    if args.playlist:
        process_playlist(args.playlist)


def generate_playlist(url, filename='playlist.csv'):
    playlist = Playlist(url)
    playlist.populate_video_urls()
    with open(filename, 'w') as fp:
        wrt = csv.writer(fp)
        header = ['url', 'start', 'end']
        wrt.writerow(header)
        for url in playlist.video_urls:
            wrt.writerow([url, '', ''])
    return filename


def process_playlist(playlist_filename):
    clips = []
    with open(playlist_filename) as fp:
        reader = csv.DictReader(fp)
        for video in reader:
            print('Processing clip: ', video['url'])
            filename = download_video(video['url'])
            if not filename:  # Video or user was deleted
                continue
            clip = VideoFileClip(filename)
            if video['start'] or video['end']:
                clip = clip.subclip(int(video['start']), int(video['end']))
            if clip.w < 720:
                clip = clip.resize(height=720)
            clips.append(clip)
    print('Combining clips:\n', clips)
    concat_videos(clips)
    print('Video Complete.')
    # Todo: cleanup clips when done


def download_video(url, destination=None, filename=None):
    try:
        video = YouTube(url).streams.filter(progressive=True).order_by('resolution').desc().first()
        video.download(output_path=destination, filename=filename)
        return video.default_filename
    except Exception:
        print('{} - Video unavailable. Skipped.'.format(url))
        return None


def concat_videos(videos):
    try:
        combined = concatenate_videoclips(videos, method="compose")
        combined.write_videofile("final.mp4", codec="mpeg4", audio_codec="aac")
    except Exception as e:
        print('Something went wrong: ', e)


if __name__ == '__main__':
    main()
