from .misc import run_command

def video_length(video_path) -> float:
    process = run_command((
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path
    ))
    if process.ret: raise Exception(f'FFmpeg error: {process.err.decode("utf-8")}')
    return float(process.out)

def video_size(video_path):
    process = run_command((
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', video_path
    ))
    if process.ret: raise Exception(f'FFmpeg error: {process.err.decode("utf-8")}')
    return tuple(map(int, process.out.decode('utf-8').strip().split('x')))

def has_audio(video_path):
    process = run_command((
        'ffprobe', '-i', video_path, '-show_streams', '-select_streams', 'a', '-v', 'error'
    ))
    if process.ret: raise Exception(f'FFmpeg error: {process.err.decode("utf-8")}')
    return bool(process.out)