#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

game = {
    "game_name": "test game",
    "start_time": 0,
    "duration": 0,
    "teams": ["team1", "team2", "team3"],
    "Levels": [
        {
            "ID": 1,
            "lvl_name": "Alice",
            "task": "Тестовое задание 1. Ответ:123",
            "answer": "123"
        },
        {
            "ID": 2,
            "lvl_name": "Bob",
            "task": "Тестовое задание 2. Ответ:qwe",
            "answer": "qwe"
        }
    ]
}

class Game:
    """docstring"""

    def __init__(self):
        """Constructor"""
        self.levels = {}
        self.teams = {}
        self.time_start = None
        self.duration = None
        pass


def dump_json():
    with open("GameFile1.py", "w") as write_file:
        json.dump(data, write_file)




def main():

    pass


if __name__ == '__main__':
    main()