from flask import Flask, render_template, request, redirect, session, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # შეცვალე ნამდვილ აპლიკაციაში!

USERS_FILE = 'users.json'
ANSWERS_FILE = 'answers.json'

def load_json(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('questionnaire'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_json(USERS_FILE)
        if email in users:
            flash('მომხმარებელი უკვე არსებობს!')
            return redirect(url_for('register'))
        users[email] = {'password': password}
        save_json(USERS_FILE, users)
        flash('რეგისტრაცია წარმატებით დასრულდა, შედით სისტემაში.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_json(USERS_FILE)
        if email in users and users[email]['password'] == password:
            session['user'] = email
            return redirect(url_for('questionnaire'))
        flash('ელ-ფოსტა ან პაროლი არასწორია!')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('გამოსვლა წარმატებით განხორციელდა.')
    return redirect(url_for('login'))

@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        closed = {}
        for i in range(1, 11):
            closed[f'q{i}'] = request.form.get(f'q{i}', '')

        single = {}
        for i in range(11, 16):
            single[f'q{i}'] = request.form.get(f'q{i}', '')

        multi = {}
        for i in range(16, 21):
            # .getlist აბრუნებს ყველა მონიშნულ მნიშვნელობას როგორც სიას
            multi[f'q{i}'] = request.form.getlist(f'q{i}')

        answers = load_json(ANSWERS_FILE)
        answers[session['user']] = {'closed': closed, 'single': single, 'multi': multi}
        save_json(ANSWERS_FILE, answers)
        flash('თქვენი პასუხი წარმატებით შეინახა!')
        return redirect(url_for('questionnaire'))

    answers = load_json(ANSWERS_FILE)
    user_answer = answers.get(session['user'], {'closed': {}, 'single': {}, 'multi': {}})
    return render_template('questionnaire.html', user=session['user'], user_answer=user_answer)

@app.route('/admin/answers')
def admin_answers():
    # პრიმიტიული დაცვა: (მაგალითად მხოლოდ შენი იმეილით)
    if 'user' not in session or session['user'] != 'achimgebr12@gmail.com':
        return "Access denied!", 403
    answers = load_json(ANSWERS_FILE)
    return render_template('admin_answers.html', answers=answers)


if __name__ == '__main__':
    app.run(debug=True)
