from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import sys

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        #note = request.form.get('note')

        # if len(note) < 1:
        #    flash('Note is too short!', category='error')
        # else:
        #    new_note = Note(data=note, User_id=current_user.id)
        #    db.session.add(new_note)
        #    db.session.commit()
        #    flash('Note added!', category='success')

        sys.path.append(
            "C:/Users/Uživatel/Desktop/python/Flask-Web-App-Tutorial-main/website/extractors")
        try:
            import main_extractor
            flash('Extractor prebehol uspesne!', category='success')
        except:
            flash('V extractore nastala chyba!', category='error')
    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
