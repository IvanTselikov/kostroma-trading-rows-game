# from moviepy.editor import *
import cv2
from PIL import Image, ImageSequence
import shutil
import os
import speech_recognition as sr  # pip install SpeechRecognition
import subprocess
from moviepy.video.io.VideoFileClip import VideoFileClip
import config as cfg


class MediaConverter:
    def __init__(self):
        pass

    def loadVideo(self, fname):
        ''' Ищет видео по указанному пути или с указанной камеры.'''
        video = cv2.VideoCapture(fname)
        counter = 300
        while counter > 0 and not video.isOpened():  # для файлов должно сработать сразу
            cv2.waitKey(10)
            counter -= 1
        if counter == 0:
            raise IOError('Failed to open video.')
        return video

    def changeVideoResolution(self, path, resolution): 
        # путь к файлу, кортеж - разрешение (напр. (480, 480)), новое имя (с расширением файла)
        vid = self.loadVideo(path)
        height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        if height==width and height<=640 :
            return
        extension = self.getFileExtension(path)
        supportFileName = self.getFilePathWithoutFname(path)+"supportFile"+extension
        shutil.copy(path, supportFileName)
        video = VideoFileClip(path)
        result = video.resize(resolution)
        result.write_videofile(supportFileName)
        vid.release()
        os.remove(path)
        shutil.copy(supportFileName, path)
        os.remove(supportFileName)

    def changeImageResolution(self, path, resolution): 
        # путь к файлу, кортеж - разрешение (напр. (480, 480)), новое имя (с расширением файла)
        extension = self.getFileExtension(path)
        supportFileName = self.getFilePathWithoutFname(path)+"supportFile"+extension
        shutil.copy(path, supportFileName)
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        result = cv2.resize(image, resolution)
        cv2.imwrite(supportFileName, result)
        os.remove(path)
        shutil.copy(supportFileName, path)
        os.remove(supportFileName)

    def changeGIFResolution(self, path, resolution):  
        extension = self.getFileExtension(path)
        supportFileName = self.getFilePathWithoutFname(path)+"supportFile"+extension
        shutil.copy(path, supportFileName)
        gif = Image.open(path)
        frames = ImageSequence.Iterator(gif)
        frames = self.thumbnails(frames, resolution)
        om = next(frames) # Handle first frame separately
        om.info = gif.info # Copy sequence info
        om.save(supportFileName, save_all=True, append_images=list(frames), loop=0)
        os.remove(path)
        shutil.copy(supportFileName, path)
        os.remove(supportFileName)


    def thumbnails(self, frames, resolution): # вспомогательная функция
        # Output (max) size
        #size = 320, 240
        #size = resolution
        for frame in frames:
            thumbnail = frame.copy()
            #thumbnail.thumbnail(size, Image.ANTIALIAS)
            thumbnail = thumbnail.resize(resolution)
            yield thumbnail

    def getFileExtension(self, path):
        lastDotIndex = path.rindex(".")
        return path[lastDotIndex:]

    def getFilePathWithoutFname(self, path):
        try:
            lastIndexOfSlash = path.rindex("/")
        except:
            lastIndexOfSlash = 0
        return path[:lastIndexOfSlash]


    UNKNOWN = '#'
    def voiceToText(self, audio_ogg):
        audio_wav = audio_ogg + '.wav'
        command = f'{cfg.FFMPEG_PATH}*-loglevel*quiet*-i*{audio_ogg}*-y*-c:a*pcm_s16le*{audio_wav}'
        process = subprocess.run(command.split('*'))
        r = sr.Recognizer()
        with sr.AudioFile(audio_wav) as source:
            audio = r.record(source)
        try:
            text = r.recognize_google(audio, language = 'ru-RU')
        except:
            text = self.UNKNOWN
        os.remove(audio_wav)
        os.remove(audio_ogg)
        return text


    def convertToOgg(self, path):
        """Конвертирует файл в формат .ogg и возвращает путь до нового файла."""
        new_path, fmat = os.path.splitext(path)
        new_path += '.ogg'
        if fmat == '.mp3':
            command = f'{cfg.FFMPEG_PATH}*-loglevel*quiet*-i*{path}*-y*-c:a*libvorbis*-q:a*4*{new_path}'
        elif fmat == '.wav':
            command = f'{cfg.FFMPEG_PATH}*-loglevel*quiet*-i*{path}*-y*-acodec*libvorbis*{new_path}'
        else:
            raise Exception(f'Не удалось преобразовать {path} к формату голосового сообщения.')
        process = subprocess.run(command.split('*'))
        return new_path


    def convertToMp3(self, path):
        """Конвертирует файл в формат .mp3 и возвращает путь до нового файла."""
        new_path, fmat = os.path.splitext(path)
        new_path += '.mp3'
        if fmat == '.wav' or fmat == '.ogg':
            command = f'{cfg.FFMPEG_PATH}*-loglevel*quiet*-i*{path}*-y*-acodec*libmp3lame*{new_path}'
        else:
            raise Exception(f'Не удалось преобразовать {path} к формату .mp3.')
        process = subprocess.run(command.split('*'))
        return new_path
