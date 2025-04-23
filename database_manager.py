import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name

    def connect(self):

        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def close(self):

        if hasattr(self, "connection"):
            self.connection.close()

    def get_user_by_login(self, login):

        self.cursor.execute("SELECT * FROM Uzytkownicy WHERE login = ?", (login,))
        return self.cursor.fetchone()

    def get_user_with_personal_data(self, user_id):

        self.cursor.execute("""
            SELECT u.id_uzytkownika, u.login, u.email, u.rola, 
                   d.imie, d.nazwisko, d.nr_tel
            FROM Uzytkownicy u
            INNER JOIN "Dane_osobowe" d ON u.id_uzytkownika = d.id_uzytkownika
            WHERE u.id_uzytkownika = ?
        """, (user_id,))
        return self.cursor.fetchone()

    def get_all_users_with_personal_data(self):

        self.cursor.execute("""
            SELECT u.id_uzytkownika, u.login, u.email, u.rola, 
                   d.imie, d.nazwisko, d.nr_tel
            FROM Uzytkownicy u
            INNER JOIN "Dane_osobowe" d ON u.id_uzytkownika = d.id_uzytkownika
        """)
        return self.cursor.fetchall()

    def add_user(self, login, password, email, role, first_name, last_name, phone):

        try:
            self.cursor.execute("""
                INSERT INTO Uzytkownicy (login, haslo, email, rola)
                VALUES (?, ?, ?, ?)
            """, (login, password, email, role))
            user_id = self.cursor.lastrowid

            self.cursor.execute("""
                INSERT INTO "Dane_osobowe" (id_uzytkownika, imie, nazwisko, nr_tel)
                VALUES (?, ?, ?, ?)
            """, (user_id, first_name, last_name, phone))

            self.connection.commit()
            return user_id
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e

    def delete_user(self, user_id):

        try:
            self.cursor.execute("DELETE FROM Uzytkownicy WHERE id_uzytkownika = ?", (user_id,))
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e

    def edit_user(self, user_id, login=None, password=None, email=None, role=None, first_name=None, last_name=None,
                  phone=None):

        try:
            if login or password or email or role:
                query = "UPDATE Uzytkownicy SET "
                params = []
                if login:
                    query += "login = ?, "
                    params.append(login)
                if password:
                    query += "haslo = ?, "
                    params.append(password)
                if email:
                    query += "email = ?, "
                    params.append(email)
                if role:
                    query += "rola = ?, "
                    params.append(role)
                query = query.rstrip(", ") + " WHERE id_uzytkownika = ?"
                params.append(user_id)
                self.cursor.execute(query, tuple(params))

            if first_name or last_name or phone:
                query = "UPDATE 'Dane_osobowe' SET "
                params = []
                if first_name:
                    query += "imie = ?, "
                    params.append(first_name)
                if last_name:
                    query += "nazwisko = ?, "
                    params.append(last_name)
                if phone:
                    query += "nr_tel = ?, "
                    params.append(phone)
                query = query.rstrip(", ") + " WHERE id_uzytkownika = ?"
                params.append(user_id)
                self.cursor.execute(query, tuple(params))

            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e



    def get_vehicle(self, id_pojazd):

        self.cursor.execute("""
                    SELECT id_pojazd, nazwa, numer_rejestracyjny, typ_pojazdu, dostepnosc
            FROM Pojazdy_sluzbowe
                    WHERE id_pojazd = ?
                """, (id_pojazd,))
        return self.cursor.fetchone()

    def get_all_vehicles(self):

        self.cursor.execute("""
            SELECT id_pojazd, nazwa, numer_rejestracyjny, typ_pojazdu, dostepnosc
            FROM Pojazdy_sluzbowe
        """)
        return self.cursor.fetchall()

    def add_vehicle(self, name, registration_number, vehicle_type, availability):

        try:
            self.cursor.execute("""
                INSERT INTO Pojazdy_sluzbowe (nazwa, numer_rejestracyjny, typ_pojazdu, dostepnosc)
                VALUES (?, ?, ?, ?)
            """, (name, registration_number, vehicle_type, availability))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e

    def delete_vehicle(self, vehicle_id):

        try:
            self.cursor.execute("DELETE FROM Pojazdy_sluzbowe WHERE id_pojazd = ?", (vehicle_id,))
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e

    def edit_vehicle(self, vehicle_id, name=None, registration_number=None, vehicle_type=None, availability=None):

        try:
            query = "UPDATE Pojazdy_sluzbowe SET "
            params = []
            if name:
                query += "nazwa = ?, "
                params.append(name)
            if registration_number:
                query += "numer_rejestracyjny = ?, "
                params.append(registration_number)
            if vehicle_type:
                query += "typ_pojazdu = ?, "
                params.append(vehicle_type)
            if availability is not None:
                query += "dostepnosc = ?, "
                params.append(availability)
            query = query.rstrip(", ") + " WHERE id_pojazd = ?"
            params.append(vehicle_id)
            self.cursor.execute(query, tuple(params))
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e



    def get_accommodation_by_delegation(self,delegation_id):
        self.cursor.execute("""
                    SELECT id_zakwaterowanie, id_delegacja, miejscowosc, ulica, nr_budynku, nr_mieszkania 
                           data_od, data_do, typ_zakwaterowania, liczba_osob
                    FROM Zakwaterowanie
                    WHERE id_delegacja = ?
                        """, (delegation_id,))
        return self.cursor.fetchall()

    def get_accommodation(self, id_zakwaterowanie):

        self.cursor.execute("""
            SELECT id_zakwaterowanie, id_delegacja, miejscowosc, ulica, nr_budynku, nr_mieszkania , 
                   data_od, data_do, typ_zakwaterowania, liczba_osob
            FROM Zakwaterowanie
            WHERE id_zakwaterowanie = ?
                """, (id_zakwaterowanie,))
        return self.cursor.fetchone()

    def get_all_accommodations(self):

        self.cursor.execute("""
            SELECT id_zakwaterowanie, id_delegacja, miejscowosc, ulica, nr_budynku, nr_mieszkania , 
                   data_od, data_do, typ_zakwaterowania, liczba_osob
            FROM Zakwaterowanie
        """)
        return self.cursor.fetchall()

    def add_accommodation(self, delegation_id, city, street, nr_budynku, nr_mieszkania, start_date, end_date, accommodation_type, number_of_people):

        try:
            self.cursor.execute("""
                INSERT INTO Zakwaterowanie (id_delegacja, miejscowosc, ulica, nr_budynku, nr_mieszkania , 
                                            data_od, data_do, typ_zakwaterowania, liczba_osob)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (delegation_id, city, street, nr_budynku, nr_mieszkania, start_date, end_date, accommodation_type, number_of_people))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e

    def delete_accommodation(self, accommodation_id):

        try:
            self.cursor.execute("DELETE FROM Zakwaterowanie WHERE id_zakwaterowanie = ?", (accommodation_id,))
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e

    def edit_accommodation(self, accommodation_id, city=None, street=None, nr_budynku=None, nr_mieszkania=None , start_date=None, end_date=None, accommodation_type=None, number_of_people=None):

        try:
            query = "UPDATE Zakwaterowanie SET "
            params = []
            if city:
                query += "miejscowosc = ?, "
                params.append(city)
            if street:
                query += "ulica = ?, "
                params.append(street)
            if nr_budynku:
                query += "nr_budynku = ?, "
                params.append(nr_budynku)
            if nr_mieszkania:
                query += "nr_mieszkania = ?, "
                params.append(nr_mieszkania)
            if start_date:
                query += "data_od = ?, "
                params.append(start_date)
            if end_date:
                query += "data_do = ?, "
                params.append(end_date)
            if accommodation_type:
                query += "typ_zakwaterowania = ?, "
                params.append(accommodation_type)
            if number_of_people is not None:
                query += "liczba_osob = ?, "
                params.append(number_of_people)
            query = query.rstrip(", ") + " WHERE id_zakwaterowanie = ?"
            params.append(accommodation_id)
            self.cursor.execute(query, tuple(params))
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e



    def get_user_delegations(self, user_id):

        self.cursor.execute("""
            SELECT d.id_delegacja, d.miejsce, d.data_rozpoczecia, d.data_zakonczenia, d.status, d.opis
            FROM Delegacje d
            INNER JOIN Delegacje_Uzytkownicy du ON d.id_delegacja = du.id_delegacja
            WHERE du.id_uzytkownika = ?
        """, (user_id,))
        return self.cursor.fetchall()

    def approve_delegation(self, delegation_id):

        self.cursor.execute(
            "UPDATE Delegacje SET status = 'zatwierdzone' WHERE id_delegacja = ?", (delegation_id,)
        )
        self.connection.commit()

    def archive_delegation(self, delegation_id):

        self.cursor.execute(
            "UPDATE Delegacje SET status = 'archiwum' WHERE id_delegacja = ?", (delegation_id,)
        )
        self.connection.commit()

    def get_delegation(self, delegation_id):

        self.cursor.execute("""
            SELECT d.id_delegacja, d.miejsce, d.data_rozpoczecia, d.data_zakonczenia, d.transport, 
                   d.status, d.opis, z.miejscowosc, z.ulica, z.data_od, z.data_do, z.typ_zakwaterowania
            FROM Delegacje d
            LEFT JOIN Zakwaterowanie z ON d.id_delegacja = z.id_delegacja
            WHERE d.id_delegacja = ?
        """, (delegation_id,))
        return self.cursor.fetchone()

    def get_all_delegations(self):
        self.cursor.execute("""
            SELECT DISTINCT d.id_delegacja, d.miejsce, d.data_rozpoczecia, d.data_zakonczenia, d.status, d.opis
            FROM Delegacje d
            LEFT OUTER JOIN Delegacje_Uzytkownicy du ON d.id_delegacja = du.id_delegacja
        """)
        return self.cursor.fetchall()

    def add_delegation(self, place, start_date, end_date, transport, status, description):

        try:
            self.cursor.execute("""
                    INSERT INTO Delegacje (miejsce, data_rozpoczecia, data_zakonczenia, transport, status, opis)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (place, start_date, end_date, transport, status, description))

            self.connection.commit()

            return self.cursor.lastrowid

        except sqlite3.Error as e:
            self.connection.rollback()
            print(f"Database error: {e}")
            raise e

    def delete_delegation(self, delegation_id):

        try:
            self.cursor.execute("DELETE FROM Delegacje WHERE id_delegacja = ?", (delegation_id,))
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e

    def edit_delegation(self, delegation_id, place=None, start_date=None, end_date=None, transport=None, status=None,
                        description=None):

        try:
            query = "UPDATE Delegacje SET "
            params = []
            if place:
                query += "miejsce = ?, "
                params.append(place)
            if start_date:
                query += "data_rozpoczecia = ?, "
                params.append(start_date)
            if end_date:
                query += "data_zakonczenia = ?, "
                params.append(end_date)
            if transport:
                query += "transport = ?, "
                params.append(transport)
            if status:
                query += "status = ?, "
                params.append(status)
            if description:
                query += "opis = ?, "
                params.append(description)
            query = query.rstrip(", ") + " WHERE id_delegacja = ?"
            params.append(delegation_id)
            self.cursor.execute(query, tuple(params))
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e

    def add_full_delegation(self, place, start_date, end_date, transport, status, description, users,
                            accommodations_with_users, vehicles_with_users):

        try:
            self.cursor.execute("""
                INSERT INTO Delegacje (miejsce, data_rozpoczecia, data_zakonczenia, transport, status, opis)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (place, start_date, end_date, transport, status, description))
            delegation_id = self.cursor.lastrowid

            for user_id in users:
                self.cursor.execute("""
                    INSERT INTO Delegacje_Uzytkownicy (id_delegacja, id_uzytkownika)
                    VALUES (?, ?)
                """, (delegation_id, user_id))

            for acc_data in accommodations_with_users:
                acc = acc_data["accommodation"]
                users = acc_data["users"]

                self.cursor.execute("""
                    INSERT INTO Zakwaterowanie (id_delegacja, miejscowosc, ulica, nr_budynku, nr_mieszkania, 
                                                data_od, data_do, typ_zakwaterowania, liczba_osob)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (delegation_id, acc["city"], acc["street"], acc["nr_budynku"], acc["nr_mieszkania"],
                      acc["start_date"], acc["end_date"], acc["type"], acc["number_of_people"]))
                accommodation_id = self.cursor.lastrowid

                for user_id in users:
                    self.cursor.execute("""
                        INSERT INTO Zakwaterowanie_Uzytkownicy (id_zakwaterowanie, id_uzytkownik)
                        VALUES (?, ?)
                    """, (accommodation_id, user_id))

            for vehicle_data in vehicles_with_users:
                vehicle_id = vehicle_data["vehicle_id"]
                users = vehicle_data["users"]

                self.cursor.execute("""
                    INSERT INTO Delegacje_Pojazdy (id_delegacja, id_pojazd)
                    VALUES (?, ?)
                """, (delegation_id, vehicle_id))

                for user_id in users:
                    self.cursor.execute("""
                        INSERT INTO Transport_Uzytkownicy (id_delegacja, id_pojazd, id_uzytkownik)
                        VALUES (?, ?, ?)
                    """, (delegation_id, vehicle_id, user_id))

            self.connection.commit()
            return delegation_id
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e

    def edit_full_delegation(self, delegation_id, place=None, start_date=None, end_date=None, transport=None,
                             status=None, description=None, users=None, accommodations_with_users=None,
                             vehicles_with_users=None):

        try:
            if any([place, start_date, end_date, transport, status, description]):
                query = "UPDATE Delegacje SET "
                params = []
                if place:
                    query += "miejsce = ?, "
                    params.append(place)
                if start_date:
                    query += "data_rozpoczecia = ?, "
                    params.append(start_date)
                if end_date:
                    query += "data_zakonczenia = ?, "
                    params.append(end_date)
                if transport:
                    query += "transport = ?, "
                    params.append(transport)
                if status:
                    query += "status = ?, "
                    params.append(status)
                if description:
                    query += "opis = ?, "
                    params.append(description)
                query = query.rstrip(", ") + " WHERE id_delegacja = ?"
                params.append(delegation_id)
                self.cursor.execute(query, tuple(params))

            if users is not None:
                self.cursor.execute("""
                    DELETE FROM Delegacje_Uzytkownicy WHERE id_delegacja = ?
                """, (delegation_id,))
                for user_id in users:
                    self.cursor.execute("""
                        INSERT INTO Delegacje_Uzytkownicy (id_delegacja, id_uzytkownika)
                        VALUES (?, ?)
                    """, (delegation_id, user_id))

            if accommodations_with_users is not None:
                self.cursor.execute("""
                    DELETE FROM Zakwaterowanie WHERE id_delegacja = ?
                """, (delegation_id,))
                for acc_data in accommodations_with_users:
                    acc = acc_data["accommodation"]
                    users = acc_data["users"]

                    self.cursor.execute("""
                        INSERT INTO Zakwaterowanie (id_delegacja, miejscowosc, ulica, nr_budynku, nr_mieszkania, 
                                                    data_od, data_do, typ_zakwaterowania, liczba_osob)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (delegation_id, acc["city"], acc["street"], acc["nr_budynku"], acc["nr_mieszkania"],
                          acc["start_date"], acc["end_date"], acc["type"], acc["number_of_people"]))
                    accommodation_id = self.cursor.lastrowid

                    for user_id in users:
                        self.cursor.execute("""
                            INSERT INTO Zakwaterowanie_Uzytkownicy (id_zakwaterowanie, id_uzytkownik)
                            VALUES (?, ?)
                        """, (accommodation_id, user_id))

            if vehicles_with_users is not None:
                self.cursor.execute("""
                    DELETE FROM Delegacje_Pojazdy WHERE id_delegacja = ?
                """, (delegation_id,))
                self.cursor.execute("""
                    DELETE FROM Transport_Uzytkownicy WHERE id_delegacja = ?
                """, (delegation_id,))
                for vehicle_data in vehicles_with_users:
                    vehicle_id = vehicle_data["vehicle_id"]
                    users = vehicle_data["users"]

                    self.cursor.execute("""
                        INSERT INTO Delegacje_Pojazdy (id_delegacja, id_pojazd)
                        VALUES (?, ?)
                    """, (delegation_id, vehicle_id))

                    for user_id in users:
                        self.cursor.execute("""
                            INSERT INTO Transport_Uzytkownicy (id_delegacja, id_pojazd, id_uzytkownik)
                            VALUES (?, ?, ?)
                        """, (delegation_id, vehicle_id, user_id))

            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e

    def get_users_for_delegation(self, delegation_id):

        self.cursor.execute("""
            SELECT u.id_uzytkownika, u.login, u.email, u.rola, 
                   d.imie, d.nazwisko, d.nr_tel
            FROM Uzytkownicy u
            INNER JOIN Delegacje_Uzytkownicy du ON u.id_uzytkownika = du.id_uzytkownika
            INNER JOIN "Dane_osobowe" d ON u.id_uzytkownika = d.id_uzytkownika
            WHERE du.id_delegacja = ?
        """, (delegation_id,))
        return self.cursor.fetchall()

    def get_vehicles_for_delegation(self, delegation_id):

        self.cursor.execute("""
            SELECT p.id_pojazd, p.nazwa, p.numer_rejestracyjny, p.typ_pojazdu, p.dostepnosc
            FROM Pojazdy_sluzbowe p
            INNER JOIN Delegacje_Pojazdy dp ON p.id_pojazd = dp.id_pojazd
            WHERE dp.id_delegacja = ?
        """, (delegation_id,))
        return self.cursor.fetchall()

    def get_accommodations_for_delegation(self, delegation_id):

        self.cursor.execute("""
            SELECT z.id_zakwaterowanie, z.miejscowosc, z.ulica, z.nr_budynku, z.nr_mieszkania, z.data_od, z.data_do, 
                   z.typ_zakwaterowania, z.liczba_osob
            FROM Zakwaterowanie z
            WHERE z.id_delegacja = ?
        """, (delegation_id,))
        return self.cursor.fetchall()

    def get_users_for_accommodations(self, delegation_id):

        self.cursor.execute("""
            SELECT u.id_uzytkownika, u.login, u.email, u.rola, z.miejscowosc, z.ulica, z.nr_budynku, z.nr_mieszkania
            FROM Uzytkownicy u
            INNER JOIN Zakwaterowanie_Uzytkownicy zu ON u.id_uzytkownika = zu.id_uzytkownik
            INNER JOIN Zakwaterowanie z ON z.id_zakwaterowanie = zu.id_zakwaterowanie
            WHERE z.id_delegacja = ?
        """, (delegation_id,))
        return self.cursor.fetchall()

    def get_users_for_vehicles(self, delegation_id):

        self.cursor.execute("""
            SELECT u.id_uzytkownika, u.login, u.email, u.rola, p.nazwa AS pojazd_nazwa, p.numer_rejestracyjny
            FROM Uzytkownicy u
            INNER JOIN Transport_Uzytkownicy tu ON u.id_uzytkownika = tu.id_uzytkownik
            INNER JOIN Pojazdy_sluzbowe p ON p.id_pojazd = tu.id_pojazd
            WHERE tu.id_delegacja = ?
        """, (delegation_id,))
        return self.cursor.fetchall()
