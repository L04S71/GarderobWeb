from flask import Flask, render_template, make_response, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.sqlite import DATETIME


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wardrobe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["DEBUG"] = False
db = SQLAlchemy(app)
db.app = app
db.init_app(app)

class CatalogItem(db.Model):
    __tablename__ = 'Full_Catalog'
    idf = db.Column(db.Integer, primary_key=True)
    Name_Season = db.Column(db.String(15))
    Name_Clothes = db.Column(db.String(20))
    Comment = db.Column(db.Text)
    Gender = db.Column(db.String(10))

class Clothes(db.Model):
    __tablename__ = 'Foto_Clothes'
    id_foto = db.Column(db.Integer, primary_key=True)
    Foto = db.Column(db.BLOB)
    Comment = db.Column(db.Text)
    Data = DATETIME(storage_format="%(day)02d/%(month)02d/%(year)04d")
    Id_Clothes = db.Column(db.Integer)

class TypeClothes(db.Model):
    __tablename__ = 'Type_Clothes'
    ID_Clothes = db.Column(db.Integer, primary_key=True)
    Name_Clothes = db.Column(db.String(20))
    Gender = db.Column(db.String(10))
    ID_Season = db.Column(db.Integer)

class Season(db.Model):
    __tablename__ = 'Season'
    ID = db.Column(db.Integer, primary_key=True)
    Name_Season = db.Column(db.String(15))

@app.route('/catalog/item/image/<int:id>')
def image(id):
    image = Clothes.query.get(id)
    response = make_response(image.Foto)
    response.headers.set("Content-Type", "image/jpeg")
    response.headers.set("Content-Disposition", "attachment", filename=f"image{id}.png")
    return response

@app.route('/catalog')
def catalog():
    filter_seasons = request.args.getlist('seasons[]')
    filter_genders = request.args.getlist('genders[]')

    seasons = Season.query.all()
    seasons = [season.Name_Season for season in seasons if not filter_seasons or str(season.ID) in filter_seasons]
    genders = [gender for gender in ['мужской', 'женская'] if not filter_genders or gender in filter_genders]

    items = CatalogItem.query.filter(CatalogItem.Name_Season.in_(seasons)).filter(CatalogItem.Gender.in_(genders)).all()
    return render_template("catalog.html", items=items)

@app.route('/add', methods=["POST"])
def add():
    file = request.files["item-image"]
    image = file.read()

    clothes = TypeClothes.query.all()
    row = next((c for c in clothes if c.Name_Clothes == request.form['item-clothes']
        and c.Gender == request.form['item-gender']
        and c.ID_Season == int(request.form['item-season'])), None)
    if not row:
        row = TypeClothes(
            Name_Clothes=request.form['item-clothes'],
            Gender=request.form['item-gender'],
            ID_Season=int(request.form['item-season']))
        db.session.add(row)
        db.session.flush()

    item = Clothes(Data="date('now')", Comment=request.form['item-comment'], Id_Clothes=row.ID_Clothes, Foto=image)
    db.session.add(item)
    db.session.commit()
    return redirect('/')

@app.route('/del', methods=["POST"])
def delete():
    id = request.form.get("id")
    item = Clothes.query.get(int(id))
    db.session.delete(item)
    db.session.commit()
    return redirect('/')

@app.route('/')
def index():
    seasons = Season.query.all()
    return render_template("index.html", seasons=seasons)

if __name__ == '__main__':
    app.run()