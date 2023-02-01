from flask import Flask, render_template, flash, session, redirect, url_for
from petForms import *
from petdb import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mySecret'


@app.route('/')
def index():
    DBConnection.dbConnect()
    return render_template('pet_home.html')


@app.route('/user', methods=['GET', 'POST'])
def registerUser():
    form = OwnerForm()
    if form.validate_on_submit():
        session['uname'] = form.name.data
        DBConnection.dbConnect()
        DBConnection.insertTable('owners', [session.get('uname', None)])
        flash(f'Owner {session["uname"]} added')
        form.name.data = ''
    return render_template('register_user.html', form=form)


@app.route('/pet', methods=['GET', 'POST'])
def registerPet():
    form = PetForm()
    if form.validate_on_submit():
        try:
            session['pname'] = form.name.data
            session['price'] = form.price.data
            session['pcategory'] = form.category.data
            DBConnection.dbConnect()
            DBConnection.insertTable('pets', [session.get('pname', None), session.get('price', None), session.get('pcategory', None)])
            flash(f'Pet {session["pname"]} of category {session["pcategory"]} added')
            form.name.data = ''
            form.category.data = ''
        except psycopg2.Error as pe:
            return pe
        except Exception as e:
            return e
    return render_template('register_pet.html', form=form)


@app.route('/ownapet', methods=['GET', 'POST'])
def ownPet():
    form = RegisterForm()
    if form.validate_on_submit():
        session['uname'] = form.ownerName.data
        session['pname'] = form.petName.data
        DBConnection.dbConnect()
        user = DBConnection.selectTable("owners", f"owner_name = '{form.ownerName.data}'")
        pet = DBConnection.selectTable("pets", f"pet_name = '{form.petName.data}'")
        
        if len(user) == 0 or len(pet) == 0:
            flash('This user or pet does not exist')
        else:
            userid = user[0][0]
            petid = pet[0][0]
            owner = DBConnection.selectTable("ownership", f"pet_id = {petid}")
            if len(owner) > 0:
                ownerName = DBConnection.selectTable("owners", f"owner_id = {owner[0][0]}")
                flash(f'Pet {pet[0][1]} already belongs to {ownerName[0][1]}')
            else:
                flash(f'Pet {pet[0][1]} now belongs to {user[0][1]}')
                DBConnection.insertTable('ownership', [userid, petid])
        form.ownerName.data = ''
        form.petName.data = ''
    return render_template('register_ownership.html', form=form)


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/createTables', methods=['GET', 'POST'])
def createTables():
    DBConnection.dbConnect()
    DBConnection.createTables()
    flash('Tables created')
    return render_template('admin.html')


@app.route('/displayOwners', methods=['GET', 'POST'])
def dispOwners():
    DBConnection.dbConnect()
    rows = DBConnection.selectTable(tname="owners", additions=" ORDER BY owner_id")
    return render_template('display_owners.html', rows=rows)


@app.route('/displayPets', methods=['GET', 'POST'])
def dispPets():
    DBConnection.dbConnect()
    rows = DBConnection.selectTable(tname="pets", additions=" ORDER BY pet_id")
    return render_template('display_pets.html', rows=rows)


@app.route('/displayOwnership', methods=['GET', 'POST'])
def dispOwnership():
    DBConnection.dbConnect()
    rows = DBConnection.selectTable(tname="ownership", additions=" GROUP BY owner_id, pet_id ORDER BY owner_id, pet_id")
    ownerships = []
    for row in rows:
        user = DBConnection.selectTable("owners", f"owner_id = {row[0]}")[0]
        pet = DBConnection.selectTable("pets", f"pet_id = {row[1]}")[0]
        ownerships.append((user[1], pet[1], pet[2], pet[3], user[0], pet[0]))
    return render_template('display_ownerships.html', rows=ownerships)


@app.route('/deleteOwner/<ownerId>')
def deleteOwner(ownerId):
    DBConnection.dbConnect()
    DBConnection.deleteTable("owners", f"owner_id={ownerId}")
    return redirect(url_for('dispOwners'))


@app.route('/deletePet/<petId>')
def deletePet(petId):
    DBConnection.dbConnect()
    DBConnection.deleteTable("pets", f"pet_id={petId}")
    return redirect(url_for('dispPets'))


@app.route('/deleteOwnership/<petId>')
def deleteOwnership(petId):
    DBConnection.dbConnect()
    DBConnection.deleteTable("ownership", f"pet_id = {petId}")
    return redirect(url_for('dispOwnership'))


@app.route('/modifyOwner/<ownerId>', methods=['GET', 'POST'])
def modifyOwner(ownerId):
    form = OwnerForm()
    form.ownerId.data = ownerId
    if form.validate_on_submit():
        session['uname'] = form.name.data
        ownerId = int(form.ownerId.data)
        DBConnection.dbConnect()
        DBConnection.updateTable("owners", f"owner_name='{session.get('uname', None)}'", f"owner_id={ownerId}")
        form.name.data = ''
        form.ownerId.data = -1
        return redirect(url_for('dispOwners'))
    return render_template('register_user.html', form=form)


@app.route('/modifyPet/<petId>', methods=['GET', 'POST'])
def modifyPet(petId):
    form = PetForm()
    form.petId.data = petId
    if form.validate_on_submit():
        session['pname'] = form.name.data
        session['price'] = form.price.data
        session['pcategory'] = form.category.data
        petId = int(form.petId.data)
        setStr = f"pet_name='{session.get('pname', None)}', pet_price={session.get('price', None)}, pet_category='{session.get('pcategory', None)}'"
        DBConnection.dbConnect()
        DBConnection.updateTable("pets", setStr, f"pet_id={petId}")
        form.name.data = ''
        form.price.data = -1
        form.category.data = ''
        form.petId.data = -1
        return redirect(url_for('dispPets'))
    return render_template('register_pet.html', form=form)


@app.route('/modifyOwnership/<petId>/<petName>', methods=['GET', 'POST'])
def modifyOwnership(petId, petName):
    form = ModifyOwnershipForm()
    form.petId.data = petId
    if form.validate_on_submit():
        newName = form.ownerName.data
        petId = int(form.petId.data)
        DBConnection.dbConnect()
        owner_id = DBConnection.selectTable("owners", f"owner_name='{newName}'")[0]
        DBConnection.updateTable("ownership", f"owner_id={owner_id[0]}", f"pet_id={petId}")
        form.petId.data = -1
        form.ownerName.data = ''
        return redirect(url_for('dispOwnership'))
    return render_template('updateOwnership.html', petId=petId, petName=petName, form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)