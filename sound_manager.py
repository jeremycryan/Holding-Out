import pygame


class SoundManager:
    """
    Static class to handle loading of pygame surfaces to improve performance
    """

    initialized = False
    sounds = None

    @staticmethod
    def init():
        SoundManager.initialized = True
        SoundManager.sounds = {}

    @staticmethod
    def check_initialized():
        if not SoundManager.initialized:
            raise Exception("Must call ImageHandler.init() before any other methods.")

    @staticmethod
    def clear(path):
        """
        Forgets one thing.
        :param path: The path of the file to remove from memory
        :return:
        """
        SoundManager.check_initialized()
        if path in SoundManager.sounds:
            del SoundManager.sounds[path]

    @staticmethod
    def clear_all():
        """
        Forgets everything
        """
        SoundManager.check_initialized()
        SoundManager.sounds = {}

    @staticmethod
    def load(path):
        """
        Loads a surface from file or from cache
        :param path: The path of the image
        :return: The surface. This is likely the same reference others are using, so don't be destructive.
        """
        SoundManager.check_initialized()
        if path in SoundManager.sounds:
            return SoundManager.sounds[path]
        sound = pygame.mixer.Sound(path)
        SoundManager.sounds[path] = sound
        return sound
