#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    '''
    a = 1
    b = 0
    c = a/b
    return c
	'''
    return 'Hello World!'

@app.route('/user/<username>')
def show_username(username):
    return 'User %s' % username

@app.route('/post/<int:post_id>')
def show_postid(post_id):
    return 'Post %d' % post_id

if __name__ == '__main__':
    app.run(debug=True)