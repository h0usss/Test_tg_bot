from enum import Enum


class Gender(Enum):
    male = "male"
    female = "female"
    other = "other"
    laminate = "laminate"

    @classmethod
    def get_list_names(cls):
        return [values.name for values in cls]


class Cars(Enum):
    Toyota = "Toyota"
    Honda = "Honda"
    Nissan = "Nissan"
    Mazda = "Mazda"
    Subaru = "Subaru"
    Mitsubishi = "Mitsubishi"
    Suzuki = "Suzuki"
    Hyundai = "Hyundai"
    Kia = "Kia"
    Daewoo = "Daewoo"
    Ford = "Ford"
    Chevrolet = "Chevrolet"
    Chrysler = "Chrysler"
    Jeep = "Jeep"
    Volkswagen = "Volkswagen"
    Audi = "Audi"
    BMW = "BMW"
    Mercedes = "Mercedes"

    @classmethod
    def get_list_names(cls):
        return [values.name for values in cls]
