# For a SQL skills testing app, I recommend using Python with:
# - Flask/Django for the web framework
# - SQLite/PostgreSQL for the database
# - HTML/CSS/JavaScript for the frontend

# Here's a basic Flask structure to get started:

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
try:
    from gpt4all import GPT4All
except ImportError:
    print("Error: gpt4all module not found. Please install it using 'pip install gpt4all'")
    exit(1)

app = Flask(__name__)

# Initialize the model with a context manager to ensure proper resource handling
try:
    # Initialize the model - using a smaller model that's more likely to be available
    model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Please ensure you have downloaded the model file. You can download it using:")
    print("from gpt4all import GPT4All")
    print("model = GPT4All.retrieve_model('mistral-7b-instruct-v0.1.Q4_0.gguf')")
    exit(1)

# Dictionary to store table schemas and their corresponding questions
SQL_TEST_CASES = [
    {
        "tables": """
Employees (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    salary DECIMAL(10,2),
    department_id INT,
    hire_date DATE
)

Departments (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    location VARCHAR(100),
    manager_id INT
)
        """,
        "sample_data": {
            "Employees": [
                {"id": 1, "name": "김철수", "salary": 65000.00, "department_id": 1, "hire_date": "2022-03-15"},
                {"id": 2, "name": "이영희", "salary": 72000.00, "department_id": 2, "hire_date": "2021-08-22"},
                {"id": 3, "name": "박민준", "salary": 58000.00, "department_id": 1, "hire_date": "2023-01-10"}
            ],
            "Departments": [
                {"id": 1, "name": "개발팀", "location": "서울", "manager_id": 1},
                {"id": 2, "name": "영업팀", "location": "부산", "manager_id": 2}
            ]
        },
        "questions": [
            "각 부서별 평균 급여가 전체 평균 급여보다 높은 부서의 이름과 해당 부서의 평균 급여를 구하는 SQL 쿼리를 작성하세요.",
            "부서별로 가장 높은 급여를 받는 직원의 이름과 급여를 찾는 쿼리를 작성하세요.",
            "같은 부서에서 자신보다 먼저 입사한 직원의 수를 각 직원별로 계산하는 쿼리를 작성하세요."
        ]
    },
    {
        "tables": """
Orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    total_amount DECIMAL(10,2)
)

OrderDetails (
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2)
)

Products (
    product_id INT PRIMARY KEY,
    name VARCHAR(100),
    category_id INT,
    unit_price DECIMAL(10,2)
)
        """,
        "sample_data": {
            "Orders": [
                {"order_id": 1, "customer_id": 1, "order_date": "2023-01-01", "total_amount": 100.00},
                {"order_id": 2, "customer_id": 2, "order_date": "2023-01-02", "total_amount": 150.00},
                {"order_id": 3, "customer_id": 3, "order_date": "2023-01-03", "total_amount": 200.00}
            ],
            "OrderDetails": [
                {"order_id": 1, "product_id": 1, "quantity": 2, "unit_price": 50.00},
                {"order_id": 2, "product_id": 2, "quantity": 3, "unit_price": 50.00},
                {"order_id": 3, "product_id": 3, "quantity": 4, "unit_price": 50.00}
            ],
            "Products": [
                {"product_id": 1, "name": "Product A", "category_id": 1, "unit_price": 50.00},
                {"product_id": 2, "name": "Product B", "category_id": 2, "unit_price": 50.00},
                {"product_id": 3, "name": "Product C", "category_id": 3, "unit_price": 50.00}
            ]
        },
        "questions": [
            "각 제품별로 전월 대비 판매량 증가율을 계산하는 SQL 쿼리를 작성하세요.",
            "2023년도 월별 매출액이 이전 달보다 증가한 제품들을 찾는 쿼리를 작성하세요.",
            "각 제품별로 가장 많이 주문된 분기와 그 수량을 찾는 쿼리를 작성하세요."
        ]
    },
    {
        "tables": """
Users (
    user_id INT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100),
    join_date DATE
)

Posts (
    post_id INT PRIMARY KEY,
    user_id INT,
    content TEXT,
    post_date TIMESTAMP,
    likes INT
)

Comments (
    comment_id INT PRIMARY KEY,
    post_id INT,
    user_id INT,
    content TEXT,
    comment_date TIMESTAMP
)
        """,
        "sample_data": {
            "Users": [
                {"user_id": 1, "name": "김철수", "email": "kim@example.com", "join_date": "2022-03-15"},
                {"user_id": 2, "name": "이영희", "email": "lee@example.com", "join_date": "2021-08-22"},
                {"user_id": 3, "name": "박민준", "email": "park@example.com", "join_date": "2023-01-10"}
            ],
            "Posts": [
                {"post_id": 1, "user_id": 1, "content": "First post", "post_date": "2023-01-01", "likes": 10},
                {"post_id": 2, "user_id": 2, "content": "Second post", "post_date": "2023-01-02", "likes": 15},
                {"post_id": 3, "user_id": 3, "content": "Third post", "post_date": "2023-01-03", "likes": 20}
            ],
            "Comments": [
                {"comment_id": 1, "post_id": 1, "user_id": 1, "content": "First comment", "comment_date": "2023-01-01"},
                {"comment_id": 2, "post_id": 2, "user_id": 2, "content": "Second comment", "comment_date": "2023-01-02"},
                {"comment_id": 3, "post_id": 3, "user_id": 3, "content": "Third comment", "comment_date": "2023-01-03"}
            ]
        },
        "questions": [
            "사용자별로 작성한 게시물의 평균 좋아요 수를 계산하는 쿼리를 작성하세요.",
            "자신의 게시물에 달린 댓글 수가 가장 많은 상위 5명의 사용자를 찾는 쿼리를 작성하세요.",
            "2023년에 매달 꾸준히 1개 이상의 게시물을 작성한 사용자를 찾는 쿼리를 작성하세요."
        ]
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    current_question = request.json.get('current_question', '')
    
    try:
        # Use GPT4All to generate structured feedback
        system_prompt = """You are a Korean SQL interviewer. Analyze the SQL query and provide feedback in the following format:

[오류 분석]
- 쿼리의 문제점들을 bullet points로 나열

[개선된 답안]
개선된 SQL 쿼리 제시

[점수] 
100점 만점 기준으로 점수 제시 (예: 75점)
"""
        prompt_template = f"""
        System: {system_prompt}
        Question: {current_question}
        User's Answer: {user_message}
        Assistant: Let me analyze this SQL query.
        """
        
        response = model.generate(
            prompt=prompt_template,
            max_tokens=800,
            temp=0.7,
            top_k=40,
            top_p=0.4,
            repeat_penalty=1.18
        )
        
        # Store the conversation in database
        save_conversation(current_question, user_message, response)
        
        return jsonify({
            "response": response,
            "score": extract_score(response)
        })
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}", "score": 0})

@app.route('/start_test', methods=['POST'])
def start_test():
    test_case = random.choice(SQL_TEST_CASES)
    question = random.choice(test_case["questions"])
    
    return jsonify({
        "tables": test_case["tables"],
        "sample_data": test_case["sample_data"],
        "question": question
    })

# Add these new functions
from datetime import datetime
import sqlite3

def init_db():
    conn = sqlite3.connect('sql_test.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  question TEXT,
                  answer TEXT,
                  feedback TEXT,
                  score INTEGER,
                  date TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_conversation(question, answer, feedback):
    score = extract_score(feedback)
    conn = sqlite3.connect('sql_test.db')
    c = conn.cursor()
    c.execute('INSERT INTO conversations (question, answer, feedback, score, date) VALUES (?, ?, ?, ?, ?)',
             (question, answer, feedback, score, datetime.now()))
    conn.commit()
    conn.close()

def extract_score(feedback):
    try:
        # Look for the score in the feedback (e.g., "[점수] 75점")
        score_line = [line for line in feedback.split('\n') if '[점수]' in line]
        if score_line:
            return int(''.join(filter(str.isdigit, score_line[0])))
        return 0
    except:
        return 0

# Add this to get conversation history
@app.route('/get_conversations')
def get_conversations():
    conn = sqlite3.connect('sql_test.db')
    c = conn.cursor()
    c.execute('SELECT question, answer, feedback, score, date FROM conversations ORDER BY date DESC')
    conversations = c.fetchall()
    conn.close()
    
    # Format the conversations for display
    formatted_conversations = []
    for conv in conversations:
        question = conv[0]
        formatted_conversations.append({
            'question': question,
            'answer': conv[1],
            'feedback': conv[2],
            'score': conv[3],
            'date': conv[4]
        })
    
    return jsonify(conversations=formatted_conversations)

# Add this at the end of the file
init_db()  # Initialize the database when the app starts

if __name__ == '__main__':
    app.run(debug=True)
