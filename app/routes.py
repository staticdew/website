# routes.py
#
# This file defines the different URLs (routes) our webserver implements.
# Handlers for each of these routes, known as views, are also defined here.
#
# Yeahhh boiiii - das my guy - Clancy Rye

import csv
import datetime
import os

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import app
from app.appointment import *
from app.centre import *
from app.forms import LoginForm, RegistrationForm
from app.health_care_system import HealthCareSystem
from app.user import *
from app.user_manager import UserManager
from app.centre_manager import CentreManager

import sys
import logging
from termcolor import colored

logger = logging.getLogger(__name__)
# Dirty hack - basically makes sure we don't try to use the database unless we're sure it's ready.
# Otherwise Flask will try to use the database - even if we are using 'flask init_db' or 'flask rm_db'
if sys.argv[1] == 'run':
    hsc = HealthCareSystem()

from app.models import Centre, User


@app.route('/')
@login_required
def index():
    """
    This view represents the handler for the root 'index' or 'home' screen of
    the application.

    This is loaded when no route is specified in the URL, or when redirected to
    as a 'safety net'.
    """

    return render_template('index.html', title='home')


@app.route('/booking', methods=['GET', 'POST'])
def booking():


    pass
    # done_booking = 0
    # now = str(datetime.datetime.now())
    # date = now[0:now.find(" ")]
    # time = now[now.find(" ") + 1:now.find(".") - 3]
    # app = ""
    # if request.method == "POST":
    #     book = int(request.form["book"])
    #     # parameters for search
    #     is_centre_search = request.form["is_centre_search"]  # search for centres
    #     p = request.form["p"]  # search for providers
    #     search = request.form["search"]  # search input
    #     provider = request.form['provider']  # provider currently being booked for
    #
    #     for prov in provider_list:
    #         if prov._full_name == provider:
    #             provider_class = prov  # returns the instance of provider
    #
    #     if (book):  # if we are booking
    #
    #         # set date/time/centre
    #
    #         date = request.form["date"]
    #         centre = request.form["centre"]
    #         time = str(request.form["time"])
    #         length = int(request.form["length"])
    #
    #         # convert time to minutes then add on the legnth of appointment.csv and convert back to time
    #         total_len = time_to_min(time) + length
    #         time_end = min_to_time(total_len)
    #
    #         print("curent appointment.csv starts:" + time + " ends:" + time_end)
    #         # checking the times and dates are valid
    #         for app in provider_class._appointment_list:
    #             clash = time_clash(time, app._start_time, time_end, app._end_time)
    #             if (clash):
    #                 return render_template('booking.html', user=curr_user, is_centre_search=is_centre_search, p=p, search=search, \
    #                                        provider=provider_class, book=-1, t=time, d=date, app=app)
    #
    #         if (date == ""):  # just for testing, this should never happen
    #             return render_template('booking.html', user=curr_user, is_centre_search=is_centre_search, p=p, search=search, provider=provider_class,
    #                                    noDate=1)
    #
    #         app = Appointment(start_time=time, end_time=time_end, date=date, patient=curr_user,
    #                           health_care_provider=provider_class, centre=centre)
    #         done_booking = 1
    #
    # return render_template('booking.html', user=curr_user, is_centre_search=is_centre_search, p=p, search=search, provider=provider_class,
    #                        book=done_booking, t=time, d=date, app=app)


@app.route('/profile/<name>', methods=['POST', 'GET'])
def profile(name):
    """
    Endpoint that handles User and Centre profiles.

    :param name: The user or centre name whose profile we're viewing.
    :return:
      GET:  Creates and renders a profile page for a Centre or User.
      POST: ???
    """

    # Determine what kind of profile we should be rendering
    profile_type = hsc.determine_type(name)
    if profile_type == 'user':
        obj = UserManager.get_user(name)
    elif profile_type == 'centre':
        obj = CentreManager.get_centre(name)
    else:
        return 'Something went wrong, undetermined type for "%s"' % name

    logger.warn(colored(name, "red"))
    logger.warn(colored(obj, "red"))

    return render_template('profile.html', object=obj, type=profile_type)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    This view represents the handler for our registration screen. Its behaviour
    varies depending on which HTTP verb is used with it:

        GET:  Creates and renders registration page, along with form.
        POST: Submits registration form for validation & processing.
    """

    # If the user is already logged in, get 'em outta here.
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Otherwise, create a RegistrationForm for them to enter their details,
    # then validate said details after submission.
    form = RegistrationForm()
    if form.validate_on_submit():
        # If entered details have passed validation, create the new user and add them to our user table.
        # -- TODO: We're assuming user is a patient, should update form to allow for role and workplace.
        hsc.user_manager.add_user(form.username.data, form.email.data, form.password.data, role='Patient')

        flash('Woohoo, you did it! Redirecting to login screen.')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    This view represents the handler for the 'login' screen. Its behaviour
    varies depending on which HTTP verb is used with it:

        GET:  Creates and renders login page, along with form.
        POST: Attempts to authenticate user with submitted login form.
    """

    # If user is already logged in, redirect them to the index page.
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Otherwise, create a LoginForm for them to enter their credz, then attempt
    # to authenticate them after validation.
    form = LoginForm()
    if form.validate_on_submit():

        # If credz pass validation, attempt to log the user in using them.
        if hsc.user_manager.login_user(form.username.data, form.password.data):
            # If we've arrived here, their credz are correct and they have been authenticated, redirect to the index.
            return redirect(url_for('index'))

        else:
            # User has failed to log in, display an error and redirect to the login screen.
            flash('Error: Provided username or password is incorrect.')
            return redirect(url_for('login'))

    # Render the login screen.
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    """
    This view simply logs out the user, if they're logged in. (By terminating
    their current session).

    If the user is not logged in, this method does nothing.
    """

    hsc.user_manager.logout_user()
    return redirect(url_for('index'))


