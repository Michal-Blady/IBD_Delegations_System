
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from database_manager import DatabaseManager

app = Flask(__name__)
app.secret_key = "your_secret_key"

DATABASE = "example.db"


def get_db():
    if "db" not in g:
        g.db = DatabaseManager(DATABASE)
        g.db.connect()
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.get_user_by_login(username)

        if user and (user["haslo"] == password):
            session["username"] = user["login"]
            session["role"] = user["rola"]
            session["user_id"] = user["id_uzytkownika"]
            return redirect(url_for("dashboard"))
        else:
            flash("Nieprawidłowa nazwa użytkownika lub hasło", "error")
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    db = get_db()
    if session['role'] in ['manager', 'admin']:
        delegacje = db.get_all_delegations()
    else:
        delegacje = db.get_user_delegations(session["user_id"])
    if "role" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", role=session["role"], delegations = delegacje )


@app.route("/delegation/approve/<int:delegation_id>")
def approve_delegation(delegation_id):
    db = get_db()
    db.approve_delegation(delegation_id)
    flash("Delegacja została zatwierdzona.", "success")
    return redirect(url_for("dashboard"))

@app.route("/delegation/archive/<int:delegation_id>")
def archive_delegation(delegation_id):
    db = get_db()
    db.archive_delegation(delegation_id)
    flash("Delegacja została zarchiwizowana.", "success")
    return redirect(url_for("dashboard"))

@app.route("/delegation/<int:delegation_id>")
def delegation_details(delegation_id):
    db = get_db()
    delegation = db.get_delegation(delegation_id)

    if not delegation:
        flash("Nie znaleziono delegacji.", "error")
        return redirect(url_for("dashboard"))

    users = db.get_users_for_delegation(delegation_id)
    vehicles = db.get_vehicles_for_delegation(delegation_id)
    accommodations = db.get_accommodations_for_delegation(delegation_id)

    return render_template(
        "delegation_details.html",
        delegation=delegation,
        users=users,
        vehicles=vehicles,
        accommodations=accommodations
    )



@app.route('/add_delegation', methods=['GET', 'POST'])
def add_delegation():
    db = get_db()
    if request.method == 'GET':
        vehicles = db.get_all_vehicles()
        users = db.get_all_users_with_personal_data()

        return render_template('add_delegation.html', vehicles=vehicles, users=users)

    if request.method == 'POST':
        try:
            place = request.form.get('place')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            transport = request.form.get('transport')
            status = "niezatwierdzone"
            description = request.form.get('description', '')

            users = request.form.getlist('users[]')
            users = [int(user_id) for user_id in users]

            vehicles_with_users = []
            vehicle_ids = request.form.getlist('vehicles[]')
            for vehicle_id in vehicle_ids:
                vehicle_users_key = f'vehicle_users_{vehicle_id}[]'
                vehicle_users = request.form.getlist(vehicle_users_key)
                vehicle_users = [int(user_id) for user_id in vehicle_users]
                vehicles_with_users.append({
                    'vehicle_id': int(vehicle_id),
                    'users': vehicle_users
                })

            accommodations_with_users = []
            accommodation_cities = request.form.getlist('accommodation_city[]')
            accommodation_streets = request.form.getlist('accommodation_street[]')
            accommodation_buildings = request.form.getlist('accommodation_building[]')
            accommodation_places = request.form.get('accommodation_place[]')
            accommodation_starts = request.form.getlist('accommodation_start[]')
            accommodation_ends = request.form.getlist('accommodation_end[]')
            accommodation_people = request.form.getlist('accommodation_people[]')

            for i in range(len(accommodation_cities)):
                accommodation_users_key = f'accommodation_users_{i}[]'
                accommodation_users = request.form.getlist(accommodation_users_key)
                accommodation_users = [int(user_id) for user_id in accommodation_users]

                accommodations_with_users.append({
                    'accommodation': {
                        'city': accommodation_cities[i],
                        'street': accommodation_streets[i],
                        'nr_budynku': accommodation_buildings[i],
                        'nr_mieszkania': accommodation_places[i],
                        'start_date': accommodation_starts[i],
                        'end_date': accommodation_ends[i],
                        'type': 'hotel',
                        'number_of_people': int(accommodation_people[i])
                    },
                    'users': accommodation_users
                })

            delegation_id = db.add_full_delegation(
                place=place,
                start_date=start_date,
                end_date=end_date,
                transport=transport,
                status=status,
                description=description,
                users=users,
                accommodations_with_users=accommodations_with_users,
                vehicles_with_users=vehicles_with_users
            )

            flash(f"Delegacja została pomyślnie utworzona (ID: {delegation_id}).", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f"Błąd podczas tworzenia delegacji: {str(e)}", "error")
            print(str(e))
            return redirect(url_for('add_delegation'))




