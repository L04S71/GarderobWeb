from flask import Flask, render_template, make_response, request
from flask_sqlalchemy import SQLAlchemy


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

@app.route('/')
def index():
    seasons = Season.query.all()
    return render_template("index.html", seasons=seasons)

if __name__ == '__main__':
    app.run()