@app.route('/appointments')
def appointments():
    return render_template('appointments.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Endpoint that handles user searches. Given specific search criteria, queries the Medi-soft database then displays
    the results to the user.

    :return:
        GET:  Creates and renders the search page, along with search forms used to submit a search.
        POST: Submits search query and returns renders results.
    """

    logger.info(colored(request.form, "red"))
    results_found = False

    # If user is submitting a search, perform the search and display results
    if request.method == 'POST':
        # Initialise results to be None so we don't error on return.
        centre_results = user_results = []

        # Fetch the search query and search options.
        do_centre_search = request.form.get('do_centre_search', False)
        do_user_search = request.form.get('do_user_search', False)

        # do_centre_search = do_provider_search = False
        logger.info(colored("do_centre_search: %s" % do_centre_search, 'red'))
        logger.info(colored("do_user_search: %s" % do_user_search, 'red'))

        # # If we're performing a Centre search, fetch appropriate variables.
        if do_centre_search:

            name = request.form['c_name']
            type = request.form['c_type']
            suburb = request.form['c_suburb']
            centre_results = Centre.do_search(name, type, suburb)

            logger.info(colored("Centre results:", "red"))
            logger.info(colored(centre_results, "red"))

        # If we're performing a Provider search, fetch appropriate variables.
        if do_user_search:

            name = request.form['u_name']
            type = request.form['u_type']
            user_results = User.do_search(name, type)

            logger.info(colored("User results:", "red"))
            logger.info(colored(user_results, "red"))

        # If there are any results, set results_found to True, otherwise set it to False.
        if len(centre_results) > 0 or len(user_results) > 0:
            results_found = True
        else:
            results_found = False

        return render_template('search.html', form=request.form, results_found=results_found,
                               centre_results=centre_results, user_results=user_results)
    return render_template('search.html', form=None, results_found=results_found, display_results=False, title='Search')


@app.route('/manage_bookings', methods=["GET", "POST"])
def manage_bookings():
    """
    Enables the user to view their current bookings / appointments.

    :return:
        GET:  Creates and renders the booking page, along with forms used to book an appointment.
        POST: ??
    """

    logger.warn(colored(current_user.username, 'yellow'))
    return render_template('currBooking.html', user=current_user)

    # cancel = 0
    # if (request.method == 'POST'):
    #     view = int(request.form['view'])
    #     if (view):
    #         is_centre_search = request.form['is_centre_search']
    #         p = request.form['p']
    #         s = request.form['search']
    #         result = request.form['result']
    #         provider = request.form['provider']
    #
    #         return render_template('currBooking.html', user=curr_user, cancel=cancel, l=len(curr_user._appointment_list),
    #                                view=view, is_centre_search=is_centre_search, p=p, search=s, result=result, provider=provider)
    #
    #     name = request.form['name']
    #     time = request.form['time']
    #     date = request.form['date']
    #     centre = request.form['centre']
    #     print(name + time + date + centre)
    #     for a in curr_user._appointment_list:
    #         if (
    #                                 time == a._start_time and date == a._date and centre == a._centre and name == a._health_care_provider._full_name):
    #             curr_user.remove_appointment(a)
    #             cancel = 1
    #             # curr_user.removeAppointment(app)
    # length = len(curr_user._appointment_list)
    # return render_template('currBooking.html', user=curr_user, cancel=cancel, l=length)
