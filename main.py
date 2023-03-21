import openai
import os
import logging
from markupsafe import Markup
from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
csrf = CSRFProtect(app)

logging.basicConfig(level=logging.DEBUG)

openai.api_key = os.environ.get('OPENAI_API_KEY')

def init_conversation():
    return [{"role": "system", "content": "You are a Job Description Generator that gives a full length job description based off user input"}]

messages = init_conversation()

class InputForm(FlaskForm):
    company = StringField("Company", validators=[DataRequired()])
    job_title = StringField("Job Title", validators=[DataRequired()])
    years_of_experience = IntegerField("Years of Experience", validators=[DataRequired()])
    additional_requirements = StringField("Additional Requirements", validators=[DataRequired()])
    submit = SubmitField("Generate")

def CustomChatGPT(user_input):
    global messages
    messages = init_conversation()
    messages.append({"role": "user", "content": user_input})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        ChatGPT_reply = response["choices"][0]["message"]["content"].strip()
        messages.append({"role": "assistant", "content": ChatGPT_reply})
        return ChatGPT_reply
    except Exception as e:
        app.logger.error(f"Error during OpenAI API call: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    form = InputForm()
    response = None
    response_text = None
    if request.method == 'POST':
        company = form.company.data
        job_title = form.job_title.data
        years_of_experience = form.years_of_experience.data
        additional_requirements = form.additional_requirements.data
        user_input = f"Job Title: {job_title}, Company: {company}, Years of Experience: {years_of_experience}, Additional Requirements: {additional_requirements}"
        response_text = CustomChatGPT(user_input)
    else:
        company = request.args.get('company', '')
        job_title = request.args.get('jobTitle', '')
        years_of_experience = request.args.get('yearsOfExperience', '')

        if job_title:
            user_input = f"Job Title: {job_title}"
            if company:
                user_input += f", Company: {company}"
            if years_of_experience:
                user_input += f", Years of Experience: {years_of_experience}"
            response_text = CustomChatGPT(user_input)
            if response_text:
                response = Markup(markdown.markdown(response_text))

    print(f"Response text: {response_text}")  # Add this line
    return render_template('index.html', form=form, response=response)

@app.route('/generate')
def generate():
    company = request.args.get('company')
    job_title = request.args.get('jobTitle')
    years_of_experience = request.args.get('yearsOfExperience')

    # Call the function to generate the job description and return it as text
    job_description = CustomChatGPT(f"Job Title: {job_title}, Company: {company}, Years of Experience: {years_of_experience}")
    return job_description

@app.route('/generate_from_params')
def generate_from_params():
    company = request.args.get('company')
    job_title = request.args.get('jobTitle')
    years_of_experience = request.args.get('yearsOfExperience')
    additional_requirements = request.args.get('additionalRequirements')
    job_description = CustomChatGPT(f"Job Title: {job_title}, Company: {company}, Years of Experience: {years_of_experience}, Additional Requirements: {additional_requirements}")
    return jsonify(job_description=job_description)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 80)))
