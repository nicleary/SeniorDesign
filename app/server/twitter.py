from db.database_connection import create_session
from authorization.auth_utils import get_token, does_user_have_permission, secure_hash
from util.make_error import make_error
from server.tasks import tweet_puller, retrieve_user_info_by_id, retrieve_users_info_by_ids, \
    retrieve_user_info_by_username, get_job
from db.models import User, Task
from db.db_utils import get_single_object, create_single_object

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify
)
from celery import uuid
import time

bp = Blueprint('twitter', __name__)


@bp.route('/tweets/stream/search', methods=(['GET']))
def stream_search():
    session = create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, 'No access token provided', 'Provide access token')
    user = get_single_object(session, User, key_hash=secure_hash(token))
    if user is None or not does_user_have_permission(user, 'twitter_tasks'):
        session.close()
        return make_error(403, 1, 'Unauthorized access token', 'Contact Nick')
    query_param = request.args.get('query')
    if query_param is None:
        return make_error(405, 1, "No Query", "Add a query parameter")
    task_id = uuid()
    tweet_puller.apply_async((query_param, 0), task_id=task_id)
    created = create_single_object(session, Task, task_id=task_id, defaults={
        'user_id': user.id,
        'task_type': 'tweets.stream.search',
        'status': 'PENDING',
        'message': 'Task has been queued'
    })
    user.tasks.append(created)
    session.commit()
    session.close()
    return jsonify("Task created")


@bp.route('/users/lookup/by_id/single', methods=(['GET']))
def single_user_lookup():
    session = create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, 'No access token provided', 'Provide access token')
    user = get_single_object(session, User, key_hash=secure_hash(token))
    if user is None or not does_user_have_permission(user, 'twitter_tasks'):
        session.close()
        return make_error(403, 1, 'Unauthorized access token', 'Contact Nick')
    user_param = request.args.get('user')
    if user_param is None:
        return make_error(405, 1, "No user", "Add a user parameter")
    task_id = uuid()
    retrieve_user_info_by_id.apply_async((user_param, 0), task_id=task_id)
    session.close()
    return jsonify("Task created")


@bp.route('/users/lookup/by_username/single', methods=(['GET']))
def single_user_lookup_username():
    session = create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, 'No access token provided', 'Provide access token')
    user = get_single_object(session, User, key_hash=secure_hash(token))
    if user is None or not does_user_have_permission(user, 'twitter_tasks'):
        session.close()
        return make_error(403, 1, 'Unauthorized access token', 'Contact Nick')
    user_param = request.args.get('username')
    if user_param is None:
        return make_error(405, 1, "No user", "Add a user parameter")
    task_id = uuid()
    retrieve_user_info_by_username.apply_async((user_param, 0), task_id=task_id)
    session.close()
    return jsonify("Task created")


@bp.route('/users/lookup/by_id/multiple', methods=(['GET']))
def multiple_user_lookup():
    session = create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, 'No access token provided', 'Provide access token')
    user = get_single_object(session, User, key_hash=secure_hash(token))
    if user is None or not does_user_have_permission(user, 'twitter_tasks'):
        session.close()
        return make_error(403, 1, 'Unauthorized access token', 'Contact Nick')
    users_param = request.args.get('users')
    if users_param is None:
        return make_error(405, 1, "No user", "Add a user parameter")
    task_id = uuid()
    retrieve_users_info_by_ids.apply_async((users_param, 0), task_id=task_id)
    session.close()
    return jsonify("Task created")
