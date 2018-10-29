"""
Description: vygeneruje AIS ve formátu CSV na základě vložených udájích i službách
ToDO:
1) konvertující funkce
2) generátor CSV
3) Format_in: D1, D2, D3, Z, N1, DK, NK, D, P,
3 Format_out: "od hh:mm - do hh:mm; pauza od hh:mm - do hh:mm; celkem čas hh,
"""

import pandas as pd
import datetime
import calendar
from czech_holidays import holidays

class Sluzba:
    """
    NaN     - všední pracovní den: " 07:00 - 15:30, 11:30 - 12:00, 8, 0, 0, 0, 0, 0 "
            - víkend, svátek: " None, None, 0, 0, 0, 0, 0, 0
    D1/D2/DK- všední den: "07:00 - 19:00, 11:30 - 12:00, 11.5, 3.5, 0, 0, 0, 0 "
            - víkend, svátek: "07:00 - 19:00, None, 12, 0, 12, 0, 12, 12 "
            - svátek: "07:00 - 19:00, None, 12, 0, 12, 0, 0, 12 "
            - víkend: "07:00 - 19:00, None, 12, 0, 12, 0, 12, 0 (12) "
    D3      - vikend, (svátek): "07:00 - 11:00, None, 4, 0, 4, 0, 4, 0 (4) "
    Z/N1/NK - všední den: "07:00 - 00:00, 11:00 - 19:00, 9, 0, 0, 2, 0, 0 "
            - víkend, (svátek): "19:00 - 00:00, None, 5, 0, 5, 2, 5, 0 (5) "
    Z_d/N1_d- všední den: "00:00 - 07:00, None, 7, 0, 0, 6, 0, 0 "
            - víkend, (svátek): "00:00 - 07:00, None, 7, 0, 7, 6, 7, 0 (7) "
            """

    def __init__(self, name, day):
        self.name = name
        self.today_date = day
        self.day = day.weekday()
        self.date_day = day.day
        self.svatek = self.today_date in holidays
        self.vikend = False
        self.act_variable = [None, 1, 2, 3]

        self.nan_pd = " 07:00", "15:30", "11:30", "12:00", None, None, 8, None, None, None, None, None, self.name
        self.nan_san = None, None, None, None, None, None, None, None, None, None, None, None, self.name
        self.nan_san_sv = None, None, None, None, None, None, None, None, None, None, None, None, self.name
        self.nan_sv = None, None, None, None, None, None, 8, None, None, None, None, None, self.name
        self.d1_pd = "07:00", "19:00", "11:30", "12:00", None, None, 11.5, 3.5, None, None, None, None, self.name
        self.d1_san = "07:00", "19:00", None, None, None, None, 12, None, 12, None, 12, None, self.name
        self.d1_sv = "07:00", "19:00", None, None, None, None, 12, None, 12, None, None, 12, self.name
        self.d1_san_sv = "07:00", "19:00", None, None, None, None, 12, None, 12, None, 12, 12, self.name
        self.d3_san = "07:00", "11:00", None, None, None, None, 4, None, 4, None, 4, None, self.name
        self.d3_san_sv = "07:00", "11:00", None, None, None, None, 4, None, 4, None, 4, 4, self.name
        self.d3_sv = "07:00", "11:00", None, None, None, None, 4, None, 4, None, None, 4, self.name
        self.z_pd = "07:00", "00:00", "11:00", "19:00", None, None, 9, None, None, 2, None, None, self.name
        self.z_san = ["19:00", "00:00", None, None, None, None, 5, None, 5, 2, 5, None, self.name]
        self.z_san_sv = ["19:00", "00:00", None, None, None, None, 5, None, 5, 2, 5, 5, self.name]
        self.z_sv = ["19:00", "00:00", None, None, None, None, 5, None, None, 2, None, 5, self.name]
        self.z_d_pd = ["00:00", "07:00", None, None, None, None, 7, None, None, 6, None, None, self.name]
        self.z_d_san = ["00:00", "07:00", None, None, None, None, 7, None, 7, 6, 7, None, self.name]
        self.z_d_san_sv = ["00:00", "07:00", None, None, None, None, 7, None, 7, 6, 7, 7, self.name]
        self.z_d_sv = ["00:00", "07:00", None, None, None, None, 7, None, None, 6, None, 7, self.name]

    def set_variables(self):
        # def set_variables(self,csv_to_change)
        if self.day < 5:
            self.vikend = False
        else:
            self.vikend = True

        if self.name == "d1" or self.name == "d2" or self.name == "dk":
            if not self.vikend and not self.svatek:
                self.act_variable = self.d1_pd
            elif not self.vikend and self.svatek:
                self.act_variable = self.d1_sv
            elif self.vikend and self.svatek:
                self.act_variable = self.d1_san_sv
            else:
                self.act_variable = self.d1_san
        elif self.name == "d3":
            if self.vikend and not self.svatek:
                self.act_variable = self.d3_san
            elif self.vikend and self.svatek:
                self.act_variable = self.d3_san_sv
            else:
                self.act_variable = self.d3_sv
        elif self.name == "z" or self.name == "n1" or self.name == "nk":
            if not self.vikend and not self.svatek:
                self.act_variable = self.z_pd
            elif not self.vikend and self.svatek:
                self.act_variable = self.z_sv
            elif self.vikend and self.svatek:
                self.act_variable = self.z_san_sv
            else:
                self.act_variable = self.z_san
        elif self.name == "z_d" or self.name == "n1_d" or self.name == "nk_d":
            if not self.vikend and not self.svatek:
                self.act_variable = self.z_d_pd
            elif not self.vikend and self.svatek:
                self.act_variable = self.z_d_sv
            elif self.vikend and self.svatek:
                self.act_variable = self.z_d_san_sv
            else:
                self.act_variable = self.z_d_san
        elif self.name == "nan":
            if not self.vikend and not self.svatek:
                self.act_variable = self.nan_pd
            elif not self.vikend and self.svatek:
                self.act_variable = self.nan_sv
            elif self.vikend and self.svatek:
                self.act_variable = self.nan_san_sv
            else:
                self.act_variable = self.nan_san

    def name_reload(self):
        self.act_variable[12] = self.name


