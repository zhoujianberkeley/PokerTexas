# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 20:00:54 2020

@author: Lantian
"""
import logging
import datetime
import os


class AI_Logger(object):
    '''
    record the log when u want
    u need to create a folder log under the folder tool
    problem may be found using spyder, use cmd instead
    '''
    def __init__(self, filename, loggerFolder ="log", level=logging.DEBUG):
        self.logger = logging.getLogger(filename)
        self.logger.setLevel(level)
        fmt = '%(asctime)-15s %(filename)s[line:%(lineno)d] - %(levelname)s - %(name)s : %(message)s'
        if len(self.logger.handlers) == 0:
            formatter = logging.Formatter(fmt=fmt)
            streamHandler  = logging.StreamHandler()
            streamHandler.setFormatter(formatter)
            streamHandler.setLevel(logging.CRITICAL)
            self.logger.addHandler(streamHandler)
            
            if not os.path.exists(loggerFolder):
                os.makedirs(loggerFolder)
            logRecordFile = os.path.join(loggerFolder,filename) +"_"+datetime.datetime.now().strftime("%h-%d-%H:%M%:%S.log")
            fileHandler=logging.FileHandler(logRecordFile, encoding='utf-8')
            fileHandler.setFormatter(formatter)
            fileHandler.setLevel(logging.INFO)
            self.logger.addHandler(fileHandler)
        
    def debug(self,msg):
        self.logger.debug(msg)
    
    def info(self, msg):
        self.logger.info(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def error(self, msg):
        self.logger.error(msg)
        
    def critical(self, msg):
        self.logger.critical(msg)
        
    def log(self, level, msg):
        self.logger.log(level, msg)
        
    def setLevel(self, level):
        self.logger.setLevel(level)
        
    def disable(self):
        logging.disable(50) 

if __name__=='__main__':
    fileName = 'loggerTest'
    logger = AI_Logger(fileName)
    logger.debug("some word")
    logger.info('start running '+fileName)
    logger.warning('something wrong with '+fileName)
    logger.critical('we have to break '+fileName)
    logging.shutdown()
    
    