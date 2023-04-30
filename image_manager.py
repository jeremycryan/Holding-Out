import pygame


class ImageManager:
    """
    Static class to handle loading of pygame surfaces to improve performance
    """

    initialized = False
    sounds = None

    @staticmethod
    def init():
        ImageManager.initialized = True
        ImageManager.sounds = {}

    @staticmethod
    def check_initialized():
        if not ImageManager.initialized:
            raise Exception("Must call ImageHandler.init() before any other methods.")

    @staticmethod
    def clear(path):
        """
        Forgets one thing.
        :param path: The path of the file to remove from memory
        :return:
        """
        ImageManager.check_initialized()
        if path in ImageManager.sounds:
            del ImageManager.sounds[path]

    @staticmethod
    def clear_all():
        """
        Forgets everything
        """
        ImageManager.check_initialized()
        ImageManager.sounds = {}

    @staticmethod
    def load(path):
        """
        Loads a surface from file or from cache
        :param path: The path of the image
        :return: The surface. This is likely the same reference others are using, so don't be destructive.
        """
        ImageManager.check_initialized()
        if path in ImageManager.sounds:
            return ImageManager.sounds[path]
        sound = pygame.image.load(path).convert_alpha()
        ImageManager.sounds[path] = sound
        return sound

    @staticmethod
    def load_copy(path):
        return ImageManager.load(path).copy()