def populator_2(rozpis_sluzeb_pd, mesic, rok):
    """vygeneruje Sluzba classy na daný měsíc"""
    sluzby_mesic_pop = []
    curr_day = datetime.date(rok, mesic, 1)
    for i in rozpis_sluzeb_pd.values:
        name = i[0]
        if name == "":
            name = "nan"
        elif name != "":
            name = name.lower()
        sluzba = Sluzba(name, curr_day)
        sluzba.set_variables()
        sluzby_mesic_pop.append(sluzba)
        curr_day += datetime.timedelta(days=1)
    return sluzby_mesic_pop


def generate_ais(uzivatel, rozpis_sluzeb, rok, mes, den=1):
    """
    1) generuje ais = pd.DataFrame podle akt. měsíce
    2) extrahuje služby na daný měsíc
    3) via populator() ke každému dni přiřadí koresp. obj. Sluzba()
    4) modifikuje další den po "z" z "nan" na "z_d"
    5) postupně dle koresp. obj. Sluzba() modifikuje řádek k danému dni v ais
    """
    datum = datetime.date(rok, mes, den)
    days_in_month = calendar.monthrange(datum.year, datum.month)

    ais = pd.DataFrame(index=range(1, days_in_month[1] + 1), columns=range(1, 14))
    # print(ais)

    moje_sluzby = []

    # for item in rozpis_sluzeb.loc["MUDr. Bortel", :].values[0]:
    for item in rozpis_sluzeb.loc[uzivatel, :].values[0]:
        if type(item) != str:
            item = ''
        moje_sluzby.append(item)

    # ze sluzeb zkonstruovat tabulku - y_datum, x_typ_sluzby
    moje_sluzby_pd = pd.DataFrame({"služba": moje_sluzby}, index=range(1, len(moje_sluzby) + 1))
    # print(moje_sluzby_pd)

    # generuje obj. Sluzba() - POZN: upravit fci aby returnovala list sluzeb
    sluzby_mesic_lst = populator_2(moje_sluzby_pd, datum.month, datum.year)
    # print(sluzby_mesic_lst)

    for sluzba in sluzby_mesic_lst:
        if (sluzba.name == "z" or sluzba.name == "nk") and sluzby_mesic_lst.index(sluzba) < len(sluzby_mesic_lst) - 1:
            if sluzba.name == "z":
                sluzby_mesic_lst[sluzby_mesic_lst.index(sluzba) + 1].name = "z_d"
            elif sluzba.name == "nk":
                sluzby_mesic_lst[sluzby_mesic_lst.index(sluzba) + 1].name = "nk_d"
            sluzby_mesic_lst[sluzby_mesic_lst.index(sluzba) + 1].set_variables()
            sluzby_mesic_lst[sluzby_mesic_lst.index(sluzba) + 1].name_reload()
        for d in range(13):
            ais.at[sluzba.date_day, d + 1] = sluzba.act_variable[d]

    return ais

class Generate_for_all:
    """
    Objekt, který bere .xlsx dokument, extrahuje všechny uzivatele, vytvoří dict: key= uzivatel, value=ais pro daného
    uživatele.
    """

    def __init__(self, rozpis_sluzeb_file, year, month):
        self.all_clear = True
        self.rozpis_sluzeb = pd.read_excel(rozpis_sluzeb_file)
        self.year = year
        self.month = month

        self.uzivatele = []
        for name in self.rozpis_sluzeb.index.tolist():
            if "MUDr" in name[0]:
                self.uzivatele.append(name[0])
            elif "externisté" in name[0]:
                break
        self.uzivatele_dict = {}

    def gen_ais_all(self):
        for uzivatel in self.uzivatele:
            # print("adding %s into dict" %uzivatel)
            self.uzivatele_dict[uzivatel] = generate_ais(uzivatel, self.rozpis_sluzeb, self.year, self.month)
            # print("done, %s added" %uzivatel)

        # print(self.uzivatele_dict)
        return self.uzivatele_dict

    def gen_ais(self, inpt):
        return generate_ais(inpt, self.rozpis_sluzeb)
