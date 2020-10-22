#!/usr/bin/python
# coding: utf-8

import time

def init_logfile(filename):
    fd = open(filename,'a')
    return fd


def print_log(fd, s, prefix=' ', suffix=' '):
    log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    fd.write(log_time + prefix + s + suffix + '\n')
    fd.flush()
