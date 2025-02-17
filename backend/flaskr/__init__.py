from werkzeug.exceptions import HTTPException
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from sqlalchemy import null

from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try: 
            categories = Category.query.order_by('id').all()
            formatted_categories = {category.id: category.type for category in categories}
            return jsonify({
                'success': True,
                'categories': formatted_categories,
                'total_categories': len(formatted_categories)
            })
        except Exception as e:
            abort(500)    
    
        
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            # get all questions from database
            selection = Question.query.order_by('id').all()
            # paginate questions with 10 questions per page
            current_questions = paginate_questions(request, selection)
            # get all categories
            categories = Category.query.order_by('type').all()
            
            formatted_categories = {category.id: category.type for category in categories}
            
            if len(current_questions) == 0:
                abort(404)
            return jsonify({
                'success': True,
                'categories': formatted_categories,
                'total_questions': len(selection),
                'questions': current_questions,
                'current_category': None
            })

        # to check if the error comes from HTTPException    
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(500)        

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        
        try:
            question = Question.query.filter(Question.id==id).one_or_none()
           
            
            if question is None:
                abort(404)
            question.delete()
            

            return jsonify({
            'success': True,
            'deleted':id
        })
            

        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(400)   

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_question():
        try:
            body = request.get_json()
            new_question = body.get('question')
            new_category = body.get('category')
            new_difficulty = body.get('difficulty')
            new_answer = body.get('answer')
            
            if new_answer == '' or new_question == '' or new_difficulty == '' or new_category == '': 
            
                abort(400)
            
            try:
                question = Question(
                question=new_question,
                answer= new_answer,
                difficulty= new_difficulty,
                category= new_category
                )
                question.insert() 

                return jsonify({
                'success': True,
                'created':question.id
                
            })

            except:
                abort(422)  
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(500)          

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        try:
            body = request.get_json()
            searchTerm = body.get('searchTerm')
            selection = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()
            if len(selection) == 0:    
                    abort(404)
            try:
                current_questions = paginate_questions(request, selection)
                
                if len(current_questions) == 0:    
                    abort(404)
                return jsonify({
                'success': True,
                'questions':current_questions,
                'total_questions': len(selection),
                'current_category': None
                
            })

            except Exception as e:
                if isinstance(e, HTTPException):
                    abort(e.code)
                else:
                    abort(422)    
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(500)


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_category(id):
        try:
            category = Category.query.get(id)
            
            if category is None:
                abort(404)
            try:    
                selection = Question.query.filter_by(category=category.id).all()
                
                current_questions = paginate_questions(request, selection)

                if len(current_questions) == 0:
                    abort(404)
                return jsonify({
                    'success': True,
                    'total_questions': len(selection),
                    'questions': current_questions,
                    'current_category': category.format()
                })
            except Exception as e:
                if isinstance(e, HTTPException):
                    abort(e.code)
                else:
                    abort(422)  
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(500)


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()
            quiz_category = body.get('quiz_category')
            previous_questions=body.get('previous_questions')    
                
            try:
                if quiz_category['id'] == 0:
                    questions = Question.query.all()
                else:
                    questions = Question.query.filter(Question.category==quiz_category['id']).all()
                available_questions = []
                for question in questions:
                    if question.id in previous_questions:
                        pass
                    else:
                        available_questions.append(question)
                        
             
                if len(available_questions) == 0:
                    question = None
                else:
                    question = random.choice(available_questions).format()
                
               
                return jsonify({
                'success': True,
                'question': question,
                'totalQuestions':len(questions)
                
                
            })

            except Exception as e:
                if isinstance(e, HTTPException):
                    abort(e.code)
                else:
                    abort(422)    
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(500)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400    


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource(s) Not Found'

        }

        ), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Not Processable"
        }), 422

    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

           

    return app

