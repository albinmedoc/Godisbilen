from datetime import datetime
import json, os
from flask import Blueprint, render_template, current_app, url_for, redirect
from flask_mail import Message
from .utils import shop_open
from .forms import ContactForm
from godisbilen.app import mail, db
from godisbilen.order import Order, OrderForm
from godisbilen.campaign import Campaign, CampaignOrder
from godisbilen.campaign.forms import JoinCampaignForm

bp_main = Blueprint("main", __name__)

@bp_main.route("/", methods=["GET", "POST"])
def home():
    campaigns = Campaign.query.filter(Campaign.start < datetime.now(), Campaign.end > datetime.now()).all()
    order_form = OrderForm()
    if(order_form.validate_on_submit()):
        order = Order.create(order_form.phone_number.data, order_form.lat.data, order_form.lng.data)
        return redirect(url_for("order.receipt", order_number=order.order_number.number))
    return render_template("main/home.html", shop_open=shop_open(), campaigns=campaigns, order_form=order_form)

@bp_main.route("/assortment")
def assortment():
    return render_template("main/assortment.html")

@bp_main.route("/regions")   
def regions():
    return render_template("main/regions.html")

@bp_main.route("/tos")   
def tos():
    return render_template("main/tos.html")

@bp_main.route("/contact", methods=["GET", "POST"])   
def contact():
    form = ContactForm()
    if(form.validate_on_submit()):
        msg = Message(subject=form.subject.data, recipients=[current_app.config["MAIL_DEFAULT_SENDER"]])
        msg.body = "Meddelande från " + form.name.data + "(" + form.email.data + ")" + ". Innehåll: " + form.message.data
        if(form.order_number.data.strip() != ""):
            msg.body = msg.body + ". Ordernummer: " + form.order_number.data
        mail.send(msg)
        return render_template("main/contact.html", form=form, message_sent=True)
    return render_template("main/contact.html", form=form)

@bp_main.route("/about")   
def about():
    return render_template("main/about.html")

@bp_main.route("/faq")   
def faq():
    return render_template("main/faq.html")