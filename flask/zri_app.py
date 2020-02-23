
import flask 
from flask import Flask, render_template, request, Response

import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')


#import data for ZRI index, fitted values based on model, and residuals
zri_data = pd.read_csv('data/kdw_residuals.csv')
#change the date column to a datetime object
zri_data.loc[:,'date'] =  pd.to_datetime(zri_data.loc[:,'date'])


#function that takes a zipcode input, checks whether it exists in the data
#if zipcode exists make a plot of predction values and actual values to compare
#if zipcode does not exist in the data, return an error 
def read_csv_by_zip(zip_code_):
    zip_code = int(zip_code_)
    if zri_data[zri_data['RegionName']==zip_code].shape[0]==0:
        return 'Error'
    else:
        plt.switch_backend('agg')
        plt.plot(zri_data['date'].where(zri_data['RegionName']==zip_code),zri_data['Predictions'].where(zri_data['RegionName']==zip_code),label='Predictions')
        plt.plot(zri_data['date'].where(zri_data['RegionName']==zip_code),zri_data['Actuals'].where(zri_data['RegionName']==zip_code),label='Actuals')
        plt.legend(loc='upper left')
        plt.axvline(dt.datetime(2018, 1, 1), color='gray')
        plt.axvline(dt.datetime(2019, 1, 1), color='gray')
        plt.xticks(rotation=20)
        plt.title('ZRI Model Predictions')
        plt.savefig('static/new_plot1.png')


#function that takes a zipcode input, checks whether it exists in the data
#if zipcode it does, make a plot of the residual values from the csv file
#if the zipcode does not exist in the data, return an error
def residuals(zip_code_):
    zip_code = int(zip_code_)
    if zri_data[zri_data['RegionName']==zip_code].shape[0]==0:
        return 'Error'
    else:
        plt.switch_backend('agg')
        plt.plot(zri_data['date'].where(zri_data['RegionName']==zip_code),zri_data['Residuals'].where(zri_data['RegionName']==zip_code),label='Residuals')
        plt.axvline(dt.datetime(2018, 1, 1), color='gray')
        plt.axvline(dt.datetime(2019, 1, 1), color='gray')
        plt.xticks(rotation=20)
        plt.title('Residuals')
        plt.savefig('static/new_plot2.png')


#initialize flask app and disable the cache
app = flask.Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


#initial page with a html form input with regex validation for a 5 digit number
@app.route('/', methods=['GET'])
def zip_input_form():
    return render_template('form.html')


#second page which returns the graphs of the fitted model as well as a graph of residuals
#if zipcode typed in is not within the data, the user will be directed to an error page 
@app.route('/handle_data', methods=['GET','POST'])
def handle_data():
    zip_code = request.form['zip']
    if read_csv_by_zip(zip_code)=='Error' or residuals(zip_code)=='Error':
        return render_template('index2.html', name='zipcode not found in ZRI data')
    else:
        zip_ = int(zip_code)
        place_name = zri_data['Area_Name'][zri_data['RegionName']==zip_].values[0]
        zip_title = 'ZRI Predictions for Zipcode: {} in {}'.format(zip_code, place_name)
        img_url1 = flask.url_for('static', filename='new_plot1.png')
        img_url2 = flask.url_for('static', filename='new_plot2.png')
        return render_template('index.html', name = zip_title, image1_url=img_url1, image2_url=img_url2)

#Disable caching after each app request in order to retrieve new data each time
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


if __name__ == '__main__':
    app.run(debug=True, port=5001)

