
# DjSurvey — Dynamic Survey Builder (Django + HTMX)

A full-featured, production-ready Survey Builder & Response Platform built entirely with Django, Django Forms/Formsets, and HTMX — no frontend frameworks required.

DjSurvey demonstrates how far you can go with modern Django patterns: dynamic forms, inline formsets, unique prefixes, HTMX-powered partial rendering, validation rules, and an end-to-end system where survey creators can build complex questionnaires and users can submit responses smoothly without page reloads.

This project is part of my backend portfolio and showcases real-world problem-solving in Django + HTMX.

## 🚀 Features
### 🛠 Survey Creation (Creator Dashboard)

- Create a survey with title & description
- Add unlimited questions
- Each question supports:
    - Text Answer
    - Multiple Choice (with dynamic choice formset)
    - HTMX-powered dynamic rendering
    - Add/remove questions without page reload
    - Changing question type instantly updates available inputs
    - Add/remove choices dynamically

### 📝 Smart Form Architecture
- Custom Django InlineFormset for choices
- Custom form prefixes to avoid ID collisions
- Field-level and form-level validation
- Survey builder supports:
    - Required minimum choices for multiple-choice
    - Preventing empty choices
    - Cleaning unused forms automatically
    - Handling creation + edit modes cleanly

### 📩 Response Submission
- Users can see survey questions dynamically generated from the DB
- Each question is paired with an AnswerForm
- A single POST request saves all answers at once
- Clean, reliable validation flow
- Prevents duplicate answers using update_or_create
- Works for both text and multiple-choice questions

### 🔎 Creator Analytics
- Survey creators can browse submitted responses
- Answers grouped cleanly per question
- Shows counts and all submitted values
- Optimized DB queries for response fetching

### ⚡ Powered Entirely by Django + HTMX
- Zero React/Vue/Angular
- Zero REST API needed for the UI
- All interactivity powered by server-rendered partials + HTMX

## 🧠 Architecture Overview
```
Survey
 ├── Question
 │     ├── title
 │     ├── question_type (text | multiple_choice)
 │     └── related Choice(s)
 └── Answers (per user)
        ├── text_answer (Text questions)
        └── choice (Multiple-choice)
```

### Dynamic UI Flow (HTMX)
- [Question Type Select] --(change)--> /choice-area/partial
    - returns dynamic choice formset
    - rendered inside #choice-area-{{prefix}}

### Response Submission Flow
- Form (all AnswerForms) → POST /survey/<slug>/response/
    - Validate each AnswerForm
    - update_or_create answers
    - redirect to response summary

## 📂 Project Structure
```
DjSurvey/
│
├── survey/
│   ├── models.py        # Survey, Question, Choice, Answer
│   ├── forms.py         # QuestionForm, ChoiceFormset, AnswerForm
│   ├── views.py         # Creation, editing, dynamic HTMX endpoints
│   ├── templates/
│   │   ├── survey/
│   │   │   ├── create/
│   │   │   ├── edit/
│   │   │   ├── htmx_partials/
│   │   │   ├── response/
│   │   │   └── detail/
│   └── utils/           # Helper logic for prefixes, cleaning, formset tools
│
├── accounts/            # Authentication
├── static/
└── templates/
```

## 📸 Video Preview

https://github.com/user-attachments/assets/55675b91-b608-4a4f-ab6f-e82f075472f3



## 🧩 Key Technical Highlights
### ✨ HTMX Integration
- hx-post, hx-target, hx-swap, hx-trigger used for:
    - Dynamically loading choice formsets
    - Rendering updated question blocks
    - Inline partial updates

### ✨ Complex Django Formset Logic
- Custom InlineChoiceFormset with:
    - Minimum choice enforcement
    - Removal of empty forms
    - Validation logic based on question type

### ✨ Custom Prefix System
- Django formsets produce identical field IDs by default — problematic when multiple forms exist on the same page.
- This project solves it using:
    - `prefix = f"question-{question.id or 'new'}"`
    - This ensures:
        - Stable IDs
        - Correct HTMX updates
        - No HTML duplication errors

### ✨ Clean Answer Saving Flow
- All answers submitted in one request
- Bound AnswerForms per question
- `update_or_create()` prevents duplicates
- Efficient DB access with `select_related/prefetch`

## 🧪 Testing the Project
Install & run:
```
git clone https://github.com/Farzan-79/DjSurvey.git
cd DjSurvey
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Access:
- http://127.0.0.1:8000/ → homepage
- /survey/create/ → create survey
- /survey/<slug>/response/ → answer survey

## 📚 Tech Stack
- Python 3
- Django 4+
- Django Formsets & ModelForms
- HTMX
- Bootstrap (styling)
- SQLite / PostgreSQL
- Custom validation & model logic

## 🧑‍💻 About This Project
This project showcases:
- Advanced Django backend knowledge
- Clean architecture principles
- Complex dynamic forms
- Partial rendering with HTMX
- Real-world model relationships
- User-specific access logic
- Solid template structuring
- Robust formset validation

## 🚀 Future Extensions and Scalability
This project is designed with scalability in mind. It provides a solid foundation that can be easily extended to include new features and functionalities. Some areas for future development include:

- **Django Rest Framework (DRF)**: An API layer can be added to provide RESTful services for the survey data, allowing external applications to interact with the surveys and responses.
- **Real-time Updates**: Using technologies like WebSockets or Django Channels, real-time features (e.g., live survey results) can be incorporated.
- **Advanced Analytics**: Further analytical features can be added, such as advanced data visualizations and more detailed response breakdowns.
- **User Authentication & Permissions**: More complex user roles and permissions can be introduced to allow for advanced survey access controls and multi-user functionality.
- **Internationalization**: With the current architecture, this project can be expanded to support multiple languages and localization.

This application has a lot of potential to grow as the needs of the user base evolve, and I'm open to adding more features as required.

If you want to hire me to build or extend a Django/HTMX/DRF project, feel free to reach out or open an issue.

## 📬 Contact
Developer: Farzan
GitHub: https://github.com/Farzan-79
LinkedIn: https://www.linkedin.com/in/farzan79/
Email: far.kalantarii@gmail.com

## ❤️ License
MIT — free to use, modify, distribute.
