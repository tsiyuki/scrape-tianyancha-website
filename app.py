from flask import Flask, render_template, make_response, jsonify, request, redirect
import json, os
from scrape import Scrape

app = Flask(__name__)

app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['JSON_AS_ASCII'] = False

from wtforms import StringField, SubmitField, validators
from flask_wtf import FlaskForm


class KeyForm(FlaskForm):
    key_word = StringField("key_word", [validators.DataRequired()])
    submit = SubmitField('Search')


class CompanyForm(FlaskForm):
    company = StringField("company", [validators.DataRequired()])
    submit = SubmitField('Search')

@app.route('/')
def index():
    return "This is the home page"

@app.route('/key_word', methods=['GET', 'POST'])
def key_word():
    keyForm = KeyForm(request.form)
    companyForm = CompanyForm(request.form)
    key_word = None
    names = None
    company = None
    number = 0
    if keyForm.validate_on_submit():
        key_word = keyForm.key_word.data
        scrape = Scrape(key_word)
        number, driver = scrape.login()
        tags, names = scrape.get_company_list(driver)
    if companyForm.validate_on_submit():
        company = companyForm.company.data
        scrape = Scrape(company)
        number, driver = scrape.login()
        driver = scrape.select_company(driver, company)
        lists = scrape.scrapy(driver)
        return render_template('company.html', lists=lists)
    return render_template('index.html',
                           keyForm=keyForm,
                           companyForm=companyForm,
                           key_word=key_word,
                           names=names,
                           number=number,
                           company=company)


@app.route('/mystring', methods=['GET', 'POST'])
def mystring():
    return "Searching..."

@app.route('/company/<item>', methods=['GET', 'POST'])
def company(item):
    return "Searching..."

@app.route('/get_company_list', methods=['GET'])
def get_list():
    keyWord = request.args.get("keyWord")
    scrape = Scrape(keyWord)
    number, driver = scrape.login()
    tags, names = scrape.get_company_list(driver)
    name_list = []
    for key in names.keys():
        name_list.append(key)
    return jsonify({"num": number, "list": name_list})

@app.route('/get_company_info', methods=['GET'])
def get_info():
    companyName = request.args.get("companyName")
    scrape = Scrape(companyName)
    number, driver = scrape.login()
    driver = scrape.select_company(driver, companyName)
    list = scrape.scrapy(driver)
    return jsonify(list)

app.run(port=5000)