@app.route('/edit_delegation/<int:delegation_id>', methods=['GET', 'POST'])
def edit_delegation(delegation_id):
    db = get_db()

    if request.method == 'GET':
        delegation = db.get_delegation(delegation_id)

        users = db.get_all_users_with_personal_data()

        vehicles = db.get_all_vehicles()

        accommodations = db.get_accommodation_by_delegation(delegation_id)

        vehicles_with_users = []
        for vehicle in vehicles:
            vehicle_users = db.get_users_for_vehicles(delegation_id)
            vehicle_user_ids = [user['id_uzytkownika'] for user in vehicle_users]
            vehicles_with_users.append({
                'vehicle_id': vehicle['id_pojazd'],
                'users': vehicle_user_ids
            })

        accommodations_with_users = []
        for accommodation in accommodations:
            accommodation_users = db.get_users_for_accommodations(delegation_id)
            accommodation_user_ids = [user['id_uzytkownika'] for user in accommodation_users]
            accommodations_with_users.append({
                'accommodation': accommodation,
                'users': accommodation_user_ids
            })

        return render_template('edit_delegation.html', delegation=delegation, vehicles=vehicles, users=users, accommodations=accommodations_with_users)

    if request.method == 'POST':
        place = request.form.get('place')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        transport = request.form.get('transport')
        status = request.form.get('status', 'niezatwierdzone')
        description = request.form.get('description', '')

        users = request.form.getlist('users[]')
        users = [int(user_id) for user_id in users]

        vehicles_with_users = []
        vehicle_ids = request.form.getlist('vehicles[]')
        for vehicle_id in vehicle_ids:
            vehicle_users_key = f'vehicle_users_{vehicle_id}[]'
            vehicle_users = request.form.getlist(vehicle_users_key)
            vehicle_users = [int(user_id) for user_id in vehicle_users]
            vehicles_with_users.append({
                'vehicle_id': int(vehicle_id),
                'users': vehicle_users
            })

        accommodations_with_users = []
        accommodation_cities = request.form.getlist('accommodation_city[]')
        accommodation_streets = request.form.getlist('accommodation_street[]')
        accommodation_buildings = request.form.getlist('accommodation_building[]')
        accommodation_places = request.form.get('accommodation_place[]')
        accommodation_starts = request.form.getlist('accommodation_start[]')
        accommodation_ends = request.form.getlist('accommodation_end[]')
        accommodation_people = request.form.getlist('accommodation_people[]')

        for i in range(len(accommodation_cities)):
            accommodation_users_key = f'accommodation_users_{i}[]'
            accommodation_users = request.form.getlist(accommodation_users_key)
            accommodation_users = [int(user_id) for user_id in accommodation_users]

            accommodations_with_users.append({
                'accommodation': {
                    'city': accommodation_cities[i],
                    'street': accommodation_streets[i],
                    'nr_budynku': accommodation_buildings[i],
                    'nr_mieszkania': accommodation_places[i],
                    'start_date': accommodation_starts[i],
                    'end_date': accommodation_ends[i],
                    'type': 'hotel',
                    'number_of_people': int(accommodation_people[i])
                },
                'users': accommodation_users
            })

        try:
            db.edit_full_delegation(
                delegation_id=delegation_id,
                place=place,
                start_date=start_date,
                end_date=end_date,
                transport=transport,
                status=status,
                description=description,
                users=users,
                accommodations_with_users=accommodations_with_users,
                vehicles_with_users=vehicles_with_users
            )
            flash(f"Delegacja została zaktualizowana (ID: {delegation_id}).", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f"Błąd podczas edytowania delegacji: {str(e)}", "error")
            print(str(e))
            return redirect(url_for('edit_delegation', delegation_id=delegation_id))




