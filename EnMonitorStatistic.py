#!/usr/bin/env python
# coding: utf-8
import lxml
import re
import math
import requests as req
from bs4 import BeautifulSoup


class StatisticsMonitor:

    def __init__(self,
                 url=None,
                 file=None,
                 page=None):
        self.url = url
        self.file = file
        self.page = page
        self.teams = {}
        self.online = False

    @staticmethod
    def lvl_num(obj):
        """Исправляет неправельный подсчет уровней"""
        lvl = len(obj) - 2
        return lvl

    def set_game(self, str_in):
        """Choose it's online or offline monitoring"""
        if 'en.cx' in str_in:
            self.url = str_in
            self.online = True
        else:
            self.file = str_in
            self.online = False

    def load_page_file(self):
        if self.file is None:
            print('Файл пустой')
            return None

        with open(self.file, 'r', encoding='utf-8') as f:
            contents = f.read()
            soup = BeautifulSoup(contents, 'lxml')
            print(soup.find("a", id="lnkGameName").text)
            self.page = soup

    def load_page(self):
        if self.online:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/53.0.2785.89 '
                              'Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
            }
            resp = req.get(self.url, headers=headers)
            self.page = BeautifulSoup(resp.text, 'lxml')
        else:
            self.load_page_file()
            if self.page is not None:
                return True
            else:
                False

    def add_team(self, string):
        """Add team with id"""
        value = string.split(':')
        return self.teams.update({value[0]: value[1]})

    def look_team(self):
        """show list teams with id"""
        return self.teams

    def return_stats_teams(self, team_name, team_checkpoints_display, levels_text):
        return '{0} - {1} ({2}/{3})'.format(team_name,
                                            levels_text[self.lvl_num(team_checkpoints_display)],
                                            self.lvl_num(team_checkpoints_display),
                                            len(levels_text) - 4
                                            )

    def stats_for_team(self, team_name, team_id):
        table = self.page.find("table", id="GameStatObject_DataTable")

        levels_tr = table.find("tr", {"class": "levelsRow"})
        levels_text = [e.text for e in levels_tr.children if e.name is not None]
        # print(levels_text)

        class_id_for_team = 'id{0}'.format(team_id)
        team_checkpoints = table.findAll("td", {"class": class_id_for_team})

        result = []

        if self.online:
            # print(self.return_stats_teams(team_name, team_checkpoints, levels_text))
            return self.return_stats_teams(team_name, team_checkpoints, levels_text)
        else:
            team_checkpoints_display = []
            for e in team_checkpoints:
                test = e.find("div", {"style": "display: none;"})
                if test is None:
                    team_checkpoints_display.append(e)
            # print(self.return_stats_teams(team_name, team_checkpoints_display, levels_text))
            return self.return_stats_teams(team_name, team_checkpoints_display, levels_text)

    def show_stats(self):
        if self.page is None:
            return "Пустая страница"

        if len(self.teams) < 1:
            return "Команды для мониторинга отсутствуют"

        result = []

        for key, value in self.teams.items():
            result.append(self.stats_for_team(key, value))

        return '\n'.join(result)

    def show_position_teams(self):
        table = self.page.find("table", id="GameStatObject_DataTable")

        levels_tr = table.find("tr", {"class": "levelsRow"})
        total = table.findAll("td", {"class": "totalCell"})

        team_list = []
        time_list = []

        for key, value in self.teams.items():
            # Search cell for team
            class_select_team = 'totalCell id{0}'.format(value)
            total_select_team = table.findAll("td", {"class": class_select_team})

            # Search position in result table
            finish_position = math.ceil((total.index(total_select_team[0]) + 1) / 2)
            finish_position_with_bonus = math.ceil((total.index(total_select_team[1]) + 1) / 2)
            team_list.append('{0} - {1}|{2}'.format(key, finish_position, finish_position_with_bonus))

            # Search time lag
            cell_text = total_select_team[0].get_text(' ')
            time = self.take_int_from_string(cell_text)
            time_list.append(time)

        result = []
        index = 0
        for item in time_list:
            # If there is not bonus
            if len(item) > 1:
                item.append(0)

            if index == 0:
                result.append("{0}\t Time:{1}, Bonus: {2}".format(team_list[index],
                                                             self.second_to_string(item[0]),
                                                             self.second_to_string(item[1]))
                              )
            else:
                lag = (item[0] - time_list[index - 1][0])
                result.append("{0}\t Time:{1} (+{3}), Bonus: {2}".format(team_list[index],
                                                                   self.second_to_string(item[0]),
                                                                   self.second_to_string(item[1]),
                                                                   self.second_to_string(lag))
                              )
            index += 1

        return '\n'.join(result)

    def show_time_lags(self):
        table = self.page.find("table", id="GameStatObject_DataTable")

        levels_tr = table.find("tr", {"class": "levelsRow"})
        total = table.findAll("td", {"class": "totalCell"})

        time_list = []

        for key, value in self.teams.items():
            class_select_team = 'totalCell id{0}'.format(value)
            total_select_team = table.findAll("td", {"class": class_select_team})

            cell_text = total_select_team[0].get_text(' ')
            time = self.take_int_from_string(cell_text)
            time_list.append(time)

        index = 0
        result = []
        for item in time_list:
            index += 1
            if index == 1:
                result.append("{0}, Bonus: {1}".format(self.second_to_string(item[0]),
                                                       self.second_to_string(item[1]))
                              )
            else:
                lag = (item[0] - time_list[index - 2][0])
                result.append("{0} ({2}), Bonus: {1}".format(self.second_to_string(item[0]),
                                                             self.second_to_string(item[1]),
                                                             self.second_to_string(lag))
                              )

        return result

    def take_stats(self):
        self.load_page()
        result = [self.show_stats(), '---', self.show_position_teams()]
        return '\n'.join(result)


    @staticmethod
    def string_to_second(d=0, h=0, m=0, s=0):
        d = int(d)
        h = int(h)
        m = int(m)
        s = int(s)
        result_seconds = (((((d * 24) + h) * 60) + m) * 60) + s
        return int(result_seconds)

    @staticmethod
    def second_to_string(seconds=None, granularity=2):
        intervals = (
            # ('weeks', 604800),  # 60 * 60 * 24 * 7
            ('days', 86400),  # 60 * 60 * 24
            ('hours', 3600),  # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
        )
        result = []

        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{}{}".format(value, name[:1]))
        return ' '.join(result[:granularity])

    @staticmethod
    def take_int_from_string(instr):
        result = []
        # Time
        d, h, m, s = '0', '0', '0', '0'

        match = re.search(r'\d+ д.', instr)
        if match:
            d = match.group(0)[:-3]
        match = re.search(r'\d+ ч.', instr)
        if match:
            h = match.group(0)[:-3]
        match = re.search(r'\d+ м.', instr)
        if match:
            m = match.group(0)[:-3]
        match = re.search(r'\d+ c.', instr)
        if match:
            s = match.group(0)[:-3]
        time = StatisticsMonitor.string_to_second(d=d, h=h, m=m, s=s)
        result.append(time)

        if 'бонус' in instr:
            # Bonus
            d, h, m, s = '0', '0', '0', '0'
            instr = instr[instr.index(')'):]
            match = re.search(r'\d+ в', instr)
            if match:
                d = match.group(0)[:-2]
            match = re.search(r'\d+ ч', instr)
            if match:
                h = match.group(0)[:-2]
            match = re.search(r'\d+ м', instr)
            if match:
                m = match.group(0)[:-2]
            match = re.search(r'\d+ с', instr)
            if match:
                s = match.group(0)[:-2]
            bonus = StatisticsMonitor.string_to_second(d=d, h=h, m=m, s=s)
            result.append(bonus)

        return result

        # class_otwt = 'totalCell id{0}'.format('146267')
        '''
        total_1 = []
        total_2 = []
        count = 0
        for cell in total:
            count += 1
            if count % 2 == 0:
                total_2.append(cell)
            else:
                total_1.append(cell)
        print(total_1)
        print('---')
        print(total_2)
        '''

        # print(otwt_total.text)


def set_preset(obj, i=0):
    if i == 1:
        obj.set_game(r'offline site\Статистика игры о-10 д-9 м-8 (278).html')
        obj.add_team("О.Т. Win Team:146267")
        obj.add_team("MARS`o`HOT:10301")
        obj.add_team("ДИВ:117667")
    if i == 2:
        obj.set_game('http://demo.en.cx/GameStat.aspx?type=own&gid=30415')
        obj.add_team("Test:158204")
    if i == 3:
        obj.set_game(r'offline site\Статистика игры о-10 д-9 м-8 (278).html')
        obj.add_team("О.Т. Win Team:146267")
        obj.add_team("MARS`o`HOT:10301")
        obj.add_team("ДИВ:117667")
        obj.add_team("TopChi:33464")
        obj.add_team("RG:4393")
        obj.add_team("BM:173249")


def main():
    o1 = StatisticsMonitor()
    set_preset(o1, 3)
    result = o1.take_stats()
    print(result)
    print('123')
    return result


if __name__ == '__main__':
    main()


