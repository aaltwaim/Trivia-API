import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =(page-1)*QUESTIONS_PER_PAGE
  end = start+QUESTIONS_PER_PAGE
  questions =[question.format() for question in selection]
  current_questions = questions[start:end]
  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  #CORS(app, resources={r"*/api/*": {"origins": "*"}})
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 
    'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 
    'GET,PATCH,POST,DELETE,OPTIONS')
    return response
     #done by AT
  
  @app.route('/categories')
  def retrieve_categories():
    categories = Category.query.order_by(Category.type).all()

    if len(categories) == 0:
      abort(404)
    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
    })
    #done by AT

  # added pagination


  @app.route('/questions')
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    categories = Category.query.order_by(Category.type).all()

    if(len(current_questions))==0:
      abort(404)
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories': {category.id: category.type for category in categories},
      'current_category': None

    })
    #done by AT

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      question.delete()
      return jsonify({
        'success': True,
        'deleted': question_id,
        'total_questions': len(Question.query.all())
      })
    except:
      abort(422)
  #done by AT

  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()
    if not ('question' in body and 'answer' in body and 'difficulty' in body 
    and 'category' in body):
      abort(422)

    question = body.get('question')
    answer = body.get('answer')
    category = body.get('category')
    difficulty = body.get('difficulty')

    try:
      new_question = Question(question=question,answer=answer,
      category=category,difficulty=difficulty)
      new_question.insert()
      # selection = Question.query.order_by(Question.id).all()
      # current_questions = paginate_questions(request, selection)
      return jsonify({
        'success': True,
        'created': question.id,
        # 'questions': current_questions,
        # 'total_questions': len(Question.query.all())
      })
    except:
      abort(422)
     #done by AT
    
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    targted_question = body.get('searchTerm',None)
    if targted_question:

      resulted_questions = Question.query.filter(Question.question.
      ilike(f'%{targted_question}%')).all()
      return jsonify({
        'success': True,
        'questions':[question.format() for question in resulted_questions],
        'total_questions': len(resulted_questions),
        'current_category': None
      })
    else:
      abort(404)
   #done by AT

  @app.route('/categories/<int:category_id>/questions')
  def retrieve_questions_based_on_category(category_id):
    try:
      questions_by_category = Question.query.filter(
        Question.category == str(category_id)).all()
      return jsonify({
        'success': True,
        'questions':[question.format() for question in questions_by_category],
        'total_questions': len(questions_by_category),
        'current_category': category_id

      })
    except:
      abort(404)

   #done by AT
 
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    try:
      body = request.get_json()
      category = body.get('quiz_category')
      previous_questions = body.get('previous_questions')
      if category['type'] == 'click':
        remaining_questions = Question.query.filter(
          Question.id.notin_(previous_questions)).all()
      else:
        remaining_questions = Question.query.filter_by(
          category=category['id']).filter(Question.id.notin_(previous_questions)).all()
      
      random_question = remaining_questions[random.randrange(0, 
      len(remaining_questions))].format() if len(remaining_questions)> 0 else None
      return jsonify({
        'success': True,
        'question': random_question
      })
    except:
      abort(422)
   #done by AT
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'not found'
    }), 404
    
  

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable'
    }), 422
  
  return app

    