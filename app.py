import os
from pytube import Playlist, YouTube
from pytube.exceptions import RegexMatchError
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Function to download the video or all tracks in a YouTube playlist
def download_content(url: str):
    if 'playlist' in url:
        download_playlist_tracks(url)
    else:
        download_single_video(url)

# Function to download a single video
def download_single_video(video_url: str):
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        mp3_filename = f'{yt.title}.mp3'
        audio_stream.download(output_path='downloads', filename='temp')
        os.rename(os.path.join('downloads', 'temp.mp4'), os.path.join('downloads', mp3_filename))
    except RegexMatchError:
        raise HTTPException(status_code=400, detail="Invalid video URL or video not available")

# Function to download all tracks in a YouTube playlist
def download_playlist_tracks(playlist_url: str):
    playlist = Playlist(playlist_url)
    for video in playlist.video_urls:
        try:
            yt = YouTube(video)
            audio_stream = yt.streams.filter(only_audio=True).first()
            mp3_filename = f'{yt.title}.mp3'
            audio_stream.download(output_path='downloads', filename='temp')
            os.rename(os.path.join('downloads', 'temp.mp4'), os.path.join('downloads', mp3_filename))
        except RegexMatchError:
            print(f"Skipping invalid video URL in the playlist: {video}")

@app.post('/download')
async def download(url: str = Form(...)):
    try:
        download_content(url)
        return {'message': 'Download started successfully.'}
    except Exception as e:
        return {'error': str(e)}

@app.get('/')
async def get_home():
    return FileResponse('static/index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
