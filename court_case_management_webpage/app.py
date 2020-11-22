from flask import Flask , render_template
from flask_dance.contrib.google import make_google_blueprint, google
import mysql.connector
from forms import Case , CaseUpdate , Hearing

#################################
###### Database Connection ######
#################################
config = {
  'user': 'root',
  'password': '',
  'host': 'localhost',
  'database': 'hospital',
  'raise_on_warnings': True,
}

db = mysql.connector.connect(**config)
mycursor = db.cursor(buffered=True)

###################################

app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = 'qwertyuiop'
blueprint = make_google_blueprint(client_id='',
        client_secret='',
        offline=True , scope= ['profile','email'])

app.register_blueprint(blueprint,url_prefix='/login')

@app.route("/")
def index():
    render_template("index.html")

@app.route('/login/google')
def login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v1/userinfo")
    assert resp.ok, resp.text

    form = Case()
    sql = "SELECT id , name FROM lawyers ;"
    mycursor.execute(sql)
    lawyers = mycursor.fetchall()
    form.prosecutor.choices = lawyers
    form.defender.choices = lawyers

    if form.validate_on_submit():

        sql = "INSERT INTO cases (u_id, party_name, prosecutor, defendant, defender, fir_no, case_type, status, verdict) VALUES('"+ +"','"+form.party_name.data+"','"+form.prosecutor.data+"','"+form.defendant.data+"','"+form.defender.data+"','"+form.fir_no.data+"','"+form.case_type.data+"','"+form.status.data+"','"+form.verdict.data+"');"
        mycursor.execute(sql)
        db.commit()
        #remember to implement SESSION protocol for u_id

    sql = "SELECT id, fir_no FROM cases WHERE u_id ='"+resp.json()["id"]+"';"
    mycursor.execute(sql)
    cases = mycursor.fetchall()
    return render_template("profile.html",profile = resp.json()["profile"] ,cases = cases , form=form)

@blueprint.session.authorization_required
@app.route('/case/<cid>')
def case(cid):
    update = CaseUpdate()
    if update.validate_on_submit():
        sql = "UPDATE cases SET status = '"+update.status.data+"' verdict = '"+update.verdict.data+"' WHERE c_id = "+cid+";"
        mycursor.execute(sql)
        db.commit()
        pass

    hform = Hearing()
    if hform.validate_on_submit():
        sql = "INSERT INTO hearings (date , judge, start ,end ,location, next, c_id ) VALUES ('"+hform.date.data+"','"+hform.judge.data+"','"+hform.start.data+"','"+hform.end.data+"','"+hform.location.data+"','"+hform.next.data+"','"+hform.c_id.data+"') ;"
        mycursor.execute(sql)
        db.commit()
        pass

    sql = "SELECT * FROM cases WHERE id ="+cid+";"
    mycursor.execute(sql)
    case = mycursor.fetchall()
    sql = "SELECT * FROM hearings WHERE cid ="+cid+";"
    mycursor.execute(sql)
    hearings= mycursor.fetchall()
    render_template("caseview.html", case = case ,hearings = hearings, update = update ,hform = hform )


@app.route('/search/<cid>')
def search(cid):
    # code to retrieve case details and Hearings
    sql = "SELECT * FROM cases WHERE id ="+cid+";"
    mycursor.execute(sql)
    case = mycursor.fetchall()
    sql = "SELECT * FROM hearings WHERE cid ="+cid+";"
    mycursor.execute(sql)
    hearings= mycursor.fetchall()
    render_template("caseview.html" , case = case , hearing = hearing)



if __name__ == '__main__':
    app.run(debug=True)