@app.route("/delete_delegation/<int:delegation_id>")
def delete_delegation(delegation_id):
    db = get_db()
    db.delete_delegation(delegation_id)
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/users')
def users():
    db = get_db()
    users = db.get_all_users_with_personal_data()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        login = request.form['login']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']

        db = get_db()
        db.add_user(login, email, password, role, first_name, last_name, phone)

        return redirect(url_for('users'))

    return render_template('add_user.html')


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    db = get_db()
    user = db.get_user_with_personal_data(user_id)

    if request.method == 'POST':
        login = request.form['login']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        db = get_db()
        db.edit_user(user_id, login, password, email, role, first_name, last_name, phone)
        return redirect(url_for('users'))


    return render_template('edit_user.html', user=user)


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    db = get_db()
    db.delete_user(user_id)
    return redirect(url_for("users"))


@app.route('/vehicles')
def vehicles():
    db = get_db()
    vehicles = db.get_all_vehicles()
    return render_template('vehicles.html', vehicles=vehicles)

@app.route('/add_vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        name = request.form['name']
        reg_number = request.form['reg_number']
        vehicle_type = request.form['vehicle_type']
        available = request.form['available']

        db = get_db()
        db.add_vehicle(name, reg_number, vehicle_type, available)

        return redirect(url_for('vehicles'))

    return render_template('add_vehicle.html')


@app.route('/edit_vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
def edit_vehicle(vehicle_id):
    db = get_db()
    vehicle = db.get_vehicle(vehicle_id)

    if request.method == 'POST':
        name = request.form['name']
        reg_number = request.form['reg_number']
        vehicle_type = request.form['vehicle_type']
        available = request.form['available']
        db.edit_vehicle(vehicle_id, name, reg_number, vehicle_type, available)
        return redirect(url_for('vehicles'))

    return render_template('edit_vehicle.html', vehicle=vehicle)


@app.route('/delete_vehicle/<int:vehicle_id>')
def delete_vehicle(vehicle_id):
    db = get_db()
    db.delete_vehicle(vehicle_id)
    return redirect(url_for("vehicles"))


@app.route('/accommodations')
def accommodations():
    db = get_db()
    accommodations = db.get_all_accommodations()
    return render_template('accommodations.html', accommodations=accommodations)

@app.route('/add_accommodation', methods=['GET', 'POST'])
def add_accommodation():
    if request.method == 'POST':
        city = request.form['city']
        street = request.form['street']
        nr_budynku = request.form['nr_budynku']
        nr_mieszkania = request.form['nr_mieszkania']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        accommodation_type = request.form['accommodation_type']
        people_count = request.form['people_count']


        db = get_db()
        db.add_accommodation(
            delegation_id=1,
            city=city,
            street=street,
            nr_budynku=nr_budynku,
            nr_mieszkania=nr_mieszkania,
            start_date=start_date,
            end_date=end_date,
            accommodation_type=accommodation_type,
            number_of_people=people_count
        )
        return redirect(url_for('accommodations'))

    return render_template('add_accommodation.html')



@app.route('/edit_accommodation/<int:accommodation_id>', methods=['GET', 'POST'])
def edit_accommodation(accommodation_id):
    db = get_db()
    accommodation = db.get_accommodation(accommodation_id)

    if request.method == 'POST':
        city = request.form['city']
        street = request.form['street']
        nr_budynku = request.form['nr_budynku']
        nr_mieszkania = request.form['nr_mieszkania']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        accommodation_type = request.form['accommodation_type']
        people_count = request.form['people_count']
        db.edit_accommodation(accommodation_id, city, street, nr_budynku, nr_mieszkania, start_date, end_date, accommodation_type, people_count)
        return redirect(url_for('accommodations'))

    return render_template('edit_accommodation.html', accommodation=accommodation)


@app.route('/delete_accommodation/<int:accommodation_id>')
def delete_accommodation(accommodation_id):
    db = get_db()
    db.delete_accommodation(accommodation_id)
    return redirect(url_for("accommodations"))



if __name__ == "__main__":
    app.run(debug=True)
