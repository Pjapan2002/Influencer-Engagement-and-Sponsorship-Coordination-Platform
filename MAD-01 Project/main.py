from flask import Flask,render_template,request,redirect,session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "japan@2002_Patel"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# create Database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    label = db.Column(db.String(150))
    fullName = db.Column(db.String(500))

    sponsors = db.relationship('Sponsors', back_populates='user', cascade='all, delete-orphan')
    influencers = db.relationship('Influencer', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User {self.username}>"
    
class Sponsors(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campName = db.Column(db.String(500))
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', back_populates='sponsors')
    campaigns = db.relationship('Campaign', backref='sponsor', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Sponsor(camp_name='{self.campName}', user_id={self.userId})>"
    
class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(500))
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    user = db.relationship('User', back_populates='influencers')

    def __repr__(self):
        return f"<Influencer(category_name='{self.category}', user_id={self.userId})>"
    
class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(500), nullable=False)
    campInfo = db.Column(db.String(500))
    industry = db.Column(db.String(500))
    budget = db.Column(db.String(200))
    startDate = db.Column(db.String(100), nullable=False)
    endDate = db.Column(db.String(100), nullable=False)
    visibility = db.Column(db.String(500))
    goals = db.Column(db.String(500))
    sponsorId = db.Column(db.Integer, db.ForeignKey('sponsors.id'), nullable=False)

    # sponsors = db.relationship('Sponsors', back_populates='campaign')
    
    def __repr__(self):
        return f"<Campaign(title='{self.title}',title='{self.title}',campInfo='{self.campInfo}',industry='{self.industry}',budget='{self.budget}', sponsorId={self.sponsorId})>"

class Ad_request(db.Model):
    id = db.Column(db.Integer, autoincrement=True)
    request_from = db.Column(db.String(100), default="sponsor")
    campId = db.Column(db.Integer, db.ForeignKey('campaign.id'), primary_key=True, nullable=False)
    influencerId = db.Column(db.Integer, db.ForeignKey('influencer.id'), primary_key=True, nullable=False)
    message = db.Column(db.String(500))
    paymentAmount = db.Column(db.String(300))
    status = db.Column(db.String(150), default="pending")

    def __repr__(self):
        return f"<Ad_request(camp_id='{self.campId}',influencer_id='{self.influencerId}',payment_amount='{self.paymentAmount}', status={self.status})>"
    

@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        # print(username)
        # get user data from User table
        user_data = db.session.query(
            User.id,
            User.password,
            User.label
        ).filter(User.username == username).first()
        
        if password != user_data.password:
            print("Your password is wrong!!! Please try again.")
            return redirect('/')
        
        if username in session:
            return redirect(f'/{user_data.label}')
        else:
            session['username'] = username
            return redirect(f'/{user_data.label}')
    
    return render_template('login.html')

@app.route('/signup/<label>', methods=["GET", "POST"])
def signup(label):
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get("name")
        if label == "sponsor":
            comp_name = request.form.get("comp_name")

            new_user = User(username=username, password=password, label=label, fullName=name)
            new_sponsor = Sponsors(campName=comp_name,user=new_user)
            db.session.add(new_user)
            db.session.add(new_sponsor)
            db.session.commit()
        else:
            category = request.form.get("category")
            
            new_user = User(username=username, password=password, label=label, fullName=name)
            new_Influencer = Influencer(category=category,user=new_user)
            db.session.add(new_user)
            db.session.add(new_Influencer)
            db.session.commit()

        session['username'] = username
        return redirect(f'/{label}')
    return render_template(f"{label}/signup.html")

@app.route('/logout')
def logout():
    # session.pop('username', None)
    # print("hello")
    # return redirect('/')
    # return render_template('login.html')
    return "hello"

@app.route('/sponsor')
def sponsor_home():
    name = db.session.query(
        User.fullName
    ).filter(User.username == session['username']).first()[0]

    act_camp = db.session.query(
        Campaign.title,
        Campaign.budget,
        Ad_request.status
    ).filter(
        User.username == session['username']
    ).filter(
        User.id == Sponsors.userId
    ).filter(
        Sponsors.id == Campaign.sponsorId
    ).filter(
        Campaign.id == Ad_request.campId
    ).all()

    ad_request = db.session.query(
        Ad_request.influencerId,
        Ad_request.campId,
        Ad_request.message,
        Ad_request.paymentAmount,
        Ad_request.status
    ).filter(
        User.username == session['username']
    ).filter(
        User.id == Sponsors.userId
    ).filter(
        Sponsors.id == Campaign.sponsorId
    ).filter(
        Campaign.id == Ad_request.campId
    ).filter(
        Ad_request.request_from == "influencer"
    ).all()

    return render_template("sponsor/home.html", username = name, act_camp = act_camp, ad_request = ad_request)

@app.route('/sponsor/campaigns', methods=["GET", "POST"])
def sponsor_campaigns():
    if request.method == "POST":
        title = request.form.get("title")
        camp_info = request.form.get("camp_info")
        industry = request.form.get("Industry")
        budget = request.form.get("budget")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        visibility = request.form.get("visibility")
        goals = request.form.get("goals")

        user_id = db.session.query(
            Sponsors.id
        ).filter(
            User.username == session['username']
        ).filter(
            User.id == Sponsors.userId
        ).first()
        
        new_campaign = Campaign(title=title, campInfo=camp_info, industry=industry, budget=budget, startDate=start_date, endDate=end_date, visibility=visibility, goals=goals, sponsorId=user_id[0])
        db.session.add(new_campaign)
        db.session.commit()

    camp_data = db.session.query(
        Campaign.id,
        Campaign.title,
        Campaign.budget
    ).filter(
        User.username == session['username']
    ).filter(
        User.id == Sponsors.userId
    ).filter(
        Sponsors.id == Campaign.sponsorId
    ).all()

    influencer_data = db.session.query(
        Influencer.id,
        User.fullName
    ).filter(User.id == Influencer.userId).all()
    # print(camp_data)
    return render_template("sponsor/campaigns.html", camp_data=camp_data, influencer_data = influencer_data)
    
@app.route('/sponsor/campaigns/ad_request', methods=["POST"])
def sponsor_ad_request():
    camp_id = request.form.get("camp_id")
    influencer_id = request.form.get("influencer_id")
    msg = request.form.get("msg")
    payment = request.form.get("payment")

    new_ad_request = Ad_request(campId = camp_id, influencerId = influencer_id, message = msg, paymentAmount = payment)
    db.session.add(new_ad_request)
    db.session.commit()

    return redirect('/sponsor/campaigns')

@app.route('/sponsor/find')
def sponsor_find():
    influencer_data = db.session.query(
        User.fullName
    ).filter(User.id == Influencer.userId).all()
    return render_template("sponsor/find.html", influencer_data = influencer_data)


@app.route('/influencer')
def influencer_home():
    name = db.session.query(
        User.fullName
    ).filter(User.username == session['username']).first()[0]

    received_request = db.session.query(
        Ad_request.id,
        Ad_request.campId,
        Ad_request.influencerId,
        Ad_request.message,
        Ad_request.paymentAmount,
        Ad_request.status,
        Ad_request.request_from
    ).filter(
        User.username == session['username']
    ).filter(
        User.id == Influencer.userId
    ).filter(
        Influencer.id == Ad_request.influencerId
    ).all()

    act_camp = db.session.query(
        Campaign.title,
        Campaign.budget,
        Ad_request.status
    ).filter(
        User.username == session['username']
    ).filter(
        User.id == Influencer.userId
    ).filter(
        Influencer.id == Ad_request.influencerId
    ).filter(
        Ad_request.campId == Campaign.id
    ).all()
    # print(act_camp)
    return render_template("influencer/home.html", username = name, received_request = received_request, act_camp = act_camp)

@app.route('/request_response/<response_by>', methods=["POST"])
def influencer_ad_request_responce(response_by):
    resp_data = request.json
    ad_request = db.session.get(entity= Ad_request, ident= { "campId": int(resp_data['camp_id']), "influencerId": int(resp_data["influencer_id"]) })
    
    if ad_request:
        ad_request.status = resp_data['response']
    db.session.commit()
    
    return redirect(f'/{response_by}')

@app.route('/influencer/ad_request/<camp_id>', methods=["POST"])
def influencer_ad_request(camp_id):
    influencer_id = db.session.query(
        Influencer.id
    ).filter(User.username == session["username"]).first()

    msg = request.form.get("msg")
    exp_amount = request.form.get("exp_amount")
    
    new_ad_request = Ad_request(campId = int(camp_id), influencerId = influencer_id[0], request_from = "influencer", message = msg, paymentAmount = exp_amount)
    db.session.add(new_ad_request)
    db.session.commit()
    return redirect('/influencer/find')

@app.route('/influencer/find')
def influencer_find():
    camp_data = db.session.query(
        Campaign.id,
        Campaign.title,
        Campaign.budget
    ).filter(Campaign.visibility == 'Public').all()

    return render_template("influencer/find.html", camp_data = camp_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)