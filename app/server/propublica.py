from db.database_connection import create_session
from authorization.auth_utils import get_token, does_user_have_permission, secure_hash
from util.make_error import make_error
from server.tasks import get_bill_data_by_congress
from db.models import User
from db.db_utils import get_single_object

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify
)

bp = Blueprint('propublica', __name__)


@bp.route('/bills/<congress>/<chamber>', methods=(['GET']))
def get_bills_by_congress(congress, chamber):
    session = create_session()
    token = get_token(request)
    if token is None:
        return make_error(401, 1, 'No access token provided', 'Provide access token')
    user = get_single_object(session, User, key_hash=secure_hash(token))
    if user is None or not does_user_have_permission(user, 'pro_publica_tasks'):
        session.close()
        return make_error(403, 1, 'Unauthorized access token', 'Contact Nick')
    if chamber not in ['senate', 'house']:
        session.close()
        return make_error(405, 1, 'Chamber is not either senate or house', 'Specify the chamber as house or senate')
    if not int(congress) >= 109:
        session.close()
        return make_error(405, 2, 'Congress is must be >= 109', 'Specify congress >= 109')
    get_bill_data_by_congress.delay(int(congress), chamber)
    session.close()
    return jsonify("Task created")